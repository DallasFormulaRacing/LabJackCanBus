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

bus = smbus.SMbus(1);

Register = bus.read_i2c_block_data(address, register, 6)

acc_x = Register[0]
acc_y = Register[1]
acc_z = Register[2]