import threading
from scipy.signal import butter
import busio
import board
import adafruit_lsm303_accel
import adafruit_l3gd20
from threading import Thread
from sensors.AnalogStream import Extension
import pandas as pd
import json
import logging
import traceback
import time
from telegraf.client import TelegrafClient

def butter_lowpass(cutoff, fs, order = 5):
    return butter(order, cutoff, fs = fs, btype='low', analog=False)

class Accelerometer(Extension):
    def __init__(self, session_id: float):
        self.session_id = session_id
        self.i2c = None
        self.accelerometer = None
        self.telegraf_client = TelegrafClient(host="localhost", port=8092)
        self.setup()

    def setup(self):
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.accelerometer = adafruit_lsm303_accel.LSM303_Accel(self.i2c)

    def poll(self) -> pd.DataFrame:
        accel_x, accel_y, accel_z = self.accelerometer.acceleration
        timestamp = time.time()

        try:
            self.telegraf_client.metric(
                "accel_values",
                values={"accel_x": accel_x, "accel_y": accel_y, "accel_z": accel_z},
                timestamp=str(int(timestamp * 1e9)),
                tags={"source": "accel", "session_id": self.session_id},
            )

        except Exception as e:
            logging.error(
                f"Error sending data to telegraf: {e}\n{traceback.format_exc()}"
            )

        return pd.DataFrame(
            data={
                "t": timestamp,
                "accel_x": [accel_x],
                "accel_y": [accel_y],
                "accel_z": [accel_z],
            }
        )


class Gyro(Extension):
    def __init__(self, session_id: float):
        self.session_id = session_id
        self.i2c = None
        self.gyroscope = None
        self.telegraf_client = TelegrafClient(host="localhost", port=8092)
        self.setup()

    def setup(self):
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.gyroscope = adafruit_l3gd20.L3GD20_I2C(self.i2c)

    def poll(self) -> pd.DataFrame:
        ang_x, ang_y, ang_z = self.gyroscope.gyro
        timestamp = time.time()

        try:
            self.telegraf_client.metric(
                "gyro_values",
                values={"angular_x": ang_x, "angular_y": ang_y, "angular_z": ang_z},
                timestamp=str(int(timestamp * 1e9)),
                tags={"source": "gyro", "session_id": self.session_id},
            )

        except Exception as e:
            logging.error(
                f"Error sending data to telegraf: {e}\n{traceback.format_exc()}"
            )

        return pd.DataFrame(
            data={
                "t": timestamp,
                "angular_x": [ang_x],
                "angular_y": [ang_y],
                "angular_z": [ang_z],
            }
        )


class Read(threading.Thread):

    def __init__(self):
        super().__init__(target=self.start_reading)
        self.stop_event = threading.Event()

        self.accel_df = pd.DataFrame()
        self.gyro_df = pd.DataFrame()
        self.session_id = self.retrieve_session_id()
        
        try:
            self.gyro = Gyro(self.session_id)
        except Exception as e:
            logging.error(
                f"Failed to initialize gyroscope: {e}\n{traceback.format_exc()}"
            )
            
        try:
            self.accel = Accelerometer(self.session_id)
        except Exception as e:
            logging.error(
                f"Failed to initialize accelerometer: {e}\n{traceback.format_exc()}"
            )

    def retrieve_session_id(self):
        with open("config.json", "r") as config_file:
            config = json.load(config_file)
            session_id = config["session_id"]
            logging.info(f"Retrieved session id: {session_id}")
            return session_id

    def start_reading(self):
        self.session_id = self.retrieve_session_id()
        logging.info("Processing data")
        while not self.stop_event.is_set():
            self.stop_event.wait(0.05)
            
            if self.gyro:
                gyro_data = self.gyro.poll()
                self.gyro_df = pd.concat([self.gyro_df, gyro_data], ignore_index=True)
                
            if self.accel:
                xl_data = self.accel.poll()
                self.accel_df = pd.concat([self.accel_df, xl_data], ignore_index=True)
            
        return 

    def stop_reading(self):
        logging.info("Stopping data collection")
        self.stop_event.set()

    def save(self, accel_fp: str, gyro_fp: str):
        logging.info(f"Saving data to {accel_fp} and {gyro_fp}")
        
        if self.accel:
            self.accel_df.to_csv(accel_fp, index=False)
            
        if self.gyro:
            self.gyro_df.to_csv(gyro_fp, index=False)


# if __name__ == "__main__":
#     sensor = Read()

#     try:
#         sensor._run()
#     except KeyboardInterrupt:
#         pass

#     sensor.save("accel.csv")
