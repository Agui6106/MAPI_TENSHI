# - TRANSMISION DEL VIDEO A UN SERVIDOR POR SOCKER - #

# camara_streaming.py

import io
import socketserver
from threading import Condition
from http import server
from picamera2 import Picamera2
from picamera2.encoders import MJPEGEncoder
from picamera2.outputs import FileOutput
import logging

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

# Clase para manejar el output de la cámara y almacenar los frames (maneja el video)
class StreamingOutput(io.BufferedIOBase):
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

# Handler HTTP que gestiona las solicitudes de los clientes
class StreamingHandler(server.BaseHTTPRequestHandler):
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

# Configuración del servidor HTTP para transmitir en diferentes hilos
class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

def iniciar_camara_streaming(puerto=8000, resolucion=(640, 480)):
    # Configuración de la cámara con Picamera2
    picam2 = Picamera2()
    video_config = picam2.create_video_configuration(main={"size": resolucion})
    picam2.configure(video_config)

    # Crear el output para almacenar los frames en formato MJPEG
    output = StreamingOutput()

    # Crear un encoder MJPEG para la transmisión
    encoder = MJPEGEncoder()

    # Iniciar la cámara y la grabación de video
    picam2.start()
    picam2.start_encoder(encoder, FileOutput(output))

    try:
        # Configurar el servidor HTTP en el puerto especificado
        address = ('', puerto)
        handler = lambda *args, **kwargs: StreamingHandler(output, *args, **kwargs)
        server = StreamingServer(address, handler)
        print(f"Servidor de streaming iniciado en el puerto {puerto}")
        print(f"Consulta el video la direccion url: http://192.168.116.18:8000/index.html")
        server.serve_forever()
    finally:
        # Detener la grabación y la cámara
        picam2.stop_encoder()
        picam2.stop()


