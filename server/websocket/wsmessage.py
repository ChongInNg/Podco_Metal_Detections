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

