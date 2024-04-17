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

telegraf_client = TelegrafClient(host="localhost", port=8092)


class Accelerometer(Extension):
    def __init__(self, session_id: int):
        self.session_id = session_id
        self.i2c = None
        self.accelerometer = None
        self.setup()

    def setup(self):
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.accelerometer = adafruit_lsm303_accel.LSM303_Accel(self.i2c)

    def poll(self) -> pd.DataFrame:
        accel_x, accel_y, accel_z = self.accelerometer.acceleration
        timestamp = time.time()

        payload = {
            "t": timestamp,
            "x": [accel_x],
            "y": [accel_y],
            "z": [accel_z]
        }

        telegraf_client.metric("accel_values", payload, tags={"source": "accel", "session_id": self.session_id})

        return pd.DataFrame(data=payload)


class Gyro(Extension):
    def __init__(self, session_id: int):
        self.session_id = session_id
        self.i2c = None
        self.gyroscope = None
        self.setup()

    def setup(self):
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.gyroscope = adafruit_l3gd20.L3GD20_I2C(self.i2c)

    def poll(self) -> pd.DataFrame:
        ang_x, ang_y, ang_z = self.gyroscope.gyro
        timestamp = time.time()

        payload = {
            "t": timestamp,
            "angular x": [ang_x],
            "angular y": [ang_y],
            "angular z": [ang_z]
        }

        telegraf_client.metric("gyro_values", payload, tags={"source": "gyro", "session_id": self.session_id})

        return pd.DataFrame(data=payload)


class Read(Thread):

    def __init__(self):
        super().__init__(target=self._run)

        self._stop = threading.Event()

        self.accel_df = pd.DataFrame()
        self.gyro_df = pd.DataFrame()
        self.session_id = self.retrieve_session_id()
        self.gyro = Gyro(self.session_id)
        self.accel = Accelerometer(self.session_id)

    def retrieve_session_id(self):
        with open("config.json", "r") as config_file:
            config = json.load(config_file)
            session_id = config["session_id"]
            return session_id

    def process(self):
        # loop
        while not self._stop.is_set():
            gyro_data = self.gyro.poll()
            xl_data = self.accel.poll()
            pd.concat([self.accel_df, xl_data], ignore_index=True)
            pd.concat([self.gyro_df, gyro_data], ignore_index=True)

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
