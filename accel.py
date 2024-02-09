"""
accelerometer I2C communications via raspberry PI

TODO: 
*integrate into DAQ class
*write data to CSV
*processes raw data
"""
from smbus2 import SMBus, i2c_msg
import time

address = 0x19
register = 0x28

with SMBus(1) as bus: 
    while True:
        msg = bus.read_i2c_block_data(address,register,6)
        print(msg)