from .wsmessage import *
from log.logger import Logger


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
            if isinstance(message, RegistrationWsRequest):
               await self.handle_registration(message)
            elif isinstance(message, SetThresholdRequest):
                await self.handle_set_threshold(message)
            else:
                Logger.warning(f"Cannot handle this message: {message}")
        except Exception as e:
            Logger.error(f"Handle message error:{e}")
            import traceback
            traceback.print_stack()
            await self.send_system_error("Handle message error:{e}")
            
    
    async def handle_registration(self, message: RegistrationWsRequest):
        Logger.debug(f"Handling registration message: {message}")
        self.status = Connection.Status_Registered
        self.registered_at = datetime.now().isoformat()
        self.device_id = message.device_id

        rsp = RegistrationWsResponse(
            id=message.id, code="success", message="register successfully",
            data={"device_id": message.device_id}
        )

        await self.conn.send(rsp.to_json())
        Logger.debug(f"Handle registeration success: {rsp.to_dict()}")

    async def handle_set_threshold(self, message: SetThresholdRequest):
        Logger.debug(f"Handling set threshold message: {message}")
        if self.status != Connection.Status_Registered:
            Logger.error("This connection didn't registered yet, cannot handle it.")
            return
        
        # device = DeviceManager.instance().get_device(message.device_identity)
        # rsp = None
        # if device is None:
        #     rsp = QueryDeviceResponse(
        #         id=message.id, code="device_not_found",
        #         message=f"cannot get this device:{message.device_identity}"                
        #     )
        # else:
        #     info = device.to_dict()
        #     rsp = QueryDeviceResponse(
        #         id=message.id, code="success", message="query device successfully",
        #         data=info                      
        #     )

        # await self.conn.send(rsp.to_json())
        # Logger.debug(f"Handle query device success: {rsp.to_dict()}")

    async def send_system_error(self, message: str, data:dict=None):
        rsp = SystemErrorResponse(message=message, data=data)
        await self.conn.send(rsp.to_json())
        Logger.debug(f"Send system error: {rsp}")

    async def send_notify_message(self, notify_msg: BaseWsNotify):
        json_msg = notify_msg.to_json()
        await self.conn.send(json_msg)
        Logger.debug(f"Send notify message:{notify_msg.name} successfully: {json_msg}")