from Cameras.stream import iniciar_camara_streaming
from Cameras.contornos import ejecutar_deteccion_contornos

# Creacion de multiples camaras

if __name__ == "__main__":
    print(f"MAPI-Tenshi Robot. Software Version 1.0.0 \nDeveloped and produced in Santiago de Queretaro, Mexico")
    #print(f"Iniciando camara de dteccion de contrnos...")
    #ejecutar_deteccion_contornos(resolucion=(640, 480), delay=0.5)
    print(f"Inicializamos transmision de la camara...")
    iniciar_camara_streaming(puerto=8000, resolucion=(640, 480))