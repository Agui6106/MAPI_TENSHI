# - RECEPTOR - #
import socket
import os
import time

from SerialCom import serial_sensor

# - Inicializacion de socket - #
SOCKET_PATH = '/tmp/uds_socket'

# Eliminamos el socket si ya existe
if os.path.exists(SOCKET_PATH):
    os.remove(SOCKET_PATH)

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

if __name__ == "__main__":
    # - Verifcacion de puerto y dispositivo serial - #
    if ports:
        device = connect_serial_device()
        if device:
            # - Initial ping in func? - #
            atempts = 0
            correct = 0
            incorrect = 0
            print(f'Checking Serial connection...')
            
            while atempts != 4:
                time.sleep(0.5)
                test_ans = device.send("A ")
                #print(f'Received from test: {test_ans}')
                
                if test_ans is None:
                    print(f'Attempt {atempts} of 4 failed. Retrying...')
                    incorrect += 1
                else:
                    print(f'Attempt {atempts} of 4 succesfull. Retrying...')
                    correct += 1
                atempts += 1
            
            if correct == 4 and incorrect == 0:
                print(f'{atempts} of 4 succesfull... Connection Ok')
                
            # - Socket - #
            with socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM) as server_socket:
                server_socket.bind(SOCKET_PATH)
                print("Unix Domain Socket - Server ready...")
                
                try:
                    while True:
                        # Recibimos el mensaje y la dirección del cliente
                        data, client_address = server_socket.recvfrom(1024)
                        user_in = data.decode()
                        print(f"Message from socket: {user_in}")
                        
                        # Enviamos por serial
                        if user_in:
                            ans = device.send(user_in)
                            print(f'Recieved from serial: {ans}')
                                        
                # Hasta ser interrumpidos por el teclado
                except KeyboardInterrupt:
                    print("\nCommunication terminated by user.")
                    print("\nClosing local Socket server.")
                    
                finally:
                    # Eliminamos el socket del sistema de archivos y Cerramos objeto tipo serial
                    os.remove(SOCKET_PATH)
                    if device and device.is_open():
                        device.close()
                        print("Serial device closed.")
                        
        else:
            print('No available device to connect... Leaving Serial Protocol')
    else:
        print('Not aviable ports... Leaving Serial Protocol')