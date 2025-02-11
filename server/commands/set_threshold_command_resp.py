from .base_command import BaseCommand

class SetThresholdCommandResp(BaseCommand):
    def __init__(self):
        super().__init__()
        self.name = "set_threshold_response"
        self.data_len = 1
        self.result = None

    def process(self, data):
        self.validate(data)

        self.result = self._convert_bytes_to_int(data, 0, 1)

    def to_dict(self):
        base_dict = super().to_dict()
        base_dict.update({
            "result": self.result,
        })
        return base_dict
