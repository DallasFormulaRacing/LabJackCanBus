import logging
from time import sleep
from threading import Thread

# TODO: Implement proper logging handlers here (pass into colored stream + filehandler)
class LJCBLogger(logging.Logger):
    ...
    

def setup_logger(name: str, level: int = logging.NOTSET) -> logging.Logger:
    log = LJCBLogger(name)
    
    if log_level_conf := level:
        log_level = logging.getLevelName(log_level_conf)
        log.setLevel(log_level)
        
    return log