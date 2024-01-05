"""
accelerometer I2C communications

based on the sht3x.py example in the labjack documentation

TODO: 
*Adapt numbers to fit accelerometer data sheet
*Read data from accelerometer
*Adapt into streams (after reading using standalone file)
"""

from labjack import ljm

handle = ljm.openS("ANY","ANY","ANY")

info = ljm.getHandleInfo(handle)

if info[0] == ljm.constants.dtT4:
    ljm.eWriteName(handle, "DIO_INHIBIT", 0xFFF8F)
    ljm.eWriteName(handle, "DIO_ANALOG_ENABLE", 0x00000)

    ljm.eWriteName(handle, "I2C_SDA_DIONUM", 5)
    ljm.eWriteName(handle, "I2C_SCL_DIONUM", 4)
    ljm.eWriteName(handle, "FIO6", 1)

else:

    ljm.eWriteName(handle, "I2C_SDA_DIONUM", 1)
    ljm.eWriteName(handle, "I2C_SCL_DIONUM", 0)

    ljm.eWriteName(handle, "FIO2", 1)

ljm.eWriteName(handle, "I2C_SPEED_THROTTLE", 65000)

ljm.eWriteName(handle,"IWC_SLAVE_ADDRESS", 0x44) #tentative address, will change after finding data sheet

#tentative bytes to transmit and recieve
ljm.eWriteName(handle, "I2C_NUM_BYTES_TX", 2)
ljm.eWriteName(handle, "I2C_NUM_BYTES_RX", 0)

aBytes = [0x24, 0x00] #[clock stretching disabled, high repeatability] 
                      #Will need to look at data sheet to determine best use of options

ljm.eWriteName(handle, "I2C_GO", 1) #Begin I2C communications

    
