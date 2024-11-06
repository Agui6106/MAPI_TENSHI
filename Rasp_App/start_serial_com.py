from SerialCom.serial_sensor import SerialSensor
from SerialCom.utils import find_available_serial_ports

ports = find_available_serial_ports()

def connect_serial_device() -> None:
    try:
        # Selección del primer puerto disponible
        port = ports[0]
        baudrate = 115200
        print(f'Starting Serial communications at port: {port} with baudrate: {baudrate}')

        if not port:
            print('No available ports... Failed to start.')
            return

        # Crear instancia de SerialSensor
        serial_device = SerialSensor(port=port, baudrate=baudrate)

        # Verificar si el dispositivo serial está abierto
        if serial_device.is_open():
            print(f'Connection Successful... Device connected on {port} with baudrate {baudrate}')
        else:
            print('Failed to open serial device.')
            return

        # Comunicación constante hasta interrupción manual
        while True:
            if serial_device.in_waiting() > 0:
                data_received = serial_device.reception()
                print(f"Data received: {data_received}")

                # Ejemplo de respuesta: envía "ACK" al dispositivo
                serial_device.send("ACK")

    except ValueError:
        print('Invalid baudrate specified')
    except KeyboardInterrupt:
        print("\nCommunication terminated by user.")
    finally:
        if 'serial_device' in locals() and serial_device.is_open():
            serial_device.close()
            print("Serial device closed.")

if __name__ == "__main__":
    connect_serial_device()
