import os
import can
import time
from DAQState import DAQState
from messageIDs import canMessageSort
import csv
import threading
from labjack import ljm
global ECUData
can.rc['interface']='socketcan'

os.system('sudo ip link set can0 type can bitrate 250000')
os.system('sudo ifconfig can0 up')

can0= can.interface.Bus(channel="can0",interface="socketcan")
    
class DAQObject:
    def __init__(self):
     
        self.currentState = DAQState.INIT
        self.csvFilePath = "data.csv"
        self.file = open(self.csvFilePath, mode='w')
        self.writer = csv.writer(self.file)

        
        self.ECUData = [None] * 16
        self.LJData = []
        self.writeData = [None]
        
        self.handle = ljm.openS("T7")
        info = ljm.getHandleInfo(self.handle)
        print("\nOpened a LabJack with Device type: %i, Connection type: %i,\n"
          "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per MB: %i" %
          (info[0], info[1], info[2], ljm.numberToIP(info[3]), info[4], info[5]))

    def setSMState(self, nextState):
        lastState = self.currentState
        self.currentState = nextState
    
    def readLJ(self):
        return ljm.eReadName(self.handle,"AIN0")
        

    def readCAN(self):
        while True:
            with can.Bus() as bus:
                msg = bus.recv()  
            
                index = canMessageSort.get(msg.arbitration_id)
                self.ECUData[index] = msg.data
                
               
        
    def DAQRun(self):
        
        nextTime = time.time()

        while True:
            
            if time.time() < nextTime:
                time.sleep(0)
            
            else:
                nextTime = time.time()
                
                if self.currentState == DAQState.INIT:
                    print("xd")
                    self.setSMState(DAQState.COLLECTING)
                    
                if self.currentState == DAQState.COLLECTING:
                    print(self.readLJ())
                    recordedTime = time.time()
                    self.writeData.append(time.time())
                    self.writeData.extend(self.ECUData)
                    self.writer.writerow(self.writeData)
                    self.writeData.clear()
                    
                
    def __del__(self):
        os.system('sudo ifconfig can0 down')
    


if __name__ == "__main__":
    DAQ = DAQObject()
    canbus = threading.Thread(target=DAQ.readCAN)
    run = threading.Thread(target=DAQ.DAQRun)
    
    canbus.start()
    run.start()
    print("test")
    time.sleep(10)
    
    
