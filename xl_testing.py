from labjack import ljm
import csv

class xl_testing:

    def __init__(self) -> None:
        self.handle = ljm.openS("T7", "USB", "ANY")
        # Corrected the file handle names
        self.csv_file1 = open("xl_testing1.csv", "w", newline='')
        self.csv_file2 = open("xl_testing2.csv", "w", newline='')
        self.csv_writer1 = csv.writer(self.csv_file1)
        self.csv_writer1.writerow(['X Axis', 'Y Axis', 'Z Axis'])
        self.csv_writer2 = csv.writer(self.csv_file2)
        self.csv_writer2.writerow(['X Axis', 'Y Axis', 'Z Axis'])

    def read_xl_one(self) -> None:
        x_axis = "AIN13"
        y_axis = "AIN12"
        z_axis = "AIN11"

        result_x = ljm.eReadName(self.handle, x_axis)
        result_y = ljm.eReadName(self.handle, y_axis)
        result_z = ljm.eReadName(self.handle, z_axis)

        self.csv_writer1.writerow([result_x, result_y, result_z])

        print(f"\n{x_axis} reading : {result_x} V \n{y_axis} reading : {result_y} V \n{z_axis} reading : {result_z} V")

    def read_xl_two(self) -> None:
        x_axis = "AIN10"
        y_axis = "AIN9"
        z_axis = "AIN8"
  
        result_x = ljm.eReadName(self.handle, x_axis)
        result_y = ljm.eReadName(self.handle, y_axis)
        result_z = ljm.eReadName(self.handle, z_axis)

        self.csv_writer2.writerow([result_x, result_y, result_z])

        print(f"\n{x_axis} reading : {result_x} V \n{y_axis} reading : {result_y} V \n{z_axis} reading : {result_z} V")

    def close_files(self):
        self.csv_file1.close()
        self.csv_file2.close()

def main():
    tester = xl_testing()
    count = 0

    try:
        while count < 100:
          tester.read_xl_one()
          tester.read_xl_two()
          count += 1
    finally:
        tester.close_files()

if __name__ == "__main__":
    main()
