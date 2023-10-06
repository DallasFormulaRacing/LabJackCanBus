import threading
import time
from abc.Enums import DAQState
from typing import TYPE_CHECKING, List

from labjack import ljm

from config.lj_logger import setup_logger
from config.manager import ConfigManager
from listeners import (AccelerometerListener, EngineControlUnitListener,
                       LinpotListener)
from ReadState import read_state

if TYPE_CHECKING:
    from abc.Listener import Listener 
    
class DAQObject:
    def __init__(self, output_path: str, config_file: str = "config.json"):
        self.config_manager = ConfigManager(config_file)

        self._log = setup_logger("DAQ")
        self._config = self.config_manager.get_config("DAQ")

        self.currentState = DAQState.INIT
        self.output_path = output_path

        self.active_listeners = []
        
        self._closed = True

        self.base_listeners= [EngineControlUnitListener, AccelerometerListener, LinpotListener]
        self.listeners: List["Listener"] = []
        
        self.handle = None
        self.run_lock = threading.Lock()

        self.run_count = 0

    def setSMState(self, nextState: DAQState) -> None:
        self.currentState = nextState

    def get_config(self) -> dict:
        return self._config
    
    def start(self):
        self.active_listeners: List[str] = self.get_config().get("listeners")
        self.handle = ljm.openS(self.config_manager.get_config("LJM").get("handle_device_type"))
        for base_listener in self.base_listeners:
            if base_listener.get_name() in self.active_listeners:
                self.listeners.append(base_listener(self.config_manager))
                
        for listener in self.listeners:
            listener.open()

        self.run()

    def stop(self):
        if not self._closed:
            for listener in self.listeners:
                listener.stop()
            self._closed = True

    def run(self) -> None:
        index = 0
        while True:
            with self.run_lock:
                button_clicked = read_state.read_button_state(self.handle)

                if button_clicked:
                    if self.currentState == DAQState.INIT:
                        self._log.info("[DAQ] collecting")
                        self.setSMState(DAQState.COLLECTING)
                    elif self.currentState == DAQState.SAVING:
                        self._log.info("[DAQ] collecting")
                        self.setSMState(DAQState.COLLECTING)
                else:
                    if self.currentState == DAQState.COLLECTING:
                        self._log.info("[DAQ] saving")

                        for listener in self.listeners:
                            listener.save(self.output_path, self.run_count)

                        self.setSMState(DAQState.SAVING)
                        self.run_count += 1

    def __del__(self):
        if not self._closed:
            self.stop()


if __name__ == "__main__":
    DAQ = DAQObject("data/output2")
    DAQ.start_threads()

    print("test")
    time.sleep(10)
