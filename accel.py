"""
accelerometer I2C communications

based on the sht3x.py example in the labjack documentation

TODO: 
*Read data from accelerometer
"""

from labjack import ljm

handle = ljm.openS("ANY","ANY","ANY")

info = ljm.getHandleInfo(handle)

ljm.eWriteName(handle, "I2C_SDA_DIONUM", 1) #using FIO1 as SDA
ljm.eWriteName(handle, "I2C_SCL_DIONUM", 0) #using FIO0 as SCL

ljm.eWriteName(handle, "FIO2", 1) #using FIO2 as power, setting to high continously

ljm.eWriteName(handle, "I2C_SPEED_THROTTLE", 65000)

ljm.eWriteName(handle,"IWC_SLAVE_ADDRESS", 0x6B)

#start signal
ljm.eWriteName(handle, "FIO0", 1) #hold SCL HIGH
ljm.eWriteName(handle, "FIO1", 1)
ljm.eWriteName(handle, "FIO1", 0) #HIGH to LOW on the SDA
#the I2C bus is now considered busy

#tentative bytes to transmit and recieve
ljm.eWriteName(handle, "I2C_NUM_BYTES_TX", 1)
ljm.eWriteName(handle, "I2C_NUM_BYTES_RX", 0)

ljm.eWriteName(handle, "I2C_DATA_TX", 0xD5) #send address of the slave (1101010b or 0x6B) followed by 1 for a read transaction (11010101b or 0xD5)

ljm.eWriteName(handle, "I2C_GO", 1) #send data and begin 

