from tkinter import BOTH
from tkinter import Button
from tkinter import Frame
from tkinter import Label
from tkinter import messagebox
from tkinter import Tk
from tkinter import Canvas
from tkinter import PhotoImage
from tkinter import Entry
from tkinter import filedialog
from tkinter import LabelFrame
from tkinter import Scale

from tkinter.ttk import Combobox
from tkinter.ttk import Notebook
from tkinter.ttk import Separator
from tkinter.ttk import Progressbar

import datetime as dt
import webbrowser

import subprocess
import psutil

import sys
import os

import cv2
import numpy as np
from PIL import Image, ImageTk

import math
from typing import Tuple, Union
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# - MQTT - #
from MQTT_con.MQTT_ex import get_ip_Windows
from MQTT_con.MQTT_ex import mqtt_coms

# - PS4 CONTROLLER - #
import controls.ps4_control as ps4

"""
    Nota: En teoria ya no es encesario entrar a App.
    Puesto que todo se esta modificando dentro de 
    los respecitvos frames
"""

# - Verificacion y ejecucion de Node-Red - #
def is_node_red_running():
    for process in psutil.process_iter(['pid', 'name']):
        if 'node-red' in process.info['name']:  # Busca node-red en los procesos
            return True
    return False

# Si no está en ejecución, ejecuta node-red
"""if not is_node_red_running():
    print("Node-RED no está en ejecución. Iniciando...")
    os.system('node-red')
else:
    print("Node-RED ya está en ejecución.")"""

# - Ventan de configuracion inicial - #
def open_config_window():
    # -- VARIABLES GLOBALES -- #
    def save_config():
        global ip_rasp, ip_esp, ip, server_stream, ID_bot
        ip_rasp = entry_ip_rasp.get()
        ip_esp = entry_ip_esp.get()
        server_stream = entry_server_stream.get()
        ID_bot = entry_Robot_ID.get()
        if ip_rasp == '' or ip_esp == '' or server_stream == '' or ID_bot == '' :
            ip_rasp = '0.0.0.1'
            ip_esp = '0.0.0.2'
            ID_bot = '01'
            server_stream = 'https://server-example.com'
            messagebox.showwarning("Input Empty", "No selected values. Default selected")
        
        config_window.destroy()
            
    bg_general = 'black'
    # - Configuracion de ventan inicial - #
    config_window = Tk()
    config_window.title("Welcome to MAPI")
    config_window.geometry('600x350')
    config_window.resizable(False, False)
    config_window.configure(bg=bg_general)
    
    # Imagen
    source_image = os.path.join(os.path.dirname(__file__), 'mapi_tenshi_baner_init.png')
    photo = PhotoImage(file=source_image)
    
    # - VISUAL - #.grid(row=0, column=0, columnspan=2)
    # - IMAGE - #
    x = Canvas(width=600, height=110, bg='black', highlightthickness=0)
    x.create_image((15,0),image=photo, anchor='nw')
    x.grid(row=0, column=0, columnspan=2)
    
    # - TITULO - #
    Label(config_window, 
          text="Welcome", font=('Magneto',20, 'bold'), 
          bg=bg_general,foreground='white').grid(row=1, column=0, columnspan=2)
    
    # - IP RASP - #
    Label(config_window, 
          text="IP Raspberry:", font=('Z003',13, 'bold'), justify='left',
          bg=bg_general,foreground='white').grid(row=2, column=0, pady=4)
    
    entry_ip_rasp = Entry(config_window, width=40, font=('consolas', 15))
    entry_ip_rasp.grid(row=2, column=1, pady=4)

    # - IP ESP - #
    Label(config_window, text="          IP ESP:", font=('Z003',13, 'bold'), justify='left',
          bg=bg_general,foreground='white').grid(row=3, column=0, pady=4)
    
    entry_ip_esp = Entry(config_window, width=40, font=('consolas', 15))
    entry_ip_esp.grid(row=3, column=1, pady=4)

    # - URL - #
    Label(config_window, text="   Stream URL:", font=('Z003',13, 'bold'), justify='left',
          bg=bg_general,foreground='white').grid(row=4, column=0, pady=2)
    
    entry_server_stream = Entry(config_window, width=40, font=('consolas', 15))
    entry_server_stream.grid(row=4, column=1, pady=4)
    
    # - Robot ID - #
    Label(config_window, text="      Robot ID:", font=('Z003',13, 'bold'), justify='left',
          bg=bg_general,foreground='white').grid(row=5, column=0, pady=4)
    
    entry_Robot_ID = Entry(config_window, width=40, font=('consolas', 15))
    entry_Robot_ID.grid(row=5, column=1, pady=4)

    # - BOTON - #
    Button(config_window, text="Save", width=10,font=('Magneto',14, 'bold'), 
           bg=bg_general, foreground='white' ,
           command=save_config).grid(row=6, columnspan=2, pady=5)

    config_window.mainloop()

open_config_window()

# IP Local
ip = get_ip_Windows()

# - Buscar implementar con daemons (threads)
# - RASP - #
# Mqtt client Raspberry(ipbroker, puerto, suscribcion, publica)
mqtt_client = mqtt_coms(ip, 1883, "Rasp/CmdOut", "Rasp/CmdIn")
mqtt_client.start()

# - ESP32 - #
# -- MOTORS -- #
# Mqtt client Servomotor(ipbroker, puerto, suscribcion, publica)
mqtt_esp_Servo = mqtt_coms(ip, 1883, 'ESP/Response', 'ESP/Servo')
mqtt_esp_Servo.start()

# Mqtt client MotorX(ipbroker, puerto, suscribcion, publica)
mqtt_esp_X = mqtt_coms(ip, 1883, 'ESP/Response', 'ESP/MotorX')
mqtt_esp_X.start()

# Mqtt client MotorY(ipbroker, puerto, suscribcion, publica)
mqtt_esp_Y = mqtt_coms(ip, 1883, 'ESP/Response', 'ESP/MotorY')
mqtt_esp_Y.start()

# -- SENSORS -- #
# Mqtt client MotorY(ipbroker, puerto, suscribcion, publica)
mqtt_esp_Temp = mqtt_coms(ip, 1883, 'ESP/Temperatura', 'PC/Response')
mqtt_esp_Temp.start()

# Mqtt client MotorY(ipbroker, puerto, suscribcion, publica)
mqtt_esp_Hum = mqtt_coms(ip, 1883, 'ESP/Humedad', 'PC/Response')
mqtt_esp_Hum.start()

# -- PERIFERICOS -- #
# Mqtt client Lamp(ipbroker, puerto, suscribcion, publica)
mqtt_esp_Lamp = mqtt_coms(ip, 1883, 'ESP/LampState', 'ESP/Lamp')
mqtt_esp_Lamp.start()

# Mqtt client Buzzer(ipbroker, puerto, suscribcion, publica)
mqtt_esp_Buzzer = mqtt_coms(ip, 1883, 'ESP/BuzState', 'ESP/Buzz')
mqtt_esp_Buzzer.start()

# -- GIROSCOPIO Y GPS -- #
# Mqtt client GiroscoopioX(ipbroker, puerto, suscribcion, publica)
mqtt_esp_PX = mqtt_coms(ip, 1883, 'ESP/PX', 'PC/Response')
mqtt_esp_PX.start()

