import threading
import paho.mqtt.client as mqtt
import socket

# Obtener la IP en Windows
@staticmethod
def get_ip_Windows():
    hostname = socket.gethostname()  # Obtiene el nombre del dispositivo
    ipv4 = socket.gethostbyname(hostname)  # Obtiene la dirección IPv4
    return ipv4

class mqtt_coms:
    def __init__(self, broker_ip, broker_port, topic_sub, topic_pub):
        self.broker_ip = broker_ip
        self.broker_port = broker_port
        self.topic_sub = topic_sub
        self.topic_pub = topic_pub
        self.last_message = None
        self._running = False  # Bandera para controlar el hilo

        # Crear el cliente MQTT
        self.client = mqtt.Client()

        # Asignar callbacks
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        # Conectarse al broker
        self.client.connect(self.broker_ip, self.broker_port, 60)

        # Hilo para manejar el loop
        self.thread = threading.Thread(target=self._loop_forever, daemon=True)

    # Función que se ejecuta cuando se conecta al broker MQTT
    def on_connect(self, client, userdata, flags, reasonCode, properties=None):
        print(f"Conectado con código de resultado {reasonCode}")
        client.subscribe(self.topic_sub)

    # Función que se ejecuta cuando se recibe un mensaje
    def on_message(self, client, userdata, msg):
        self.last_message = msg.payload.decode()
        print(f"Mensaje recibido en {msg.topic}: {self.last_message}")

    # Método para iniciar el loop en un hilo separado
    def start(self):
        if not self.thread.is_alive():
            self._running = True
            self.thread.start()

    # Método para detener el loop
    def stop(self):
        self._running = False
        self.client.disconnect()

    # Método para publicar mensajes
    def publish_message(self, message):
        self.client.publish(self.topic_pub, message)

    # Método privado para el loop del cliente MQTT
    def _loop_forever(self):
        while self._running:
            self.client.loop(timeout=1.0)  # Tiempo de espera para evitar uso excesivo de CPU


# Ejemplo de uso de la clase
if __name__ == "__main__":
    broker_ip = get_ip_Windows()
    broker_port = 1883
    topic_sub = "Rasp/CmdOut"
    topic_pub = "Rasp/CmdIn"

    mqtt_client = mqtt_coms(broker_ip, broker_port, topic_sub, topic_pub)
    mqtt_client.start()

    try:
        while True:
            mensaje = input("Ingresa un mensaje para publicar en 'Rasp/CmdIn': ")
            mqtt_client.publish_message(mensaje)
    except KeyboardInterrupt:
        print("Desconectando...")
        mqtt_client.stop()
