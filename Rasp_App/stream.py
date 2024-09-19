# - TRANSMISION DEL VIDEO A UN SERVIDOR POR SOCKER - #
import io
import socketserver
import sys

from threading import Condition
from http import server
from picamera2 import Picamera2
from picamera2.encoders import MJPEGEncoder
from picamera2.outputs import FileOutput
import logging

from Cameras.camera_control import CameraControl  # Importa tu control de cámara

# Página HTML para mostrar el stream
PAGE = """\
<html>
<head>
<title>Picamera2 MJPEG Streaming</title>
</head>
<body>
<img src="stream.mjpg" width="640" height="480" />
</body>
</html>
"""

class StreamingOutput(io.BufferedIOBase):
    # Aquí no necesitas cambios
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)

class StreamingHandler(server.BaseHTTPRequestHandler):
    # Aquí tampoco necesitas cambios
    def __init__(self, output, *args, **kwargs):
        self.output = output
        super().__init__(*args, **kwargs)

    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with self.output.condition:
                        self.output.condition.wait()
                        frame = self.output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning('Removed streaming client %s: %s', self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True
    
def camera_stream(puerto, resolucion):
    # Crea una nueva instancia de CameraControl dentro de este script
    picam2 = CameraControl(resolution=resolucion)

    # Crear el output para almacenar los frames en formato MJPEG
    output = StreamingOutput()

    # Crear un encoder MJPEG para la transmisión
    encoder = MJPEGEncoder()

    # Iniciar la cámara y la grabación de video
    picam2.iniciar_camara()
    picam2.picam2.start_recording(encoder, FileOutput(output))

    try:
        # Configurar el servidor HTTP en el puerto especificado
        address = ('', puerto)
        handler = lambda *args, **kwargs: StreamingHandler(output, *args, **kwargs)
        server = StreamingServer(address, handler)
        print(f"Servidor de streaming iniciado con exito en el puerto: {puerto}")
        server.serve_forever()
    finally:
        # Detener la grabación y la cámara
        picam2.picam2.stop_recording()
        picam2.detener_camara()

if __name__ == "__main__":
    camera_stream(puerto=8000, resolucion=(640, 480))
