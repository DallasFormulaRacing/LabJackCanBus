import os
import threading
import time
from abc.Listener import Listener
from copy import copy
from threading import Thread

from can import (
    BufferedReader,
    CSVWriter,
    Message,
    Notifier,
    ThreadSafeBus
)

from config.lj_logger import setup_logger


class EcuTimeSyncManager:
    """Atomic time class that is used to synchronize the ECU and DAQ"""

    # TODO: Implement rate manager so we don't constantly lock this time value and increase speed

    def __init__(self):
        self.log_time = 0
        self.log_val = 0
        self._lock = threading.Lock()

    def log_ecu_timestamp(self, timestamp: int) -> None:
        """Log the ECU time to the class"""
        with self._lock:
            self.log_time = time.time()
            self.log_val = timestamp / 1000.0

    def time(self):
        with self._lock:
            return time.time() - self.log_time + self.log_val

    def reset(self):
        with self._lock:
            self.log_time = 0
            self.log_val = 0


class EngineControlUnit(Listener, Thread):
    def __init__(self, config: dict):
        self.statistics = {"MessagesReceived": 0, "MessagesSent": 0}
        super().__init__()

        # Running manages the runtime of the main loop
        self._running = False

        # stopped manages the os level connections to can
        self._stopped = True
        self.ecu_time_manager = EcuTimeSyncManager()
        self._log = setup_logger(self.get_name())
        self.__bus = None
        self.__bus_error = None
        self.__parse_config(config)

    def __parse_config(self, config: dict):
        # TODO: Config manager
        self.__config = config.get_config("ECU")

    @staticmethod
    def get_name():
        return "ECU Reader"

    def get_config(self):
        return self.__config

    def is_connected(self):
        return self.__bus is not None and self.__bus.state == "connected"

    def open(self):
        self._log.info("[%s] starting...", self.get_name())
        self._stopped = False
        os.system("sudo ip link set can0 type can bitrate 250000")
        os.system("sudo ifconfig can0 up")
        self.start()

    def close(self):
        if not self._stopped:
            self._stopped = True
            self._log.debug("[%s] Stopping", self.get_name())
            self.ecu_time_manager.reset()
            os.system("sudo ifconfig can0 down")

    def run(self):
        self._running = True

        self._log.debug("[%s] Running", self.get_name())
        while self._running:
            bus_notifier = None

            try:
                channel = self.get_config().get("channel")
                interface = self.get_config().get("interface")

                self.__bus = ThreadSafeBus(channel=channel, interface=interface)
                self._log.debug("[%s] Opened CAN Bus", self.get_name())

                reader = BufferedReader()
                writer = CSVWriter(file=self.get_config().get("csv_file"), append=True)
                bus_notifier = Notifier(self.__bus, [reader, writer])

                self._log.info(
                    "[%s] Connected to CAN bus (interface=%s,channel=%s)",
                    self.get_name(),
                    interface,
                    channel,
                )

                # TODO: Decide on connected flags for other program parts
                # self.__connected = True
                # self.__reconnect_count = 0

                while not self._stopped:
                    message = reader.get_message()

                    if message is not None:
                        self._log.debug(
                            "[%s] Received message: %s", self.get_name(), message
                        )
                        self.process_message(message)
                    self.check_errors()

            except Exception as err:  # pylint: disable=broad-except
                self._log.error("[%s] Error on CAN Bus: %s", self.get_name(), str(err))
                time.sleep(1)
            finally:
                try:
                    if bus_notifier is not None:
                        bus_notifier.stop()
                    if self.__bus is not None:
                        self._log.debug(
                            "[%s] Closing CAN Bus connection (state=%s)",
                            self.get_name(),
                            self.__bus.state,
                        )
                        self.__bus.shutdown()
                    self._log.debug("[%s] Closed CAN Bus", self.get_name())
                except Exception as err:  # pylint: disable=broad-except
                    self._log.error(
                        "[%s] Error on shutdown connection to CAN bus: %s",
                        self.get_name(),
                        str(err),
                    )

                # TODO: Implement reconnect logic here
                if self._stopped:
                    self._running = False

    def process_message(self, message: Message) -> None:
        """Generates the data points from the message and sends them to the websocket server"""
        if message.arbitration_id not in self.__nodes:
            self._log.debug(
                "[%s] Ignoring CAN message. Unknown arbitration_id %d",
                self.get_name(),
                message.arbitration_id,
            )
            return

        parse_node = self.__nodes[message.arbitration_id]

        datapoints = parse_node.parse(message)

        self._log.info("[%s] Parsed datapoints: %s", self.get_name(), datapoints)
        # TODO: Send this to the websocket server to deliver data to the laptops

        self.statistics["MessagesReceived"] += 1
        self.ecu_time_manager.log_ecu_timestamp(message.timestamp)
        self._log.debug("[%s] Message: %s", self.get_name(), message)

    # This check error code is for when sending is implemented
    def on_bus_error(self, e):
        self.__bus_error = e

    def check_errors(self):
        if self.__bus_error is not None:
            e = copy(self.__bus_error)
            self.__bus_error = None
            raise e
