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

        return pd.DataFrame(
            data={
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

        self.df = pd.DataFrame()
        self.combined = pd.DataFrame()

        # loop
        while not self._stop.is_set():

            gyro_data = gyro.poll()
            xl_data = xl.poll()

            self.df = pd.concat(
                [self.df, xl_data, gyro_data], ignore_index=True)

    def stop(self):
        self._stop.set()
        self.join()

    def save(self, input_csv: str):
        for i in range(0, len(self.df) - 1, 2): # hacky solution for test day
            row = self.df.iloc[i].fillna(self.df.iloc[i + 1])
            self.combined = self.combined.append(row, ignore_index = True)
        self.df.to_csv(input_csv, index=False)

if __name__ == "__main__":
    sensor = Main()

    try:
        sensor._run()
    except KeyboardInterrupt:
        pass

    sensor.save("accel.csv")