# Mqtt client GiroscoopioY(ipbroker, puerto, suscribcion, publica)
mqtt_esp_PY = mqtt_coms(ip, 1883, 'ESP/PY', 'PC/Response')
mqtt_esp_PY.start()

# Mqtt client GiroscoopioY(ipbroker, puerto, suscribcion, publica)
mqtt_esp_Lat = mqtt_coms(ip, 1883, 'ESP/Lat', 'PC/Response')
mqtt_esp_Lat.start()

# Mqtt client GiroscoopioY(ipbroker, puerto, suscribcion, publica)
mqtt_esp_Long = mqtt_coms(ip, 1883, 'ESP/Long', 'PC/Response')
mqtt_esp_Long.start()

# Fecha de hoy
date = dt.datetime.now()
        
year = date.year
month = date.month
day = date.day

hour = date.hour
minute = date.minute
segs = date.second

# - Clase Principal Aplicacion - #
class App(Frame):
    def __init__(self, parent, *args, **kwargs):       
        Frame.__init__(self, parent, *args, **kwargs)
        self.parent: Tk = parent
        
        # - Creacion de Notebook (pestañas) - #
        self.notebook = self._Create_notebook()
        
        # - Creacion de los objetos - #
        self.init_gui()
    
    # - Colocamos los elementos visuales - #
    def init_gui(self)-> None:
        # -- Propiedades de la App principal -- #
        self.parent.title(f'MAPI-Tenshi Control Panel - V1.0. on Robot ID: {ID_bot} with IP: {ip_rasp}')
        # Size del monitor
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        root.geometry(f'{screen_width-50}x{screen_height-110}')
        root.resizable(False, False)

        # -- Colocacion de widgets -- #
        self.pack(fill=BOTH, expand=True)

        # Colocamos el Notebook en la ventana
        self.notebook.pack(fill=BOTH, expand=True)
    
    # - Creacion del Notebook con pestañas - #
    def _Create_notebook(self) -> Notebook:
        notebook = Notebook(self)
        
        # Creamos un frame simple para Tab 1
        self.tab1 = Frame(notebook)
        self.tab3 = FrameOptions(notebook)
        self.tab4 = FrameWebControl(notebook)
        self.tab5 = FrameAbout(notebook)
        # Agregamos las pestañas al Notebook
        notebook.add(self.tab1, text='Main')
        notebook.add(self.tab3, text='Options')
        notebook.add(self.tab4, text='Web Control')
        notebook.add(self.tab5, text='About')

        # - Atributos y elementos de aplicacion - #
        # - TITULO - #
        Label(self.tab1, text=f"Control Panel. Robot {ID_bot}",
              foreground='black',
              font=("Magneto", 20, "bold")).grid(row=0, column=0, columnspan=2)
        """
        Interfaz Esperada:
        
            |   0    |      1        |
            --------------------------
          1 | mqtt   |   Raw Cam     |
            --------------------------
          2 | CMD    |   Pos Cam     |
            --------------------------
        """
        # Control MQTT
        frame_mqtt_control = Frame_Main_MQTT_Control(self.tab1)  # Instanciar el frame aquí
        frame_mqtt_control.grid(row=1, column=0, sticky='nsew')

        # Camara sin proceso
        frame_Raw_camera = Frame_Main_Raw_Camera(self.tab1)  # Instanciar el frame aquí
        frame_Raw_camera.grid(row=1, column=1, sticky='nsew')
        
        # Camara procesada
        frame_pros_camera = Frame_Main_Pros_Camera(self.tab1)
        frame_pros_camera.grid(row=2, column=1, sticky='nsew')
        
        # Command Prompt
        frame_CMD_promt = Frame_CMD(self.tab1)
        frame_CMD_promt.grid(row=2,column=0,sticky='nsew')
        frame_CMD_promt.config(bg='black')
        
        return notebook

# ----------------------------------- #
# --------- Frames de MAIN ---------- #
# ----------------------------------- #

