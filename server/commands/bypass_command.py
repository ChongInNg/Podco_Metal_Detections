from .base_command import BaseCommand

class BypassCommand(BaseCommand):
    def __init__(self):
        super().__init__()
        self.name = "bypass"
        self.data_len = 2
        self.bypass = None

    def process(self, data):
        self.validate(data)
        self.bypass = self._convert_bytes_to_int(data, 0, 2)

    def to_dict(self):
        base_dict = super().to_dict()
        base_dict.update({
            "bypass": self.bypass,
        })
        return base_dict
