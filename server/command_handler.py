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

    def handle_command(self, message):
        command = message[0]
        size = message[1]
        data = message[2:]
        
        if len(data) != size:
            raise ValueError(f"Size mismatch: expected {size} bytes, got {len(data)} bytes from the controller")

        command_class = self.COMMANDS.get(command)
        if not command_class:
            raise ValueError(f"Unknown command: {hex(command)}")

        ins = command_class()
        ins.process(data)
        return ins.to_dict()
