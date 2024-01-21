"""
accelerometer I2C communications

based on the sht3x.py example in the labjack documentation

TODO: 
*integrate into DAQ class
*convert data to usable format
*write data to CSV
"""
import time
from labjack import ljm

handle = ljm.openS("ANY","ANY","ANY")

info = ljm.getHandleInfo(handle)

print(info)

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

ljm.eWriteName(handle, "I2C_NUM_BYTES_TX", 1)
ljm.eWriteName(handle, "I2C_NUM_BYTES_RX", 2)

while True:
    ljm.eWriteNameByteArray(handle, "I2C_DATA_TX",1,[0x28])
    DATA = ljm.eReadNameByteArray(handle, "I2C_DATA_RX", 2)

    ljm.eWriteName(handle, "I2C_GO", 1) 

    SAK = ljm.eReadNameByteArray(handle, "I2C_ACKS", 2);

    print(DATA)
    time.sleep(1)