import threading
import requests
import time

# Configura la conexión serial con la ESP32
THINGSPEAK_API_KEY = "A1IY1Q9BAR6WMV4X"  # Reemplaza con tu Write API Key

def send_to_thingspeak(data: dict, callback=None):
    """
    Envía múltiples datos a ThingSpeak en una sola petición.

    Args:
        data (dict): Diccionario con pares campo-valor, por ejemplo {'field1': valor1, 'field2': valor2}.
    """
    url = f'https://api.thingspeak.com/update?api_key={THINGSPEAK_API_KEY}'
    response = requests.post(url, data=data)
    
    if response.status_code == 200:
        print(f"Data sent successfully: {data}")
        if callback:
            callback(success=True, data=data)  # Callback indicando éxito
        
    else:
        print("Error al enviar a ThingSpeak.")
        if callback:
            callback(success=False, data=data)  # Callback indicando error
        
def read_and_send_data_to_thingspeak(info, send_to_thingspeak, callback=None):
    """
    Lee datos de un dispositivo y los envía a ThingSpeak.
    
    Args:
        info (list): Lista con datos del dispositivo.
        send_to_thingspeak (callable): Función para enviar los datos a ThingSpeak.
    """
    print('Initializing ThingSpeak communications...')
    while True:
        try:
            if len(info) >= 2 and info[0] != 'nan' and info[1] != 'nan':
                data_to_send = {
                    'field1': info[0],
                    'field2': info[1],
                    'field3': info[2] if len(info) > 2 else None
                }
                send_to_thingspeak(data_to_send, callback=callback)
                time.sleep(15)
            else: 
                print('Valor nan detectado en los datos')
        except KeyboardInterrupt:
            print('Process manually interrupted')
            break
        except Exception as e:
            print(f"Error: {e}")
            break

def start_thingspeak_thread(info, callback=None):
    """
    Inicia un hilo para enviar datos a ThingSpeak.

    Args:
        info (list): Lista con datos del dispositivo.
    """
    thread = threading.Thread(target=read_and_send_data_to_thingspeak, args=(info, send_to_thingspeak, callback))
    thread.daemon = True
    thread.start()
    return thread

# Asegurarse de que el script no se ejecute automáticamente al ser importado
# Asegurarse de que el script no se ejecute automáticamente al ser importado
if __name__ == "__main__":
    def notify(status, data):
        print(f"Callback: {'Success' if status else 'Failure'} - Data: {data}")

    info = ['25.0', '60.0', 'OK']
    start_thingspeak_thread(info, callback=notify)
    print("El programa principal puede continuar ejecutándose.")
    while True:
        time.sleep(1)
