from .base_command import BaseCommand

class CalibrationCommand(BaseCommand):
    def __init__(self):
        super().__init__()
        self.name = "calibration"
        self.data_len = 14
        self.pos_threshold1 = None
        self.neg_threshold1 = None
        self.pos_threshold2 = None
        self.neg_threshold2 = None
        self.mid_ch1 = None
        self.mid_ch2 = None
        self.area_threshold = None

    def process(self, data):
        self.validate(data)

        self.pos_threshold1 = self._convert_bytes_to_int(data, 0, 2)
        self.neg_threshold1 = self._convert_bytes_to_int(data, 2, 4)
        self.pos_threshold2 = self._convert_bytes_to_int(data, 4, 6)
        self.neg_threshold2 = self._convert_bytes_to_int(data, 6, 8)
        self.mid_ch1 = self._convert_bytes_to_int(data, 8, 10)
        self.mid_ch2 = self._convert_bytes_to_int(data, 10, 12)
        self.area_threshold = self._convert_bytes_to_int(data, 12, 14)

        self._save_calibration_log()

    def _save_calibration_log(self):
        from log_manager import LogManager
        LogManager.instance().update_calibration_data(self.area_threshold)

    def to_dict(self):
        base_dict = super().to_dict()
        base_dict.update({
            "pos_threshold1": self.pos_threshold1,
            "neg_threshold1": self.neg_threshold1,
            "pos_threshold2": self.pos_threshold2,
            "neg_threshold2": self.neg_threshold2,
            "mid_ch1": self.mid_ch1,
            "mid_ch2": self.mid_ch2,
            "area_threshold": self.area_threshold,
        })
        return base_dict
