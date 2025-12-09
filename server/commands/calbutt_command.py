from .base_command import BaseCommand

class CalButtCommand(BaseCommand):
    def __init__(self):
        super().__init__()
        self.name = "calbutt"
        self.data_len = 2
        self.calbutt = 0

    def process(self, data):
        self.validate(data)
        self.calbutt = self._convert_bytes_to_int(data, 0, 2)

    def to_dict(self):
        base_dict = super().to_dict()
        base_dict.update({
            "calbutt": self.calbutt,
        })
        return base_dict
