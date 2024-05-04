import time
from labjack import ljm
from DAQState import DAQState
from telegraf.client import TelegrafClient
from sensors.GyroAndAccel import Read
import logging
import traceback


class read_state:

    def check_button_state(result: float) -> bool:
        if result < 1:
            return True
        else:
            return False

    def read_button_state(handle) -> bool:
        timestamp = time.time()
        name = "FIO0"

        try:
            telegraf_client = TelegrafClient(host="localhost", port=8092)
            session_id = Read.retrieve_session_id()

            result = ljm.eReadName(handle, name)
            button_pressed = read_state.check_button_state(result)

            telegraf_client.metric(
                "button_voltage",
                values={"voltage": result},
                timestamp=str(int(timestamp * 1e9)),
                tags={"source": "button", "session_id": session_id},
            )

            return button_pressed

        except Exception as e:
            logging.error(
                f"Error sending data to telegraf: {e}\n{traceback.format_exc()}"
            )

    def close_read(self):
        self.currentState = DAQState.SAVING
        ljm.close(self.handle)
