import json
from datetime import datetime
from typing import Any
import ulid
import ulid.ulid

MessageType_Request = "request"
MessageType_Response = "response"
MessageType_Notify = "notify"

MessageName_Registration = "registration"
MessageName_GetLastNDetections = "get_last_n_detections"
MessageName_SetThreshold = "set_threshold"
MessageName_SetDefaultCalibration = "set_default_calibration"
MessageName_GetCalibration = "get_calibration"
MessageName_SystemError = "system_error"

MessageName_NotifyByPass = "notify_bypass"
MessageName_NotifyCalibration = "notify_calibration"
MessageName_NotifyDetection = "notify_detection"
MessageName_NotifyRawData = "notify_raw_data"
MessageName_NotifyThresholdAdjusted = "notify_threshold_adjusted"
MessageName_NotifyCalibration_Failed = "notify_calibration_failed"
MessageName_NotifyEngineHour = "notify_engine_hour"

class Header:
    def __init__(self, name: str, message_type: str, id: str=None, ts: str = None):
        self.name = name
        self.id = id or str(ulid.new())
        self.ts = ts or datetime.now().isoformat()
        self.message_type = message_type
    
    def is_request(self):
        return self.message_type == MessageType_Request
    
    def is_response(self):
        return self.message_type == MessageType_Response
    
    def is_notify(self):
        return self.message_type == MessageType_Notify

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "id": self.id,
            "ts": self.ts,
            "type": self.message_type
        }
    
    def is_registration_message(self):
        return self.name == MessageName_Registration

    def is_get_last_n_detections_message(self):
        return self.name == MessageName_GetLastNDetections
    
    def is_get_calibration_message(self):
        return self.name == MessageName_GetCalibration
    
    def is_set_threshold_message(self):
        return self.name == MessageName_SetThreshold
    
    def is_set_default_calibration_message(self):
        return self.name == MessageName_SetDefaultCalibration
    
    def is_notify_bypass_message(self):
        return self.name == MessageName_NotifyByPass

    def is_notify_calibration_message(self):
        return self.name == MessageName_NotifyCalibration

    def is_notify_detection_message(self):
        return self.name == MessageName_NotifyDetection

    def is_notify_raw_data_message(self):
        return self.name == MessageName_NotifyRawData

    def is_notify_threshold_adjusted_message(self):
        return self.name == MessageName_NotifyThresholdAdjusted
    
    def is_system_error_message(self):
        return self.name == MessageName_SystemError
    
    def is_notify_calibration_failed_message(self):
        return self.name == MessageName_NotifyCalibration_Failed

    def is_notify_engine_hour_message(self):
        return self.name == MessageName_NotifyEngineHour
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'Header':
        name = data.get("name")
        message_type = data.get("type")
        cls.validate_message_name(name)
        cls.validater_message_type(message_type)
        return cls(
            name=name,
            message_type=message_type,
            id=data.get("id"),
            ts=data.get("ts")
        )
    
    @classmethod
    def validate_message_name(cls, message_name: str):
        for name in [
            MessageName_Registration, MessageName_NotifyByPass,
            MessageName_NotifyCalibration, MessageName_NotifyDetection,
            MessageName_NotifyRawData, MessageName_NotifyThresholdAdjusted,
            MessageName_NotifyEngineHour,
            MessageName_GetLastNDetections,
            MessageName_SetDefaultCalibration,
            MessageName_SetThreshold,
            MessageName_GetCalibration,
            MessageName_SystemError,
            MessageName_NotifyCalibration_Failed,
        ]:
            if name == message_name:
                return
        raise ValueError(f"Message name:{message_name} is not supported")

    @classmethod
    def validater_message_type(cls, message_type: str):
        for name in [MessageType_Request, MessageType_Response, MessageType_Notify]:
            if name == message_type:
                return
        raise ValueError(f"Message type:{message_type} is not supported")

