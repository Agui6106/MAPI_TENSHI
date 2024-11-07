from SerialCom import serial_sensor

# - Obtener todos los ports - #
ports = serial_sensor.find_available_serial_ports()

# - Conectamos con el dispositvo - #
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
        serial_device = serial_sensor.SerialSensor(port=port, baudrate=baudrate)

        # Verificar si el dispositivo serial está abierto
        if serial_device.is_open():
            print(f'Connection Successful... Device connected on {port} with baudrate {baudrate}')
            return serial_device
        else:
            print('Failed to open serial device.')
            return
        
    except ValueError:
        print('Invalid baudrate specified')
        
    """finally:
        if 'serial_device' in locals() and serial_device.is_open():
            serial_device.close()
            print("Serial device closed.")"""

# - Leemos el dispositivo - #
def read_serial(device: serial_sensor.SerialSensor):
    if device.in_waiting() > 0:
        try:
            data = device.reception()
            return data
        except:
            return None
    return None

# - Escribimos el dispositivo - #
def communicate_with_device(device: serial_sensor.SerialSensor):
    try:
        while True:
            # Solicitar entrada del usuario y enviar
            user_input = input("Enter message to send to device (or type 'exit' to quit): ")
            if user_input.lower() == 'exit':
                break
            elif user_input:
                device.send_data(user_input)
            
            # Leer datos del dispositivo
            data_received = read_serial(device)
            if data_received:
                print(f"Data received: {data_received}")
    except KeyboardInterrupt:
        print("\nCommunication terminated by user.")
    finally:
        if device and device.is_open():
            device.close()
            print("Serial device closed.")

if __name__ == "__main__":
    if ports:
        device = connect_serial_device()
        if device:
            try:
                while True:
                    user_in = input("Message: ")
                    if user_in.lower() == 'exit':
                        break
                    elif user_in:
                        ans = device.send(user_in)
                    print(ans)
            except KeyboardInterrupt:
                print("\nCommunication terminated by user.")
            finally:
                if device and device.is_open():
                    device.close()
                    print("Serial device closed.")
            
            #communicate_with_device(device)
        else:
            print('No available device to connect... Leaving Serial Protocol')
    else:
        print('Not aviable ports... Leaving Serial Protocol')