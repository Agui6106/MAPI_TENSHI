# Importamos librerias python
import threading
import time
import subprocess

# Importamos libreriras locales
from Cameras.camera_control import CameraControl
from Cameras.contornos import contornos

# Creacion de multiples camaras

if __name__ == "__main__":
    # - Inicializacion y bienvenida - #
    print(f"MAPI-Tenshi Robot. Software Version 1.0.0 \nDeveloped and produced in Santiago de Queretaro, Mexico\n")
    cam4vid = CameraControl(resolution=(640, 480))
    ip = CameraControl.get_ip()
    print(f"Ip de raspberry actual: {ip}")
    
    cam4vid.prev()
    cam4vid.detener_camara()
    # - FUNCIONES DE CAMARA - #
    # Comenzar transmision de video
    print(f"\nInicializando transmision de la camara...")
    try:
        subprocess.run(["python3", "./stream.py"])
    except Exception as e:
        print(f'Failed to start transmision: {str(e)}')
    

    
    
    # Toma de decision en base a contrnos
    #print(f"Iniciando camara de dteccion de contrnos...")
    #contornos(resolucion=(640, 480), delay=0.5)
    
    # Toma de fotograifa
    
    
    # - FUNCIONES DE COMUNICACION SERIALES (ESP32) - #
    
    # - FUNCIONES DE COMUNICACION MQTT (App PC) - #