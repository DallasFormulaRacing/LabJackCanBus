# front sensor
# AN13 is x
# AN12 is y
# AN11 is z

# middle sensor
# AIN10 is x
# AIN9 is y
# AIN8 is z

# back sensor
# AIN7 is x
# AIN6 is y
# AIN5 is z

from labjack import ljm


class read_xl_analog1:

  def read_xl(handle):
    x_axis = "AIN13"
    y_axis = "AIN12"
    z_axis = "AIN11"

    result_x = ljm.eReadName(handle, x_axis)
    result_y = ljm.eReadName(handle, y_axis)
    result_z = ljm.eReadName(handle, z_axis)

    print(f"\n{x_axis} reading : {result_x} V \n{y_axis} reading : {result_y} V \n{z_axis} reading : {result_z} V")


class read_xl_analog2:

  def read_xl(handle):
    x_axis = "AIN10"
    y_axis = "AIN9"
    z_axis = "AIN8"

    result_x = ljm.eReadName(handle, x_axis)
    result_y = ljm.eReadName(handle, y_axis)
    result_z = ljm.eReadName(handle, z_axis)

    print(f"\n{x_axis} reading : {result_x} V \n{y_axis} reading : {result_y} V \n{z_axis} reading : {result_z} V")


class read_xl_analog3:

  def read_xl(handle):
    x_axis = "AIN7"
    y_axis = "AIN6"
    z_axis = "AIN5"

    result_x = ljm.eReadName(handle, x_axis)
    result_y = ljm.eReadName(handle, y_axis)
    result_z = ljm.eReadName(handle, z_axis)

    print(f"\n{x_axis} reading : {result_x} V \n{y_axis} reading : {result_y} V \n{z_axis} reading : {result_z} V")