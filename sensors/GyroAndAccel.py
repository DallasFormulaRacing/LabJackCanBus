import threading
import time
import busio
import board
import adafruit_lsm303_accel
import adafruit_l3gd20
from threading import Thread
from sensors.AnalogStream import Extension
import pandas as pd

from telegraf.client import TelegrafClient

telegraf_client = TelegrafClient(host="localhost", port=8092)


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

    def send_a_g_metrics(self, accel_df: pd.DataFrame, gyro_df: pd.DataFrame):

        with self.lock:
            for columns in accel_df.columns, gyro_df.columns:
                accel_metric_name = "accelerometer_".join(columns.lower())
                gyro_metric_name = "_".join(columns.lower().split())
                accel_value = accel_df[columns].values[-1]
                gyro_value = gyro_df[columns].values[-1]
                timestamp_accel = accel_df["t"].values[-1]
                timestamp_gyro = gyro_df["t"].values[-1]

                telegraf_client.metric(accel_metric_name, accel_value, timestamp=timestamp_accel)
                telegraf_client.metric(gyro_metric_name, gyro_value, timestamp=timestamp_gyro)

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

            self.send_a_g_metrics(self.accel_df, self.gyro_df)

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
