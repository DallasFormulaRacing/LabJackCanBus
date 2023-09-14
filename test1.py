import os
import can
import threading
import time
from messageIDs import canMessageSort
from labjack import ljm

can.rc['interface']='socketcan'

os.system('sudo ip link set can0 type can bitrate 250000')
os.system('sudo ifconfig can0 up')

can0= can.interface.Bus(channel="can0",interface="socketcan")

##


csv = can.CSVWriter("testfile.csv",append=True)
global canData
canData = [None] * 16

def can_thread():
    while True:
        with can.Bus() as bus:
            msg = bus.recv()  
            
            #print(type(msg.arbitration_id))
            index = canMessageSort.get(msg.arbitration_id)
            canData[index] = msg.data
            print(msg)

            
def LJ():
    handle = ljm.openS("T7")
    info = ljm.getHandleInfo(handle)
    print("\nOpened a LabJack with Device type: %i, Connection type: %i,\n"
      "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per MB: %i" %
      (info[0], info[1], info[2], ljm.numberToIP(info[3]), info[4], info[5]))
    while True:
        result = ljm.eReadName(handle,"AIN0")
        print(result)
        
    

        
        
if __name__ == "__main__":
    can_thread = threading.Thread(target=can_thread)
    LJ = threading.Thread(target=LJ)

    
    can_thread.start()
    LJ.start()
    time.sleep(10)
          
                              

