from .base_command import BaseCommand

class ThresholdAdjustedCommand(BaseCommand):
    def __init__(self):
        super().__init__()
        self.name = "threshold"
        self.data_len = 2
        self.area_threshold = None

    def process(self, data):
        self.validate(data)

        self.area_threshold = self._convert_bytes_to_int(data, 0, 2)

    def to_dict(self):
        base_dict = super().to_dict()
        base_dict.update({
            "area_threshold": self.area_threshold,
        })
        return base_dict
