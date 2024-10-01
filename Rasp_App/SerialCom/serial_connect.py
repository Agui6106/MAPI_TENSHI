from utils import find_available_serial_ports
from serial_sensor import BAUDRATES
from serial_sensor import SerialSensor


class serial_object:
    # Conectamos al objeto
    def connect_serial_device(self) -> None:
        try:        
            baudrate = 115200
            port = ''
            if port == '':
                print(f'WARNING. Port not selected. Select a valid port {port =}')
                return

            self.serial_device = SerialSensor(
                port = port,
                baudrate = baudrate
            ) 

            if self.serial_device.is_open():
                print(f'Connection Successful. Control connected successfully on {port} with baudrate {baudrate}')

        except ValueError:
            print(f'WARNING. Wrong baudrate. Baudrate not valid or incompatible')
            return
