import threading
import time
import busio
import board
import adafruit_lsm303_accel
import adafruit_l3gd20
from threading import Thread
from sensors.AnalogStream import Extension
import pandas as pd
import json

from telegraf.client import TelegrafClient


TIME_ID = "t"


class Accelerometer(Extension):
    def __init__(self):
        self.i2c = None
        self.accelerometer = None
        self.setup()

    def setup(self):
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.accelerometer = adafruit_lsm303_accel.LSM303_Accel(self.i2c)

    def poll(self) -> pd.DataFrame:
        accel_x, accel_y, accel_z = self.accelerometer.acceleration
        t = time.time()

        return pd.DataFrame(
            data={
                "t": t,
                "x": [accel_x],
                "y": [accel_y],
                "z": [accel_z]
            }
        )


class Gyro(Extension):
    def __init__(self):
        self.i2c = None
        self.gyroscope = None
        self.setup()

    def setup(self):
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.gyroscope = adafruit_l3gd20.L3GD20_I2C(self.i2c)

    def poll(self) -> pd.DataFrame:
        ang_x, ang_y, ang_z = self.gyroscope.gyro
        t = time.time()

        return pd.DataFrame(
            data={
                "t": t,
                "angular x": [ang_x],
                "angular y": [ang_y],
                "angular z": [ang_z]
            }
        )


class Read(Thread):

    def __init__(self):
        super().__init__(target=self._run)

        self._stop = threading.Event()

        self.accel_df = pd.DataFrame()
        self.gyro_df = pd.DataFrame()
        self.telegraf_client = TelegrafClient(host="localhost", port=8092)
        self.session_id = self.retrieve_session_id()

    def process(self):
        # intiialzize
        gyro = Gyro()
        xl = Accelerometer()

        # loop
        while not self._stop.is_set():

            gyro_data = gyro.poll()
            xl_data = xl.poll()
            pd.concat([self.accel_df, xl_data], ignore_index=True)
            pd.concat([self.gyro_df, gyro_data], ignore_index=True)

            self.send_accel_metrics(xl_data)
            self.send_gyro_metrics(gyro_data)

    def retrieve_session_id(self):
        with open("config.json", "r") as config_file:
            config = json.load(config_file)
            return config["session_id"]

    def send_accel_metrics(self, accel_df: pd.DataFrame):
        for i, row in accel_df.iterrows():
            time_value = row[TIME_ID]
            payload = {
                'fields': {
                    'accel_x': row['x'],
                    'accel_y': row['y'],
                    'accel_z': row['z']
                }
            }
            self.telegraf_client.metric("accel_values", payload, tags={"source": "accel", "session_id": self.session_id}, timestamp=time_value)

    def send_gyro_metrics(self, gyro_df: pd.DataFrame):
        for i, row in gyro_df.iterrows():
            time_value = row[TIME_ID]

            payload = {
                'fields': {
                    'angular_x': row['angular x'],
                    'angular_y': row['angular y'],
                    'angular_z': row['angular z']
                }
            }
            self.telegraf_client.metric("gyro_values", payload, tags={"source": "gyro", "session_id": self.session_id}, timestamp=time_value)

    def stop(self):
        self._stop.set()
        self.join()

    def save(self, accel_fp: str, gyro_fp: str):
        self.accel_df.to_csv(accel_fp, index=False)
        self.gyro_df.to_csv(gyro_fp, index=False)


# if __name__ == "__main__":
#     sensor = Read()

#     try:
#         sensor._run()
#     except KeyboardInterrupt:
#         pass

#     sensor.save("accel.csv")
