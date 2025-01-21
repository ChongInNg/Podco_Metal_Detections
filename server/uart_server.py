import serial # type: ignore
import threading
import queue
from command_handler import CommandHandler
class UartServer:
    def __init__(self, port, baudrate=115200, timeout=None):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial = None
        self.cmd_queue = queue.Queue()
        self.running = False
        self.command_handler = CommandHandler()


    def connect(self):
        try:
            self.serial = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
            self.running = True
            print("UART connection established.")
            self.start()
        except Exception as e:
            print(f"Failed to connect to UART on port:{self.port}, baudrate:{self.baudrate}, err: {e}")

    def start(self):
        self.read_thread = threading.Thread(target=self._read_data, daemon=True)
        self.proces_thread = threading.Thread(target=self._process_queue_data, daemon=True)
        self.read_thread.start()
        self.proces_thread.start()
        print("Start read data and process data thread success.")

    def _read_data(self):
        while self.running:
            if self.serial.in_waiting:
                data = self.serial.readline().decode('utf-8').strip()
                self.cmd_queue.put(data)

    def _write_data(self, data):
        if self.serial and self.serial.is_open:
            self.serial.write(data.encode('utf-8'))

    def _process_queue_data(self):
        while not self.cmd_queue.empty():
            raw_message = self.cmd_queue.get()
            try:
                result = self.command_handler.handle_command(raw_message)
                print("Processed Command:", result)
            except ValueError as e:
                print(f"Command handling error: {e}, raw_message:{raw_message}")

    def close(self):
        self.running = False
        if self.serial and self.serial.is_open:
            self.serial.close()
            print("UART connection closed.")
            self.read_thread.join()
            print("Read queue thread closed.")
            self.proces_thread.join()
            print("Process queue thread closed.")

