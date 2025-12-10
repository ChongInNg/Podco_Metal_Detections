class BaseCommand:
    def __init__(self):
        self.name = "Base"
        self.data_len = 0
        self.bytes_endian = "big"
        self.command = 0xFF

    def process(self, data):
        raise NotImplementedError("Subclasses must implement the process method")
    
    def validate(self, data):
        if self.data_len != len(data):
            raise ValueError(f"Invalid data length for {self.name}, expected_len:{self.data_len}, actual_len:{len(data)}")
        
    
    def _convert_bytes_to_int(self, data: bytes, start_pos:int, end_pos:int)->int:
        return int.from_bytes(data[start_pos:end_pos], self.bytes_endian)
    
    def to_dict(self):
        return {
            "name": self.name,
            "len": self.data_len,
            "command": self.command
        }
    
class AckCommand(BaseCommand):
    def __init__(self):
        super().__init__()
        self.name = "ACKResp" # should overwrite by subclass
        self.data_len = 1
        self.result = None

    def process(self, data):
        self.validate(data)

        self.result = self._convert_bytes_to_int(data, 0, 1)

    def to_dict(self):
        base_dict = super().to_dict()
        base_dict.update({
            "result": self.result,
        })
        return base_dict