class BaseWsMessage:
    def __init__(self, header: Header):
        self.header = header

        # make these variables to be access conveniently
        self.name = self.header.name
        self.id = self.header.id
        
    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    def to_dict(self) -> dict[str, Any]:
        return self.header.to_dict()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'BaseWsMessage':
        header = Header.from_dict(data)
        msg_data = data.get("data")
        if msg_data is None or not isinstance(msg_data, dict):
            raise ValueError("Message data format is wrong. should be a dictionary.")
        
        if header.is_registration_message():
            if header.is_request():
                return RegistrationWsRequest.from_dict(header=header, data=msg_data)
            else:
                return RegistrationWsResponse.from_dict(header=header, data=msg_data)
        elif header.is_get_last_n_detections_message():
            if header.is_request():
                return GetLastNDetectionsRequest.from_dict(header=header, data=msg_data)
            else:
                return GetLastNDetectionsResponse.from_dict(header=header, data=msg_data)
        elif header.is_set_threshold_message():
            if header.is_request():
                return SetThresholdRequest.from_dict(header=header, data=msg_data)
            else:
                return SetThresholdResponse.from_dict(header=header, data=msg_data)
        elif header.is_get_calibration_message():
            if header.is_request():
                return GetCalibrationRequest.from_dict(header=header, data=msg_data)
            else:
                return GetCalibrationResponse.from_dict(header=header,data=msg_data)
        elif header.is_set_default_calibration_message():
            if header.is_request():
                return SetDefaultCalibrationRequest.from_dict(header=header, data=msg_data)
            else:
                return SetDefaultCalibrationResponse.from_dict(header=header, data=msg_data)
        elif header.is_system_error_message():
            return SystemErrorResponse.from_dict(header=header, data=msg_data)
        elif header.is_notify_bypass_message():
            return NotifyByPassMessage.from_dict(header=header, data=msg_data)
        elif header.is_notify_calibration_message():
            return NotifyCalibrationMessage.from_dict(header=header, data=msg_data)
        elif header.is_notify_detection_message():
            return NotifyDetectionMessage.from_dict(header=header, data=msg_data)
        elif header.is_notify_raw_data_message():
            return NotifyRawDataMessage.from_dict(header=header, data=msg_data)
        elif header.is_notify_threshold_adjusted_message():
            return NotifyThresholdAdjustedMessage.from_dict(header=header, data=msg_data)
        elif header.is_notify_calibration_failed_message():
            return NotifyCalibrationFailedMessage.from_dict(header=header, data=msg_data)
        elif header.is_notify_engine_hour_message():
            return NotifyEngineHourMessage.from_dict(header=header, data=msg_data)
        else:
            raise ValueError(f"Message name is wrong. {header.to_dict()}")
        
class BaseWsRequest(BaseWsMessage):
    def __init__(self, header: Header):
        self.validate(header=header)
        super().__init__(header=header)
    
    def validate(self, header: Header):
        if not header.is_request():
            raise ValueError("Message type wrong, should be request")

class BaseWsResponse(BaseWsMessage):
    def __init__(self, header: Header, code:str, message: str, meta: str=None):
        self.validate(header=header, code=code,message=message)
        super().__init__(header=header)
        self.code = code
        self.message = message
        self.meta = meta

    def is_success(self):
        if self.code == "OK" or self.code == "success":
            return True
        return False

    def to_dict(self) -> dict[str, Any]:
        base_dict = super().to_dict()
        base_dict.update({
            "data": {
                "code": self.code,
                "message": self.message
            }
        })

        if self.meta is not None:
            base_dict["data"].update({
                "meta": self.meta
            })

        return base_dict
    
    def validate(self, header: Header, code: str, message: str):
        if not header.is_response():
            raise ValueError("Message type wrong, should be response")
        
        if code is None or not isinstance(code, str):
            raise ValueError("code is not valid.")
        
        if message is None or not isinstance(message, str):
            raise ValueError("message is not valid.")

class BaseWsNotify(BaseWsMessage):
    def __init__(self, header: Header):
        self.validate(header=header)
        super().__init__(header=header)
    
    def validate(self, header: Header):
        if not header.is_notify():
            raise ValueError("Message type wrong, should be notify")


class RegistrationWsRequest(BaseWsRequest):
    def __init__(self, header: Header, device_id: str):
        super().__init__(header=header)
        self.device_id = device_id

    def to_dict(self) -> dict[str, Any]:
        base_dict = super().to_dict()
        base_dict["data"] = {
            "device_id": self.device_id,
        }
        return base_dict

    @classmethod
    def from_dict(cls, header: Header, data: dict[str, Any]) -> 'RegistrationWsRequest':
        if not header.is_registration_message():
            raise ValueError("Message is not RegistrationWsRequest.")
        
        device_id = data.get("device_id")
        if device_id is None or not isinstance(device_id, str):
            raise ValueError("Device id is not valid.")
        return cls(header, device_id)
    
    @classmethod
    def create_message(cls, device_id: str) -> 'RegistrationWsRequest':
        if device_id is None or not isinstance(device_id, str):
            raise ValueError("Device id is not valid.")
        
        header = Header(name=MessageName_Registration, message_type=MessageType_Request)
        return cls(header, device_id)

