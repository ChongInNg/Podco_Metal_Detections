from .base_command import BaseCommand

class RawDataCommand(BaseCommand):
    def __init__(self):
        super().__init__()
        self.name = "raw_data"
        self.data_len = 12
        self.input1_raw = None
        self.input2_raw = None
        self.ch1_area_p = None
        self.ch1_area_n = None
        self.ch2_area_p = None
        self.ch2_area_n = None

    def process(self, data):
        self.validate(data)

        self.input1_raw = self._convert_bytes_to_int(data, 0, 2)
        self.input2_raw = self._convert_bytes_to_int(data, 2, 4)
        self.ch1_area_p = self._convert_bytes_to_int(data, 4, 6)
        self.ch1_area_n = self._convert_bytes_to_int(data, 6, 8)
        self.ch2_area_p = self._convert_bytes_to_int(data, 8, 10)
        self.ch2_area_n = self._convert_bytes_to_int(data, 10, 12)

    def to_dict(self):
        base_dict = super().to_dict()
        base_dict.update({
            "input1_raw": self.input1_raw,
            "input2_raw": self.input2_raw,
            "ch1_area_p": self.ch1_area_p,
            "ch1_area_n": self.ch1_area_n,
            "ch2_area_p": self.ch2_area_p,
            "ch2_area_n": self.ch2_area_n,
        })
        return base_dict
