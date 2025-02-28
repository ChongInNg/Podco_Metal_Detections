from command_processor import CommandProcessor
from serial_handler import SerialHandler, CommandData
from log.logger import Logger
from datetime import time
import os

def get_current_program_folder():
  return os.path.dirname(os.path.abspath(__file__))

def handle_response(command_name, command_data: CommandData):
    if command_data is None:
        Logger.error(f"Command: {command_name}, Didn't get the response, timeout")
        return
    
    if command_data.data_length == 1:
        result = command_data.data[0]
        if result == 1:
            Logger.info(f"Command: {command_name}, Received response success of: {hex(command_data.command_type)}, result: {result}")
        else:
            Logger.error(f"Command: {command_name}, Received response failed of: {hex(command_data.command_type)}, result: {result}")
    else:
        Logger.error(f"Command: {command_name}, Received unexpected length data: {command_data.to_dict()}")

if __name__ == "__main__":
    Logger.info("Command Test Program started")
    processor = CommandProcessor(f"{get_current_program_folder()}/command_data.json")
    serial_handler = SerialHandler(port="COM1", baudrate=115200, timeout=0.5)
    if not serial_handler.connect():
        Logger.info("Command Test Program exited")
        exit(100)
    while True:
        command_mapping = {i + 1: command["name"] for i, command in enumerate(processor.commands)}
        command_mapping[9] = "raw data stress test"
        print("\nAvailable commands:")
        for number, name in command_mapping.items():
            print(f" {number}. {name}")
        print(" 0. Exit")

        try:
            choice = input("\nEnter the number of the command you want to send: ").strip()
            if not choice.isdigit():
                print("Invalid input. Please enter a number.")
                continue

            choice = int(choice)
            if choice == 0:
                Logger.info("Exiting the program.")
                break
            elif choice == 9:
                count = 0
                while True:
                    raw_data_command = processor.encode_raw_data_command()
                    serial_handler.send(raw_data_command)
                    command_data:CommandData = serial_handler.receive()
                    handle_response(f"raw_data: {count}", command_data)
                    count += 1
                    # time.sleep(0.1)

            if choice not in command_mapping:
                print("Invalid choice. Please select a valid command number.")
                continue

            command_name = command_mapping[choice]
            encoded_command = processor.encode_command(command_name)
            Logger.info(f"Encoded command: {encoded_command.hex()}")

            serial_handler.send(encoded_command)
            command_data:CommandData = serial_handler.receive()
            handle_response(command_name, command_data)
        except ValueError as e:
            Logger.error(f"Error: {e}")
