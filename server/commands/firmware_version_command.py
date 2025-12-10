from .base_command import BaseCommand

class FirmwareVersionCommand(BaseCommand):
    def __init__(self):
        super().__init__()
        self.name = "firmware_version"
        self.command = 0xBF
        self.data_len = 6
        self.major = None
        self.minor = None
        self.bugfix = None

    def process(self, data):
        self.validate(data)

        self.major = self._convert_bytes_to_int(data, 0, 2)
        self.minor = self._convert_bytes_to_int(data, 2, 4)
        self.bugfix = self._convert_bytes_to_int(data, 4, 6)

    def to_dict(self):
        base_dict = super().to_dict()
        base_dict.update({
            "major": self.major,
            "minor": self.minor,
            "bugfix": self.bugfix,
        })
        return base_dict