class RegistrationWsResponse(BaseWsResponse):
    def __init__(self, header: Header, code: str, message: str, meta: dict=None):
        super().__init__(header=header, code=code, message=message, meta=meta)

    @classmethod
    def from_dict(cls, header: Header, data: dict[str, Any]) -> 'RegistrationWsResponse':
        if not header.is_registration_message():
            raise ValueError("Message is not RegistrationWsResponse.")
        
        code = data.get("code")
        message = data.get("message")
        meta = data.get("meta")
        return cls(header, code, message, meta)
    
    @classmethod
    def create_message(cls, id: str, code: str, message: str, meta: str=None) -> 'RegistrationWsResponse':
        if id is None or not isinstance(id, str):
            raise ValueError("Id is not valid.")
                
        header = Header(id=id, name=MessageName_Registration, message_type=MessageType_Response)
        return cls(header, code, message, meta)
    

class GetLastNDetectionsRequest(BaseWsRequest):
    def __init__(self,  header: Header,  last_n: int):
        super().__init__(header=header)
        self.last_n = last_n

    def to_dict(self) -> dict[str, Any]:
        base_dict = super().to_dict()
        base_dict["data"] = {
            "last_n": self.last_n,
        }
        return base_dict

    @classmethod
    def from_dict(cls, header: Header, data: dict[str, Any]) -> 'GetLastNDetectionsRequest':
        if not header.is_get_last_n_detections_message():
            raise ValueError("Message is not GetLastNDetectionsRequest.")
        
        last_n = data.get("last_n")
        if last_n is None or not isinstance(last_n, int):
            raise ValueError("last n is not valid.")
        return cls(header, last_n)
    
    @classmethod
    def create_message(cls, last_n: int) -> 'GetLastNDetectionsRequest':
        if last_n is None or not isinstance(last_n, int):
            raise ValueError("Lat N is not valid.")
        
        header = Header(name=MessageName_GetLastNDetections, message_type=MessageType_Request)
        return cls(header, last_n)

