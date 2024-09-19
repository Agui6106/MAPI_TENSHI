# deteccion_contornos.py

from picamera2 import Picamera2
import cv2
import numpy as np
import time

class ContourDetector:
    def __init__(self, resolution=(640, 480)):
        # Inicializar la cámara
        self.picam2 = Picamera2()
        camera_config = self.picam2.create_preview_configuration(main={"size": resolution})
        self.picam2.configure(camera_config)

    def iniciar_camara(self):
        # Iniciar la cámara
        self.picam2.start()

    def detener_camara(self):
        # Detener la cámara
        self.picam2.stop()

    def capturar_frame(self):
        # Capturar el frame de la cámara
        return self.picam2.capture_array()

    def detectar_contornos(self, frame):
        imgContour = frame.copy()
        imgGray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)   # Convertir a escala de grises
        imgBlur = cv2.GaussianBlur(imgGray, (7, 7), 1)      # Aplicar desenfoque
        imgCanny = cv2.Canny(imgBlur, 100, 100)             # Detectar bordes
        
        contours, hierarchy = cv2.findContours(imgCanny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)  # Encontrar contornos
        
        for cnt in contours:
            area = cv2.contourArea(cnt)  # Calcular el área del contorno
            if area > 500:  # Filtrar contornos pequeños
                cv2.drawContours(imgContour, cnt, -1, (0, 255, 0), 3)  # Dibujar contornos
                perimeter = cv2.arcLength(cnt, True)  # Calcular el perímetro
                approx = cv2.approxPolyDP(cnt, 0.02 * perimeter, True)  # Aproximar la forma
                print(f"Area: {area}, Perimeter: {perimeter}, Approx points: {len(approx)}")

        return imgContour

    def mostrar_frame(self, frame, ventana="Contour Detection"):
        cv2.imshow(ventana, frame)

    def cerrar_ventanas(self):
        cv2.destroyAllWindows()

# Función principal para correr el bucle de detección de contornos
def contornos(resolucion=(640, 480), delay=0.5):
    detector = ContourDetector(resolution=resolucion)
    detector.iniciar_camara()

    try:
        while True:
            frame = detector.capturar_frame()  # Capturar el frame de la cámara
            imgContour = detector.detectar_contornos(frame)  # Detectar contornos
            detector.mostrar_frame(imgContour)  # Mostrar el frame con contornos

            time.sleep(delay)

            if cv2.waitKey(1) & 0xFF == ord('q'):  # Salir si se presiona 'q'
                break
    finally:
        detector.detener_camara()  # Detener la cámara
        detector.cerrar_ventanas()  # Cerrar las ventanas de OpenCV
