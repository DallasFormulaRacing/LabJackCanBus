import logging
import os
import sys
import threading
import time
import traceback
from datetime import datetime
from typing import List

import numpy as np
import pandas as pd
from labjack import ljm
from telegraf.client import TelegrafClient


logging.basicConfig(level=logging.DEBUG)

TIME_IDX = "SYSTEM_TIMER_20HZ"


class Extension(object):
    aScanListNames: List[str]

    def setup(self, _si: "Stream") -> None:
        """Initializes the extension

        Args:
            _si (Stream): The stream object
        """

    def process(self, _data: pd.DataFrame) -> None:
        """Processes the data

        Args:
            _data (pd.DataFrame): The data to process
        """

    def save(self, _fp: str, *, _index: bool = False) -> None:
        """Saves the data

        Args:
            _fp (str): The file path to save to
            _index (bool, optional): Whether to save the index. Defaults to False.
        """


class Linpot(Extension):
    def __init__(self):
        self.aScanList = {
            "AIN1": "Front Left",
            "AIN2": "Rear Left",
            "AIN3": "Rear Right",
            "AIN4": "Front Left",
        }

        self.aScanListNames = list(self.aScanList.keys())
        self.lock = threading.Lock()
        print("CREATING PANDAS DATAFRAME")
        self.df = pd.DataFrame(columns=list(self.aScanList.values()) + [TIME_IDX])
        self.telegraf_client = TelegrafClient(host="localhost", port=8092)

    def setup(self, si: "Stream"):
        si.aScanListNames.extend(self.aScanListNames)

        frames = [
            "AIN1_RESOLUTION_INDEX",
            "AIN2_RESOLUTION_INDEX",
            "AIN3_RESOLUTION_INDEX",
            "AIN4_RESOLUTION_INDEX",
        ]
        ljm.eWriteNames(si.handle, len(frames), frames, [12] * len(frames))

    def send_linpot_metrics(self, data: pd.DataFrame):

        with self.lock:
            for column_name in data.columns:

                if column_name == "SYSTEM_TIMER_20HZ":
                    continue

                metric_name = "_".join(column_name.lower().split())
                value = data[column_name].iloc[-1]
                time = data["SYSTEM_TIMER_20HZ"].iloc[-1]
                self.telegraf_client.metric(metric_name, value, tags={"source": "linpot"}, timestamp=time)

    def process(self, data: pd.DataFrame):
        data.rename(columns=self.aScanList, inplace=True)

        with self.lock:
            self.df = pd.concat([self.df, data], ignore_index=True)
            self.send_linpot_metrics(data)
        print(self.df)

    def save(self, fp: str, *, index: bool = False) -> None:
        fp = fp.format("linpot")
        exists = os.path.isfile(fp)
        with self.lock:
            print("saving: ", self.df)
            self.df.to_csv(fp.format("linpot"), index=index, header=not exists)

            # clear the existing one
            self.df = pd.DataFrame(columns=self.df.columns)


