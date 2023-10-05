from time import sleep
from labjack import ljm

# Slave:
# binary read: 00110011 in hex: 0x33
# binary write: 00110010 in hex: 0x32

# try the other function as well eReadNameByteArray

class read_xl:

  @staticmethod
  def read_xl_input(handle):

    # For the T7 and other devices, using FIO0 and FIO1 for the SCL and SDA
    # pins.
    ljm.eWriteName(handle, "I2C_SDA_DIONUM", 1)  # SDA pin number = 1 (FIO1)
    ljm.eWriteName(handle, "I2C_SCL_DIONUM", 0)  # SCL pin number = 0 (FIO0)
    # Use FIO2 for power by setting it to output high
    ljm.eWriteName(handle, "FIO2", 1)

    # Speed throttle is inversely proportional to clock frequency. 0 = max.
    ljm.eWriteName(handle, "I2C_SPEED_THROTTLE", 65000)  # Speed throttle = 65516 (~100 kHz)

    # Options bits:
    #     bit0: Reset the I2C bus.
    #     bit1: Restart w/o stop
    #     bit2: Disable clock stretching.
    ljm.eWriteName(handle, "I2C_OPTIONS", 0)  # Options = 0

    # The SHT3x address could be 0x44 or 0x45 depending on the address pin voltage
    # A slave address of 0x44 indicates the ADDR pin is connected to a logic low
    ljm.eWriteName(handle, "I2C_SLAVE_ADDRESS", 0xd4)

    # Start with a single shot write command to the SHT3x sensor.
    ljm.eWriteName(handle, "I2C_NUM_BYTES_TX", 1)  # Set the number of bytes to transmit
    ljm.eWriteName(handle, "I2C_NUM_BYTES_RX", 0)  # Set the number of bytes to receive

    # Set the TX bytes
    numBytes = 1
    # 0x24 = clock stretching disabled, 0x00 = high repeatability
    aBytes = [0x0f]
    ljm.eWriteNameByteArray(handle, "I2C_DATA_TX", numBytes, aBytes)
    ljm.eWriteName(handle, "I2C_GO", 1)  # Do the I2C communications.

    # The sensor needs at least 15ms for the measurement. Wait 20ms
    sleep(0.02)

    # Do a read only transaction to obtain the readings
    ljm.eWriteName(handle, "I2C_NUM_BYTES_TX", 0)  # Set the number of bytes to transmit
    ljm.eWriteName(handle, "I2C_NUM_BYTES_RX", 1)  # Set the number of bytes to receive
    ljm.eWriteName(handle, "I2C_GO", 1)  # Do the I2C communications.

    # SHT3x sensors should always return 6 bytes for single shot acquisition:
    # [temp MSB, temp LSB, CRC, RH MSB, RH LSB, CRC]
    numBytes = 1
    aBytes = [0]*1
    aBytes = ljm.eReadNameByteArray(handle, "I2C_DATA_RX", numBytes)
    data = aBytes
    print("Data:" + data)

  @staticmethod
  def append_bits(axis_list) -> str:
      low_byte = str(axis_list[0])
      high_byte = str(axis_list[1])

      appended_bit = high_byte + low_byte

      return appended_bit

  @staticmethod
  def convert_bit_to_dec(appended_bit) -> int:
      decimal_value = int(appended_bit)

      return decimal_value
