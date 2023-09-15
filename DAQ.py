import os
import can
import time
from DAQState import DAQState
from messageIDs import canMessageSort
import csv
import threading
from labjack import ljm

global ECUData

can.rc['interface'] = 'socketcan'
os.system('sudo ip link set can0 type can bitrate 250000')
os.system('sudo ifconfig can0 up')
can0 = can.interface.Bus(channel="can0", interface="socketcan")


class DAQObject:

    def __init__(self, output_file: str):

        self.currentState = DAQState.INIT
        self.output_file = output_file
        self.file = open(self.output_file, mode='w')
        self.writer = csv.writer(self.file)
        self.ECUData = [None] * 16
        self.LJData = []
        self.writeData = [None]
        self.handle = ljm.openS("T7")
        info = ljm.getHandleInfo(self.handle)
        self.print_labjack_info(info)

        self.canbus = threading.Thread(target=self.readCAN)
        self.run = threading.Thread(target=self.DAQRun)
        self.can_read_lock = threading.Lock()
        self.daq_run_lock = threading.Lock()
        self.daq_run_lock.acquire()

    def print_labjack_info(self, info) -> None:
        print(f"""\nOpened a LabJack with Device type: {info[0]},\n
            Connection type: {info[1]},\n Serial number: {info[2]},\n
            IP address: {ljm.numberToIP(info[3])},\n Port: {info[4]},\n
            Max bytes per MB: {info[5]}\n""")

    def setSMState(self, nextState: DAQState) -> None:
        self.currentState = nextState

    def readLJ(self):
        return ljm.eReadName(self.handle, "AIN0")

    def start_threads(self):
        self.canbus.start()
        self.run.start()

    def readCAN(self):

        while True:
            with can.Bus() as bus:
                self.daq_run_lock.acquire()
                msg = bus.recv()
                index = canMessageSort.get(msg.arbitration_id)
                self.ECUData[index] = msg.data
                self.daq_run_lock.release()

    def resolveError(self) -> bool:
        try:
            return True
        except ljm.LJMError:
            return False

    def DAQRun(self) -> None:

        nextTime = time.time()

        while True:
            self.can_read_lock.acquire()
            if time.time() < nextTime:
                time.sleep(0)

            else:
                nextTime = time.time()

                if self.currentState == DAQState.INIT:
                    self.setSMState(DAQState.COLLECTING)

                if self.currentState == DAQState.COLLECTING:

                    try:
                        print(self.readLJ())
                    except ljm.LJMError:
                        self.currentState == DAQState.ERROR

                        if self.resolveError():
                            break
                        
                        print("LabJack Error", ljm.LJMError)

                    # recordedTime = time.time()
                    self.writeData.append(time.time())
                    self.writeData.extend(self.ECUData)
                    self.writer.writerow(self.writeData)
                    self.writeData.clear()

            self.can_read_lock.release()

    def __del__(self):

        os.system('sudo ifconfig can0 down')


if __name__ == "__main__":

    DAQ = DAQObject("data/output.csv")
    DAQ.start_threads()

    print("test")
    time.sleep(10)
