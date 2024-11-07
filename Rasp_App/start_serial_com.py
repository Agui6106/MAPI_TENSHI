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
  
# -- LOOP INFINITO -- #
# - Leemos el dispositivo - #
def read_serial(device):
    if device.in_waiting > 0:
        try:
            data = device.readline().decode().strip()
            return data
        except:
            return None
    return None

# - Escribimos el dispositivo - #
"""
Opcion A:
    # Comunicación constante hasta interrupción manual
    while True:
        # Solicitar entrada del usuario para enviar un mensaje
        user_input = input("Enter message to send to Arduino (or type 'exit' to quit): ")

        if user_input.lower() == 'exit':
            print("Exiting communication...")
            break  # Salir del bucle si el usuario escribe 'exit'
        elif user_input:
            # Enviar el mensaje ingresado por el usuario
            device.send(user_input)
            print(f"Sent to Arduino: {user_input}")
            #print(f'Arduino Response: {command}')

Opcion B
while True:
    if serial_device.in_waiting() > 0:
        data_received = serial_device.reception()
        print(f"Data received: {data_received}"
        # Ejemplo de respuesta: envía "ACK" al dispositivo
        serial_device.send("ACK")
"""