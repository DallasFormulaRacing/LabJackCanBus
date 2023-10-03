import time
from labjack import ljm
from DAQState import DAQState


'''
Currently reads in the voltage from AIN0, which is connected to the button.
need to implement it in a way that will return bool true when the button is pressed
and false when it is not pressed. when pressed in Collecting State else in the Error state
'''


class read_state:

    def check_button_state(result: float) -> bool:
        if result > 1:
            return True
        else:
            return False

    def read_button_state(handle) -> bool:
        name = "FIO2"
        result = ljm.eReadName(handle, name)
        # print(f"\n{name} reading : {result} V")
        button_pressed = read_state.check_button_state(result)
        return button_pressed

    def close_read(self):
        self.currentState = DAQState.SAVING
        ljm.close(self.handle)
