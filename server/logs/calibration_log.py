from datetime import datetime
from .base_log import BaseLog
from log.logger import Logger

class CalibrationLogData:
    def __init__(self, started_at:str, 
            pos_threshold1: int, neg_threshold1: int, pos_threshold2: int,
            neg_threshold2: int, mid_ch1: int, mid_ch2: int,
            area_threshold: int, t_value: float, d_value: int
        ):
        if started_at is None or len(started_at) == 0:
            self.started_at = datetime.now()
        else:
            self.started_at = datetime.fromisoformat(started_at)
        
        self.pos_threshold1 = pos_threshold1
        self.neg_threshold1 = neg_threshold1
        self.pos_threshold2 = pos_threshold2
        self.neg_threshold2 = neg_threshold2
        self.mid_ch1 = mid_ch1
        self.mid_ch2 = mid_ch2
        self.area_threshold = area_threshold
        self.t_value:float = t_value
        self.d_value = d_value

    def _is_default(self):
        return self.pos_threshold1 == 0
    
    @classmethod
    def from_dict(cls, data: dict) -> 'CalibrationLogData':
        return cls(
            started_at=data.get("started_at"),
            pos_threshold1=data.get("pos_threshold1"),
            neg_threshold1=data.get("neg_threshold1"),
            pos_threshold2=data.get("pos_threshold2"),
            neg_threshold2=data.get("neg_threshold2"),
            mid_ch1=data.get("mid_ch1"),
            mid_ch2=data.get("mid_ch2"),
            area_threshold=data.get("area_threshold"),
            t_value=data.get("t_value"),
            d_value=data.get("d_value"),
        )
        
    def to_dict(self):
        return {
            "started_at": self.started_at.isoformat(),
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
    
class CalibrationLogHistories:
    def __init__(self):
        self.calibrations:list[CalibrationLogData] = []

    def add_calibration_log(self, calibration_log: CalibrationLogData):
        self.calibrations.append(calibration_log)

    def parse_data(self, data: list):
         for item in data:
            self.add_calibration_log(CalibrationLogData.from_dict(item))

    def to_dict(self):
        return [item.to_dict() for item in self.calibrations]
    

class CalibrationLog(BaseLog):
    def __init__(self, log_directory:str, file_name:str="calibrations.json"):
        super().__init__(log_directory=log_directory, file_name=file_name)

    def get_current_calibration(self) -> CalibrationLogData:
        calibration_log = self._read_json() or {}
        return self._read_current_calibration_log(calibration_log.get("current_calibration"))
           
    def update_calibration_log_data(self, calibration_log_data: CalibrationLogData):
        if calibration_log_data is None or not isinstance(calibration_log_data, CalibrationLogData):   
            raise ValueError("calibration_log_data is invalid.")
        calibration_log = self._read_json() or {}
        current_calibration_log = self._read_current_calibration_log(calibration_log.get("current_calibration"))
        histories = self._read_current_calibration_log_histories(calibration_log.get("calibration_histories"))

        if not current_calibration_log._is_default():
            histories.add_calibration_log(current_calibration_log)

        current_calibration_log = calibration_log_data
        data = {
            "current_calibration": current_calibration_log.to_dict(),
            "calibration_histories": histories.to_dict()
        }
        self._write_json(data)

    def _read_current_calibration_log(self, calibration_dict: dict)->CalibrationLogData:
        if calibration_dict is not None:
            return CalibrationLogData.from_dict(calibration_dict)
        else:
            return CalibrationLogData(
                started_at=None,
                pos_threshold1=0,
                neg_threshold1=0,
                pos_threshold2=0,
                neg_threshold2=0,
                mid_ch1=0,
                mid_ch2=0,
                area_threshold=0,
                t_value=0.0,
                d_value=0
            )

    def _read_current_calibration_log_histories(self, history_list: list)->CalibrationLogHistories:
        histories = CalibrationLogHistories()
        if history_list is not None:
            histories.parse_data(history_list)
        return histories
