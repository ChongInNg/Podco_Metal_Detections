from log.logger import Logger
from log_manager import LogManager

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from share.wsmessage import *


import asyncio

class Connection:
    Status_Registered = "registered"
    Status_UnRegistered = "unregistered"
    def __init__(self, conn):
        self.conn = conn
        self.client_id = id(conn)
        self.status = Connection.Status_Registered
        self.registered_at = None
        self.device_id = None

    def get_identity(self):
        return self.device_id
    
    async def handle_message(self, message: BaseWsMessage):
        try:
            Logger.debug(f"Handling message: {message.to_dict()}")
            if isinstance(message, RegistrationWsRequest):
               await self.handle_registration(message)
            elif isinstance(message, SetThresholdRequest):
                await self.handle_set_threshold(message)
            elif isinstance(message, GetLastNDetectionsRequest):
                await self.handle_get_last_n_detections(message)
            elif isinstance(message, SetDefaultCalibrationRequest):
                await self.handle_set_default_calibration(message)
            elif isinstance(message, GetCalibrationRequest):
                await self._handle_get_calibration_data(message)
            else:
                Logger.warning(f"Cannot handle this message: {message}")
        except Exception as e:
            import traceback
            traceback.print_stack()
            await self.send_system_error(f"Handle message error:{e}")
            
    
    async def handle_registration(self, message: RegistrationWsRequest):
        self.status = Connection.Status_Registered
        self.registered_at = datetime.now().isoformat()
        self.device_id = message.device_id

        rsp = RegistrationWsResponse.create_message(
            id=message.id, code="OK", message="register successfully",
            meta={"device_id": message.device_id}
        )

        await self.conn.send(rsp.to_json())
        Logger.debug(f"Handle registeration success: {rsp.to_dict()}")

    async def handle_set_threshold(self, message: SetThresholdRequest):
        from serial_server import SerialServer
        if self.status != Connection.Status_Registered:
            Logger.error("This connection didn't registered yet, cannot handle set threshold message.")
            await self.send_error_response(message, "connection didn't registered yet")
            return
        
        await asyncio.to_thread(SerialServer.instance().send_threshold_request(message.threshold))

        rsp = SetThresholdResponse.create_message(
            id=message.id, code="OK", 
            message="set threshold completed."
        )
        await self.conn.send(rsp.to_json())
        Logger.debug(f"Handle set threshold success: {rsp.to_dict()}")
        

    async def handle_set_default_calibration(self, message: SetDefaultCalibrationRequest):
        from serial_server import SerialServer
        if self.status != Connection.Status_Registered:
            Logger.error("This connection didn't registered yet, cannot handle set default calibration message.")
            await self.send_error_response(message, "connection didn't registered yet")
            return
        
        await asyncio.to_thread(SerialServer.instance().send_default_calibration_request())
        rsp = SetDefaultCalibrationResponse.create_message(
            id=message.id, code="OK", 
            message="set default calibration completed."
        )
        await self.conn.send(rsp.to_json())
        Logger.debug(f"Handle set default calibration success: {rsp.to_dict()}")

    async def handle_get_last_n_detections(self, message: GetLastNDetectionsRequest):
        if self.status != Connection.Status_Registered:
            Logger.error("This connection didn't registered yet, cannot handle set default calibration message.")
            await self.send_error_response(message, "connection didn't registered yet")
            return
        
        detections = LogManager.instance().get_last_n_detections(message.last_n)
        detection_logs = DetectionLogs()
        for detection in detections:
            log = DetectionLog.from_dict(detection.to_dict())
            detection_logs.add_log(log)

        rsp = GetLastNDetectionsResponse.create_message(
            id=message.id, code="OK",
            message="get last n detections successfully.",
            detections=detection_logs
        )

        await self.conn.send(rsp.to_json())
        Logger.debug(f"Send back last n detections: {len(detections)}")


    async def send_system_error(self, message: str, data:dict=None):
        rsp = SystemErrorResponse.create_message(message)
        await self.conn.send(rsp.to_json())
        Logger.debug(f"Send system error: {rsp}")

    async def send_error_response(self, req: BaseWsMessage, message: str, meta: dict=None):
        response_map = {
            RegistrationWsRequest: RegistrationWsResponse,
            SetDefaultCalibrationRequest: SetDefaultCalibrationResponse,
            SetThresholdRequest: SetThresholdResponse,
            GetLastNDetectionsRequest: GetLastNDetectionsResponse,
            GetCalibrationRequest: GetCalibrationResponse,
        }
        
        response_cls = response_map.get(type(req))
        if response_cls is None:
            await self.send_system_error(message) 
        
        rsp = response_cls.create_message(
            id= req.id, 
            code="error",
            message=message,
            meta=meta
        )
        await self.conn.send(rsp.to_json())
            
    async def send_notify_message(self, notify_msg: BaseWsNotify):
        json_msg = notify_msg.to_json()
        await self.conn.send(json_msg)
        Logger.debug(f"Send notify message:{notify_msg.name} successfully: {json_msg}")

    async def _handle_get_calibration_data(self, message: GetCalibrationRequest):
        if self.status != Connection.Status_Registered:
            Logger.error("This connection didn't registered yet, cannot handle get calibration data .")
            await self.send_error_response(message, "connection didn't registered yet")
            return

        calibration_log = LogManager.instance().get_current_calibration_data()
        calibration_data = CalibrationData.from_dict(calibration_log.to_dict())
        rsp = GetCalibrationResponse.create_message(
            id=message.id, code="OK",
            message="get calibration data successfully.",
            calibration_data=calibration_data
        )

        await self.conn.send(rsp.to_json())
        Logger.debug(f"Send back current_calibration data: {rsp.to_dict()}")