# -- Control por mqtt -- #
class Frame_Main_MQTT_Control(Frame):
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        # - MQTT - #
        self.get_response()
    
        # - Creacion de objetos TKinter - #
        self.title: Label = self._Create_title()
        # SubFrames
        self.vital_Data_frame: LabelFrame = self._create_VitalData()
        self.positions_frame: LabelFrame = self._create_Pos()
        self.recv_data_frame: LabelFrame = self._create_Data()
        self.out_ESP_Label = Label(self, text="ESP Output:", font=('Consolas', 15))
        self.dev_button: Button = self._button_Open_Dev()
        self.output: Entry = self._ESP_output()
        
        # -- VITAL-DATA ELEMENTS -- #
        # - TITULOS - #
        self.Motors_title = Label(self.vital_Data_frame, text="Main Motors", font=('Z003', 15, 'bold'))
        self.servo_title = Label(self.vital_Data_frame, text="Camera angle", font=('Z003', 15, 'bold'))
        self.perifercials_title = Label(self.vital_Data_frame, text="Peripherals", font=('Z003', 15, 'bold'))
        self.status_label = Label(self.vital_Data_frame, text="Status", font=('Z003', 15, 'bold'))
        self.buz_on_label = Label(self.vital_Data_frame, text="Off", font=('Z003', 15, 'bold'), foreground='red')
        self.lamp_on_label = Label(self.vital_Data_frame, text="Off", font=('Z003', 15, 'bold'), foreground='red')
        
        # - MOTORES - #
        self.motorX_label = Label(self.vital_Data_frame, text="Motor X: ", font=('Z003', 14))
        self.motorY_label = Label(self.vital_Data_frame, text="Motor Y: ", font=('Z003', 14))
        self.motorX_data: Label = self._motorX_Data()
        self.motorY_data: Label = self._motorY_Data()
        
        # - PERIFERICOS - #
        self.cam_scale: Scale = self._create_joystick_slider()
        self.buz_but: Button = self._button_Buz()
        self.lamp_but: Button = self._button_lamp()
        
        # - STATUS - #
        self.statuts1_label = Label(self.vital_Data_frame, text="Status 1", font=('Z003', 13))
        self.statuts2_label = Label(self.vital_Data_frame, text="Status 2", font=('Z003', 13))
        self.statuts3_label = Label(self.vital_Data_frame, text="Status 3", font=('Z003', 13))
        self.statuts4_label = Label(self.vital_Data_frame, text="Status 4", font=('Z003', 13))
        self.status1: Button = self.stat_1()
        self.status2: Button = self.stat_2()
        self.status3: Button = self.stat_3()
        self.status4: Button = self.stat_4()
        
        # -- POSITIONS ELEMENTS -- #
        # - GIROSCOPIO - #
        self.X_Label = Label(self.positions_frame, text="X:", font=('Z003', 15, 'bold'))
        self.Y_Label = Label(self.positions_frame, text="Y:", font=('Z003', 15, 'bold'))
        self.X_Data =  Label(self.positions_frame, text="00000", font=('Z003', 15,))
        self.Y_Data = Label(self.positions_frame,  text="00000", font=('Z003', 15,))
        
        # - GPS - #
        self.Latitud_Label = Label(self.positions_frame,  text="  Latitud:", font=('Z003', 15, 'bold'))
        self.Longitud_Label = Label(self.positions_frame, text="Longitud:", font=('Z003', 15, 'bold'))
        self.Latitud_Data = Label(self.positions_frame, text="000.000", font=('Z003', 15,))
        self.Longitud_Data = Label(self.positions_frame, text="000.000", font=('Z003', 15,))
        
        # - ACCIONES - #
        self.Google_maps_But: Button = self.launch_GM_Butt()
        self.empty_space_positions = Label(self.positions_frame, text=" ", font=('Z003', 15, 'bold'))
        self.empty_space_recv = Label(self.recv_data_frame, text=" ", font=('Z003', 15, 'bold'))
        
        # -- DATA ELEMENTS -- #
        # Titulos
        self.dist_front_title = Label(self.recv_data_frame, text="Frontal Distance", font=('Z003', 15, 'bold'))
        self.dist_back_title = Label(self.recv_data_frame, text="Back Distance", font=('Z003', 15, 'bold'))
        self.sensors_title = Label(self.recv_data_frame, text="Sensors", font=('Z003', 15, 'bold'))
        
        # Sensores distancias
        self.frontal_Ultr: Label = self.ultr_label()
        self.frontal_Infr: Label = self.infr_label()
        
        self.back_Ultr: Label = self.ultr_label()
        self.back_Infr: Label = self.infr_label()
        
        # Sensores generales
        self.temp_label = Label(self.recv_data_frame, text="Temperatura:", font=('Z003', 15, 'bold'))
        self.Hum_label = Label(self.recv_data_frame,  text="    Humedad:", font=('Z003', 15, 'bold'))
        self.Gas_label = Label(self.recv_data_frame,  text="          Gas:", font=('Z003', 15, 'bold'))
        self.gas_levels: Progressbar = self._progress_GAS()
        
        self.data_temp: Label = self.data_label()
        self.data_Hum: Label = self.data_label()
        self.data_Dist_InfrF: Label = self.data_label()
        self.data_Dist_UltrF: Label = self.data_label()
        self.data_Dist_InfrB: Label = self.data_label()
        self.data_Dist_UltrB: Label = self.data_label()
        
        # - Obtenemos lso valores del control - #        
        self.update_vals()

        # - Creacion de elementos visuales -#
        self.init_main_gui()
        self.init_gui_of_VitalData()
        self.init_gui_of_Positions()
        self.init_gui_of_RecvData()
        
    # - Colocamos los elementos visuales - #
    def init_main_gui(self)-> None:
        self.title.grid(row=0, column=0, columnspan=2)
        
        #self.grid_rowconfigure(1, weight=1)
        #self.grid_columnconfigure(0, weight=1)

        # - LABEL FRAMES -#
        self.vital_Data_frame.grid(row=1, column=0, columnspan=3, sticky="nsew", ipadx=10, pady=10) # 10x3
        self.positions_frame.grid(row=2, column=2, sticky="nsew", ) # 7x2
        self.recv_data_frame.grid(row=2, column=0, sticky="nsew", columnspan=2)
        
        self.out_ESP_Label.grid(row=3,column=0, pady=10)
        self.dev_button.grid(row=3,column=2)
        self.output.grid(row=3,column=1)
        
    def init_gui_of_VitalData(self) -> None:
        # - CONTENTS VITAL- #
        # Ttitulos
        self.Motors_title.grid(row=0, column=0,columnspan=2,)
        self.servo_title.grid(row=0,column=2,columnspan=2)
        self.perifercials_title.grid(row=0,column=4,columnspan=2)
        self.status_label.grid(row=0,column=6,columnspan=4)
        
        # Elementos Motor
        self.motorX_label.grid(row=1,column=0, padx=10)
        self.motorY_label.grid(row=2,column=0, padx=10)
        self.motorX_data.grid(row=1,column=1)
        self.motorY_data.grid(row=2,column=1)
        
        # Servo
        self.cam_scale.grid(row=1,column=2,columnspan=2,padx=5)
        
        # Perifericos
        self.buz_but.grid(row=1,column=4, padx=10)
        self.lamp_but.grid(row=2,column=4, padx=10, pady=5)
        self.buz_on_label.grid(row=1,column=5, padx=3)
        self.lamp_on_label.grid(row=2,column=5, padx=3)
        
        # Status
        self.statuts1_label.grid(row=2,column=6, padx=10)
        
        self.status1.grid(row=1,column=6, padx=10)
        self.status2.grid(row=1,column=7, padx=10)
        self.status3.grid(row=1,column=8, padx=10)
        self.status4.grid(row=1,column=9, padx=10)
        self.statuts2_label.grid(row=2,column=7)
        self.statuts3_label.grid(row=2,column=8)
        self.statuts4_label.grid(row=2,column=9)
        
        #self.status1.grid_remove()
        #self.status2.grid_remove()
        #self.status3.grid_remove()
        #self.status4.grid_remove()
    
    def init_gui_of_Positions(self) -> None:
        # - CONTENTS POSITIONS - #
        #self.empty_space_positions.grid(row=1, column=0, padx=70)
        # Giroscopio
        self.X_Label.grid(row=1, column=0, pady=5, ipadx=15)
        self.Y_Label.grid(row=2, column=0, pady=5)
        
        self.X_Data.grid(row=1,column=1, )
        self.Y_Data.grid(row=2,column=1, )
        
        # Coordenadas
        self.Latitud_Label.grid(row=1, column=2, )
        self.Longitud_Label.grid(row=2,column=2, )
        
        self.Latitud_Data.grid(row=1,column=3, columnspan=2)
        self.Longitud_Data.grid(row=2,column=3, columnspan=2)
        
        self.Google_maps_But.grid(row=3,column=1, columnspan=4,)
        
    def init_gui_of_RecvData(self) -> None:
        # - CONTENTS DATA - #
        self.empty_space_recv.grid(row=0,column=0, padx=10)
        # Titulos
        self.dist_front_title.grid(row=0, column=1, columnspan=2)
        self.dist_back_title.grid(row=0, column=3, columnspan=2)
        self.sensors_title.grid(row=3, column=1,columnspan=4, pady=5)
        
        # Etiquetas
        self.frontal_Ultr.grid(row=1, column=1, pady=10)
        self.frontal_Infr.grid(row=2, column=1, )
        
        self.back_Ultr.grid(row=1,column=3)
        self.back_Infr.grid(row=2,column=3)
        
        self.temp_label.grid(row=4,column=1)
        self.Hum_label.grid(row=4,column=3)
        self.Gas_label.grid(row=5,column=1)
        
        # Data
        self.data_Dist_UltrF.grid(row=1, column=2)
        self.data_Dist_InfrF.grid(row=2, column=2)
        self.data_Dist_InfrB.grid(row=1,column=4)
        self.data_Dist_UltrB.grid(row=2,column=4)
        
        self.gas_levels.grid(row=5,column=2, columnspan=3)
        
        self.data_temp.grid(row=4,column=2)
        self.data_Hum.grid(row=4,column=4)
        
    # - Atributos y elementos de aplicacion - #
    # - TITULO - #
    def _Create_title(self) -> Label:
        return Label(
            master=self,
            text='Robot Control and Data',
            foreground='black',
            font=("Z003", 20, "bold")
        )
    
    def _button_Open_Dev(self) -> Button:
        return Button(self, 
                      text='Open Web Debugger', 
                      font=("Magneto", 13),
                      width=20,
                      command= self.open_user)
        
    def _ESP_output(self) -> Entry:
        return Entry(self, 
                     foreground='black',
                     bg = 'black',
                     font=('consolas', 14),  
                     justify='left',
                     state='readonly',
                     width=35)
        
    def open_user(self):
        nav1 = webbrowser.get()
        nav1.open(f"http://{ip}:1880/ui")
    
    # - Sub Frames -#
    def _create_VitalData(self) -> LabelFrame:
        return LabelFrame(
            self,
            text="Vital Data",
            font=("Magneto", 17,),
            
        )
    def _create_Pos(self) -> LabelFrame:
        return LabelFrame(
            self,
            text="Actual Positions",
            font=("Magneto", 17,),
        )
    def _create_Data(self) -> LabelFrame:
        return LabelFrame(
            self,
            text="General Data",
            font=("Magneto", 17,),
            
        )
    
    # - CONTENIDOS SUBFRAMES - #
    # - Vital Data - #
    # Motors 
    def _motorX_Data(self) -> Label:
        #x,y = self.update_Motors_val()
        return Label(self.vital_Data_frame, font=('Z003', 14), text=f'0000')
    def _motorY_Data(self) -> Label:
        #x,y = self.update_Motors_val()
        return Label(self.vital_Data_frame, font=('Z003', 14), text=f'0000')
   
    # Slider
    def _create_joystick_slider(self) -> Scale:
        return Scale(self.vital_Data_frame, from_=-1, to=1, 
                     resolution=0.01, orient='horizontal',sliderlength=20, length=200)
    
    # Perifericos
    def _button_Buz(self) -> Button:
        return Button(self.vital_Data_frame, 
                      font=('Magneto', 14), text="Lamp",width=6,
                      command=self.send_buttons_info(topic='Buzzer'))
    def _button_lamp(self) -> Button:
        return Button(self.vital_Data_frame, 
                      font=('Magneto', 14), text="Buzzer",width=6,
                      command=self.send_buttons_info(topic='Lamp'))
    
    # Status
    def stat_1(self) -> Button:
        return Button(self.vital_Data_frame, 
                      text='',width=6, 
                      bg='green', default='disabled', state='disabled')
    def stat_2(self) -> Button:
        return Button(self.vital_Data_frame, 
                      text='',width=6, 
                      bg='yellow', default='disabled', state='disabled') 
    def stat_3(self) -> Button:
        return Button(self.vital_Data_frame, 
                      text='',width=6, 
                      bg='red', default='disabled', state='disabled')
    def stat_4(self) -> Button:
        return Button(self.vital_Data_frame, 
                      text='',width=6, 
                      bg='blue', default='disabled', state='disabled')
    
    # - Positions - #
    def launch_GM_Butt(self) -> Button:
        return Button(self.positions_frame, 
                      font=('Magneto', 14), text="Open on Google Maps",
                      command=self.get_and_launch_MAPS)
    # Obtener las coordenadas en google maps
    def get_and_launch_MAPS(self):
        pass
    
    # - Data - #    
    def ultr_label(self) -> Label:
        return Label(self.recv_data_frame, text="Ultrasonico:", font=('Z003', 15, 'bold'))
    def infr_label(self) -> Label:
        return Label(self.recv_data_frame, text="    Infrarojo:", font=('Z003', 15, 'bold'))
    def data_label(self) -> Label:
        return Label(self.recv_data_frame, text="0000", font=('Z003', 15,))
    
    def _progress_GAS(self) -> Progressbar:
        return Progressbar(self.recv_data_frame, orient='horizontal', mode='determinate', length=300)
    
    # -- OPERATIVO -- #
    def update_vals(self):
        # Verificamos que haya un control Conectado
        if not ps4.check_ps4_connection():
            pass
        else:
            # Obtenemos los valores y redondeamos los necesarios
            xr,yr = ps4.get_joys_right()
            xl,yl = ps4.get_joys_left()
            
            xr = round(xr, 2)
            yr = round(yr, 2)
            xl = round(xl, 2)
            yl = round(yl, 2)
            
            # Escritura en interfaz
            self.cam_scale.set(xr)
            self.motorX_data.config(text=xl)
            self.motorY_data.config(text=yl)
            
            # Enviar x mqtt
            self.send_motors_vals(Servo=xr, MotorX=xl, MotorY=yl)
            self.after(50, self.update_vals)
        
    # - MQTT PROTOCOL - #
    # Envio
    def send_motors_vals(self, Servo, MotorX, MotorY):
        try:
            mqtt_esp_Servo.publish_message(Servo)  
            mqtt_esp_X.publish_message(MotorX)
            mqtt_esp_Y.publish_message(MotorY)
        except Exception as e:
            print(f"Failed to send info due to: {e}")
            
    def send_buttons_info(self, topic):
        try:
            if topic == 'Lamp':
                mqtt_esp_Lamp.publish_message('lamp')
            elif topic == 'Buzzer':
                mqtt_esp_Buzzer.publish_message('buzz')
        except Exception as e:
            print(f"Failed to send info due to: {e}")
    
    # Recepcion        
    def get_response(self):
        # Perifericos
        self.mensaje_lamp = mqtt_esp_Lamp.last_message
        self.mensaje_buzz = mqtt_esp_Buzzer.last_message
        # Giroscopio
        self.mensaje_PX = mqtt_esp_PX.last_message
        self.mensaje_PY = mqtt_esp_PY.last_message
        # Coordenadas
        self.Lat = mqtt_esp_Lat.last_message
        self.Long = mqtt_esp_Long.last_message
        # Sensores
        self.response_temp = mqtt_esp_Temp.last_message
        self.response_hum = mqtt_esp_Hum.last_message
        
        # Verificar respuesta en lampara
        if self.mensaje_lamp:
            if self.mensaje_lamp == 'LPOn':
                self.buz_on_label.config(text='On', foreground='green')
            elif self.mensaje_lamp == 'LPOff':
                self.lamp_on_label.config(text='Off',foreground='red')
        
        # Verificar respuesta del buzzer
        if self.mensaje_buzz:
            if self.mensaje_lamp == 'BSOn':
                self.buz_on_label.config(text='On', foreground='green')
            elif self.mensaje_lamp == 'BSOff':
                self.lamp_on_label.config(text='Off',foreground='red')
                
        # Escritura de los valores del giroscopio
        if self.mensaje_PX:
            self.X_Data.config(text=self.mensaje_PX)
        if self.mensaje_PY:
            self.Y_Data.config(text=self.mensaje_PY)
            
        # Escritura de coordenadas
        if self.Lat:
            self.Latitud_Data.config(text=self.Lat)
        if self.Long:
            self.Longitud_Data.config(text=self.Long)
            
        # Verifica respuesat del status
        if self.response_hum:
            self.data_Hum.config(text=self.response_hum)
        if self.response_temp:
            self.data_temp.config(text=self.response_temp)
            
