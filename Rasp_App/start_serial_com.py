"""# - RECEPTOR - #
import socket
import os
import time
import glob
from SerialCom import serial_sensor

# Ruta del socket en el sistema de archivos
SOCKET_PATH = "/tmp/uds_socket"

# Create the Unix socket client
client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
# Connect to the server
client.connect(SOCKET_PATH)

# Identificadores específicos de dispositivos
ARDUINO_ID = "Arduino"  # Cambia según tu Arduino
ESP_ID = "Silicon_Labs"  # Cambia según tu ESP (puede ser "CH340" si usa ese chip)

# - Obtener todos los puertos - #
ports = serial_sensor.find_available_serial_ports()


def find_specific_device(target_id):
    # Busca el dispositivo serial que coincide con el identificador proporcionado.
    devices = glob.glob('/dev/serial/by-id/*')
    for device in devices:
        if target_id in device:
            return device
    return None


# - Conectar con el dispositivo serial - #
def connect_serial_device():
    try:
        # Buscar el puerto de la ESP
        esp_port = find_specific_device(ESP_ID)
        baudrate = 115200

        if not esp_port:
            print(f'No se encontró un dispositivo con identificador {ESP_ID}')
            return None

        print(f'Iniciando comunicación serial en {esp_port} con baudrate {baudrate}')

        # Crear instancia de SerialSensor
        serial_device = serial_sensor.SerialSensor(port=esp_port, baudrate=baudrate)

        # Verificar si el dispositivo serial está abierto
        if serial_device.is_open():
            print(f'Conexión exitosa en {esp_port} con baudrate {baudrate}')
            return serial_device
        else:
            print('No se pudo abrir el dispositivo serial.')
            return None

    except ValueError:
        print('Baudrate especificado inválido')
        return None


# - Verificar conexión serial - #
def check_connections(device: serial_sensor.SerialSensor):
    atempts = 0
    correct = 0
    incorrect = 0
    print(f'Checking Serial connection...')
    
    while atempts < 4:
        time.sleep(2)
        test_ans = device.read_serial()
        
        if test_ans is None:
            print(f'Attempt {atempts + 1} of 4 failed. Retrying in 1 sec...')
            incorrect += 1
        else:
            print(f'Attempt {atempts + 1} of 4 successful. Retrying in 1 sec...')
            correct += 1
        atempts += 1
    
    if correct == 4 and incorrect == 0:
        print(f'{correct} of 4 successful... Connection Ok')
        return 'Ok'
    if correct != 4 and incorrect > 0:
        print(f'{correct} of 4 successful... Connection unstable')
        return 'Unstable'
    if correct == 0 and incorrect == 4:
        print(f'{correct} of 4 successful... Connection Unsuccessful')
        return 'Unsuccessful'


if __name__ == "__main__":
    # - Verificación de puerto y dispositivo serial - #
    if ports:
        device = connect_serial_device()
        if device:
            test1 = check_connections(device=device)
            
            # Lectura de serial y recepción por socket   
            while True:
                try:
                    # Recibimos el mensaje y la dirección del cliente
                    data, _ = client.recvfrom(1024)
                    user_in = data.decode()
                    print(f"Message from socket: {user_in}")
                    
                    bus_data = device.read_serial()
                    serial_data = bus_data.split(',')
                    print(serial_data)
                    
                    # Enviamos por serial
                    if user_in:
                        if user_in == 'esp.test':
                            results = check_connections(device=device)
                            print(results)
                        else:
                            ans = device.send(user_in)
                            x = f'{ans}'
                            print(x)
                            client.sendall(x.encode())
                    else:
                        TS_Data = device.send('data')
                        print(TS_Data)
                                        
                # Hasta ser interrumpidos por el teclado
                except KeyboardInterrupt:
                    print("\nCommunication terminated by user.")
                    print("\nClosing local Socket server.")

                    # Eliminamos el socket del sistema de archivos y Cerramos objeto tipo serial
                    client.close()
                    if device and device.is_open():
                        device.close()
                        print("Serial device closed.")
                        
        else:
            print('No available device to connect... Leaving Serial Protocol')
    else:
        msg = 'Not Ports'
        client.sendall(msg.encode())
        print('No available ports... Leaving Serial Protocol')
"""