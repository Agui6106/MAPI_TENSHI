from picamera2 import Picamera2

# Iniciar la cámara
def iniciar_camara(self):
    self.picam2.start()

# Detener la cámara
def detener_camara(self):
    self.picam2.stop()

# Capturar el frame de la cámara
def capturar_frame(self):
    return self.picam2.capture_array()

# Tomar y guardar localmente fotografia

# Tomar y enviar al servidor fotografia