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

class SerialSensor:
    
    def __init__(self,
                 port:str,
                 baudrate: int = 115200,
                 timeout: float = 2.,
                 connection_time: float = 3.,
                 reception_time: float = .5
            ) -> None:
            self._serial = serial.Serial(
                port=port,
                baudrate=baudrate,
                timeout=timeout
            )
            self.connection_time = connection_time
            self.reception_time = reception_time
            time.sleep(connection_time)
            #recieved = self.send('OK')
            
    def send(self, to_send:str) -> str:
        self._serial.write(to_send.encode('utf-8')) #Codificar
        time.sleep(self.reception_time) #Tiempo de espera para que se puedan sincronzar ambos dispositivos
        recieved = self._serial.readline()
        return recieved.decode(encoding='utf-8') #Decodificar
    
    def reception(self,) -> str:
        recieved = self._serial.readline()
        return recieved.decode('utf-8')
    
    def is_open(self):
        return self._serial.is_open
    
    def in_waiting(self):
        return self._serial.in_waiting
    
    def close(self) -> None:
        self._serial.close()
            
    def __str__(self) -> str:
        return f"Serial Sensor({self._serial=}, {self.connection_time=},{self.reception_time=})"
    
    def __repr__(self) -> str:
        return f"Serial Sensor({self._serial=}, {self.connection_time=},{self.reception_time=})"
    
    def __del__(self) -> None:
        self.close()