from Cameras.stream import iniciar_camara_streaming

if __name__ == "__main__":
    iniciar_camara_streaming(puerto=8000, resolucion=(640, 480))