# -- Camara sin procesar -- #
class Frame_Main_Raw_Camera(Frame):
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        
        # Imagen si no se encunetra stream
        nocamav = os.path.join(os.path.dirname(__file__), 'novideo_finall.png')
        self.novidcam = PhotoImage(file=nocamav)
        
        self.stream_url = server_stream
    
        # - Creacion de objetos TKinter - #
        self.title: Label = self._Create_title()
        self.camera: Canvas = self._Camera_canva_()
        
        # Creamos los objetos
        self.init_gui()
        
        # Iniciamos stream y verifcamos
        self.cap = cv2.VideoCapture(self.stream_url)
        if not self.cap.isOpened():
            self.camera.create_image((0,0),image=self.novidcam, anchor='nw')
            print(f"Error: No se pudo abrir el stream en {self.stream_url}")
        else:
            self.update_frame()  # Iniciar actualización de frames
        
        
    # - Colocamos los elementos visuales - #
    def init_gui(self)-> None:
        self.title.grid(row=0, column=0, columnspan=2)
        self.camera.grid()
        
    # - ELEMENTOS VISUALES - # 
    # - TITULO - #
    def _Create_title(self) -> Label:
        return Label(
            master=self,
            text=f'Camara View {day}-{month}-{year}',
            foreground='black',
            font=("Z003", 20, "bold")
        )
    
    # - CAMARA VISUAL - #
    def _Camera_canva_(self) -> Canvas:
        return Canvas(self, width=640, height=480,bg='black')
    
    # - OPERATIVO - #
    def update_frame(self):
        ret, frame = self.cap.read()  # Leer el frame del stream

        if ret:
            # Convertir de BGR a RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Convertir el frame a imagen PIL
            img = Image.fromarray(frame_rgb)
            img = img.resize((640, 480), Image.Resampling.LANCZOS)  # Redimensionar
            img_tk = ImageTk.PhotoImage(img)

            # Mostrar la imagen en el canvas
            self.camera.create_image(0, 0, anchor="nw",  image=img_tk)
            self.camera.image = img_tk  # Mantener referencia de la imagen

        # Volver a llamar la función después de un intervalo de tiempo
        self.after(10, self.update_frame)

