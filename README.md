# LabJackCanbus
This repository contains Python scripts developed by Dallas Formula Racing for the purpose of reading data from a LabJack DAQ into CSV files. These scripts are intended to facilitate data acquisition and logging for data-analysis and manipulation. The labjack device we are using is the LabJackT7Pro, information about this device can be found here: https://labjack.com/pages/support?doc=%2Fdatasheets%2Ft-series-datasheet%2F

## Labjack Link
https://github.com/labjack/labjack-ljm-python/tree/master

## Sensor Data Sheets
- Analog Acel: https://www.analog.com/media/en/technical-documentation/data-sheets/adxl335.pdf
- Digital Acel: https://www.adafruit.com/product/4438
- Linpot: https://www.pegasusautoracing.com/productselection.asp?Product=MC-206&utm_source=google&utm_medium=cpc&utm_campaign=MC-206&gad_source=1&gclid=Cj0KCQiAy9msBhD0ARIsANbk0A8R3RR0sLIwCP6Y3Wp2lnhvHBwkFSwJzNTXNTJI-pUplBrkuiK3jzgaAv8YEALw_wcB

## Requirements
1. Start a virtual enviornment by running 'python -m venv venv_name_here'
2. activate your virtual enviornment
3. install the requiremetns, to install the requirements run the command 'pip install -r requirements.txt' this will install all of the necesarry packages for this project.

## File Overview
DAQ.py: Main handler, contains a single while loop and utilizes the xl and linpot classes to read and record data
Data: contains test data from initial runs
Read_Xl: Digital sensor code utilizing I2C
Read_Xl_Analog: Analog sensor code

## Current Goal / Future Implementations
- Migration to Streams for analog inputs: This will allow us to sample the linear potentiometers at a higher frequency
- Live Telemtry