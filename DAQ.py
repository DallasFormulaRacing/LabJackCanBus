import time
from DAQState import DAQState
from ReadState import read_state
from read_can import read_can
from read_xl_analog import read_xl_analog
from read_xl import read_xl
import threading
from labjack import ljm
import pandas as pd
from datetime import datetime

class DAQObject:

    def __init__(self, output_file: str):

        self.currentState = DAQState.INIT
        self.output_file = output_file
        self.linpot_df = pd.DataFrame(
            columns=["Time", "Front Right", "Front Left", "Rear Right", "Rear Left"])
        self.LJData = []
        self.writeData = [None]
        self.handle = ljm.openS("T7")

        self.canbus = read_can(channel="can0", interface="socketcan")
        self.run = threading.Thread(target=self.DAQRun)
        self.can_read_lock = threading.Lock()
        self.daq_run_lock = threading.Lock()
        # self.daq_run_lock.acquire()

        self.fr_names = ["AIN1_RESOLUTION_INDEX"]
        self.fl_names = ["AIN2_RESOLUTION_INDEX"]
        self.rr_names = ["AIN3_RESOLUTION_INDEX"]
        self.rl_names = ["AIN4_RESOLUTION_INDEX"]
        self.num_frames = len(self.fr_names)
        self.aValues = [12]
        ljm.eWriteNames(self.handle, self.num_frames, self.fr_names, self.aValues)
        ljm.eWriteNames(self.handle, self.num_frames, self.fl_names, self.aValues)
        ljm.eWriteNames(self.handle, self.num_frames, self.rr_names, self.aValues)
        ljm.eWriteNames(self.handle, self.num_frames, self.rl_names, self.aValues)

        self.run_count = 0

    def setSMState(self, nextState: DAQState) -> None:
        self.currentState = nextState

    def readLJ(self):
        return ljm.eReadName(self.handle, "AIN0")

    def start_threads(self):
        self.canbus.start()
        self.run.start()

    def resolveError(self) -> bool:
        try:
            return True
        except ljm.LJMError:
            return False

    def DAQRun(self) -> None:

        nextTime = time.time()
        index = 0
        while True:

            self.can_read_lock.acquire()
            button_clicked = read_state.read_button_state(self.handle)
            # print(button_clicked)

            if time.time() < nextTime:
                time.sleep(0)

            else:
                nextTime = time.time()

            if button_clicked:
                if self.currentState == DAQState.INIT:
                    print("collecting")
                    self.setSMState(DAQState.COLLECTING)
                elif self.currentState == DAQState.SAVING:
                    print("collecting")
                    self.setSMState(DAQState.COLLECTING)

                if self.currentState == DAQState.COLLECTING:

                    try:
                        read_xl.read_xl_input(self.handle)
                        # print(ljm.eReadName(
                        #     self.handle, "AIN1"))
                        current_time = time.time()
                        self.linpot_df.loc[index, "Time"] = current_time
                        self.linpot_df.loc[index, "Front Right"] = ljm.eReadName(
                            self.handle, "AIN1")
                        self.linpot_df.loc[index, "Front Left"] = ljm.eReadName(
                            self.handle, "AIN2")
                        self.linpot_df.loc[index, "Rear Right"] = ljm.eReadName(
                            self.handle, "AIN3")
                        self.linpot_df.loc[index, "Rear Left"] = ljm.eReadName(
                            self.handle, "AIN4")
                        index += 1
                        read_xl_analog.read_xl(self.handle)
                        # print(self.readLJ())
                        print(self.linpot_df.tail(1))
                        
                        self.linpot_df.to_csv()
                    except ljm.LJMError:
                        self.currentState == DAQState.ERROR

                        if self.resolveError():
                            break

                        print("LabJack Efrrfffor", ljm.LJMError)
                        # self.write_zero_row()

            else:
                if self.currentState == DAQState.COLLECTING:
                    print("saving")
                    
                    now = datetime.strftime(datetime.now(), "%Y-%m-%d_%H-%M-%S")
                    self.linpot_df.to_csv(
                        f"{self.output_file}_linpot_{now}.csv", index=False)
                    
                    # clear linpot_df
                    self.linpot_df = pd.DataFrame(columns=self.linpot_df.columns)
                    
                    self.canbus.flush_buffer(file=f"{self.output_file}_ecu_{now}.csv")
                    self.setSMState(DAQState.SAVING)
                    self.run_count += 1

            self.can_read_lock.release()

    def __del__(self):
        if getattr(self, "canbus", None):
            self.canbus.stop()


if __name__ == "__main__":

    DAQ = DAQObject("data/output2")
    DAQ.start_threads()

    print("test")
    time.sleep(10)
