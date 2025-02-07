import serial # type: ignore
import threading
import queue
from typing import  Optional
from command_handler import CommandHandler
from log.logger import Logger

class CommandData:
    def __init__(self, command_type: int, data_length: int, data: bytes):
        self.command_type = command_type
        self.data_length = data_length
        self.data = data
    def to_dict(self):
        return {
            "command_type": hex(self.command_type) ,
            "data_length": self.data_length,
            "data": self.data.hex()
        }
    
class SerialServer:
    _instance: Optional['SerialServer'] = None
    def __init__(self):
        self.port = None
        self.baudrate = 115200
        self.timeout = None # None: means nonblcoking, it is good to handle a lot of data receiving
        self.serial = None
        self.bytes_endian = "big"
        self.cmd_queue = queue.Queue()
        self.running = False
        self.command_handler = CommandHandler()

    @classmethod
    def instance(cls) -> 'SerialServer':
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def connect(self, port, baudrate=115200, timeout=None) -> bool:
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        try:
            self.serial = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
            self.running = True
            Logger.instance().info(f"Serial connection established. port:{self.port}, baudrate: {self.baudrate}, timeout mode: {self.timeout}")
            self.start()
            return True
        except Exception as e:
            Logger.instance().error(f"Failed to connect to Serial on port:{self.port}, baudrate:{self.baudrate}, err: {e}")
            return False

    def start(self):
        self.read_thread = threading.Thread(target=self._read_data, daemon=True)
        self.proces_thread = threading.Thread(target=self._process_queue_data, daemon=True)
        self.read_thread.start()
        self.proces_thread.start()
        Logger.instance().info("Start read data and process data thread success.")

    def send_default_calibration_request(self):
        pass

    def send_threshold_request(self):
        pass
    
    def _read_data(self):
        while self.running:
            if self.serial.in_waiting:
                Logger.instance().info(f"There are data comming from serial, len:{self.serial.in_waiting}")
                header = self.serial.read(2) 
                if len(header) < 2: 
                    continue

                command_type = header[0]
                data_length = header[1]

                Logger.instance().info(f"command type hex: {hex(command_type)}, data_length: {data_length}")
                data = self.serial.read(data_length)
                command_data = CommandData(command_type, data_length, data)
                self.cmd_queue.put(command_data)
                Logger.instance().info(f"Read data from the serial port: {command_data.to_dict()}")
                self._send_response(command_data.command_type)
                Logger.instance().info(f"Send response to controller, command_type: {hex(command_type)}")

    def _write_data(self, data: bytes):
        if self.serial and self.serial.is_open:
            self.serial.write(data)
            Logger.instance().info(f"Write to serial success. {data.hex()}")
        else:
            Logger.instance().error(f"Didn't connect to serial port, cannot send. {data.hex()}")

    def _process_queue_data(self):
        while self.running:
            Logger.instance().info("waitting for the queue data.")
            command_data: CommandData = self.cmd_queue.get()
            try:
                result = self.command_handler.handle_command(
                    command_type=command_data.command_type,
                    data_length=command_data.data_length,
                    data=command_data.data,
                )
                Logger.instance().info("Processed Command:", result)
                self._send_response(result["command_name"])
            except ValueError as e:
                self._send_error_response(command_data.command_type)
                Logger.instance().error(f"Command handling error: {e}, raw_command:{command_data}")

    def close(self):
        self.running = False
        if self.serial and self.serial.is_open:
            self.serial.close()
            Logger.instance().info("Serial connection closed.")
            self.read_thread.join()
            Logger.instance().info("Read queue thread closed.")
            self.proces_thread.join()
            Logger.instance().info("Process queue thread closed.")

    def _send_response(self, command_type: int):
        resp_value = 1
        encoded = command_type.to_bytes(1, self.bytes_endian) # command_type
        data_length = 1
        encoded += data_length.to_bytes(1, self.bytes_endian) # data_length
        encoded += resp_value.to_bytes(1, self.bytes_endian) # data value
        
        self._write_data(encoded)

    def _send_error_response(self, command_type: int):
        resp_value = 0
        encoded = command_type.to_bytes(1, self.bytes_endian)
        encoded += resp_value.to_bytes(1, self.bytes_endian)
        
        self._write_data(encoded)