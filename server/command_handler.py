from commands.detection_command import DetectionCommand
from commands.calibration_command import CalibrationCommand
from commands.raw_data_command import RawDataCommand
from commands.threshold_adjusted_command import ThresholdAdjustedCommand
from commands.bypass_command import BypassCommand
from commands.base_command import BaseCommand
from websocket.connection_manager import ConnectionManager
from log_manager import LogManager
from logs.detection_log import DetectionLogData
from logs.calibration_log import CalibrationLogData
import time
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from share.wsmessage import *


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
            return NotifyByPassMessage.create_message(bypass=command.bypass)
        elif isinstance(command, CalibrationCommand):
            return NotifyCalibrationMessage.create_message(
                t_value=LogManager.instance().get_current_engine_time(),
                d_value=command.area_threshold,
                pos_threshold1=command.pos_threshold1,
                pos_threshold2=command.pos_threshold2,
                mid_ch1=command.mid_ch1,
                mid_ch2=command.mid_ch2,
                neg_threshold1=command.neg_threshold1,
                neg_threshold2=command.neg_threshold2,
                area_threshold=command.area_threshold
            )
        elif isinstance(command, DetectionCommand):
            return NotifyDetectionMessage.create_message(
                t_value=LogManager.instance().get_current_engine_time(),
                d_value=LogManager.instance().get_current_calibration_data().area_threshold,
                ch1_area_n=command.ch1_area_n,
                ch1_area_p=command.ch1_area_p,
                ch2_area_n=command.ch2_area_n,
                ch2_area_p=command.ch2_area_p
            )
        elif isinstance(command, RawDataCommand):
            return NotifyRawDataMessage.create_message(
                input1_raw=command.input1_raw,
                input2_raw=command.input2_raw,
                ch1_area_n=command.ch1_area_n,
                ch1_area_p=command.ch1_area_p,
                ch2_area_n=command.ch2_area_n,
                ch2_area_p=command.ch2_area_p,
                timestamp=time.time()
            )
        elif isinstance(command, ThresholdAdjustedCommand):
            return NotifyThresholdAdjustedMessage.create_message(area_threshold=command.area_threshold)
        else:
            raise ValueError(f"Unknown command: {command.name}")
        
    def log_to_file(self, command: BaseCommand):
        LogManager.instance().log_message(f"{command.to_dict()}")
        if isinstance(command, DetectionCommand):
            log_data = DetectionLogData.from_dict(command.to_dict())
            log_data.t_value = LogManager.instance().get_current_engine_time()
            log_data.d_value = LogManager.instance().get_current_calibration_data().area_threshold
            LogManager.instance().save_detection(log_data)

        elif isinstance(command, CalibrationCommand):
            log_data = CalibrationLogData.from_dict(command.to_dict())
            log_data.t_value = LogManager.instance().get_current_engine_time()
            log_data.d_value = command.area_threshold
            LogManager.instance().update_calibration_data(log_data)