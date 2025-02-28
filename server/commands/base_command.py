class BaseCommand:
    def __init__(self):
        self.name = "Base"
        self.data_len = 0
        self.bytes_endian = "big"

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
            "len": self.data_len
        }