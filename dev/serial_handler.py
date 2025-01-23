import serial # type: ignore

class CommandData:
    def __init__(self, command_type: int, data_length: int, data: bytes):
        self.command_type = command_type
        self.data_length = data_length
        self.data = data
    def to_dict(self):
        return {
            "command_type": hex(self.command_type) ,
            "data_length": self.data_length,
            "data": self.data
        }
    
class SerialHandler:
    def __init__(self, port, baudrate=115200, timeout=1):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial = None
    def connect(self) -> bool:
        try:
            self.serial = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
            self.running = True
            print(f"Serial connection established. port:{self.port}, baudrate: {self.baudrate}, timeout mode: {self.timeout}")
            return True
        except Exception as e:
            print(f"Failed to connect to serial on port:{self.port}, baudrate:{self.baudrate}, err: {e}")
            return False

    def send(self, data):
        self.serial.write(data)
        print(f"Sent: {data.hex()}")

    def receive(self):
        try:
            header = self.serial.read(2)  
            if len(header) < 2: 
                return

            command_type = header[0]
            data_length = header[1]

            data = self.serial.read(data_length)
            return CommandData(command_type=command_type, data_length=data_length, data=data)
        except serial.SerialTimeoutException:
            print(f"Timeout: No data received within {self.timeout} seconds.")
