from .base_command import BaseCommand

class FirmwareVersionCommand(BaseCommand):
    def __init__(self):
        super().__init__()
        self.name = "firmware_version"
        self.command = 0xBF
        self.data_len = 12
        self.major = None
        self.minor = None
        self.bugfix = None
        self.h_major = None
        self.h_minor = None
        self.h_bugfix = None

    def process(self, data):
        self.validate(data)

        self.major = self._convert_bytes_to_int(data, 0, 2)
        self.minor = self._convert_bytes_to_int(data, 2, 4)
        self.bugfix = self._convert_bytes_to_int(data, 4, 6)
        self.h_major = self._convert_bytes_to_int(data, 6, 8)
        self.h_minor = self._convert_bytes_to_int(data, 8, 10)
        self.h_bugfix = self._convert_bytes_to_int(data, 10, 12)

    def to_dict(self):
        base_dict = super().to_dict()
        base_dict.update({
            "major": self.major,
            "minor": self.minor,
            "bugfix": self.bugfix,
            "h_major": self.h_major,
            "h_minor": self.h_minor,
            "h_bugfix": self.h_bugfix,
        })
        return base_dict
