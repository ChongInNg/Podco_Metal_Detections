from .base_command import BaseCommand

class BypassCommand(BaseCommand):
    def __init__(self):
        super().__init__()
        self.name = "bypass"
        self.data_len = 1
        self.bypass_status = None

    def process(self, data):
        self.validate(data)

        self.bypass_status = self._convert_bytes_to_int(data, 0, 1)

        self.log_to_file()

    def to_dict(self):
        base_dict = super().to_dict()
        base_dict.update({
            "bypass_status": self.bypass_status,
        })
        return base_dict
