import json

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

