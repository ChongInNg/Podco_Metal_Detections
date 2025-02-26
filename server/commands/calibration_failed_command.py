from .base_command import BaseCommand

class CalibrationFailedCommand(BaseCommand):
    def __init__(self):
        super().__init__()
        self.name = "calibration_failed"
        self.data_len = 2
        self.reason = None

    def process(self, data):
        self.validate(data)

        self.reason = self._convert_bytes_to_int(data, 0, 2)

    def to_dict(self):
        base_dict = super().to_dict()
        base_dict.update({
            "reason": self.reason
        })
        return base_dict
