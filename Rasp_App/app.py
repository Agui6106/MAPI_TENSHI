import threading
import time

import subprocess
import re

import signal
import os

# -- FUNCIONES DE CONTROL-- #
# Función para obtener la IP local
def get_ip():
    try:
        resultado = subprocess.check_output(["ifconfig"], encoding='utf-8')
        ip_local = re.findall(r'inet (\d+\.\d+\.\d+\.\d+)', resultado)
        ip_local = [ip for ip in ip_local if ip != "127.0.0.1"]
        if ip_local:
            return ip_local[0]
        else:
            return "No se pudo encontrar la IP local."
    except subprocess.CalledProcessError as e:
        return f"Error al ejecutar el comando: {e}"

# Función para iniciar el proceso de streaming
def iniciar_transmision():
    print("Inicializando transmisión de la cámara...")
    try:
        proc = subprocess.Popen(["python3", "./stream.py"])
        print(f'Transmision iniciada con exito\n')
        return proc
    except Exception as e:
        print(f'Failed to start transmission: {str(e)}')
        return None

# Función para iniciar el proceso de ...
def iniciar_ejemplo():
    print("Inicializando ejemplo...")
    try:
        proc = subprocess.Popen(["python3", "./example.py"])
        return proc
    except Exception as e:
        print(f'Failed to start example: {str(e)}')
        return None

# Función para detener un proceso dado su objeto de proceso
def detener_proceso(proc):
    if proc:
        os.kill(proc.pid, signal.SIGTERM)
        print(f"Proceso {proc.pid} detenido.")
    else:
        print("El proceso no está en ejecución.")
        
# -- FUNCIONES AUXILIARES PARA EL USARIO -- #
def help():
    print(f"stop stream - Detiene el stream de la camara \n")
    print(f"stop example - Detiene la funcion example \n")
    print(f"exit - Detiene por compelto la aplicacion \n")
    
# -- FUNCIONES DE COMUNICACION ESP32 -- #

# -- FUNCIONES DE COMUNICACION MQTT -- #

# - Aplicacion principal basada en comandos -#
if __name__ == "__main__":
    # - Inicialización - #
    print(f"MAPI-Tenshi Robot. Software Version 1.0\nDesarrollado en Santiago de Queretaro, México. 2024\n")
    ip = get_ip()
    print(f"IP actual: {ip}")

    # Iniciar los procesos
    transmision_proc = iniciar_transmision()
    mqtt_proc = "MQTT stopped"
    serial_proc = "Serial stopped"
    ejemplo_proc = iniciar_ejemplo()
    
    print(f"Consulta el video la direccion url: http://{ip}:8000/index.html\n")
    
    # Interfaz de consola
    while True:
        comando = input("Input command : ")

        if comando == 'stop stream':
            detener_proceso(transmision_proc)
        elif comando == 'stop example':
            detener_proceso(ejemplo_proc)
            
        elif comando == 'stop MQTT':
            mqtt_proc
        elif comando == 'stop serial':
            serial_proc
        elif comando == 'exit':
            print("Saliendo del programa...")
            detener_proceso(transmision_proc)
            detener_proceso(ejemplo_proc)
            print("Thanks for choosing MAPI software.inc")
            break
        else:
            print(f"Comando no reconocido. Use help to list all commands.\n")