class DetectionLog:
    def __init__(self, t_value: float, d_value: int, ch1_area_p:int,
            ch1_area_n:int, ch2_area_p:int, ch2_area_n: int):
        self.t_value:float = t_value
        self.d_value:int = d_value
        self.ch1_area_p:int = ch1_area_p
        self.ch1_area_n:int = ch1_area_n
        self.ch2_area_p:int = ch2_area_p
        self.ch2_area_n:int = ch2_area_n
    
    def to_dict(self):
        return {
            "t_value": self.t_value,
            "d_value": self.d_value,
            "ch1_area_p": self.ch1_area_p,
            "ch1_area_n": self.ch1_area_n,
            "ch2_area_p": self.ch2_area_p,
            "ch2_area_n": self.ch2_area_n
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'DetectionLog':
        return DetectionLog(
            t_value=data.get("t_value"),
            d_value=data.get("d_value"),
            ch1_area_p=data.get("ch1_area_p"),
            ch1_area_n=data.get("ch1_area_n"),
            ch2_area_p=data.get("ch2_area_p"),
            ch2_area_n=data.get("ch2_area_n"),
        )
    
    
class DetectionLogs:
    def __init__(self, logs: list[DetectionLog] = None):
        self.logs = logs or []

    def to_dict(self) -> list[dict[str, int]]:
        return [log.to_dict() for log in self.logs]

    @classmethod
    def from_dict(cls, data: list[dict[str, int]]) -> 'DetectionLogs':
        logs = [DetectionLog.from_dict(log_data) for log_data in data]
        return cls(logs)

    def add_log(self, log: DetectionLog):
        if isinstance(log, DetectionLog):
            self.logs.append(log)
        else:
            raise TypeError("Only DetectionLog instances can be added.")

class GetLastNDetectionsResponse(BaseWsResponse)   :
    def __init__(self, header: Header, code: str, message: str, meta: dict=None,
            detections: DetectionLogs=None):
        super().__init__(header=header, code=code, message=message, meta=meta)
        self.detections:DetectionLogs = detections or DetectionLogs()

    def to_dict(self):
        base_dict = super().to_dict()
        base_dict["data"].update({
            "detections": self.detections.to_dict()
        })
        return base_dict
    
    @classmethod
    def from_dict(cls, header: Header, data: dict[str, Any]) -> 'GetLastNDetectionsResponse':
        if not header.is_get_last_n_detections_message():
            raise ValueError("Message is not GetLastNDetectionsResponse.")
        
        code = data.get("code")
        message = data.get("message")
        meta = data.get("meta")
        detections = data.get("detections")
        if detections is not None:
            detection_logs = DetectionLogs.from_dict(detections)
        else:
            detection_logs = DetectionLogs()
        return cls(header, code, message, meta, detection_logs)
    
    @classmethod
    def create_message(cls, id: str, code: str, message: str, meta: dict=None, 
            detections: DetectionLogs=None) -> 'GetLastNDetectionsResponse':
        if id is None or not isinstance(id, str):
            raise ValueError("Id is not valid.")
        if detections is None or not isinstance(detections, DetectionLogs):
            raise ValueError("Detections is not the DetectionLogs instance")        
        header = Header(id=id, name=MessageName_GetLastNDetections, message_type=MessageType_Response)
        return cls(header, code, message, meta, detections)

class SetThresholdRequest(BaseWsRequest):
    def __init__(self,  header: Header,  threshold: int):
        super().__init__(header=header)
        self.threshold = threshold

    def to_dict(self) -> dict[str, Any]:
        base_dict = super().to_dict()
        base_dict["data"] = {
            "threshold": self.threshold,
        }
        return base_dict

    @classmethod
    def from_dict(cls, header: Header, data: dict[str, Any]) -> 'SetThresholdRequest':
        if not header.is_set_threshold_message():
            raise ValueError("Message is not SetThresholdRequest.")
        
        threshold = data.get("threshold")
        if threshold is None or not isinstance(threshold, int):
            raise ValueError("threshold is not valid.")
        return cls(header, threshold)
    
    @classmethod
    def create_message(cls, threshold: int) -> 'SetThresholdRequest':
        if threshold is None or not isinstance(threshold, int):
            raise ValueError("Threshold is not valid.")
        
        header = Header(name=MessageName_SetThreshold, message_type=MessageType_Request)
        return cls(header, threshold)
    
class SetThresholdResponse(BaseWsResponse)   :
    def __init__(self, header: Header, code: str, message: str, meta: dict=None):
        super().__init__(header=header, code=code, message=message, meta=meta)

    @classmethod
    def from_dict(cls, header: Header, data: dict[str, Any]) -> 'SetThresholdResponse':
        if not header.is_set_threshold_message():
            raise ValueError("Message is not SetThresholdResponse.")
        
        code = data.get("code")
        message = data.get("message")
        meta = data.get("meta")
        return cls(header, code, message, meta)
    
    @classmethod
    def create_message(cls, id: str, code: str, message: str, meta: str=None) -> 'SetThresholdResponse':
        if id is None or not isinstance(id, str):
            raise ValueError("Id is not valid.")
                
        header = Header(id=id, name=MessageName_SetThreshold, message_type=MessageType_Response)
        return cls(header, code, message, meta)

class GetCalibrationRequest(BaseWsRequest):
    def __init__(self,  header: Header):
        super().__init__(header=header)
    
    def to_dict(self) -> dict[str, Any]:
        base_dict = super().to_dict()
        base_dict["data"] = {}
        return base_dict

    @classmethod
    def from_dict(cls, header: Header, data: dict[str, Any]) -> 'GetCalibrationRequest':
        if not header.is_get_calibration_message():
            raise ValueError("Message is not GetCalibrationRequest.")
        
        return cls(header)
    
    @classmethod
    def create_message(cls) -> 'GetCalibrationRequest':
        header = Header(name=MessageName_GetCalibration, message_type=MessageType_Request)
        return cls(header)

class CalibrationData:
    def __init__(self,
            pos_threshold1: int, neg_threshold1: int, pos_threshold2: int,
            neg_threshold2: int, mid_ch1: int, mid_ch2: int,
            area_threshold: int, t_value: float, d_value: int,
            current_threshold: int, current_bypass: int, engine_hour: str,
            is_calibration_failed: bool, calibration_failed_reason: int
        ):

        self.pos_threshold1 = pos_threshold1
        self.neg_threshold1 = neg_threshold1
        self.pos_threshold2 = pos_threshold2
        self.neg_threshold2 = neg_threshold2
        self.mid_ch1 = mid_ch1
        self.mid_ch2 = mid_ch2
        self.area_threshold = area_threshold
        self.t_value:float = t_value
        self.d_value = d_value
        self.current_threshold = current_threshold
        self.current_bypass = current_bypass
        self.engine_hour = engine_hour
        self.is_calibration_failed = is_calibration_failed
        self.calibration_failed_reason = calibration_failed_reason

    def to_dict(self):
        return {
            "pos_threshold1": self.pos_threshold1,
            "neg_threshold1": self.neg_threshold1,
            "pos_threshold2": self.pos_threshold2,
            "neg_threshold2": self.neg_threshold2,
            "mid_ch1": self.mid_ch1,
            "mid_ch2": self.mid_ch2,
            "area_threshold": self.area_threshold,
            "t_value": self.t_value,
            "d_value": self.d_value,
            "current_threshold": self.current_threshold,
            "current_bypass": self.current_bypass,
            "engine_hour": self.engine_hour,
            "is_calibration_failed": self.is_calibration_failed,
            "calibration_failed_reason": self.calibration_failed_reason
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'CalibrationData':
        return CalibrationData(
            pos_threshold1=data.get("pos_threshold1"),
            neg_threshold1=data.get("neg_threshold1"),
            pos_threshold2=data.get("pos_threshold2"),
            neg_threshold2=data.get("neg_threshold2"),
            mid_ch1=data.get("mid_ch1"),
            mid_ch2=data.get("mid_ch2"),
            area_threshold=data.get("area_threshold"),
            t_value=data.get("t_value"),
            d_value=data.get("d_value"),
            current_threshold=data.get("current_threshold"),
            current_bypass=data.get("current_bypass"),
            engine_hour=data.get("engine_hour"),
            is_calibration_failed=data.get("is_calibration_failed"),
            calibration_failed_reason=data.get("calibration_failed_reason")
        )
    

class GetCalibrationResponse(BaseWsResponse)   :
    def __init__(self, header: Header, code: str, message: str, meta: dict=None,
            calibration_data: CalibrationData=None):
        super().__init__(header=header, code=code, message=message, meta=meta)
        self.calibration_data = calibration_data 

    def to_dict(self):
        base_dict = super().to_dict()
        base_dict["data"].update({
            "calibration": self.calibration_data.to_dict()
        })
        return base_dict

    @classmethod
    def from_dict(cls, header: Header, data: dict[str, Any]) -> 'GetCalibrationResponse':
        if not header.is_get_calibration_message():
            raise ValueError("Message is not GetCalibrationResponse.")
        
        code = data.get("code")
        message = data.get("message")
        meta = data.get("meta")
        calibration_dict = data.get("calibration")
        if calibration_dict is None:
            raise ValueError("calibration field is not set, error.")
        
        calibration_data = CalibrationData.from_dict(calibration_dict)
        return cls(header, code, message, meta, calibration_data)
    
    @classmethod
    def create_message(cls, id: str, code: str, message: str, meta: str=None, 
            calibration_data: CalibrationData=None) -> 'GetCalibrationResponse':
        if id is None or not isinstance(id, str):
            raise ValueError("Id is not valid.")
        if calibration_data is None or not isinstance(calibration_data, CalibrationData):
            raise ValueError("Calibration data is not valid.")       
        header = Header(id=id, name=MessageName_GetCalibration, message_type=MessageType_Response)
        return cls(header, code, message, meta, calibration_data)

class SetDefaultCalibrationRequest(BaseWsRequest):
    def __init__(self,  header: Header):
        super().__init__(header=header)

    def to_dict(self) -> dict[str, Any]:
        base_dict = super().to_dict()
        base_dict["data"] = {}
        return base_dict

    @classmethod
    def from_dict(cls, header: Header, data: dict[str, Any]) -> 'SetDefaultCalibrationRequest':
        if not header.is_set_default_calibration_message():
            raise ValueError("Message is not SetDefaultCalibrationRequest.")

        return cls(header)
    
    @classmethod
    def create_message(cls) -> 'SetDefaultCalibrationRequest': 
        header = Header(name=MessageName_SetDefaultCalibration, message_type=MessageType_Request)
        return cls(header)
    
class SetDefaultCalibrationResponse(BaseWsResponse)   :
    def __init__(self, header: Header, code: str, message: str, meta: dict=None):
        super().__init__(header=header, code=code, message=message, meta=meta)

    @classmethod
    def from_dict(cls, header: Header, data: dict[str, Any]) -> 'SetDefaultCalibrationResponse':
        if not header.is_set_default_calibration_message():
            raise ValueError("Message is not SetDefaultCalibrationResponse.")
        
        code = data.get("code")
        message = data.get("message")
        meta = data.get("meta")
        return cls(header, code, message, meta)
    
    @classmethod
    def create_message(cls, id: str, code: str, message: str, meta: str=None) -> 'SetDefaultCalibrationResponse':
        if id is None or not isinstance(id, str):
            raise ValueError("Id is not valid.")
                
        header = Header(id=id, name=MessageName_SetDefaultCalibration, message_type=MessageType_Response)
        return cls(header, code, message, meta)


class NotifyByPassMessage(BaseWsNotify):
    def __init__(self, header: Header, bypass: int):
        super().__init__(header=header)
        self.bypass = bypass
    
    def to_dict(self):
        base_dict = super().to_dict()
        base_dict["data"] = {
            "bypass": self.bypass
        }
        return base_dict

    @classmethod
    def from_dict(cls, header: Header, data: dict[str, Any]) -> 'NotifyByPassMessage':
        bypass = data.get("bypass")
        if bypass is None or not isinstance(bypass, int):
            raise ValueError("bypass is not valid")
        return cls(
            header=header,
            bypass=bypass
        )

    @classmethod
    def create_message(cls, bypass: int) -> 'NotifyByPassMessage':
        if bypass is None or not isinstance(bypass, int):
            raise ValueError("bypass is not valid")
        
        header = Header(name=MessageName_NotifyByPass, message_type=MessageType_Notify)
        return cls(header, bypass)
    
class NotifyCalibrationMessage(BaseWsNotify):
    def __init__(
            self, header: Header, pos_threshold1:int, neg_threshold1:int, 
            pos_threshold2:int, neg_threshold2:int,
            mid_ch1:int, mid_ch2:int,area_threshold:int,
            t_value: float, d_value: int
        ):
        super().__init__(header=header)
        self.pos_threshold1 = pos_threshold1
        self.neg_threshold1 = neg_threshold1
        self.pos_threshold2 = pos_threshold2
        self.neg_threshold2 = neg_threshold2
        self.mid_ch1 = mid_ch1
        self.mid_ch2 = mid_ch2
        self.area_threshold = area_threshold
        self.t_value = t_value
        self.d_value = d_value

    def to_dict(self):
        base_dict = super().to_dict()
        base_dict["data"] = {
            "pos_threshold1": self.pos_threshold1,
            "neg_threshold1": self.neg_threshold1,
            "pos_threshold2": self.pos_threshold2,
            "neg_threshold2": self.neg_threshold2,
            "mid_ch1": self.mid_ch1,
            "mid_ch2": self.mid_ch2,
            "area_threshold": self.area_threshold,
            "t_value": self.t_value,
            "d_value": self.d_value
        }
        return base_dict

    @classmethod
    def from_dict(cls, header: Header, data: dict[str, Any]) -> 'NotifyCalibrationMessage':
        pos_threshold1 = data.get("pos_threshold1")
        neg_threshold1 = data.get("neg_threshold1")
        pos_threshold2 = data.get("pos_threshold2")
        neg_threshold2 = data.get("neg_threshold2")
        mid_ch1 = data.get("mid_ch1")
        mid_ch2 = data.get("mid_ch2")
        area_threshold = data.get("area_threshold")
        t_value = data.get("t_value")
        d_value = data.get("d_value")
        # do validate
        return cls(
            header=header,
            pos_threshold1=pos_threshold1,
            neg_threshold1=neg_threshold1,
            pos_threshold2=pos_threshold2,
            neg_threshold2=neg_threshold2,
            mid_ch1=mid_ch1,
            mid_ch2=mid_ch2,
            area_threshold=area_threshold,
            t_value=t_value,
            d_value=d_value
        )

    @classmethod
    def create_message(cls, 
            pos_threshold1:int, neg_threshold1:int, 
            pos_threshold2:int, neg_threshold2:int,
            mid_ch1:int, mid_ch2:int,area_threshold:int,
            t_value: float, d_value: int
        ) -> 'NotifyCalibrationMessage':
        if pos_threshold1 is None or not isinstance(pos_threshold1, int):
            raise ValueError("pos_threshold1 is not valid")
        
        header = Header(name=MessageName_NotifyCalibration, message_type=MessageType_Notify)
        return cls(
            header, 
            pos_threshold1=pos_threshold1, neg_threshold1=neg_threshold1,
            pos_threshold2=pos_threshold2, neg_threshold2=neg_threshold2,
            mid_ch1=mid_ch1, mid_ch2=mid_ch2, area_threshold=area_threshold,
            t_value=t_value, d_value=d_value
        )
    
class NotifyDetectionMessage(BaseWsNotify):
    def __init__(
            self, header: Header, ch1_area_p: int, ch1_area_n: int, 
            ch2_area_p: int, ch2_area_n: int,
            t_value: float, d_value: int
        ):
        super().__init__(header=header)
        self.ch1_area_p = ch1_area_p
        self.ch1_area_n = ch1_area_n
        self.ch2_area_p = ch2_area_p
        self.ch2_area_n = ch2_area_n
        self.t_value = t_value
        self.d_value = d_value
    
    def to_dict(self):
        base_dict = super().to_dict()
        base_dict["data"] = {
            "t_value": self.t_value,
            "d_value": self.d_value,
            "ch1_area_p": self.ch1_area_p,
            "ch1_area_n": self.ch1_area_n,
            "ch2_area_p": self.ch2_area_p,
            "ch2_area_n": self.ch2_area_n
        }
        return base_dict

    @classmethod
    def from_dict(cls, header: Header, data: dict[str, Any]) -> 'NotifyDetectionMessage':
        ch1_area_p = data.get("ch1_area_p")
        ch1_area_n = data.get("ch1_area_n")
        ch2_area_p = data.get("ch2_area_p")
        ch2_area_n = data.get("ch2_area_n")
        t_value = data.get("t_value")
        d_value = data.get("d_value")
        # do validate
        return cls(
            header=header,
            ch1_area_p=ch1_area_p,
            ch1_area_n=ch1_area_n,
            ch2_area_p=ch2_area_p,
            ch2_area_n=ch2_area_n,
            t_value=t_value,
            d_value=d_value
        )
    
    @classmethod
    def create_message(cls, 
            ch1_area_p:int, ch1_area_n:int, 
            ch2_area_p:int, ch2_area_n:int,
            t_value:float, d_value=float
        ) -> 'NotifyDetectionMessage':
        if ch1_area_p is None or not isinstance(ch1_area_p, int):
            raise ValueError("ch1_area_p is not valid")
        
        header = Header(name=MessageName_NotifyDetection, message_type=MessageType_Notify)
        return cls(
            header, 
            ch1_area_p=ch1_area_p, ch1_area_n=ch1_area_n,
            ch2_area_p=ch2_area_p, ch2_area_n=ch2_area_n,
            t_value=t_value,d_value=d_value
        )
    
class NotifyRawDataMessage(BaseWsNotify):
    def __init__(
            self, header: Header, input1_raw: int, input2_raw: int, 
            ch1_area_p: int, ch1_area_n: int, 
            ch2_area_p: int, ch2_area_n: int,
            timestamp: float
        ):
        super().__init__(header=header)
        self.input1_raw = input1_raw
        self.input2_raw = input2_raw
        self.ch1_area_p = ch1_area_p
        self.ch1_area_n = ch1_area_n
        self.ch2_area_p = ch2_area_p
        self.ch2_area_n = ch2_area_n
        self.timestamp = timestamp
    
    def to_dict(self):
        base_dict = super().to_dict()
        base_dict["data"] = {
            "input1_raw": self.input1_raw,
            "input2_raw": self.input2_raw,
            "ch1_area_p": self.ch1_area_p,
            "ch1_area_n": self.ch1_area_n,
            "ch2_area_p": self.ch2_area_p,
            "ch2_area_n": self.ch2_area_n,
            "timestamp": self.timestamp
        }
        return base_dict

    @classmethod
    def from_dict(cls, header: Header, data: dict[str, Any]) -> 'NotifyRawDataMessage':
        input1_raw = data.get("input1_raw")
        input2_raw = data.get("input2_raw")
        ch1_area_p = data.get("ch1_area_p")
        ch1_area_n = data.get("ch1_area_n")
        ch2_area_p = data.get("ch2_area_p")
        ch2_area_n = data.get("ch2_area_n")
        timestamp = data.get("timestamp")
        return cls(
            header=header,
            input1_raw=input1_raw,
            input2_raw=input2_raw,
            ch1_area_p=ch1_area_p,
            ch1_area_n=ch1_area_n,
            ch2_area_p=ch2_area_p,
            ch2_area_n=ch2_area_n,
            timestamp=timestamp
        )

    @classmethod
    def create_message(cls, 
            input1_raw: int, input2_raw: int, 
            ch1_area_p: int, ch1_area_n: int, 
            ch2_area_p: int, ch2_area_n: int,
            timestamp: float
        ) -> 'NotifyRawDataMessage':
        if input1_raw is None or not isinstance(input1_raw, int):
            raise ValueError("input1_raw is not valid")
        
        header = Header(name=MessageName_NotifyRawData, message_type=MessageType_Notify)
        return cls(
            header, 
            input1_raw=input1_raw, input2_raw=input2_raw,
            ch1_area_p=ch1_area_p, ch1_area_n=ch1_area_n,
            ch2_area_p=ch2_area_p, ch2_area_n=ch2_area_n,
            timestamp=timestamp
        )
    
class NotifyThresholdAdjustedMessage(BaseWsNotify):
    def __init__(self ,header: Header, area_threshold: int):
        super().__init__(header=header)
        self.area_threshold = area_threshold
    
    def to_dict(self):
        base_dict = super().to_dict()
        base_dict["data"] = {
            "area_threshold": self.area_threshold
        }
        return base_dict

    @classmethod
    def from_dict(cls, header: Header, data: dict[str, Any]) -> 'NotifyThresholdAdjustedMessage':
        area_threshold = data.get("area_threshold")
        return cls(
            header=header,
            area_threshold=area_threshold
        )
    
    @classmethod
    def create_message(cls, area_threshold: int) -> 'NotifyThresholdAdjustedMessage':
        if area_threshold is None or not isinstance(area_threshold, int):
            raise ValueError("area_threshold is not valid")
        
        header = Header(name=MessageName_NotifyThresholdAdjusted, message_type=MessageType_Notify)
        return cls(
            header, 
            area_threshold=area_threshold,
        )

class NotifyEngineHourMessage(BaseWsNotify):
    def __init__(self ,header: Header, engine_hour: str):
        super().__init__(header=header)
        self.engine_hour = engine_hour
    
    def to_dict(self):
        base_dict = super().to_dict()
        base_dict["data"] = {
            "engine_hour": self.engine_hour
        }
        return base_dict

    @classmethod
    def from_dict(cls, header: Header, data: dict[str, Any]) -> 'NotifyEngineHourMessage':
        engine_hour = data.get("engine_hour")
        return cls(
            header=header,
            engine_hour=engine_hour
        )
    
    @classmethod
    def create_message(cls, engine_hour: str) -> 'NotifyEngineHourMessage':
        if engine_hour is None or not isinstance(engine_hour, str):
            raise ValueError("engine_hour is not valid")
        
        header = Header(name=MessageName_NotifyEngineHour, message_type=MessageType_Notify)
        return cls(
            header, 
            engine_hour=engine_hour,
        )

class NotifyCalibrationFailedMessage(BaseWsNotify):
    def __init__(self ,header: Header, reason: int):
        super().__init__(header=header)
        self.reason = reason
    
    def to_dict(self):
        base_dict = super().to_dict()
        base_dict["data"] = {
            "reason": self.reason
        }
        return base_dict

    @classmethod
    def from_dict(cls, header: Header, data: dict[str, Any]) -> 'NotifyCalibrationFailedMessage':
        reason = data.get("reason")
        return cls(
            header=header,
            reason=reason
        )
    
    @classmethod
    def create_message(cls, reason: int) -> 'NotifyCalibrationFailedMessage':
        if reason is None or not isinstance(reason, int):
            raise ValueError("reason is not valid")
        
        header = Header(name=MessageName_NotifyCalibration_Failed, message_type=MessageType_Notify)
        return cls(
            header, 
            reason=reason,
        )
    
class SystemErrorResponse(BaseWsResponse):
    def __init__(self, header: Header, code: str, message: str, meta:dict=None):
        super().__init__(header=header, code=code, message=message, meta=meta)

    @classmethod
    def create_message(cls, message: str, meta: dict=None)->'SystemErrorResponse':
        return cls(
            Header(name=MessageName_SystemError, message_type=MessageType_Response),
            code="error",
            message=message,
            meta=meta
        ) 
    @classmethod
    def from_dict(cls, header: Header, data: dict[str, Any]) -> 'SystemErrorResponse':
        code = data.get("code")
        message = data.get("message")
        meta = data.get("meta")
        return cls(
            header=header,
            code=code,
            message=message,
            meta=meta
        )