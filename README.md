# LabJackCanbus
This repository contains Python scripts developed by Dallas Formula Racing for the purpose of reading data from a LabJack DAQ into CSV files. These scripts are intended to facilitate data acquisition and logging for data-analysis and manipulation.

## LabJack
The LabJack model used is the LabJackT7Pro.
- [LabJack datasheet](https://labjack.com/pages/support?doc=%2Fdatasheets%2Ft-series-datasheet%2F)
- [LabJack python library](https://github.com/labjack/labjack-ljm-python/tree/master)

## Sensors
- [Accelerometer/Gyroscope](https://www.adafruit.com/product/1714#technical-details)
    - [Accelerometer datasheet](https://cdn-shop.adafruit.com/datasheets/LSM303DLHC.PDF)
    - [Gyroscope datasheet](https://cdn-shop.adafruit.com/datasheets/L3GD20.pdf)
- [Linear potentiometer](https://www.pegasusautoracing.com/productselection.asp?Product=MC-206)

## Getting started
1. Start a virtual environment by running `python -m venv venv_name_here`
2. Activate your virtual environment
3. Install the necessary packages by running the command `pip install -r requirements.txt`.

## File Overview
- `DAQ.py`: Main handler, contains a single while loop and utilizes the accelerometer and potentiometer classes to read and record data
- `/button/ReadState.py`: Reads a digital switch through the LabJack to determine the state of the DAQ
- `/sensors/AnalogStream.py`: Reads from analog sensors through the LabJack
- `/sensors/GyroAndAccel.py`: Reads from the accelerometer/gyroscope sensors through I2C
- `/ecu_can/CanBus.py`: Reads from the ECU through can messages
- `/data`: Contains test data from initial runs
