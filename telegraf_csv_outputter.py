from line_protocol_parser import parse_line
import csv
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
    sensor_type = line_data["tags"]["source"]
    sensor_file_path = os.path.join(
        OUTPUT_FOLDER_PATH, f"{session_id}-{sensor_type}.csv"
    )

    file_changed = True

    if sensor_type not in sensor_files:
        sensor_files[sensor_type] = open(sensor_file_path, "a")

    # Different session id
    elif sensor_files[sensor_type].name != sensor_file_path:
        sensor_files[sensor_type].close()
        sensor_files[sensor_type] = open(sensor_file_path, "a")

    else:
        file_changed = False

    fields = ["time"] + list(line_data["fields"].keys())
    writer = csv.writer(
        sensor_files[sensor_type], delimiter=",", lineterminator="\n", strict=True
    )

    if file_changed and os.stat(sensor_file_path).st_size == 0:
        writer.writerow(fields)

    else:
        writer.writerow([line_data["time"]] + list(line_data["fields"].values()))
