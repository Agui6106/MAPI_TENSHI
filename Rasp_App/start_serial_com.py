"""
# - RECEPTOR - #
import socket
import os
import time

from SerialCom import serial_sensor

# Ruta del socket en el sistema de archivos
#SOCKET_PATH = "/tmp/uds_socket"
#
## Create the Unix socket client
#client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
## Connect to the server
#client.connect(SOCKET_PATH)

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
            
# - Verificamos conexion - #
def check_connections(device: serial_sensor.SerialSensor):
    # - Initial ping  - #
    atempts = 0
    correct = 0
    incorrect = 0
    print(f'Checking Serial connection...')
    
    while atempts != 4:
        time.sleep(2)
        #print(f'Received from test: {test_ans}')
        test_ans = device.read_serial()
        
        if test_ans is None:
            print(f'Attempt {atempts} of 4 failed. Retrying in 1 sec...')
            incorrect += 1
        else:
            print(f'Attempt {atempts} of 4 succesfull. Retrying in 1 sec...')
            correct += 1
        atempts += 1
    
    if correct == 4 and incorrect == 0:
        print(f'{correct} of 4 succesfull... Connection Ok')
        return 'Ok'
    
    if correct != 4 and incorrect > 0:
        print(f'{correct} of 4 succesfull... Connection unstable')
        return 'Unstable'

    if correct == 0 and incorrect == 4: 
        print(f'{correct} of 4 succesfull... Connection Unsuccessful')
        return 'Unsuccessful'

if __name__ == "__main__":
    
    
    # - Verifcacion de puerto y dispositivo serial - #
    if ports:
        device = connect_serial_device()
        if device:
            test1 = check_connections(device=device)
            
            # Lectura de serial y recepcion por socket   
            while True:
                try:
                    #while True:
                    # Recibimos el mensaje y la dirección del cliente
                    data, _ = client.recvfrom(1024)
                    user_in = data.decode()
                    print(f"Message from socket: {user_in}")
                    
                    bus_data = device.read_serial()
                    serial_data = bus_data.split(',')
                    print(serial_data)
                    
                    # Enviamos por serial
                    if user_in:
                        if user_in == 'esp.test ':
                             results = check_connections(device=device)
                             print(results)
                        else:
                            ans = device.send(user_in)
                            x = f'{ans}'
                            print(x)
                            client.sendall(x.encode())
                    else:
                        TS_Data = device.send('data ')
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
        print('Not aviable ports... Leaving Serial Protocol')
    """
if __name__ == "__main__":
    print('Good to go')