from enum import Enum


class DAQState(Enum):
    INIT = 'INIT'
    SAVING = 'SAVING'
    COLLECTING = 'COLLECTING'
    ERROR = "ERROR"
