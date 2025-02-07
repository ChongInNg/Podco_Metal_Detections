from commands.detection_command import DetectionCommand
from commands.calibration_command import CalibrationCommand
from commands.raw_data_command import RawDataCommand
from commands.threshold_adjusted_command import ThresholdAdjustedCommand
from commands.bypass_command import BypassCommand
from commands.base_command import BaseCommand
from websocket.wsmessage import *
from websocket.connection_manager import ConnectionManager
from log_manager import LogManager
from logs.detection_log import DetectionLogData

class CommandHandler:
    COMMANDS = {
        0x0A: DetectionCommand,
        0xA0: CalibrationCommand,
        0xAA: RawDataCommand,
        0xF0: ThresholdAdjustedCommand,
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
        notify_message = self.create_notify_message(ins)
        ConnectionManager.instance().send_notify_message(notify_message)
        self.log_to_file(ins)
        return ins.to_dict()

    def create_notify_message(self, command: BaseCommand) -> BaseWsNotify:
        if isinstance(command, BypassCommand):
            return NotifyByPassMessage.from_dict(command.to_dict())
        elif isinstance(command, CalibrationCommand):
            msg_dict = command.to_dict()
            msg_dict.update({
                "t_value": LogManager.instance().get_current_engine_time(),
                "d_value": LogManager.instance().get_current_calibration_threshold()
            })
            return NotifyCalibrationMessage.from_dict(msg_dict)
        elif isinstance(command, DetectionCommand):
            return NotifyDetectionMessage.from_dict(self.compose_detection_dict(command))
        elif isinstance(command, RawDataCommand):
            return NotifyRawDataMessage.from_dict(command.to_dict())
        elif isinstance(command, ThresholdAdjustedCommand):
            return NotifyThresholdAdjustedMessage.from_dict(command.to_dict())
        else:
            raise ValueError(f"Unknown command: {command.name}")
        
    def log_to_file(self, command: BaseCommand):
        from log_manager import LogManager
        LogManager.instance().log_message(f"{command.to_dict()}")
        if isinstance(command, DetectionCommand):
            LogManager.instance().save_detection(
                 DetectionLogData.from_dict(self.compose_detection_dict(command))
            )

    def compose_detection_dict(self, command: DetectionCommand):
        msg_dict = command.to_dict()
        msg_dict.update({
            "t_value": LogManager.instance().get_current_engine_time(),
            "d_value": LogManager.instance().get_current_calibration_threshold()
        })
        return msg_dict