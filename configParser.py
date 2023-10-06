import json

class config_parser():

    #Dictionary to hold config data
    config_dict = {}

    #Init class. Takes location of config file as string
    def __init__(self,config_file_loc):
        try:
            with open(config_file_loc) as config_file:
                self.config_dict = json.load(config_file)
        except FileNotFoundError:
            print("File not found")
    
    #Utility function to update config dictionary and config file if required
    def update_config(self, new_conf_dict,config_file_loc):
        self.config_dict = new_conf_dict
        with open(config_file_loc, 'w') as write_file:
            json.dump(self.config_dict,write_file)

    #Parsing function. Pass sensor name as a string to get its input values as a list
    def read_sensor_config(self,sensor_name) -> [[]]:
        try:
            sensor_data = self.config_dict['Sensors'][sensor_name]['inputs']
            sensor_list = list(map(lambda x: list(x.values()), sensor_data))
            return sensor_list
        except KeyError:
            print("Incorrect Sensor name")


conf = config_parser("configs/sample.json")
print(conf.read_sensor_config("Accelerometers"))






