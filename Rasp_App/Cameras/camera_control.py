from picamera2 import Picamera2, Preview
from picamera2.encoders import MJPEGEncoder
from picamera2.outputs import FileOutput

import subprocess
import re

import cv2
import time

camera = Picamera2

class CameraControl:
    def __init__(self, resolution=(640, 480)):
        # Inicializar la cámara
        self.picam2 = Picamera2()
        camera_config = self.picam2.create_video_configuration(main={"size": resolution})
        self.picam2.configure(camera_config)
    
    def get_ip():
        try:
            # Ejecuta el comando ifconfig
            resultado = subprocess.check_output(["ifconfig"], encoding='utf-8')
            
            # Usamos una expresión regular para buscar la IP local (IPv4)
            ip_local = re.findall(r'inet (\d+\.\d+\.\d+\.\d+)', resultado)
            
            # Filtramos la IP local que no sea la de loopback (127.0.0.1)
            ip_local = [ip for ip in ip_local if ip != "127.0.0.1"]
            
            if ip_local:
                return ip_local[0]
            else:
                return "No se pudo encontrar la IP local."
        except subprocess.CalledProcessError as e:
            return f"Error al ejecutar el comando: {e}"
    
    # Iniciamos vista previa de la camara
    def prev(self):
        camera_config = self.picam2.create_preview_configuration()
        self.picam2.configure(camera_config)
        self.picam2.start_preview(Preview.QTGL)
        self.picam2.start()
        time.sleep(5)
        self.picam2.stop()
        
    # Iniciar la cámara
    def iniciar_camara(self):
        self.picam2.start()

    # Detener la cámara
    def detener_camara(self):
        self.picam2.stop()
    
    def encoders(self,encode,output):
        self.picam2.start_encoder(encoder=encode,output=output)
        
    def stop_encoder(self):
        self.picam2.stop_encoder()

    # Capturar el frame de la cámara
    def capturar_frame(self):
        img = self.picam2.capture_array()
        return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Tomar y guardar una fotografía localmente
    def tomar_fotografia(self, file_path="foto.jpg"):
        frame = self.capturar_frame()  # Capturar frame
        cv2.imwrite(file_path, frame)  # Guardar la imagen en el archivo
        print(f"Fotografía guardada en {file_path}")

    # Tomar y enviar una fotografía al servidor
    def tomar_fotografia_y_enviar(self, server_url):
        frame = self.capturar_frame()  # Capturar frame
        _, encoded_image = cv2.imencode('.jpg', frame)  # Codificar la imagen como JPG
        data = encoded_image.tobytes()

        # Aquí se implementaría el código para enviar la imagen al servidor
        # Esto puede hacerse con la librería requests, por ejemplo:
        # import requests
        # response = requests.post(server_url, files={'image': data})
        # print(f"Respuesta del servidor: {response.status_code}")
        
        print("Fotografía enviada al servidor (funcionalidad pendiente)")

    # Mostrar el frame en tiempo real (opcional)
    def mostrar_frame(self, ventana="Vista en tiempo real"):
        frame = self.capturar_frame()
        cv2.imshow(ventana, frame)
        cv2.waitKey(1)

    # Cerrar las ventanas de OpenCV (cuando se usa mostrar_frame)
    def cerrar_ventanas(self):
        cv2.destroyAllWindows()
