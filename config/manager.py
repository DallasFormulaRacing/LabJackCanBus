try:
    # Faster json
    import orjson as json
except ImportError:
    import json

from typing import Union
from os import PathLike 

class ConfigManager(object):
    """A class to manage the config file and configuration for all parts of the program

    Args:
        config_file (StringPathLike): The path to the config file
    """
    def __init__(self, config_file: Union[str, PathLike], encoding: str = 'utf-8'):
        self.config_file = config_file
        self.encoding = encoding
        self._config = {}
        
        # special runtime set variables
        self._xconfig = {}
        self.read_config()
    
    def read_config(self):
        """Read the config file into memory"""
        with open(self.config_file, 'r', encoding=self.encoding) as f:
            self._config = json.load(f)
            
    def write_config(self):
        """Write the config file to disk"""
        with open(self.config_file, 'w', encoding=self.encoding) as f:
            json.dump(self._config, f)
    
    def update_config(self, key: str, value):
        """Update the config file with a new value

        Args:
            key (str): The key to update
            value (_type_): The value to update
        """
        self._config[key] = value
        self.write_config()
    
    def set_config(self, new_config: dict):
        """Set the config file to a new value

        Args:
            new_config (dict): The new config
        """
        self._config = new_config
        self.write_config()
        
    def get_config(self, key: str, default=None):
        """Get a value from the config file

        Args:
            key (str): The key to get
            default (_type_, optional): The default value to return if the key is not found. Defaults to None.

        Returns:
            JSONValue: The value of the key
            
        Examples:
            get_config("LHM.handle_data_type") -> "LJM": {"handle_data_type": "LJM"} -> "LJM"
        """
        conf = self._config
        for part in key.split("."):
            if part in conf:
                conf = conf[part]
            else:
                return default
        return conf