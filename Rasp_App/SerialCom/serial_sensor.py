import time
import serial

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