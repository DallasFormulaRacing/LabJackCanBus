class config():

  @staticmethod
  def export_config() -> dict:

    return {
          "ECU": 
          {
              "channel": "can0",
              "interface": "socketcan",
              "csv_file": "ecudata.csv"
          },
          "LJM": 
          {
              "handle_device_type": "T7"
          },
          "linpot": 
          {
              "output_file": "linpotdata.csv",
              "AIN": {
                  "Front Right": "AIN1",
                  "Front Left": "AIN2",
                  "Rear Right": "AIN3",
                  "Rear Left": "AIN4"
              }
          },
          "button":
          {
            "name": "AIN0"
          },
          "accelerometer_front":
          {
              "front": {
                "x": "AIN13",
                "y": "AIN12",
                "z": "AIN11"
              },
          },
          "accelerometer_middle":
          {
              "middle": {
                "x": "AIN10",
                "y": "AIN9",
                "z": "AIN8"
              },
          },
          "accelerometer_back":
          {
              "back": {
                "x": "AIN7",
                "y": "AIN6",
                "z": "AIN5"
              },
          }
    }
