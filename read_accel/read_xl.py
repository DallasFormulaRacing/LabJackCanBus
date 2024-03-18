from time import sleep
from labjack import ljm

# Slave:
# binary read: 00110011 in hex: 0x33
# binary write: 00110010 in hex: 0x32

# try the other function as well eReadNameByteArray


class read_xl:

    @staticmethod
    def read_xl_input(handle):

        ljm.eWriteName(handle, "I2C_SDA_DIONUM", 1)
        ljm.eWriteName(handle, "I2C_SCL_DIONUM", 0)
        ljm.eWriteName(handle, "FIO2", 1)
        ljm.eWriteName(handle, "I2C_SPEED_THROTTLE", 65000)

        # Options bits
        ljm.eWriteName(handle, "I2C_OPTIONS", 0)
        # writing to slave
        ljm.eWriteName(handle, "I2C_SLAVE_ADDRESS", 0xd4)

        numBytes = 6  # number of bytes to transmit

        while True:
            sleep(0.02)

            # Do a read only transaction to obtain the readings
            # Set the number of bytes to transmit
            ljm.eWriteName(handle, "I2C_NUM_BYTES_TX", 0)
            # Set the number of bytes to receive
            ljm.eWriteName(handle, "I2C_NUM_BYTES_RX", 6)
            ljm.eWriteName(handle, "I2C_GO", 1)  # Do the I2C communications.

            # out_var = [low_byte, high_byte]
            read_x_axis = [0x28, 0x29]
            read_y_axis = [0x2A, 0x2B]
            read_z_axis = [0x2C, 0x2D]
            who_am_i = [0x0f]

            xBytes = [0] * 2
            yBytes = [0] * 2
            zBytes = [0] * 2
            who_buff = [0] * 1

            ljm.eWriteNameByteArray(handle, "I2C_DATA_TX", 2, read_x_axis)
            ljm.eWriteNameByteArray(handle, "I2C_DATA_TX", 2, read_y_axis)
            ljm.eWriteNameByteArray(handle, "I2C_DATA_TX", 2, read_z_axis)
            ljm.eWriteNameByteArray(handle, "I2C_DATA_TX", 1, who_am_i)

            xBytes = ljm.eReadNameByteArray(handle, "I2C_DATA_RX", 2)
            yBytes = ljm.eReadNameByteArray(handle, "I2C_DATA_RX", 2)
            zBytes = ljm.eReadNameByteArray(handle, "I2C_DATA_RX", 2)
            who_buff = ljm.eReadNameByteArray(handle, "I2C_DATA_RX", 1)

           #  print("x: ", xBytes, " y: ", yBytes, " z: ", zBytes)

            print("who_am_i", who_buff)

            # xBytes = ljm.eReadAddressByteArray(handle, read_x_axis, 2)
            # yBytes = ljm.eReadAddressByteArray(handle, read_y_axis, 2)
            # zBytes = ljm.eReadAddressByteArray(handle, read_z_axis, 2)

          #   x_in_bits = read_xl.append_bits(xBytes)
          #   y_in_bits = read_xl.append_bits(yBytes)
          #   z_in_bits = read_xl.append_bits(zBytes)

          #   x_decimal = read_xl.convert_bit_to_dec(x_in_bits)
          #   y_decimal = read_xl.convert_bit_to_dec(y_in_bits)
          #   z_decimal = read_xl.convert_bit_to_dec(z_in_bits)

          #  print("x: ", x_decimal, " y: ", y_decimal, " z: ", z_decimal)

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
