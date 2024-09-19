from Cameras.stream import camera_stream, get_ip
from Cameras.contornos import contornos

# Creacion de multiples camaras

if __name__ == "__main__":
    # - Inicializacion y bienvenida - #
    print(f"MAPI-Tenshi Robot. Software Version 1.0.0 \nDeveloped and produced in Santiago de Queretaro, Mexico")
    
    ip = get_ip()
    print(f"Ip de raspberry actual: {ip}")
    
    # - FUNCIONES DE CAMARA - #
    # Comenzar transmision de video
    print(f"\nInicializamos transmision de la camara...")
    camera_stream(puerto=8000, resolucion=(640, 480))
    
    # Toma de decision en base a contrnos
    #print(f"Iniciando camara de dteccion de contrnos...")
    #contornos(resolucion=(640, 480), delay=0.5)
    
    # Toma de fotograifa
    
    
    # - FUNCIONES DE COMUNICACION SERIALES (ESP32) - #
    
    # - FUNCIONES DE COMUNICACION MQTT (App PC) - #