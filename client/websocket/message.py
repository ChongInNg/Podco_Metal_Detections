import json
from datetime import datetime
from typing import Dict, Any, Type, List
import ulid
import ulid.ulid

MessageType_Request = "request"
MessageType_Response = "response"
MessageType_Notify = "notify"

MessageName_Registration = "registration"

MessageName_NotifyByPass = "notify_bypass"
MessageName_NotifyCalibration = "notify_calibration"
MessageName_NotifyDetection = "notify_detection"
MessageName_NotifyRawData = "notify_raw_data"
MessageName_NotifyThresholdAdjusted = "notify_threshold_adjusted"

class Message:
    def __init__(self, header, data):
        self.header = header
        self.data = data
        pass

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

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "id": self.id,
            "ts": self.ts,
            "type": self.message_type
        }
    
    def is_registration_message(self):
        return self.name == MessageName_Registration

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

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Header':
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
        
    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return self.header.to_dict()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseWsMessage':
        header = Header.from_dict(data)
        msg_data = data.get("data")
        if msg_data is None or not isinstance(msg_data, Dict):
            raise ValueError("Message data format is wrong. should be a dictionary.")
        
        if header.is_registration_message():
            if header.is_request():
                return RegistrationWsRequest.from_dict(header=header, data=msg_data)
            else:
                return RegistrationWsResponse.from_dict(header=header, data=data)
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
        else:
            raise ValueError("Message name is wrong.")
        
class BaseWsRequest(BaseWsMessage):
    def __init__(self, header: Header):
        self.validate(header=header)
        super().__init__(header=header)
    
    def validate(self, header: Header):
        if not header.is_request():
            raise ValueError("Message type wrong, should be request")

class BaseWsResponse(BaseWsMessage):
    def __init__(self, header: Header, code:str, message: str):
        self.validate(header=header, code=code,message=message)
        super().__init__(header=header)
        self.code = code
        self.message = message

    def to_dict(self) -> Dict[str, Any]:
        base_dict = super().to_dict()
        base_dict["code"] = self.code
        base_dict["message"] = self.message
        return base_dict
    
    def validate(self, header: Header, code: str, message: str):
        if not header.is_response():
            raise ValueError("Message type wrong, should be response")
        
        if code is None or not isinstance(code, str):
            raise ValueError("code is not valid.")
        
        # if message is None or not isinstance(message, str):
        #     raise ValueError("message is not valid.")

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

    def to_dict(self) -> Dict[str, Any]:
        base_dict = super().to_dict()
        base_dict["data"] = {
            "device_id": self.device_id,
        }
        return base_dict

    @classmethod
    def from_dict(cls, header: Header, data: Dict[str, Any]) -> 'RegistrationWsRequest':
        if not header.is_registration_message():
            raise ValueError("Message name is not valid.")
        
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
    def __init__(self, header: Header, code: str, message: str, meta: Dict=None):
        super().__init__(header=header, code=code, message=message)
        self.meta = meta

    def to_dict(self) -> Dict[str, Any]:
        base_dict = super().to_dict()
        if self.meta is not None:
            base_dict["meta"] = self.meta 
        return base_dict

    @classmethod
    def from_dict(cls, header: Header, data: Dict[str, Any]) -> 'RegistrationWsResponse':
        if not header.is_registration_message():
            raise ValueError("Message name is not valid.")
        
        code = data.get("code")
        message = data.get("message")
        meta = data.get("meta")
        if code is None or not isinstance(code, str):
            raise ValueError("Code id is not valid.")
        return cls(header, code, message, meta)
    
    @classmethod
    def create_message(cls, id: str, code: str, message: str, meta: str=None) -> 'RegistrationWsResponse':
        if id is None or not isinstance(id, str):
            raise ValueError("Id is not valid.")
        
        header = Header(id=id, name=MessageName_Registration, message_type=MessageType_Response)
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
    def from_dict(cls, header: Header, data: Dict[str, Any]) -> 'NotifyByPassMessage':
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
    def __init__(self, header: Header, pos_threshold1:int, neg_threshold1:int, 
                 pos_threshold2:int, neg_threshold2:int,
                 mid_ch1:int, mid_ch2:int,area_threshold:int):
        super().__init__(header=header)
        self.pos_threshold1 = pos_threshold1
        self.neg_threshold1 = neg_threshold1
        self.pos_threshold2 = pos_threshold2
        self.neg_threshold2 = neg_threshold2
        self.mid_ch1 = mid_ch1
        self.mid_ch2 = mid_ch2
        self.area_threshold = area_threshold

    def to_dict(self):
        base_dict = super().to_dict()
        base_dict["data"] = {
            "pos_threshold1": self.pos_threshold1,
            "neg_threshold1": self.neg_threshold1,
            "pos_threshold2": self.pos_threshold2,
            "neg_threshold2": self.neg_threshold2,
            "mid_ch1": self.mid_ch1,
            "mid_ch2": self.mid_ch2,
            "area_threshold": self.area_threshold
        }
        return base_dict

    @classmethod
    def from_dict(cls, header: Header, data: Dict[str, Any]) -> 'NotifyCalibrationMessage':
        pos_threshold1 = data.get("pos_threshold1")
        neg_threshold1 = data.get("neg_threshold1")
        pos_threshold2 = data.get("pos_threshold2")
        neg_threshold2 = data.get("neg_threshold2")
        mid_ch1 = data.get("mid_ch1")
        mid_ch2 = data.get("mid_ch2")
        area_threshold = data.get("area_threshold")
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
        )

    @classmethod
    def create_message(cls, 
            pos_threshold1:int, neg_threshold1:int, 
            pos_threshold2:int, neg_threshold2:int,
            mid_ch1:int, mid_ch2:int,area_threshold:int
        ) -> 'NotifyCalibrationMessage':
        if pos_threshold1 is None or not isinstance(pos_threshold1, int):
            raise ValueError("pos_threshold1 is not valid")
        
        header = Header(name=MessageName_NotifyCalibration, message_type=MessageType_Notify)
        return cls(
            header, 
            pos_threshold1=pos_threshold1, neg_threshold1=neg_threshold1,
            pos_threshold2=pos_threshold2, neg_threshold2=neg_threshold2,
            mid_ch1=mid_ch1, mid_ch2=mid_ch2, area_threshold=area_threshold,
        )
    
