from .base_command import BaseCommand

class VoltageCommand(BaseCommand):
    def __init__(self):
        super().__init__()
        self.name = "voltage"
        self.data_len = 2
        self.voltage = None

    def process(self, data):
        self.validate(data)
        self.voltage = self._convert_bytes_to_int(data, 0, 2)

    def to_dict(self):
        base_dict = super().to_dict()
        base_dict.update({
            "voltage": self.voltage,
        })
        return base_dict
