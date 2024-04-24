"""
CanBus Reader that writes to a provided file
"""

import os
import can
from telegraf.client import TelegrafClient


class ECU(object):
    def __init__(self, output_path: str):
        self.output_file = output_path
        self.bus = None
        self.notifier = None
        self.writer = None
        self.session_id = None
        self.telegraf_client = TelegrafClient(host="localhost", port=8092)

        os.system("sudo ip link set can0 type can bitrate 250000")
        os.system("sudo ifconfig can0 up")

    @property
    def file(self) -> str:
        """Get the output file

        Returns:
            str: The output file
        """
        return self.output_file

    @file.setter
    def file(self, value):
        self.output_file = value

    def start(self, session_id: int):
        self.session_id = session_id
        self.bus = can.interface.Bus(channel="can0", interface="socketcan")
        # Initialize CSVWriter to log messages to the global OUTPUT_FILE
        self.writer = can.CSVWriter(
            self.output_file + "_ecu_" + str(self.session_id) + ".csv", overwrite=True
        )

        # Create a Notifier with the bus and the writer as listener
        self.notifier = can.Notifier(self.bus, [self.writer, self.process_message])

    def save(self):
        # In this context, messages are automatically saved by the CSVWriter as they arrive.
        # If you need to implement a manual save feature, you could potentially flush
        # the CSVWriter or manage the file directly.
        # Since CSVWriter handles writing in real-time, there's no explicit save method required.
        pass

    def process_message(self, message: can.Message):
        # send to telegraf
        self.telegraf_client.metric(
            measurement_name="ecu_values",
            values={"id": message.arbitration_id, "data": message.data},
            tags={"source": "ecu", "session_id": self.session_id},
            timestamp=message.timestamp,
        )

    def stop(self):
        # Stop the notifier to clean up resources
        if self.notifier:
            self.notifier.stop()

        # Close the CSVWriter to ensure all data is flushed to the file
        if self.writer:
            self.writer.stop()

        if self.bus:
            self.bus.shutdown()

    def __del__(self):
        # Ensure that the CAN interface is brought down when the object is deleted
        # This is in __del__ because we do not want to bring down the interface if the object is paused
        # Bring down the CAN interface
        os.system("sudo ifconfig can0 down")
