#Librerias standard
import time
#Librerias de 3ros
import serial

#Velocidad a la que se envian o reciben los caracteres
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