class NotifyDetectionMessage(BaseWsNotify):
    def __init__(self, header: Header, ch1_area_p: int, ch1_area_n: int, 
                 ch2_area_p: int, ch2_area_n: int, ):
        super().__init__(header=header)
        self.ch1_area_p = ch1_area_p
        self.ch1_area_n = ch1_area_n
        self.ch2_area_p = ch2_area_p
        self.ch2_area_n = ch2_area_n
    
    def to_dict(self):
        base_dict = super().to_dict()
        base_dict["data"] = {
            "ch1_area_p": self.ch1_area_p,
            "ch1_area_n": self.ch1_area_n,
            "ch2_area_p": self.ch2_area_p,
            "ch2_area_n": self.ch2_area_n
        }
        return base_dict

    @classmethod
    def from_dict(cls, header: Header, data: Dict[str, Any]) -> 'NotifyDetectionMessage':
        ch1_area_p = data.get("ch1_area_p")
        ch1_area_n = data.get("ch1_area_n")
        ch2_area_p = data.get("ch2_area_p")
        ch2_area_n = data.get("ch2_area_n")
        # do validate
        return cls(
            header=header,
            ch1_area_p=ch1_area_p,
            ch1_area_n=ch1_area_n,
            ch2_area_p=ch2_area_p,
            ch2_area_n=ch2_area_n
        )
    
    @classmethod
    def create_message(cls, 
            ch1_area_p:int, ch1_area_n:int, 
            ch2_area_p:int, ch2_area_n:int,
        ) -> 'NotifyCalibrationMessage':
        if ch1_area_p is None or not isinstance(ch1_area_p, int):
            raise ValueError("ch1_area_p is not valid")
        
        header = Header(name=MessageName_NotifyDetection, message_type=MessageType_Notify)
        return cls(
            header, 
            ch1_area_p=ch1_area_p, ch1_area_n=ch1_area_n,
            ch2_area_p=ch2_area_p, ch2_area_n=ch2_area_n,
        )
    
class NotifyRawDataMessage(BaseWsNotify):
    def __init__(self, header: Header, input1_raw: int, input2_raw: int, 
                 ch1_area_p: int, ch1_area_n: int, 
                 ch2_area_p: int, ch2_area_n: int):
        super().__init__(header=header)
        self.input1_raw = input1_raw
        self.input2_raw = input2_raw
        self.ch1_area_p = ch1_area_p
        self.ch1_area_n = ch1_area_n
        self.ch2_area_p = ch2_area_p
        self.ch2_area_n = ch2_area_n
    
    def to_dict(self):
        base_dict = super().to_dict()
        base_dict["data"] = {
            "input1_raw": self.input1_raw,
            "input2_raw": self.input2_raw,
            "ch1_area_p": self.ch1_area_p,
            "ch1_area_n": self.ch1_area_n,
            "ch2_area_p": self.ch2_area_p,
            "ch2_area_n": self.ch2_area_n
        }
        return base_dict

    @classmethod
    def from_dict(cls, header: Header, data: Dict[str, Any]) -> 'NotifyRawDataMessage':
        input1_raw = data.get("input1_raw")
        input2_raw = data.get("input2_raw")
        ch1_area_p = data.get("ch1_area_p")
        ch1_area_n = data.get("ch1_area_n")
        ch2_area_p = data.get("ch2_area_p")
        ch2_area_n = data.get("ch2_area_n")
      
        return cls(
            header=header,
            input1_raw=input1_raw,
            input2_raw=input2_raw,
            ch1_area_p=ch1_area_p,
            ch1_area_n=ch1_area_n,
            ch2_area_p=ch2_area_p,
            ch2_area_n=ch2_area_n
        )

    @classmethod
    def create_message(cls, 
            input1_raw: int, input2_raw: int, 
            ch1_area_p: int, ch1_area_n: int, 
            ch2_area_p: int, ch2_area_n: int
        ) -> 'NotifyCalibrationMessage':
        if input1_raw is None or not isinstance(input1_raw, int):
            raise ValueError("input1_raw is not valid")
        
        header = Header(name=MessageName_NotifyRawData, message_type=MessageType_Notify)
        return cls(
            header, 
            input1_raw=input1_raw, input2_raw=input2_raw,
            ch1_area_p=ch1_area_p, ch1_area_n=ch1_area_n,
            ch2_area_p=ch2_area_p, ch2_area_n=ch2_area_n,
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
    def from_dict(cls, header: Header, data: Dict[str, Any]) -> 'NotifyThresholdAdjustedMessage':
        area_threshold = data.get("area_threshold")
        return cls(
            header=header,
            area_threshold=area_threshold
        )
    
    @classmethod
    def create_message(cls, 
            area_threshold: int,
        ) -> 'NotifyCalibrationMessage':
        if area_threshold is None or not isinstance(area_threshold, int):
            raise ValueError("area_threshold is not valid")
        
        header = Header(name=MessageName_NotifyThresholdAdjusted, message_type=MessageType_Notify)
        return cls(
            header, 
            area_threshold=area_threshold,
        )