import threading
import time

import subprocess
import re

import signal
import os

# -- FUNCIONES -- #
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

# - Aplicacion principal basada en comandos -#
if __name__ == "__main__":
    # - Inicialización - #
    print(f"MAPI-Tenshi Robot. Software Version 1.0\nDesarrollado en Santiago de Queretaro, México\n")
    ip = get_ip()
    print(f"IP actual: {ip}")

    # Iniciar los procesos
    transmision_proc = iniciar_transmision()
    ejemplo_proc = iniciar_ejemplo()
    
    print(f"Consulta el video la direccion url: http://{ip}:8000/index.html")

    # Interfaz de consola
    while True:
        comando = input("Escribe 'stop stream', 'stop example' o 'exit' para detener procesos: ")

        if comando == 'stop stream':
            detener_proceso(transmision_proc)
        elif comando == 'stop example':
            detener_proceso(ejemplo_proc)
        elif comando == 'exit':
            print("Saliendo del programa...")
            detener_proceso(transmision_proc)
            detener_proceso(ejemplo_proc)
            break
        else:
            print("Comando no reconocido.")
