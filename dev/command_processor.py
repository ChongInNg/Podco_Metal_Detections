import json
from random import randint

class CommandProcessor:
    def __init__(self, json_file):
        self.json_file = json_file
        self.commands = self._load_commands()
        self.bytes_endian = "big"

    def _load_commands(self):
        try:
            with open(self.json_file, "r") as f:
                data = json.load(f)
                return data["commands"]
        except (FileNotFoundError, KeyError, json.JSONDecodeError) as e:
            raise ValueError(f"Error loading JSON file: {e}")

    def get_command(self, name):
        self.commands = self._load_commands() # update every time
        for command in self.commands:
            if command["name"] == name:
                return command
        raise ValueError(f"Command '{name}' not found.")

    def encode_command(self, name):
        command = self.get_command(name)

        command_type = int(command["command_type"], 16)  
        data_length = int(command["data_length_bytes"])
        item_size = int(command["each_item_bytes"])
        data = command["data"]

        if len(data) * item_size != data_length:
            raise ValueError(f"Data length mismatch for command '{name}': "
                             f"expected {data_length} bytes, got {len(data) * item_size} bytes.")
        
        encoded = command_type.to_bytes(1, self.bytes_endian)
        encoded += data_length.to_bytes(1, self.bytes_endian)

        for value in data:
            encoded += value.to_bytes(item_size, self.bytes_endian)

        return encoded
    
    def encode_raw_data_command(self):
        command = self.get_command("raw_data")

        command_type = int(command["command_type"], 16)  
        data_length = int(command["data_length_bytes"])
        item_size = int(command["each_item_bytes"])

        encoded = command_type.to_bytes(1, self.bytes_endian)
        encoded += data_length.to_bytes(1, self.bytes_endian)

        v1 = randint(2000, 2500)
        v2 = randint(2000, 2500)
        encoded += v1.to_bytes(item_size, self.bytes_endian)
        encoded += v2.to_bytes(item_size, self.bytes_endian)

        ch1_p = randint(0, 2300)
        ch1_n = randint(0, 1000)
        ch2_p = randint(0, 2800)
        ch2_n = randint(0, 1)

        encoded += ch1_p.to_bytes(item_size, self.bytes_endian)
        encoded += ch1_n.to_bytes(item_size, self.bytes_endian)

        encoded += ch2_p.to_bytes(item_size, self.bytes_endian)
        encoded += ch2_n.to_bytes(item_size, self.bytes_endian)
        return encoded

