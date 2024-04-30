from line_protocol_parser import parse_line
import os

# Output folder path
OUTPUT_FOLDER_PATH = "/home/rayyans/LabJackCanBus_Telegraf/Telegraf_Output"

current_session = None
sensor_files = {}

while True:
    data = input()
    
    try:
        line_data = parse_line(data)
    except:
        print("Could not parse input")
        continue

    if "session_id" not in line_data["tags"]:
        continue

    print(line_data)
    session_id = line_data["tags"]["session_id"]
    
    session_folder = os.path.join(OUTPUT_FOLDER_PATH, rf"session_{session_id}")
    if not os.path.exists(session_folder):
        os.makedirs(session_folder)
    
    sensor_type = line_data["tags"]["source"]

    if sensor_type not in sensor_files:
        sensor_files[sensor_type] = open(
            os.path.join(session_folder, f"{sensor_type}.csv"), "a"
        )
        sensor_files[sensor_type].write(
            "time," + ",".join(line_data["fields"].keys()) + "\n"
        )

    # Sensor file exists in different session folder
    elif not os.path.exists(os.path.join(session_folder, f"{sensor_type}.csv")):
        sensor_files[sensor_type].close()
        sensor_files[sensor_type] = open(
            os.path.join(session_folder, f"{sensor_type}.csv"), "a"
        )

    sensor_files[sensor_type].write(
        f"{line_data['time']},"
        + ",".join([str(value) for value in line_data["fields"].values()])
        + "\n"
    )
