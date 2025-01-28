import json
from datetime import datetime
from typing import Dict, Any, Type, List
import ulid
import ulid.ulid

MessageType_Request = "request"
MessageType_Response = "response"
MessageType_Notify = "unregistered"
class BaseWsMessage:
    def __init__(self, name: str, message_type: str, id: str=None, ts: str = None):
        self.name = name
        self.id = id or str(ulid.new())
        self.ts = ts or datetime.now().isoformat()
        self.message_type = message_type
        
    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "id": self.id,
            "ts": self.ts,
            "type": self.message_type
        }

class BaseWsRequest(BaseWsMessage):
    def __init__(self, name: str, id: str=None, ts: str = None):
        super().__init__(name=name, message_type="request", id=id, ts=ts)

class BaseWsResponse(BaseWsMessage):
    def __init__(self, name:str, id: str, code:str, message: str, data: dict=None):
        super().__init__(name=name, message_type="response", id=id)
        self.code = code
        self.message = message
        self.data = data

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        base_dict = super().to_dict()
        base_dict["code"] = self.code
        if self.data is not None:
            base_dict["data"] = self.data

        return base_dict
    
class RegistrationWsRequest(BaseWsRequest):
    def __init__(self, data: dict, id: str=None, ts: str=None):
        super().__init__(name="registration", id=id, ts=ts)
        self.device_id = data.get("device_id")

    def to_dict(self) -> Dict[str, Any]:
        base_dict = super().to_dict()
        base_dict["data"] = {
            "device_id": self.device_id,
        }
        return base_dict

class RegistrationWsResponse(BaseWsResponse):
    def __init__(self, id: str, code: str, message: str, data: dict=None):
        super().__init__(name="registration", id=id, code=code, message=message, data=data)

class SetThresholdRequest(BaseWsRequest):
    def __init__(self, data: dict, threshold: int=None, ts: str=None):
        super().__init__(name="set_threshold", id=id, ts=ts)
        self.threshold = threshold
        pass

    def to_dict(self) -> Dict[str, Any]:
        base_dict = super().to_dict()
        base_dict["data"] = {
            "threshold": self.threshold,
        }
        return base_dict
    
class SetThresholdResponse(BaseWsResponse):
    def __init__(self, id, code, message, data: dict=None):
        super().__init__(name="set_threshold", id=id, code=code, message=message, data=data)

class SystemErrorResponse(BaseWsResponse):
    def __init__(self, message: str, data:dict=None):
        super().__init__(name="system_error", code="error", message=message,data=data)

class BaseWsNotify(BaseWsMessage):
    def __init__(self, name: str):
        super().__init__(name=name, message_type="notify")


class NotifyByPassMessage(BaseWsNotify):
    def __init__(self, bypass: int):
        super().__init__(name="notify_bypass")
        self.bypass = bypass
    
    def to_dict(self):
        base_dict = super().to_dict()
        base_dict["data"] = {
            "bypass": self.bypass
        }
        return base_dict

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NotifyByPassMessage':
        bypass = data.get("bypass")
      
        return cls(
            bypass=bypass
        )
    
class NotifyCalibrationMessage(BaseWsNotify):
    def __init__(self, pos_threshold1:int, neg_threshold1:int, 
                 pos_threshold2:int, neg_threshold2:int,
                 mid_ch1:int, mid_ch2:int,area_threshold:int):
        super().__init__(name="notify_calibration")
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
    def from_dict(cls, data: Dict[str, Any]) -> 'NotifyByPassMessage':
        pos_threshold1 = data.get("pos_threshold1")
        neg_threshold1 = data.get("neg_threshold1")
        pos_threshold2 = data.get("pos_threshold2")
        neg_threshold2 = data.get("neg_threshold2")
        mid_ch1 = data.get("mid_ch1")
        mid_ch2 = data.get("mid_ch2")
        area_threshold = data.get("area_threshold")
      
        return cls(
            pos_threshold1=pos_threshold1,
            neg_threshold1=neg_threshold1,
            pos_threshold2=pos_threshold2,
            neg_threshold2=neg_threshold2,
            mid_ch1=mid_ch1,
            mid_ch2=mid_ch2,
            area_threshold=area_threshold,
        )

class NotifyDetectionMessage(BaseWsNotify):
    def __init__(self, ch1_area_p: int, ch1_area_n: int, 
                 ch2_area_p: int, ch2_area_n: int, ):
        super().__init__(name="notify_detection")
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
    def from_dict(cls, data: Dict[str, Any]) -> 'NotifyByPassMessage':
        ch1_area_p = data.get("ch1_area_p")
        ch1_area_n = data.get("ch1_area_n")
        ch2_area_p = data.get("ch2_area_p")
        ch2_area_n = data.get("ch2_area_n")
      
        return cls(
            ch1_area_p=ch1_area_p,
            ch1_area_n=ch1_area_n,
            ch2_area_p=ch2_area_p,
            ch2_area_n=ch2_area_n
        )
    
class NotifyRawDataMessage(BaseWsNotify):
    def __init__(self, input1_raw: int, input2_raw: int, 
                 ch1_area_p: int, ch1_area_n: int, 
                 ch2_area_p: int, ch2_area_n: int):
        super().__init__(name="notify_raw_data")
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
    def from_dict(cls, data: Dict[str, Any]) -> 'NotifyByPassMessage':
        input1_raw = data.get("input1_raw")
        input2_raw = data.get("input2_raw")
        ch1_area_p = data.get("ch1_area_p")
        ch1_area_n = data.get("ch1_area_n")
        ch2_area_p = data.get("ch2_area_p")
        ch2_area_n = data.get("ch2_area_n")
      
        return cls(
            input1_raw=input1_raw,
            input2_raw=input2_raw,
            ch1_area_p=ch1_area_p,
            ch1_area_n=ch1_area_n,
            ch2_area_p=ch2_area_p,
            ch2_area_n=ch2_area_n
        )

class NotifyThresholdAdjustedMessage(BaseWsNotify):
    def __init__(self, area_threshold: int):
        super().__init__(name="notify_threshold_adjusted")
        self.area_threshold = area_threshold
    
    def to_dict(self):
        base_dict = super().to_dict()
        base_dict["data"] = {
            "area_threshold": self.area_threshold
        }
        return base_dict

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NotifyByPassMessage':
        area_threshold = data.get("area_threshold")
        return cls(
            area_threshold=area_threshold
        )
    
WSMESSAGE_NAME_MAP: Dict[str, Type[BaseWsMessage]] = {
    "registration": RegistrationWsRequest,
    "set_threshold": SetThresholdRequest,
}

def create_from_dict(data: Dict[str, Any]) -> BaseWsMessage:
    name = data.get("name")
    id=data.get("id")
    ts=data.get("ts")
    if name not in WSMESSAGE_NAME_MAP:
        raise ValueError(f"Unknown message type: {name}")

    message_class = WSMESSAGE_NAME_MAP[name]
    if message_class != None:
        return message_class(
            data=data["data"],
            id=id,
            ts=ts
        )
    else:
        raise NotImplementedError(f"Deserialization for {name} is not implemented.")

