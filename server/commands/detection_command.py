from .base_command import BaseCommand

class DetectionCommand(BaseCommand):
    def __init__(self):
        super().__init__()
        self.name = "detection"
        self.data_len = 8
        self.t_value = None
        self.d_value = None
        self.ch1_area_p = None
        self.ch1_area_n = None
        self.ch2_area_p = None
        self.ch2_area_n = None

    def process(self, data):
        self.validate(data)

        self.ch1_area_p = self._convert_bytes_to_int(data, 0, 2)
        self.ch1_area_n = self._convert_bytes_to_int(data, 2, 4)
        self.ch2_area_p = self._convert_bytes_to_int(data, 4, 6)
        self.ch2_area_n = self._convert_bytes_to_int(data, 6, 8)

    def to_dict(self):
        base_dict = super().to_dict()
        base_dict.update({
            "t_value": self.t_value,
            "d_value": self.d_value,
            "ch1_area_p": self.ch1_area_p,
            "ch1_area_n": self.ch1_area_n,
            "ch2_area_p": self.ch2_area_p,
            "ch2_area_n": self.ch2_area_n,
        })
        return base_dict
    
    