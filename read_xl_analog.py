# AN13 is x
# AN12 is y
# AN11 is z
from labjack import ljm


class read_xl_analog:

  def read_xl(handle):
    x_axis = "AIN13"
    y_axis = "AIN12"
    z_axis = "AIN11"

    result_x = ljm.eReadName(handle, x_axis)
    result_y = ljm.eReadName(handle, y_axis)
    result_z = ljm.eReadName(handle, z_axis)

    print(f"\n{x_axis} reading : {result_x} V \n{y_axis} reading : {result_y} V \n{z_axis} reading : {result_z} V")

  def convert_volt_to_g():
    pass