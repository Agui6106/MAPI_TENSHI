from SerialCom.serial_sensor import SerialSensor
from SerialCom.utils import find_available_serial_ports

def connect_serial_device() -> None:
    try:
        # Llamada para encontrar el puerto disponible
        port = find_available_serial_ports()
        baudrate = 115200
        print(f'Starting Serial communications at port: {port} with baudrate: {baudrate}')

        if not port:
            print('No available ports... Failed to start.')
            return

        # Crear instancia de SerialSensor con el puerto y baudrate
        serial_device = SerialSensor(
            port=port,
            baudrate=baudrate
        )

        # Verificar si el dispositivo serial está abierto
        if serial_device.is_open():
            print(f'Connection Successful... Device connected on {port} with baudrate {baudrate}')
        else:
            print('Failed to open serial device.')

    except ValueError:
        print('Invalid baudrate specified')
        return

if __name__ == "__main__":
    connect_serial_device()