class Stream:
    def __init__(self, handle, extensions: List[Extension]):
        # stats
        self.handle = handle  # T7 device, Any connection, Any identifier
        self.scanRate = 100  # sets scanning rate (samples per second)
        self.scansPerRead = int(
            self.scanRate / 2
        )  # Initializes the number of scans per read
        self.streamLengthMS = 0  # Sets the stream length to run fo the desires duration

        self.done = False  # a flag to enable when program will gracefully shutdown

        self.aScanListNames = [
            "FIO_STATE",
            "SYSTEM_TIMER_20HZ",
            "STREAM_DATA_CAPTURE_16",
        ]  # the proper names for input

        self.streamRead = 0  # tbe amount of stream reads
        self.totSkip = 0  # Counts the amount of scans skipped
        self.totScans = 0  # Counts total scans
        self.logger = logging.getLogger("Stream")
        info = ljm.getHandleInfo(self.handle)

        self.logger.info(
            "Opened a LabJack with Device type: %i, Connection type: %i,\n"
            "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per MB: %i",
            info[0],
            info[1],
            info[2],
            ljm.numberToIP(info[3]),
            info[4],
            info[5],
        )

        # Initializing defaults
        self.extensions = extensions
        try:
            # Ensure triggered stream is disabled.
            ljm.eWriteName(self.handle, "STREAM_TRIGGER_INDEX", 0)

            # Enabling internally-clocked stream.
            ljm.eWriteName(self.handle, "STREAM_CLOCK_SOURCE", 0)

            ljm.eWriteName(self.handle, "STREAM_SETTLING_US", 0)

            # Enabling internally-clocked stream.
            ljm.eWriteName(self.handle, "STREAM_RESOLUTION_INDEX", 2)
        except ljm.LJMError:
            pass

        for extension in extensions:
            try:
                self.logger.debug("Setting up extension: %s", type(extension).__name__)

                extension.setup(self)
            except Exception as exc:  # pylint: disable=broad-except
                self.logger.warning(
                    "Failed to setup extension %s because %s", str(extension), str(exc)
                )
                traceback.print_exc()
                exit(1)
            else:
                self.logger.info(
                    "Setup %s extension%s",
                    len(extensions),
                    "s" if len(extensions) != 1 else "",
                )

    @property
    def numAddresses(self):
        return len(self.aScanListNames)

    @property
    def aScanList(self):
        return ljm.namesToAddresses(self.numAddresses, self.aScanListNames)[0]

    def process_buffer_callback(self, arg):
        """
        The threaded callback that unpacks buffer information and sends it to the extensions
        """
        if self.handle != arg:
            self.logger.error("myStreamReadCallback - Unexpected argument: %d", arg)
            return

        # Check if stream is done so that we don't continue processing.
        if self.done:
            return

        string = "\niteration: %3d\n" % self.streamRead
        self.streamRead += 1

        try:
            ret = ljm.eStreamRead(self.handle)
            aData = ret[0]
            deviceScanBacklog = ret[1]
            ljmScanBackLog = ret[2]
            # print("data: ", [i for p, i in enumerate(si.aData) if p % si.numAddresses == 0])
            scans = len(aData) / self.numAddresses
            self.totScans += scans

            # Count the skipped samples which are indicated by -9999 values. Missed
            # samples occur after a device's stream buffer overflows and are
            # reported after auto-recover mode ends.
            curSkip = aData.count(-9999.0)
            self.totSkip += curSkip

            string = ""
            for j in range(0, self.numAddresses):
                string += "%s = %0.5f, " % (self.aScanListNames[j], aData[j])

            self.logger.info(
                "\niteration: %3d\n  1st scan out of %i: %s\n  Scans Skipped = %0.0f, Scan Backlogs: Device = %i, LJM = %i",
                self.streamRead,
                scans,
                string,
                curSkip / self.numAddresses,
                deviceScanBacklog,
                ljmScanBackLog,
            )

            # Ensure data can be divided equally (no loss/corruption)
            assert len(aData) % len(self.aScanListNames) == 0

            num_rows = len(aData) // len(self.aScanListNames)

            # reshape the 1d array into a 2d array
            data_2d = np.array(aData).reshape(num_rows, len(self.aScanListNames))

            # convert to a pandas dataset for ease of use (can be optimized out if wanted)
            df = pd.DataFrame(data_2d, columns=self.aScanListNames)

            for extension in self.extensions:
                extension.process(
                    df[extension.aScanListNames + ["SYSTEM_TIMER_20HZ"]].copy()
                )

        # If LJM has called this callback, the data is valid, but LJM_eStreamRead
        # may return LJME_STREAM_NOT_RUNNING if another thread (such as the Python
        # main thread) has stopped stream.
        except ljm.LJMError as err:
            if err.errorCode == ljm.errorcodes.STREAM_NOT_RUNNING:
                self.logger.error("eStreamRead returned LJME_STREAM_NOT_RUNNING.")
            else:
                self.logger.error(err)

    def start(self):
        try:
            t0 = datetime.now()

            # Configure and start stream
            print(self.scansPerRead, self.numAddresses, self.aScanList, self.scanRate)
            self.scanRate = ljm.eStreamStart(
                self.handle,
                self.scansPerRead,
                self.numAddresses,
                self.aScanList,
                self.scanRate,
            )
            self.logger.info(
                "\nStream started with a scan rate of %0.0f Hz.", self.scanRate
            )

            # Set the callback function.
            ljm.setStreamCallback(self.handle, self.process_buffer_callback)

            self.logger.info("Stream running and callback set.")
        except ljm.LJMError:
            ljme = sys.exc_info()[1]
            self.logger.error(ljme)
        except Exception:
            e = sys.exc_info()[1]
            self.logger.error(e)
            traceback.print_exc()

    def stop(self):
        try:
            self.logger.info("Stop Stream")
            self.done = True
            ljm.eStreamStop(self.handle)
        except ljm.LJMError:
            ljme = sys.exc_info()[1]
            self.logger.error(ljme)
        except Exception:
            e = sys.exc_info()[1]
            self.logger.error(e)

    def save(self, fp: str):
        for extension in self.extensions:
            extension.save(fp)


if __name__ == "__main__":
    analog_stream = Stream(extensions=[Linpot()])

    analog_stream.start()
    try:
        while not analog_stream.done:
            time.sleep(1)
    except KeyboardInterrupt:
        analog_stream.stop()
    finally:
        analog_stream.save(fp="test-{}.csv")