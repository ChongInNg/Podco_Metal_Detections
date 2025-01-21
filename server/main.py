from uart_server import UartServer

if __name__ == "__main__":
    server = UartServer(port='/COM24', baudrate=115200, timeout=None)
    server.connect()
    print("This is metal detection server.")