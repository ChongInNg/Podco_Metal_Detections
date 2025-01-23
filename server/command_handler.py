from commands.detection_command import DetectionCommand
from commands.calibration_command import CalibrationCommand
from commands.raw_data_command import RawDataCommand
from commands.threshold_command import ThresholdCommand
from commands.bypass_command import BypassCommand

class CommandHandler:
    COMMANDS = {
        0x0A: DetectionCommand,
        0xA0: CalibrationCommand,
        0xAA: RawDataCommand,
        0xF0: ThresholdCommand,
        0x0F: BypassCommand,
    }

    def __init__(self):
        pass

    def handle_command(self, command_type: int, data_length: int, data: bytes):     
        if len(data) != data_length:
            raise ValueError(f"Size mismatch: expected {data_length} bytes, got {len(data)} bytes from the controller")

        command_class = self.COMMANDS.get(command_type)
        if not command_class:
            raise ValueError(f"Unknown command: {hex(command_type)}")

        ins = command_class()
        ins.process(data)
        return ins.to_dict()
