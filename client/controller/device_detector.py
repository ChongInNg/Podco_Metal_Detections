import subprocess
import os

class DeviceDetector:
    def __init__(self, mount_point) -> None:   
        self.mount_point = mount_point
        self.device_name = None

    def detect(self):
        if not self.get_device_name():
           print("There is no device found now.")
           return False
       
        self.create_mnt_folder()
        if not self.mount_device():
            print("Mounting device has error.")
            return False
        
        return True
       
    def get_device_name(self):
        detect_command = ["lsblk"]
        detect_ouput = subprocess.check_output(detect_command)
        detect_ouput_lines = detect_ouput.decode().split('\n')

        for line in detect_ouput_lines[1:]:  # Skip the header line
            fields = line.split()
            len_fields = len(fields)
            if len_fields != 6:
                continue
                
            name = fields[0]
            type = fields[5]
            if "sd" in name and type == 'part':
                index = name.find('sd') # name original is ~sda1
                self.device_name = f"/dev/{name[index:]}"
                return True
        
        return False
    
    def create_mnt_folder(self):
        os.makedirs(self.mount_point, exist_ok=True)
        print(f"The folder {self.mount_point} has been created")

    def mount_device(self):
        try:
            subprocess.run(['sudo', 'mount', self.device_name, self.mount_point], check=True)
            print(f"Device {self.device_name} mounted at {self.mount_point}.")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error mounting device: {e}")
            return False

    def umount_device(self):
        try:
            subprocess.run(['sudo', 'umount', self.device_name], check=True)
            print(f"Device {self.device_name} umounted success.")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error umounting device: {e}")
            return False
    
    def eject_device(self) -> bool:
        eject_command = ["sudo", "eject", self.device_name]
        try:
            subprocess.check_output(eject_command)
            print(f"eject the device:{self.device_name} success")
            flag = self.detect()
            print(f"detect the usb device again, did device still exist?: {flag}")
            return True
        except Exception as e:
            print(f"eject the device:{self.device_name} has something wrong: {str(e)}")
            return False
    

    def eject(self) -> None:
        if self.umount_device():
            self.eject_device()