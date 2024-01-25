"""
accelerometer I2C communications

based on the sht3x.py example in the labjack documentation

TODO: 
*integrate into DAQ class
*write data to CSV
"""
import time
from labjack import ljm

def openComms():
    handle = ljm.openS("ANY","ANY","ANY")

    info = ljm.getHandleInfo(handle)

    print(info)

def config():
    openComms()

    ljm.eWriteName(handle, "I2C_SDA_DIONUM", 1) #using FIO1 as SDA
    ljm.eWriteName(handle, "I2C_SCL_DIONUM", 0) #using FIO0 as SCL

    ljm.eWriteName(handle, "FIO2", 1) #using FIO2 as power, setting to high continously

    ljm.eWriteName(handle, "I2C_SPEED_THROTTLE", 65516)

    ljm.eWriteName(handle,"I2C_SLAVE_ADDRESS", 0x19)

    ljm.eWriteName(handle,"I2C_OPTIONS", 0)

    ljm.eWriteName(handle, "I2C_NUM_BYTES_TX", 4)
    ljm.eWriteName(handle, "I2C_NUM_BYTES_RX", 0)

    ljm.eWriteNameByteArray(handle, "I2C_DATA_TX", 2, [0x20, 0x27]) #Data Rate is set to 10Hz, disable low power, enable all axies
    ljm.eWriteNameByteArray(handle, "I2C_DATA_TX", 2, [0x23, 0x49]) #Continous update

    ljm.eWriteName(handle, "I2C_GO", 1) #send data and begin 


def readRawValues():
    ljm.eWriteName(handle, "I2C_NUM_BYTES_TX", 1)
    ljm.eWriteName(handle, "I2C_NUM_BYTES_RX", 6)

    ljm.eWriteNameByteArray(handle, "I2C_DATA_TX",1,[0x28])
    
    ljm.eWriteName(handle, "I2C_GO", 1) 

    DATA = ljm.eReadNameByteArray(handle, "I2C_DATA_RX", 6) #read six bytes of data from registers

    #Slave aknowledgment from labjack, for troubleshooting
    #SAK = ljm.eReadNameByteArray(handle, "I2C_ACKS", 2);

    return [DATA[1] << 8 | DATA[0], DATA[3] << 8 | DATA[2], DATA[5] << 8 | DATA[4]] #integer values, x, y, z accel respectively

def computeAccel():
    real_data = readRawValues()
    #linear regression for acceleration in terms of g, courtesy of William Lim
    realData[0] = 0.0006 * real_data[0] - 0.0002
    realData[1] = 0.0006 * real_data[1] - 0.0002
    realData[2] = 0.0006 * real_data[2] - 0.0002

    return real_data

while(True):
    config()
    wait(0.5)
    print(computeAccel())