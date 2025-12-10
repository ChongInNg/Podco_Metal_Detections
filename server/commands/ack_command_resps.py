from .base_command import AckCommand

Threshold_Adjusted_ACK = 0x0B
Reset_to_Factory_ACK = 0xB0
Reset_Factory_Calibration_ACK = 0x0C # not use now
Reset_To_Bootloader_ACK = 0xFA
Get_Firmware_Version_ACK = 0xFB
Get_Hardware_Version_ACK = 0xFC

class GetFirmwareVersionCommandResp(AckCommand):
    def __init__(self):
        super().__init__()
        self.name = "get_firmware_version_resp"
        self.command = Get_Firmware_Version_ACK

class GetHardwareVersionCommandResp(AckCommand):
    def __init__(self):
        super().__init__()
        self.name = "get_hardware_version_resp"
        self.command = Get_Hardware_Version_ACK

class ResetToBootloaderCommandResp(AckCommand):
    def __init__(self):
        super().__init__()
        self.name = "reset_to_bootloader_response"
        self.command = Reset_To_Bootloader_ACK

class SetDefaultCalibrationCommandResp(AckCommand):
    def __init__(self):
        super().__init__()
        self.name = "set_default_calibration_response"
        self.command = Reset_to_Factory_ACK

class SetThresholdCommandResp(AckCommand):
    def __init__(self):
        super().__init__()
        self.name = "set_threshold_response"
        self.command = Threshold_Adjusted_ACK