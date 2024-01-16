# AN13 is x
# AN12 is y
# AN11 is z
import csv
import pandas as pd
from labjack import ljm
import time
from datetime import datetime


class read_xl_analog:
  def __init__(self):
    self.csv_file1 = "xl1.csv"
    self.csv_file2 = "xl2.csv"
    self.xl1_df=pd.DataFrame(columns=['Time','X Axis', 'Y Axis', 'Z Axis'])
    self.xl2_df=pd.DataFrame(columns=['Time','X Axis', 'Y Axis', 'Z Axis'])
  
  #TODO convert to a single function, change into a single pandas frame and pass in the different channel names instead of having two separate functions

  def read_xl_one(self, handle, index) -> None:
    x_axis = "AIN13"
    y_axis = "AIN12"
    z_axis = "AIN11"

    current_time = time.time()
    self.xl1_df.loc[index, "Time"] = current_time
    self.xl1_df.loc[index, "X Axis"] = ljm.eReadName(handle, x_axis)
    self.xl1_df.loc[index, "Y Axis"] = ljm.eReadName(handle, y_axis)
    self.xl1_df.loc[index, "Z Axis"] = ljm.eReadName(handle, z_axis)

  
  def read_xl_two(self, handle, index) -> None:
    x_axis = "AIN10"
    y_axis = "AIN9"
    z_axis = "AIN8"

    current_time = time.time()
    self.xl2_df.loc[index, "Time"] = current_time
    self.xl2_df.loc[index, "X Axis"] = ljm.eReadName(handle, x_axis)
    self.xl2_df.loc[index, "Y Axis"] = ljm.eReadName(handle, y_axis)
    self.xl2_df.loc[index, "Z Axis"] = ljm.eReadName(handle, z_axis)

  def save_xl_files(self):
    now = datetime.strftime(datetime.now(), "%Y-%m-%d_%H-%M-%S")
    self.xl1_df.to_csv(f"{self.csv_file1}_xl1_{now}.csv", index=False)
    self.xl2_df.to_csv(f"{self.csv_file2}_xl2_{now}.csv", index=False)
  
  def clear_xl_files(self):
    self.xl1_df = pd.DataFrame(columns=self.xl1_df.columns)
    self.xl2_df = pd.DataFrame(columns=self.xl2_df.columns)