# -- Camara procesada -- #
class Frame_Main_Pros_Camera(Frame):
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        
        self.stream_url = server_stream
    
        # - Creacion de objetos TKinter - #
        self.title: Label = self._Create_title()
        
        # Botones para las funciones
        self.but_colors: Button = self._but_colors()
        self.but_contours: Button = self._but_contors()
        self.but_save: Button = self._but_save()
        self.but_faces: Button = self._but_faces()
        
        # Creamos los objetos
        self.init_gui()
        
    # - Colocamos los elementos visuales - #
    def init_gui(self)-> None:
        self.title.grid(row=0, column=0, columnspan=3,)
        
        # Colocamos los botones
        self.but_colors.grid(row=1, column=0, padx=30, pady=5,)
        self.but_contours.grid(row=1, column=1,)
        self.but_faces.grid(row=2, column=0, )
        self.but_save.grid(row=2, column=1,)
        
    # - Atributos y elementos de aplicacion - #
    # - TITULO - #
    def _Create_title(self) -> Label:
        return Label(
            master=self,
            text='Opciones de Camara',
            foreground='black',
            font=("Z003", 20, "bold")
        )

    # - Botones - #
    def _but_colors(self) -> Button:
        return Button(self,
                      width=18,
                      borderwidth=1,
                      command=self.detect_colors,
                      text='Colors',
                      font=('Magneto', 15))
    
    def _but_contors(self) -> Button:
        return Button(self,
                      width=18,
                      borderwidth=1,
                      command=self.detect_contorns,
                      text='Contorns',
                      font=('Magneto', 15))
    
    def _but_save(self) -> Button:
        return Button(self,
                      width=18,
                      borderwidth=1,
                      command=self.save_photo,
                      text='Save',
                      font=('Magneto', 15))
        
    def _but_faces(self) -> Button:
        return Button(self,
                      width=18,
                      borderwidth=1,
                      command=self.face_detect,
                      text='Faces',
                      font=('Magneto', 15))
        
    # -- OPERATIVO -- #
    # Colores 
    def detect_colors(self):
        cap = cv2.VideoCapture(self.stream_url)

        # Crear ventana de OpenCV
        cv2.namedWindow('Deteccion de colores')

        # Crear trackbars para ajustar los valores de HSV
        def nothing(x):
            pass
        
        # Trackbars para los rangos de color
        cv2.createTrackbar('Hue Min', 'Deteccion de colores', 0, 179, nothing)
        cv2.createTrackbar('Hue Max', 'Deteccion de colores', 179, 179, nothing)
        cv2.createTrackbar('Sat Min', 'Deteccion de colores', 0, 255, nothing)
        cv2.createTrackbar('Sat Max', 'Deteccion de colores', 255, 255, nothing)
        cv2.createTrackbar('Val Min', 'Deteccion de colores', 0, 255, nothing)
        cv2.createTrackbar('Val Max', 'Deteccion de colores', 255, 255, nothing)

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Convertir imagen a HSV
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            # Leer los valores de los trackbars
            hue_min = cv2.getTrackbarPos('Hue Min', 'Deteccion de colores')
            hue_max = cv2.getTrackbarPos('Hue Max', 'Deteccion de colores')
            sat_min = cv2.getTrackbarPos('Sat Min', 'Deteccion de colores')
            sat_max = cv2.getTrackbarPos('Sat Max', 'Deteccion de colores')
            val_min = cv2.getTrackbarPos('Val Min', 'Deteccion de colores')
            val_max = cv2.getTrackbarPos('Val Max', 'Deteccion de colores')

            # Definir el rango de color a detectar usando los valores de los trackbars
            lower_color = np.array([hue_min, sat_min, val_min])
            upper_color = np.array([hue_max, sat_max, val_max])

            # Crear la máscara para el color
            mask = cv2.inRange(hsv, lower_color, upper_color)
            result = cv2.bitwise_and(frame, frame, mask=mask)

            # Mostrar la imagen con los colores seleccionados
            cv2.imshow('Deteccion de colores', result)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
    
    # Contornos
    def detect_contorns(self): 
        cap = cv2.VideoCapture(self.stream_url)
        
        #cv2.namedWindow(f'Contour detection of robot {ID_bot}')
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Convertir imagen a escala de grises
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Detectar contornos
            edges = cv2.Canny(blurred, 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            
            # Dibujar contornos
            cv2.drawContours(frame, contours, -1, (0, 255, 0), 2)
            
            cv2.imshow('Contorns', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            
        cap.release()
        cv2.destroyAllWindows()
    
    # Deteccion de rsotros
    def face_detect(self):
        """
        Based on MediaPipe 
        """
        MARGIN = 10  # pixels
        ROW_SIZE = 10  # pixels
        FONT_SIZE = 1
        FONT_THICKNESS = 1
        TEXT_COLOR = (255, 0, 0)  # red

        def _normalized_to_pixel_coordinates(
            normalized_x: float, normalized_y: float, image_width: int,
            image_height: int) -> Union[None, Tuple[int, int]]:
          """Converts normalized value pair to pixel coordinates."""

          # Checks if the float value is between 0 and 1.
          def is_valid_normalized_value(value: float) -> bool:
            return (value > 0 or math.isclose(0, value)) and (value < 1 or
                                                              math.isclose(1, value))

          if not (is_valid_normalized_value(normalized_x) and
                  is_valid_normalized_value(normalized_y)):
            # TODO: Draw coordinates even if it's outside of the image bounds.
            return None
          x_px = min(math.floor(normalized_x * image_width), image_width - 1)
          y_px = min(math.floor(normalized_y * image_height), image_height - 1)
          return x_px, y_px

        def visualize(
            image,
            detection_result
        ) -> np.ndarray:
          """Draws bounding boxes and keypoints on the input image and return it.
          Args:
            image: The input RGB image.
            detection_result: The list of all "Detection" entities to be visualize.
          Returns:
            Image with bounding boxes.
          """
          annotated_image = image.copy()
          height, width, _ = image.shape

          for detection in detection_result.detections:
            # Draw bounding_box
            bbox = detection.bounding_box
            start_point = bbox.origin_x, bbox.origin_y
            end_point = bbox.origin_x + bbox.width, bbox.origin_y + bbox.height
            cv2.rectangle(annotated_image, start_point, end_point, TEXT_COLOR, 3)

            # Draw keypoints
            for keypoint in detection.keypoints:
              keypoint_px = _normalized_to_pixel_coordinates(keypoint.x, keypoint.y,
                                                             width, height)
              color, thickness, radius = (0, 255, 0), 2, 2
              cv2.circle(annotated_image, keypoint_px, thickness, color, radius)

            # Draw label and score
            category = detection.categories[0]
            category_name = category.category_name
            category_name = '' if category_name is None else category_name
            probability = round(category.score, 2)
            result_text = category_name + ' (' + str(probability) + ')'
            text_location = (MARGIN + bbox.origin_x,
                             MARGIN + ROW_SIZE + bbox.origin_y)
            cv2.putText(annotated_image, result_text, text_location, cv2.FONT_HERSHEY_PLAIN,
                        FONT_SIZE, TEXT_COLOR, FONT_THICKNESS)

          return annotated_image
        
        BaseOptions = mp.tasks.BaseOptions
        FaceDetector = mp.tasks.vision.FaceDetector
        FaceDetectorOptions = mp.tasks.vision.FaceDetectorOptions
        FaceDetectorResult = mp.tasks.vision.FaceDetectorResult
        VisionRunningMode = mp.tasks.vision.RunningMode
        
        # STEP 2: Create an FaceDetector object.
        source_model = os.path.join(os.path.dirname(__file__), 'blaze_face_short_range.tflite')
        detector_model = PhotoImage(file=source_model)
        base_options = python.BaseOptions(model_asset_path=detector_model)
        options = vision.FaceDetectorOptions(base_options=base_options)
        detector = vision.FaceDetector.create_from_options(options)

        # STEP 3: Load the input image.
        cap = cv2.VideoCapture(self.stream_url)
        image = mp.Image.create_from_file(cap)

        # STEP 4: Detect faces in the input image.
        detection_result = detector.detect(image)

        # STEP 5: Process the detection result. In this case, visualize it.
        image_copy = np.copy(image.numpy_view())
        annotated_image = visualize(image_copy, detection_result)
        rgb_annotated_image = cv2.cvtColor(annotated_image, cv2.COLOR_BGR2RGB)
        cv2.imshow(rgb_annotated_image)

    # Tomar foto
    def save_photo(self):
        cap = cv2.VideoCapture(self.stream_url)
    
        # Leer un solo frame
        ret, frame = cap.read()
    
        if ret:
            # Usar un cuadro de diálogo para seleccionar la ubicación y nombre del archivo
            file_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                     initialfile=f'image_{day}_{month}_{year}_at_{hour}_{minute}_by_bot_{ID_bot}.png',
                                                     filetypes=[("PNG files", "*.png"),
                                                                ("JPEG files", "*.jpg"),
                                                                ("All files", "*.*")])
            
            if file_path:
                # Guardar la imagen
                cv2.imwrite(file_path, frame)
                messagebox.showinfo("Saved!",f'Image saved successfully at:\n{file_path}')
                print(f"Foto guardada en {file_path}")
            else:
                messagebox.showwarning("Cancel", "Saved cancel")
                print("Guardado cancelado.")
        else:
            messagebox.showerror('Error at save', 'Error saving image')
            print("Error al capturar el fotograma.")

        cap.release()
    
# -- Command Promt -- #
class Frame_CMD(Frame):
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
    
        # - Creacion de objetos TKinter - #
        self.title: Label = self._Create_title()
        self.content: Label = self._In_label()
        self.command: Label = self._commands()
        self.send: Button = self._comman_send_button()
        self.out: Label = self._out_label()
        self.cmd_out: Entry = self._command_output()
        
        # - Diccionario de comandos internos - #
        self.internal_commands = {
            'help.green': 'Hmin: 35 Hmax: 85 Smin: 100 Smax: 255 Vmin: 50 Vmax: 255',
            'help.red': 'Hmin: 100 Hmax: 130 Smin: 100 Smax: 255 Vmin: 50 Vmax: 255',
            'help.blue': 'Hmin: 0 Hmax: 10 Smin: 100 Smax: 255 Vmin: 100 Vmax: 255'
        }
        
        # - Actualizamos la respuesta - #
        self.update_cmd_output()
        
        # Creamos los objetos
        self.init_gui()
        
    # - Colocamos los elementos visuales - #
    def init_gui(self)-> None:
        self.title.grid(column=0,row=0,columnspan=3)
        
        # - Envio de comandos - #
        self.content.grid(column=0,row=1)
        self.command.grid(column=1,row=1)
        self.send.grid(column=2,row=1,padx=5, rowspan=2)
        
        # - Recepcion de comandos - # 
        self.out.grid(column=0,row=2, pady=5)
        self.cmd_out.grid(column=1,row=2, pady=5)
        
    # - Atributos y elementos de aplicacion - #
    # - TITULO - #
    def _Create_title(self) -> Label:
        return Label(
            master=self,
            text='Command Prompt',
            foreground='green',
            background='black',
            font=("Z003", 20, "bold")
        )
    
    # --- ENVIO DE COMANDOS --- #
    # - Visual - #
    def _In_label(self) -> Label:
        return Label(self, 
                     foreground='white',
                     bg = 'black',
                     font=('consolas', 14),            
                     text="Input command: ")
    
    def _commands(self) -> Entry:
        return Entry(self,
                     background='black',
                     foreground='white',
                     font=('consolas', 14),
                     width=57)
        
    def _comman_send_button(self) -> Button:
        return Button(self,
                      width=7,
                      background='black',
                      foreground='green',
                      borderwidth=1,
                      command=self.send_command,
                      text='Send',
                      font=('Magneto', 15))
    
    # - Operativo - #
    def send_command(self):
        cmd_in = self.command.get().strip()

        # Verificar si el comando es interno
        if cmd_in in self.internal_commands:
            self.cmd_out.config(state='normal')
            self.cmd_out.delete(0, 'end')  # Borrar el contenido anterior
            self.cmd_out.insert(0, self.internal_commands[cmd_in])  # Insertar el mensaje
            self.cmd_out.config(state='readonly')
        else:
            # Enviar el comando por MQTT si no es un comando interno
            if cmd_in:
                try:
                    mqtt_client.publish_message(cmd_in)  # Envía el comando por MQTT
                except Exception as e:
                    messagebox.showerror("MQTT Error", f"Failed to send command: {e}")
            else:
                messagebox.showwarning("Input Error", "Please enter a command.")
    
    # --- RECEPCION DE COMANDOS --- #
    # - Visual - #
    def _out_label(self) -> Label:
        return Label(self, 
                     foreground='white',
                     bg = 'black',
                     font=('consolas', 14),    
                     justify='left',        
                     text="       Output: ")
            
    def _command_output(self) -> Entry:
        return Entry(self, 
                     foreground='black',
                     bg = 'black',
                     font=('consolas', 14),  
                     justify='left',
                     state='readonly',
                     width=57)
    
    # - Operativo - #
    def update_cmd_output(self):
        self.mensaje = mqtt_client.last_message
        self.cmd_out.config(state='normal')

        # Insertar el mensaje en el Entry
        if self.mensaje:
            self.cmd_out.delete(0, 'end')  # Borrar el contenido anterior
            self.cmd_out.insert(0, self.mensaje)  # Insertar el nuevo mensaje

        # Volver a hacer el Entry de solo lectura
        self.cmd_out.config(state='readonly')
        self.parent.after(500, self.update_cmd_output)

# ----------------------------------- #
# -------- Frames de control -------- #
# ----------------------------------- #
   
# ---- Clase ventana de Opciones ---- #
class FrameOptions(Frame):
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
    
        # - Creacion de objetos TKinter - #
        self.title: Label = self._Create_title()
        
        # - IPs - #
        self.content: Label = self._Ip_Opt_Label()
        self.HIP_label: Label = self._hostIP_Label()
        self.EsIP_label: Label = self._espIP_Label()
        self.RasIP_label: Label = self._raspIP_Label()
        
        self.host_ip: Entry = self._ip_host()
        self.esp_ip: Entry = self._ip_esp_in()
        self.rasp_ip: Entry = self._ip_rasp_in()
        
        # - SERVER -#
        self.server_label: Label = self._Server_tag()
        self.server_URL: Entry = self._server_url()
        
        # - D-PAD - #
        self.title_joys: Label = self._controls_title_()
        
        self.lable_name: Label = self._joy_name_()
        self.lable_id: Label = self._joy_pc_id_()
        self.lable_power: Label = self._joy_power_()
        self.lable_buttons: Label = self._joy_buttons_()
        self.lable_axes: Label = self._joy_axes_()
        
        self.name: Entry = self.name_label()
        self.id: Entry = self.id_label()
        self.power: Entry = self.power_label()
        self.buttons: Entry = self.buts_label()
        self.axes: Entry = self.axes_label()
        
        self.joys_updated: Button = self.but_refresh()
        self.run_tests_butt: Button = self.but_test()
        
        # Creamos los objetos
        self.init_gui()
        self.update_configs_connect()
        self.get_joy_stats()
        
    # - Colocamos los elementos visuales - #
    def init_gui(self)-> None:
        self.title.grid(row=0, column=0, columnspan=2)
        
        # - IP - #
        # - TItulos - #
        self.content.grid(row=1, column=0,columnspan=2)
        self.HIP_label.grid(row=2, column=0, pady=4)
        self.EsIP_label.grid(row=3, column=0, pady=4)
        self.RasIP_label.grid(row=4, column=0, pady=4)

        self.host_ip.grid(row=2,column=1, pady=4)
        self.esp_ip.grid(row=3,column=1, pady=4)
        self.rasp_ip.grid(row=4,column=1, pady=4)
        
        # - SERVER - #
        self.server_label.grid(row=6,column=0, )
        self.server_URL.grid(row=6,column=1,)
        
        # - JOYSTICK - #
        self.title_joys.grid(row=7,column=0,columnspan=2, pady=15)
        
        self.lable_name.grid(row=8,column=0,)
        self.lable_id.grid(row=9,column=0, pady= 4)
        self.lable_power.grid(row=10,column=0, pady= 4)
        self.lable_buttons.grid(row=11,column=0, pady= 4)
        self.lable_axes.grid(row=12,column=0, pady= 4)
         
        self.name.grid(row=8,column=1)
        self.id.grid(row=9,column=1)
        self.power.grid(row=10,column=1)
        self.buttons.grid(row=11,column=1)
        self.axes.grid(row=12,column=1)
        
        # - BUTTONS - #
        self.joys_updated.grid(row=13, column=0, columnspan=2, pady=2)
        self.run_tests_butt.grid(row=14, column=0, columnspan=2, pady=2)

    # - Atributos y elementos de aplicacion - #
    # - TITULO - #
    def _Create_title(self) -> Label:
        return Label(
            master=self,
            text='Connectivity',
            foreground='black',
            font=("Magneto", 20, "bold")
        )
    
    # - ELEMENTOS VISUALES IPs - #
    def _Ip_Opt_Label(self) -> Label:
        return Label(self, text="Actual IPs", font=("Z003", 15, "bold"))
    
    def _hostIP_Label(self) -> Label:
        return Label(self, 
                     text="        Host Ip: ", 
                     font=("Z003", 15))

    def _espIP_Label(self) -> Label:
        return Label(self, 
                     text="     ESP32 Ip: ", 
                     font=("Z003", 15))
    
    def _raspIP_Label(self) -> Label:
        return Label(self, 
                     text="Raspberry Ip: ", 
                     font=("Z003", 15))    
    
    # - Mostrar Ips correspondientes -#
    def _ip_host(self) -> Entry:
        return Entry(self, 
                     font=('consolas', 14),  
                     justify='left',
                     state='readonly',
                     width=40)
                     
    def _ip_esp_in(self) -> Entry:
        return Entry(self, 
                     font=('consolas', 14),  
                     justify='left',
                     state='readonly',
                     width=40)
    
    def _ip_rasp_in(self) -> Entry:
        return Entry(self, 
                     font=('consolas', 14),  
                     justify='left',
                     state='readonly',
                     width=40)

    # - ELEMENTOS VISUALES SERVIDOR - #
    def _Server_tag(self) -> Label:
        return Label(self, 
                     text="URL stream: ", 
                     font=("Z003", 15))
    
    def _server_url(self) -> Entry:
        return Entry(self, 
                     font=('consolas', 14),  
                     justify='left',
                     state='readonly',
                     width=40)
    
    # - Reinicamos valores - #
    def update_configs_connect(self):
        self.esp_ip.config(state='normal')
        self.rasp_ip.config(state='normal')
        self.server_URL.config(state='normal')
        self.host_ip.config(state='normal')
        
        # Insertar IP Local
        self.host_ip.delete(0, 'end')  # Borrar el contenido anterior
        self.host_ip.insert(0, ip)  # Insertar el nuevo mensaje
        self.host_ip.config(state='readonly')

        # Insertar en el ESP
        self.esp_ip.delete(0, 'end')  # Borrar el contenido anterior
        self.esp_ip.insert(0, ip_esp)  # Insertar el nuevo mensaje
        self.esp_ip.config(state='readonly')

        # Insertar en Rasp
        self.rasp_ip.delete(0, 'end')  # Borrar el contenido anterior
        self.rasp_ip.insert(0, ip_rasp)  # Insertar el nuevo mensaje
        self.rasp_ip.config(state='readonly')
        
        # Insertar en URL
        self.server_URL.delete(0, 'end')  # Borrar el contenido anterior
        self.server_URL.insert(0, server_stream)  # Insertar el nuevo mensaje
        self.server_URL.config(state='readonly')
    
    # -- CONFIG CONTROLS -- #
    def _controls_title_(self) -> Label:
        return Label(
            master=self,
            text='Joystick',
            foreground='black',
            font=("Z003", 15, "bold")
        )
    
    # - Etiquetado - #
    def _joy_name_(self) -> Label:
        return Label(self, 
                     text="         Name: ", 
                     font=("Z003", 15))
    
    def _joy_pc_id_(self) -> Label:
        return Label(self, 
                     text="     ID on PC: ", 
                     font=("Z003", 15))
        
    def _joy_power_(self) -> Label:
        return Label(self, 
                     text="       Power: ", 
                     font=("Z003", 15))
        
    def _joy_buttons_(self) -> Label:
        return Label(self, 
                     text="Total Buttons: ", 
                     font=("Z003", 15))
        
    def _joy_axes_(self) -> Label:
        return Label(self, 
                     text="   Total Axes: ", 
                     font=("Z003", 15))
        
    # - Valores - #
    def name_label(self) -> Entry:
        return Entry(self, 
                     font=('consolas', 14),  
                     justify='left',
                     state='readonly',
                     width=40)
    
    def id_label(self) -> Entry:
        return Entry(self, 
                     font=('consolas', 14),  
                     justify='left',
                     state='readonly',
                     width=40)
    
    def power_label(self) -> Entry:
        return Entry(self, 
                     font=('consolas', 14),  
                     justify='left',
                     state='readonly',
                     width=40)
    
    def buts_label(self) -> Entry:
        return Entry(self, 
                     font=('consolas', 14),  
                     justify='left',
                     state='readonly',
                     width=40)
        
    def axes_label(self) -> Entry:
        return Entry(self, 
                     font=('consolas', 14),  
                     justify='left',
                     state='readonly',
                     width=40)
    
    # - BOTONES - #
    def but_refresh(self) -> Button:
        return Button(self,
                      width=40,
                      command=self.get_joy_stats,
                      text='Refresh Control',
                      font=('Magneto', 15))
    
    def but_test(self) -> Button:
                return Button(self,
                      width=40,
                      command=self.run_test,
                      text='Test',
                      font=('Magneto', 15))
    
    # - OPERATIVO - #
    def get_joy_stats(self):
        joysticks = ps4.refresh_joys()
        
        # - Variables - #
        if not joysticks:
            name = 'No joystick'
            id = 'No joystick'
            power = 'No joystick'
            buttons = 'No joystick'
            axes = 'No joystick'
        
        elif len(joysticks) > 1:
            messagebox.showerror('Warning!!!','Only 1 controll support')
            
        else:
            name = ps4.get_pad_info(0,'name')
            id = ps4.get_pad_info(0,'id')
            power = ps4.get_pad_info(0,'power')
            buttons = ps4.get_pad_info(0,'buttons')
            axes = ps4.get_pad_info(0,'axes')
            
        # - Las aplicamos a nuestra app - #
        self.name.config(state='normal')
        self.id.config(state='normal')
        self.power.config(state='normal')
        self.buttons.config(state='normal')
        self.axes.config(state='normal')
        
        # Insertar Name
        self.name.delete(0, 'end')  # Borrar el contenido anterior
        self.name.insert(0, name)  # Insertar el nuevo mensaje
        self.name.config(state='readonly')

        # Insertar id
        self.id.delete(0, 'end')  # Borrar el contenido anterior
        self.id.insert(0, id)  # Insertar el nuevo mensaje
        self.id.config(state='readonly')

        # Insertar power
        self.power.delete(0, 'end')  # Borrar el contenido anterior
        self.power.insert(0, power)  # Insertar el nuevo mensaje
        self.power.config(state='readonly')
        
        # Insertar buttons
        self.buttons.delete(0, 'end')  # Borrar el contenido anterior
        self.buttons.insert(0, buttons)  # Insertar el nuevo mensaje
        self.buttons.config(state='readonly')
        
        # Insertar Axes
        self.axes.delete(0, 'end')  # Borrar el contenido anterior
        self.axes.insert(0, axes)  # Insertar el nuevo mensaje
        self.axes.config(state='readonly')
        
    def run_test(self):
        code_file = os.path.join(os.path.dirname(__file__), 'Control_test.py')
        try:
            subprocess.run([sys.executable, code_file])
        except Exception as e:
                messagebox.showerror('Error', f'Failed to start due to: {str(e)}')
           
# ---- Clase ventana de WebControl ---- #
class FrameWebControl(Frame):
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
    
        # - Creacion de objetos TKinter - #
        self.title: Label = self._Create_title()
        self.content: Label = self._content()
        
        # Creamos los objetos
        self.init_gui()
        
    # - Colocamos los elementos visuales - #
    def init_gui(self)-> None:
        self.title.grid(row=0, column=0, columnspan=2, padx=40)
        
        # Añadimos un Label en FrameOne usando grid()
        self.content.grid(row=1, column=0)
        
    # - Atributos y elementos de aplicacion - #
    # - TITULO - #
    def _Create_title(self) -> Label:
        return Label(
            master=self,
            text='Titulo Ventana Web Control',
            foreground='black',
            font=("Z003", 20, "bold")
        )
    
    def _content(self) -> Label:
        return Label(self, text="Contenido de la Pestaña 4 (Aqui se abrirar un dcontrol directo MQTT)")
    
# ---- Clase ventana de About ---- #
class FrameAbout(Frame):
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
    
        # - Creacion de objetos TKinter - #
        self.title: Label = self._Create_title()
        self.content: Label = self._content()
        
        # Creamos los objetos
        self.init_gui()
        
    # - Colocamos los elementos visuales - #
    def init_gui(self)-> None:
        self.title.grid(row=0, column=0, columnspan=2, padx=40)
        
        # Añadimos un Label en FrameOne usando grid()
        self.content.grid(row=1, column=0)
        
    # - Atributos y elementos de aplicacion - #
    # - TITULO - #
    def _Create_title(self) -> Label:
        return Label(
            master=self,
            text='About this software',
            foreground='black',
            font=("Z003", 20, "bold")
        )
    
    def _content(self) -> Label:
        return Label(self, text="Runing App Stable Version 0.2")
    
# ------------------------------------------------------ #
# -------------- Inicializacion de la app -------------- #
# ------------------------------------------------------ #
root = Tk()

if __name__ == '__main__':
    ex = App(root)
    root.mainloop()
    