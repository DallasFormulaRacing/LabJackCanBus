import random
import traceback
from can.thread_safe_bus import ThreadSafeBus
from can import Message, BufferedReader, Notifier, CSVWriter
import os


NOTSET = object()

class read_can:
    def __init__(self, channel: str, interface: str):
        self.channel = channel
        self.interface = interface

        self._bus = None
        self.bus_notifier = None

        self.reader = None

    def on_message_received(self, msg: Message):
        print(msg)

    def flush_buffer(self, file: str, *, append: bool = NOTSET, timeout: float = None):
        """Empties the current buffer into the specified filepath or writable file object

        Args:
            file (str): The file to pass the current buffer of messages into
            timeout (float, optional): The timeout for message reading. If using a buffer that isn't just in memory might be useful. Defaults to None.
        """
        if append == NOTSET:
            # If append is not set, then we should only append if the file doesn't exist
            append = isinstance(file, str) and not os.path.isfile(file)
            
        writer = CSVWriter(file)
        while message := self.reader.get_message(timeout=timeout):
            writer.on_message_received(message)

    def start(self):
        try:
            self.read_can()
        except Exception as exc: # pylint: disable=broad-except
            traceback.print_exc()
            print(f"SHUTTING DOWN CAN BUS (Exception: {type(exc).__name__})")
            self.stop()
            
    def read_can(self):
        os.system("sudo ip link set can0 type can bitrate 250000")
        os.system("sudo ifconfig can0 up")

        self._bus = ThreadSafeBus(channel=self.channel, interface=self.interface)

        self.reader = BufferedReader()
        self.bus_notifier = Notifier(
            self._bus, [self.reader, self.on_message_received]
        )
            
    def stop(self):
        if self.bus_notifier is not None:
            self.bus_notifier.stop()
        if self._bus is not None:
            self._bus.shutdown()

        if self.reader is not None and not self.reader.buffer.empty():
            rand_hex = hex(random.randint(0, 2 ** 32))[2:]
            print(f"WARNING: ECU Buffer not empty, dumping to file dump-{rand_hex}.csv")
            self.flush_buffer(f"dump-{rand_hex}.csv", append=True)
        os.system('sudo ifconfig can0 down')
        
        print("CAN Bus Shutdown")
