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
    def __init__(self, device_id: str, id: str=None, ts: str=None):
        super().__init__(name="registration", id=id, ts=ts)
        self.device_id = device_id

    def to_dict(self) -> Dict[str, Any]:
        base_dict = super().to_dict()
        base_dict["data"] = {
            "device_id": self.device_id,
        }
        return base_dict

class RegistrationWsResponse(BaseWsResponse):
    def __init__(self, id: str, code: str, message: str, data: dict=None):
        super().__init__(name="registration", id=id, code=code, message=message, data=data)
