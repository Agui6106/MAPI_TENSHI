from picamera2 import Picamera2
import cv2
import time

class CameraControl:
    def __init__(self, resolution=(640, 480)):
        # Inicializar la cámara
        self.picam2 = Picamera2()
        camera_config = self.picam2.create_preview_configuration(main={"size": resolution})
        self.picam2.configure(camera_config)

    # Iniciar la cámara
    def iniciar_camara(self):
        self.picam2.start()

    # Detener la cámara
    def detener_camara(self):
        self.picam2.stop()

    # Capturar el frame de la cámara
    def capturar_frame(self):
        return self.picam2.capture_array()

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

