import serial # type: ignore
import threading
import queue
from typing import  Optional
from command_handler import CommandHandler
from log.logger import Logger
from config.config import ConfigManager

SET_THRESHOLD_RESPONSE_COMMAND:int = 0x0B
SET_DEFAULT_CALIBRATION_RESPONSE_COMMAND: int = 0xB0

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
            Logger.info(f"Serial connection established. port:{self.port}, baudrate: {self.baudrate}, timeout mode: {self.timeout}")
            self.start()
            self.set_server_status_on()
            return True
        except Exception as e:
            Logger.error(f"Failed to connect to Serial on port:{self.port}, baudrate:{self.baudrate}, err: {e}")
            self.set_server_status_off()
            return False

    def start(self):
        self.read_thread = threading.Thread(target=self._read_data, daemon=True)
        self.proces_thread = threading.Thread(target=self._process_queue_data, daemon=True)
        self.read_thread.start()
        self.proces_thread.start()
        Logger.info("Start read data and process data thread success.")

    def send_default_calibration_request(self) -> int:
        req_value = 1
        command_type = SET_DEFAULT_CALIBRATION_RESPONSE_COMMAND
        encoded = command_type.to_bytes(1, self.bytes_endian) # command_type
        data_length = 1
        encoded += data_length.to_bytes(1, self.bytes_endian) # data_length
        encoded += req_value.to_bytes(1, self.bytes_endian) # data value
        
        num = self._write_data(encoded)
        print(f"Send default calibration request to serial port. bytes: {num}")
        return num

    def send_set_threshold_request(self, threshold: int) -> int:
        req_value = threshold
        command_type = SET_THRESHOLD_RESPONSE_COMMAND
        encoded = command_type.to_bytes(1, self.bytes_endian) # command_type
        data_length = 2
        encoded += data_length.to_bytes(1, self.bytes_endian) # data_length
        encoded += req_value.to_bytes(2, self.bytes_endian) # data value
        
        num = self._write_data(encoded)
        print(f"Send set threshold request to serial port. threshold: {threshold}, bytes: {num}")
        return num
    
    def _read_data(self):
        while self.running:
            if self.serial.in_waiting:
                Logger.info(f"There are data comming from serial, len:{self.serial.in_waiting}")
                header = self.serial.read(2) 
                if len(header) < 2: 
                    continue

                command_type = header[0]
                data_length = header[1]

                Logger.info(f"command type hex: {hex(command_type)}, data_length: {data_length}")
                data = self.serial.read(data_length)
                command_data = CommandData(command_type, data_length, data)
                self.cmd_queue.put(command_data)
                Logger.info(f"Read data from the serial port: {command_data.to_dict()}")

                if self.need_send_back_response_to_controller(command_data.command_type):
                    self._send_response(command_data.command_type)
                    Logger.info(f"Send response to controller, command_type: {hex(command_type)}")

    def _write_data(self, data: bytes) -> int:
        if self.serial and self.serial.is_open:
            buf_num = self.serial.write(data)
            Logger.info(f"Write to serial success. {data.hex()}, buf_num: {buf_num}")
            return buf_num
        else:
            Logger.error(f"Didn't connect to serial port, cannot send. {data.hex()}")
            return 0

    def _process_queue_data(self):
        while self.running:
            try:
                command_data: CommandData = self.cmd_queue.get(timeout=0.5)
                try:
                    result = self.command_handler.handle_command(
                        command_type=command_data.command_type,
                        data_length=command_data.data_length,
                        data=command_data.data,
                    )
                    Logger.info("Processed Command:", result)
                except ValueError as e:
                    self._send_error_response(command_data.command_type)
                    Logger.error(f"Command handling error: {e}, raw_command:{command_data}")
                finally:
                    self.cmd_queue.task_done()
            except queue.Empty:
                # Logger.info("Queue is waitting for command.")
                continue

    def close(self):
        self.running = False
        if self.serial and self.serial.is_open:
            self.serial.close()
            Logger.info("Serial connection closed.")
            self.read_thread.join()
            Logger.info("Read queue thread closed.")
            self.proces_thread.join()
            Logger.info("Process queue thread closed.")
        
        self.set_server_status_off()

    def _send_response(self, command_type: int) -> int:
        resp_value = 1
        encoded = command_type.to_bytes(1, self.bytes_endian) # command_type
        data_length = 1
        encoded += data_length.to_bytes(1, self.bytes_endian) # data_length
        encoded += resp_value.to_bytes(1, self.bytes_endian) # data value
        
        return self._write_data(encoded)

    def _send_error_response(self, command_type: int) -> int:
        resp_value = 0
        encoded = command_type.to_bytes(1, self.bytes_endian)
        encoded += resp_value.to_bytes(1, self.bytes_endian)
        
        return self._write_data(encoded)
    
    def need_send_back_response_to_controller(self, command_type: int):
        if command_type == SET_DEFAULT_CALIBRATION_RESPONSE_COMMAND or command_type == SET_THRESHOLD_RESPONSE_COMMAND:
            return False
        return True
    
    def set_server_status_on(self):
        if ConfigManager.instance().run_on_rpi():
            import RPi.GPIO as GPIO
            pin = ConfigManager.instance().server_status_pin
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.HIGH)
            print(f"set GPIO{pin} pin on.")
        else:
            print("No run on rpi, no need to set server status on.")

    def set_server_status_off(self):
        if ConfigManager.instance().run_on_rpi():
            import RPi.GPIO as GPIO
            pin = ConfigManager.instance().server_status_pin
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.LOW)
            print(f"set GPIO{pin} pin off.")
        else:
            print("No run on rpi, no need to set server status off.")