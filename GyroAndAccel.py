import threading
import time
import busio
import board
import adafruit_lsm303_accel
import adafruit_l3gd20
from threading import Thread
from AnalogStream import Extension
import pandas as pd


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
        time = time.time()

        return pd.DataFrame(
            data={
                "t": time,
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
        time = time.time()

        return pd.DataFrame(
            data={
                "t": time,
                "angular x": [ang_x],
                "angular y": [ang_y],
                "angular z": [ang_z]
            }
        )


class Main(Thread):

    def __init__(self):
        super().__init__(target=self._run)

        self._stop = threading.Event()

    def _run(self):

        # intiialzize
        gyro = Gyro()
        xl = Accelerometer()

        self.accel_df = pd.DataFrame()
        self.gyro_df = pd.DataFrame()

        # loop
        while not self._stop.is_set():
            gyro_data = gyro.poll()
            xl_data = xl.poll()
            self.accel_df = pd.concat([self.accel_df, xl_data], ignore_index=True)
            self.gyro_df = pd.concat([self.gyro_df, gyro_data], ignore_index=True)

    def stop(self):
        self._stop.set()
        self.join()

    def save(self, accel_csv: str, gyro_csv: str):
        self.accel_df.to_csv(accel_csv, index=False)
        self.gyro_df.to_csv(gyro_csv, index=False)

if __name__ == "__main__":
    sensor = Main()

    try:
        sensor._run()
    except KeyboardInterrupt:
        pass

    sensor.save("accel.csv")
