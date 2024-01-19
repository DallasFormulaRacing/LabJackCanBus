"""
accelerometer I2C communications

based on the sht3x.py example in the labjack documentation

TODO: 
*integrate into DAQ class
*Look into more readable implementation using the I2C library from labjack
"""

from labjack import ljm

handle = ljm.openS("ANY","ANY","ANY")

info = ljm.getHandleInfo(handle)

ljm.eWriteName(handle, "I2C_SDA_DIONUM", 1) #using FIO1 as SDA
ljm.eWriteName(handle, "I2C_SCL_DIONUM", 0) #using FIO0 as SCL

ljm.eWriteName(handle, "FIO2", 1) #using FIO2 as power, setting to high continously

ljm.eWriteName(handle, "I2C_SPEED_THROTTLE", 50000)

ljm.eWriteName(handle,"I2C_SLAVE_ADDRESS", 0x19)

ljm.eWriteName(handle,"I2C_OPTIONS", 0)

ljm.eWriteName(handle, "I2C_NUM_BYTES_TX", 1)
ljm.eWriteName(handle, "I2C_NUM_BYTES_RX", 0)

ljm.eWriteNameByteArray(handle, "I2C_DATA_TX", 1, [0x31])

ljm.eWriteName(handle, "I2C_GO", 1) #send data and begin 

ljm.eWriteName(handle, "I2C_NUM_BYTES_TX", 0)
ljm.eWriteName(handle, "I2C_NUM_BYTES_RX", 6)

ljm.eWriteName(handle, "I2C_GO", 1) 

DATA = ljm.eReadNameByteArray(handle, "I2C_DATA_RX", 12)

SAK = ljm.eReadNameByteArray(handle, "I2C_ACKS", 2);
print(SAK)