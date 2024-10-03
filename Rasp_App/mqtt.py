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

        # Crear el cliente MQTT
        self.client = mqtt.Client()

        # Asignar callbacks
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        # Conectarse al broker
        self.client.connect(self.broker_ip, self.broker_port, 60)
        
        self.last_message = None

    # Función que se ejecuta cuando se conecta al broker MQTT
    def on_connect(self, client, userdata, flags, reasonCode, properties=None):
        print(f"Conectado con código de resultado {reasonCode}")
        client.subscribe(self.topic_sub)

    # Función que se ejecuta cuando se recibe un mensaje
    def on_message(self, client, userdata, msg):
        self.last_message = msg.payload.decode()
        print(f"Mensaje recibido en {msg.topic}: {self.last_message}")
        

    # Método para iniciar el bucle del cliente MQTT
    def start(self):
        self.client.loop_start()

    # Método para publicar mensajes
    def publish_message(self, message):
        self.client.publish(self.topic_pub, message)

    # Método para detener el loop
    def stop(self):
        self.client.loop_stop()
        self.client.disconnect()

# Ejemplo de uso de la clase
if __name__ == "__main__":
    broker_ip = "192.168.171.58"
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
