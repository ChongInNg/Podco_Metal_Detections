from datetime import datetime
from .base_log import BaseLog
from log.logger import Logger


class DetectionLogData:
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
    def from_dict(cls, data: dict) -> 'DetectionLogData':
        return cls(
            t_value=data.get("t_value"),
            d_value=data.get("d_value"),
            ch1_area_p=data.get("ch1_area_p"),
            ch1_area_n=data.get("ch1_area_n"),
            ch2_area_p=data.get("ch2_area_p"),
            ch2_area_n=data.get("ch2_area_n"),
        )

class DetectionLog(BaseLog):
    def __init__(self, log_directory:str, file_name:str="detections.json"):
        super().__init__(log_directory=log_directory, file_name=file_name)

    def get_last_n_detections(self, n: int) -> list[DetectionLogData]:
        detections = self._read_json()
        if detections is None:
            return []
        
        last_n_detections = detections[-n:] if n > 0 else []
        resp = [DetectionLogData.from_dict(detection) for detection in last_n_detections]
        return resp
         
    def save_detection_data(self, detection_data: DetectionLogData):
        detection_log = self._read_json() or []
        detection_log.append(detection_data.to_dict())
        try:
            self._write_json(detection_log)
            Logger.debug(f"Detection data appended successfully to {self.full_name}.")
        except Exception as e:
            Logger.error(f"Failed to save detection data: {e}")