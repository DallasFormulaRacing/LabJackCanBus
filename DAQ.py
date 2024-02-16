import time
from AnalogStream import Linpot, Stream
from ReadState import read_state
from CanBus import ECU
from DAQState import DAQState
import json
from labjack import ljm
import logging 

logging.basicConfig(level=logging.DEBUG)

class DAQ(object):
    def __init__(self, output_path: str, session_id: int = 0):
        self.output_path = output_path
        
        self.log = logging.getLogger("DAQ")

        self.analog_stream: Stream | None = None

        self.canbus: ECU | None = None

        self.handle = ljm.openS(
            "T7", "ANY", "ANY"
        )
        self._state = None
        self._session_id = session_id or 0
        
        self.log.info("session id: %s", self.session_id)

    @property
    def session_id(self):
        return self._session_id

    @session_id.setter
    def session_id(self, new_session_id):
        if new_session_id == self._session_id:
            return
        self._session_id = new_session_id

        # update json file
        with open("./config.json", "r+", encoding="utf8") as f:
            try:
                config = json.load(f)
            except json.JSONDecodeError:
                config = {}
            config["session_id"] = new_session_id
            f.seek(0)
            json.dump(config, f)
            f.truncate()

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, new_state):
        if new_state == self._state:
            return
        else:
            self.log.info("New State: %s", new_state)
            print(new_state)
            
        self._state = new_state

        if new_state == DAQState.COLLECTING:
            self.session_id += 1
            if self.analog_stream:
                self.analog_stream.start()
            
            if self.canbus:
                self.canbus.start(session_id=self.session_id)

        elif new_state == DAQState.SAVING:
            if self.analog_stream:
                self.analog_stream.stop()
                
                
            if self.canbus:
                self.canbus.stop()
            
            if self.analog_stream:
                self.analog_stream.save(self.output_path + f"/analog-{{}}-{self.session_id}.csv")
                self.analog_stream = Stream(self.handle, extensions=[Linpot()])
                
            if self.canbus:
                self.canbus.save()

        elif new_state == DAQState.INIT:
            self.analog_stream = Stream(handle=self.handle, extensions=[Linpot()])
            self.canbus = ECU(output_path=self.output_path + f"/can-")
            # self.handle = self.analog_stream.handle

    def _run(self):
        while True:
            button_clicked = read_state.read_button_state(self.handle)
            if button_clicked:
                if self.state in [DAQState.INIT, DAQState.SAVING]:
                    # startup is done
                    self.state = DAQState.COLLECTING

            elif self.state == DAQState.COLLECTING:
                self.state = DAQState.SAVING
            
            time.sleep(0)


    def start(self):
        self.log.info("Starting DAQ")
        
        self.state = DAQState.INIT
        try:
            self._run()
        except KeyboardInterrupt:
            self.log.info("DAQ Stopped")
        finally:
            self.state = DAQState.SAVING
            self.log.info("DAQ Stopped")

    def __del__(self):
        if self.handle:
            ljm.close(self.handle)
            self.handle = None 
            
if __name__ == "__main__":
    try:
        with open("./config.json", "r+", encoding="utf8") as f:
            config = json.load(f)
    except:
        config = {}  
        
    daq = DAQ(config.get("output", "test-data"), session_id=config.get("session_id", 0))
    
    daq.start()
