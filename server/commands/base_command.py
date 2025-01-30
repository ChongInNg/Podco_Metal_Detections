class BaseCommand:
    def __init__(self):
        self.name = "Base"
        self.data_len = 0

    def process(self, data):
        raise NotImplementedError("Subclasses must implement the process method")
    
    def validate(self, data):
        if self.data_len != len(data):
            raise ValueError(f"Invalid data length for {self.name}, expected_len:{self.data_len}, actual_len:{len(data)}")
        
    
    def _convert_bytes_to_int(self, data: bytes, start_pos:int, end_pos:int)->int:
        return int.from_bytes(data[start_pos:end_pos], "big")
    
    def to_dict(self):
        return {
            "command_name": self.name,
            "data_len": self.data_len
        }