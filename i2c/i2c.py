from labjack import ljm

class i2c:

  read_bit = 1
  write_bit = 0
  sda_pin_out = 1 # FIO1
  scl_pin_out = 0 # FIO0
  speed_throttle = 65516

  def __init__(self, handle, seven_bit_address):
    self.seven_bit_address = seven_bit_address
    self.handle = handle
    ljm.eWriteName(handle,"I2C_SDA_DIONUM", self.sda_pin_out)
    ljm.eWriteName(handle,"I2C_SDA_DIONUM", self.scl_pin_out)
    # ljm.eWriteName(handle, "FIO2", 1)
    ljm.eWriteName(handle, "I2C_SPEED_THROTTLE", self.speed_throttle)
    ljm.eWriteName(handle, "I2C_OPTIONS", 0)
    ljm.eWriteName(handle, "I2C_SLAVE_ADDRESS", self.seven_bit_address)

  def write(self,register_address, numBytes):
    ljm.eWriteName(self.handle, "I2C_REGISTER_ADDRESS", register_address)
    

  def read(slave_read_address):
    pass

  