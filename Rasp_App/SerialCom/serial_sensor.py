import time
import serial

import sys
import glob

# Avaibale Baudrates
BAUDRATES = [  
    2400,
    4800,
    9600, 
    19200, 
    38400, 
    56000,
    57600, 
    115200
]

# - Buscamos los ports disponibles - #
def find_available_serial_ports() -> list[str]:
    if sys.platform.startswith('win'): # Computadora windows
        platform = 'win'
        ports =[f'COM{i}' for i in range(1, 256)]
    elif sys.platform.startswith('linux'): # Computadora Linux
        platform = 'linux'
        ports =glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'): # Mac
        platform = 'darwin'
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported Platform')
    result = []
    for port in ports:
        early_stop = True if platform == 'win' else False
        try:
            s= serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            if early_stop:
                break
            continue

    return result

# - Clase de objeto tipo serial - #
class SerialSensor:
    
    def __init__(self,
                 port: str,
                 baudrate: int = 115200,
                 timeout: float = 2.0,
                 connection_time: float = 3.0,
                 reception_time: float = 0.5
                 ) -> None:
        try:
            self._serial = serial.Serial(
                port=port,
                baudrate=baudrate,
                timeout=timeout
            )
        except ValueError as e:
            print(f"Invalid baudrate specified: {baudrate}")
            self._serial = None
            raise e
        except serial.SerialException as e:
            print(f"Failed to connect on port {port}: {e}")
            self._serial = None
            raise e

        self.connection_time = connection_time
        self.reception_time = reception_time
        time.sleep(connection_time)

    def send(self, to_send: str) -> str:
        if self._serial and self._serial.is_open:
            self._serial.write(to_send.encode('utf-8'))
            time.sleep(self.reception_time)
            received = self._serial.readline()
            return received.decode('utf-8')
        return ''

    def reception(self) -> str:
        if self._serial and self._serial.is_open:
            received = self._serial.readline()
            return received.decode('utf-8')
        return ''

    def is_open(self) -> bool:
        return self._serial.is_open if self._serial else False

    def in_waiting(self) -> int:
        return self._serial.in_waiting if self._serial else 0

    def close(self) -> None:
        if self._serial and self._serial.is_open:
            self._serial.close()
            
    def __str__(self) -> str:
        return f"Serial Sensor(port={self._serial.port}, connection_time={self.connection_time}, reception_time={self.reception_time})"
    
    def __repr__(self) -> str:
        return self.__str__()
    
    def __del__(self) -> None:
        if self._serial:
            self.close()