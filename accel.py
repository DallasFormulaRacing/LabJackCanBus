"""
accelerometer I2C communications

based on the sht3x.py example in the labjack documentation

TODO: 
*integrate into DAQ class
*Look into more readable implementation using the I2C library from labjack
"""

from labjack import ljm
from labjack import I2C

handle = ljm.openS("ANY","ANY","ANY")

info = ljm.getHandleInfo(handle)

ljm.eWriteName(handle, "I2C_SDA_DIONUM", 1) #using FIO1 as SDA
ljm.eWriteName(handle, "I2C_SCL_DIONUM", 0) #using FIO0 as SCL

ljm.eWriteName(handle, "FIO2", 1) #using FIO2 as power, setting to high continously

ljm.eWriteName(handle, "I2C_SPEED_THROTTLE", 65000)

ljm.eWriteName(handle,"IWC_SLAVE_ADDRESS", 0x19)

#start signal
ljm.eWriteName(handle, "FIO0", 1) #hold SCL HIGH
ljm.eWriteName(handle, "FIO1", 1)
ljm.eWriteName(handle, "FIO1", 0) #HIGH to LOW on the SDA
#the I2C bus is now considered busy

#tentative bytes to transmit and recieve
ljm.eWriteName(handle, "I2C_NUM_BYTES_TX", 1)
ljm.eWriteName(handle, "I2C_NUM_BYTES_RX", 0)

ljm.eWriteName(handle, "I2C_DATA_TX", 0x33) #send address of the slave (0011001b or 0x16) followed by 1 for a write command (0011001110b or 0x32)

ljm.eWriteName(handle, "I2C_GO", 1) #send data and begin 

ljm.eWriteName(handle, "I2C_NUM_BYTES_TX", 0)
ljm.eWriteName(handle, "I2C_NUM_BYTES_RX", 1)

ljm.eWriteName(handle, "I2C_GO", 1) #Read Slave Aknowledgement (SAK)

SAK = ljm.eReadNameByteArray(handle, "I2C_DATA_RX", 1)

print(SAK)

ljm.eWriteName(handle, "I2C_NUM_BYTES_TX", 1)
ljm.eWriteName(handle, "I2C_NUM_BYTES_RX", 0)

#place holder hex address
ljm.eWriteName(handle,"I2C_DATA_TX", 0x99) #SUB address format is 1 followed by the address of the register you want to read

ljm.eWriteName(handle, "I2C_GO", 1) #sensor is ready to send DATA

sleep(0.02) #wait for collected values

#to continously read data from the sensor, send a Master acknowledge
ljm.eWriteName(handle, "I2C_DATA_TX", 0x20) #0x20 is the temperature register, testing purposes

ljm.eWriteName(handle, "I2C_NUM_BYTES_TX", 1)
ljm.eWriteName(handle, "I2C_NUM_BYTES_RX", 2) #all registers return 2 bytes of data

ljm.eWriteName(handle, "I2C_GO", 1) # collect data

tempData = ljm.eWriteNameByteArray(handle, "I2C_DATA_RX", 2)

ljm.close(handle) #close communications when finished reading data