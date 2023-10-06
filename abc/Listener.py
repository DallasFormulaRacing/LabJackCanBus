from abc import ABC, abstractmethod

class Listener(ABC):
    @abstractmethod
    def open(self) -> None:
        pass
    
    @abstractmethod
    def close(self) -> None:
        pass
    
    @abstractmethod
    @staticmethod
    def get_name() -> str:
        pass
    
    @abstractmethod
    def is_connected(self) -> bool:
        pass