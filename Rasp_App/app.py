import threading
import time

import subprocess
import re

import signal
import os

# -- FUNCIONES DE PROTOCOLO DE INICIO-- #
"""
    SECUENCIA DE INICIALZIACION 
    * 1) Bienvenida e IP actual
    * 2) Inicialzar MQTT (Control de la app por comandos)
    * 3) Conexion serial a ESP32 por puerto USB (Pract. Arduino)
    * 4) Iniciar servidor de camara
    * S) Ya que el usuario lo ordene por MQTT - PARAR
"""

# 1) Función para obtener la IP local
def get_ip():
    try:
        resultado = subprocess.check_output(["ifconfig"], encoding='utf-8')
        ip_local = re.findall(r'inet (\d+\.\d+\.\d+\.\d+)', resultado)
        ip_local = [ip for ip in ip_local if ip != "127.0.0.1"]
        if ip_local:
            return ip_local[0]
        else:
            return "Cant obtain actual ip"
    except subprocess.CalledProcessError as e:
        return f"Error executing: {e}"
    
# 2) Función para iniciar el proceso de comunicacion MQTT
def iniciar_Mqtt():
    print("Starting Mqtt protocol...")
    try:
        proc = subprocess.Popen(["python3", "./mqtt.py"])
        return proc
    except Exception as e:
        print(f'Failed to start MQTT protocol due to: {str(e)}')
        return None
    
# 3)  Conexion serial a ESP32 por puerto USB 
def iniciar_Serial():
    print("Starting serial comunications...")
    try:
        proc = subprocess.Popen(["python3", "./start_serial_com.py"])
        return proc
    except Exception as e:
        print(f'Failed to start communication due to: {str(e)}')
        return None
    
# 4) Función para iniciar el proceso de streaming
def iniciar_transmision():
    print("Starting camera stream...\n")
    try:
        proc = subprocess.Popen(["python3", "./stream.py"])
        print(f'Transmison started succesfully\n')
        return proc
    except Exception as e:
        print(f'Failed to start transmission due to: {str(e)}')
        return None

# S) Función para detener un proceso dado su objeto de proceso
def detener_proceso(proc):
    if proc:
        os.kill(proc.pid, signal.SIGTERM)
        print(f"Process {proc.pid} succesfully stopped.")
    else:
        print(f"The process {proc.pid} is not runnig or failed to stop")
        
# -- FUNCIONES AUXILIARES PARA EL USARIO -- #
def help():
    print(f"stop stream - Detiene el stream de la camara \n")
    print(f"stop example - Detiene la funcion example \n")
    print(f"exit - Detiene por compelto la aplicacion \n")

# - Aplicacion principal basada en comandos -#
if __name__ == "__main__":
    # - Inicialización - #
    print(f"MAPI-Tenshi Robot. Software Version 1.0\nDesarrollado en Santiago de Queretaro, México. 2024\n")
    ip = get_ip()
    print(f"Actual IP: {ip}")

    # -- SECUENCIA DE INICIALZIACION -- #
    mqtt_proc = iniciar_Mqtt()
    serial_proc = iniciar_Serial()
    transmision_proc = iniciar_transmision()

    print(f"Video stream available in url: http://{ip}:8000/index.html\n")
    
    # - Interfaz de consola - #
    while True:
        comando = input("Input command: ")

        # - Comandos principales - #
        if comando == 'stop MQTT':
            detener_proceso(mqtt_proc)
        elif comando == 'stop serial':
            detener_proceso(serial_proc)
        elif comando == 'stop transmision':
            detener_proceso(transmision_proc)
            
        # - Comandos auxilaires - #
        elif comando == "help":
            help()
        
        # - Comando de salida - #
        elif comando == 'exit':
            print("Leaving program...")
            detener_proceso(mqtt_proc)
            detener_proceso(serial_proc)
            detener_proceso(transmision_proc)
        
            print("\nThanks for choosing MAPI software.inc")
            break
        else:
            print(f"Command not found. Use help to list all commands.\n")
