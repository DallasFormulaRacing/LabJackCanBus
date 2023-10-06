import time
from abc.Listener import Listener
from typing import TYPE_CHECKING
from datetime import datetime
import pandas as pd
from labjack.ljm import ljm

from config.lj_logger import setup_logger

if TYPE_CHECKING:
    from config.manager import ConfigManager


class Linpot(Listener):
    def __init__(self, config: "ConfigManager"):
        super().__init__()
        self._config = {}
        self._ljm_config = {}
        self._log = setup_logger(self.get_name())
        self._stopped = False
        
        self.index = 0
        self.linpot_df = None
        self.handle = None

        self.__parse_config(config)

    def __parse_config(self, config):
        self._config = config.get_config("Linpot")
        self._ljm_config = config.get_config("LJM")

    def open(self):
        self.handle = ljm.openS(self.get_ljm_config().get("handle_device_type"))
        self.linpot_df = pd.DataFrame(
            columns=["Time", "Front Right", "Front Left", "Rear Right", "Rear Left"]
        )

        aValues = [10]
        for value in self._config["AIN"].values():
            frames = [f"{value}_RESOLUTION_INDEX"]
            ljm.eWriteNames(self.handle, len(frames), frames, aValues)
        self._log.info("[%s] starting...", self.get_name())
        self.run()

    def close(self):
        self._stopped = True
        ljm.close(self.handle)
        now = datetime.strftime(
            datetime.fromtimestamp(time.time()), "%Y-%m-%d_%H-%M-%S"
        )
        output_file = self.get_config().get("output_file")
        self.linpot_df.to_csv(
            f"{output_file}_linpot_{now}.csv", index=False
        )
        self._log.info("[%s] Stopping", self.get_name())

    def run(self):
        # TODO: Refractor into stopped and running variables so we do not lose data when the switch is flipped
        # We risk getting incomplete data and having a corrupted csv
        while not self._stopped:
            current_time = time.time()
            self.linpot_df.loc[self.index, "Time"] = current_time
            for name, value in self._config["AIN"].items():
                self.linpot_df.loc[self.index, name] = ljm.eReadName(self.handle, value)

            self._log.debug(
                "[%s]: stored data: %s", self.get_name(), self.linpot_df.tail(1)
            )
            self.index += 1

    @staticmethod
    def get_name():
        return "Linpot"

    def get_config(self):
        return self._config
