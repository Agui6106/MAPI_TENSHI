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
from tkinter import Text

from tkinter.ttk import Notebook

import datetime as dt
import webbrowser

import psutil
import os

# - Imagen de stream - #
import cv2
import numpy as np
from PIL import Image, ImageTk

# - Proccesado de imnagen - #
import mediapipe as mp 

# - MQTT - #
from MQTT_con.MQTT_ex import get_ip_Windows
from MQTT_con.MQTT_ex import mqtt_coms

# - PS4 CONTROLLER - #
import controls.ps4_control as ps4

# IP Local
ip = get_ip_Windows()

# - Ventan de configuracion inicial - #
def open_config_window():
    # -- VARIABLES GLOBALES -- #
    def save_config():
        global ip_rasp, ip_esp, ip, server_stream, ID_bot
        ip_rasp = entry_ip_rasp.get()
        ip_esp = entry_ip_esp.get()
        server_stream = entry_server_stream.get()
        ID_bot = entry_Robot_ID.get()
        if ip_rasp == '':
            ip_rasp = '0.0.0.1'
            messagebox.showwarning("Input Empty on IP Raspberry", "No selected values. Default selected")
            
        if ip_esp == '':
            ip_esp = '0.0.0.2'
            messagebox.showwarning("Input Empty on IP ESP", "No selected values. Default selected")
            
        if ID_bot == '' :
            ID_bot = '01'
            messagebox.showwarning("Input Empty on Robot ID", "No selected values. Default selected")
            
        if server_stream == '':
            server_stream = 'https://server-example.com'
            messagebox.showwarning("Input Empty on Stream URL", "No selected values. Default selected")
        
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

# -- MQTT TOPICS -- #
# - RASP - #
# Mqtt client Raspberry(ipbroker, puerto, suscribcion, publica)
mqtt_client = mqtt_coms(ip, 1883, "Rasp/CmdOut", "Rasp/CmdIn")
mqtt_client.start()

# - ESP32 - #
# -- SERVO -- #
mqtt_esp_Servo = mqtt_coms(ip, 1883, 'ESP/Response', 'ESP/Servo')
mqtt_esp_Servo.start()

# -- SENSORS AND MAIN MOTORS -- #
mqtt_esp_Data = mqtt_coms(ip, 1883, 'ESP/Sensors', 'ESP/Motors')
mqtt_esp_Data.start()

# -- PERIFERICOS -- #
mqtt_esp_Perif = mqtt_coms(ip, 1883, 'ESP/Lamp/Buzz', 'ESP/Perifericals')
mqtt_esp_Perif.start()

# -- GIROSCOPIO Y GPS -- #
mqtt_esp_Locations = mqtt_coms(ip, 1883, 'ESP/Lat/Long/GX/GY', 'PC/Response')
mqtt_esp_Locations.start()

# - FECHA DE HOY - #
date = dt.datetime.now()
        
year = date.year
month = date.month
day = date.day

hour = date.hour
minute = date.minute
segs = date.second

# - Clase Principal Aplicacion - #
class App(Frame):
    """
    Frame principal para la colocacion de elementos secundarios
    """
    def __init__(self, parent, *args, **kwargs):       
        Frame.__init__(self, parent, *args, **kwargs)
        self.parent: Tk = parent

        # - Creacion de Notebook (pestañas) - #
        self.notebook = self._Create_notebook()
        
        # - Creacion de los objetos - #
        self.init_gui()
    
    # - Colocamos los elementos visuales - #
    def init_gui(self)-> None:
        """
        Inicializacion de elementos y colocacion
        """
        # -- Propiedades de la App principal -- #
        self.parent.title(f'MAPI-Tenshi Control Panel - V1.0. on Robot ID: {ID_bot} with IP: {ip_rasp}')
        # Size del monitor
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        root.geometry(f'{screen_width-30}x{screen_height-140}')
        root.resizable(False, False)

        # -- Colocacion de widgets -- #
        self.pack(fill=BOTH, expand=True)

        # Colocamos el Notebook en la ventana
        self.notebook.pack(fill=BOTH, expand=True)
    
    # - Creacion del Notebook con pestañas - #
    def _Create_notebook(self) -> Notebook:
        """
        Menu de seleccion de pesatnas secundarias
        """
        notebook = Notebook(self)
        
        # Creamos un frame simple para Tab 1
        self.tab1 = Frame(notebook)
        self.tab3 = FrameOptions(notebook)
        # Agregamos las pestañas al Notebook
        notebook.add(self.tab1, text='Main')
        notebook.add(self.tab3, text='Options')

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
        frame_mqtt_control.grid(row=1, column=0, rowspan=2, sticky='nsew')

        # Camara sin proceso
        frame_Raw_camera = Frame_Main_Raw_Camera(self.tab1)  # Instanciar el frame aquí
        frame_Raw_camera.grid(row=1, column=1, sticky='nsew')
        
        # Camara procesada
        frame_pros_camera = Frame_Main_Pros_Camera(self.tab1)
        frame_pros_camera.grid(row=2, column=1, sticky='nsew')
        
        return notebook

# ----------------------------------- #
# --------- Frames de MAIN ---------- #
# ----------------------------------- #

# -- Control por mqtt -- #
class Frame_Main_MQTT_Control(Frame):
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        
        # - Imagenes de direccion - #
        # Arriba
        GUp= os.path.join(os.path.dirname(__file__), './sprites/Directions/Up.png')
        self.GUp = PhotoImage(file=GUp)
        # Abajo
        GDown= os.path.join(os.path.dirname(__file__), './sprites/Directions/Down.png')
        self.GDown = PhotoImage(file=GDown)
        # Izquierda
        GLeft= os.path.join(os.path.dirname(__file__), './sprites/Directions/Left.png')
        self.GLeft = PhotoImage(file=GLeft)
        # Derecha
        GRight= os.path.join(os.path.dirname(__file__), './sprites/Directions/Right.png')
        self.GRight = PhotoImage(file=GRight)
        # Quieto
        Still= os.path.join(os.path.dirname(__file__), './sprites/Directions/Still.png')
        self.Still = PhotoImage(file=Still)
    
        # - Creacion de objetos TKinter - #
        self.title: Label = self._Create_title()
        # SubFrames
        self.vital_Data_frame: LabelFrame = self._create_VitalData()
        self.positions_frame: LabelFrame = self._create_Pos()
        self.recv_data_frame: LabelFrame = self._create_Data()
        
        # -- VITAL-DATA ELEMENTS -- #
        # - TITULOS - #
        self.Motors_title = Label(self.vital_Data_frame, text="Main Motors", font=('Z003', 15, 'bold'))
        self.servo_title = Label(self.vital_Data_frame, text="Camera angle", font=('Z003', 15, 'bold'))
        self.perifercials_title = Label(self.vital_Data_frame, text="Peripherals", font=('Z003', 15, 'bold'))
        self.status_label = Label(self.vital_Data_frame, text="Status", font=('Z003', 15, 'bold'))
        self.buz_on_label = Label(self.vital_Data_frame, text="Off", font=('Z003', 15, 'bold'), foreground='red')
        self.lamp_on_label = Label(self.vital_Data_frame, text="Off", font=('Z003', 15, 'bold'), foreground='red')
        
        # - MOTORES - #
        self.direction = Canvas(self.vital_Data_frame, width=180, height=80,bg='black')
        self.direction.create_image((0,0),image=self.Still, anchor='nw')
        
        # - PERIFERICOS - #
        self.cam_scale: Scale = self._create_joystick_slider()
        self.buz_but: Button = self._button_Buz()
        self.lamp_but: Button = self._button_lamp()
        
        # - STATUS - #
        self.statuts1_label = Label(self.vital_Data_frame, text=" Motors", font=('Z003', 13))
        self.statuts2_label = Label(self.vital_Data_frame, text="Battery", font=('Z003', 13))
        self.statuts3_label = Label(self.vital_Data_frame, text=" Serial", font=('Z003', 13))
        self.statuts4_label = Label(self.vital_Data_frame, text="  MQTT ", font=('Z003', 13))
        self.status1: Button = self.stat_1()
        self.status2: Button = self.stat_2()
        self.status3: Button = self.stat_3()
        self.status4: Button = self.stat_4()
        
        # -- POSITIONS ELEMENTS -- #
        # - GIROSCOPIO - #
        self.X_Label = Label(self.positions_frame, text="X:", font=('Z003', 15, 'bold'))
        self.Y_Label = Label(self.positions_frame, text="Y:", font=('Z003', 15, 'bold'))
        self.X_Data = Label(self.positions_frame, text="00000", font=('Z003', 15,))
        self.Y_Data = Label(self.positions_frame,  text="00000", font=('Z003', 15,))
        
        # - GPS - #
        self.Latitud_Label = Label(self.positions_frame,  text=" Latitude:", font=('Z003', 15, 'bold'))
        self.Longitud_Label = Label(self.positions_frame, text="Longitude:", font=('Z003', 15, 'bold'))
        self.Latitud_Data = Label(self.positions_frame, text="000.000", font=('Z003', 15,))
        self.Longitud_Data = Label(self.positions_frame, text="000.000", font=('Z003', 15,))
        
        # - ACCIONES - #
        self.Google_maps_But: Button = self.launch_GM_Butt()
        self.empty_space_positions = Label(self.positions_frame, text=" ", font=('Z003', 15, 'bold'))
        self.empty_space_recv = Label(self.recv_data_frame, text=" ", font=('Z003', 15, 'bold'))
        self.empty_space_recv2 = Label(self.recv_data_frame, text=" ", font=('Z003', 15, 'bold'))
        self.empty_space_recv3 = Label(self.recv_data_frame, text=" ", font=('Z003', 15, 'bold'))
        self.empty_space_recv4 = Label(self.recv_data_frame, text=" ", font=('Z003', 15, 'bold'))
        
        # -- DATA ELEMENTS -- #
        # Titulos
        self.dist_front_title = Label(self.recv_data_frame, text="Frontal ", font=('Z003', 15, 'bold'))
        self.dist_back_title = Label(self.recv_data_frame, text="Back", font=('Z003', 15, 'bold'))
        self.sensors_title = Label(self.recv_data_frame, text="Sensors", font=('Z003', 15, 'bold'))
        
        # Sensores distancias
        self.frontal_Ultr: Label = self.ultr_label()
        self.frontal_Infr: Label = self.infr_label()
        
        self.back_Ultr: Label = self.ultr_label()
        self.back_Infr: Label = self.infr_label()
        
        # Sensores generales
        self.temp_label = Label(self.recv_data_frame, text="Temperature:", font=('Z003', 15, 'bold'))
        self.Hum_label = Label(self.recv_data_frame,  text="   Humidity:", font=('Z003', 15, 'bold'))
        self.Gas_label = Label(self.recv_data_frame,  text="        Gas:", font=('Z003', 15, 'bold'))
        self.gas_levels: Label = self.data_label()
        
        self.data_temp: Label = self.data_label()
        self.data_Hum: Label = self.data_label()
        self.data_Dist_InfrF: Label = self.data_label()
        self.data_Dist_UltrF: Label = self.data_label()
        self.data_Dist_InfrB: Label = self.data_label()
        self.data_Dist_UltrB: Label = self.data_label()
        
        # - INFORMATION - #
        self.important_info_msg = Text(self, foreground='black',
                                        font=('consolas', 14), 
                                        width=85,height=6, state='disabled')
        
        #texto = f'# --------------------------------------------------------------------------------- #'
        texto = f'# --------------------------- Mappi - Tenshi Robot info --------------------------- #'
        
        self.important_info_msg.config(state='normal')
        self.important_info_msg.insert('1.0', texto)
        self.important_info_msg.config(state='disabled')
        
        # - MQTT - #
        self.get_response()
        # - Obtenemos lso valores del control - #        
        self.update_vals()       
        
        # - Creacion de elementos visuales -#
        self.init_main_gui()
        self.init_gui_of_VitalData()
        self.init_gui_of_Positions()
        self.init_gui_of_RecvData()
        
    # - Colocamos los elementos visuales - #
    def init_main_gui(self)-> None:
        self.title.grid(row=0, column=0,)

        # - LABEL FRAMES -#
        self.vital_Data_frame.grid(row=1, column=0,  sticky="nsew", ipadx=10, pady=10) # 10x3
        self.recv_data_frame.grid(row=2, column=0,  sticky="nsew", )
        self.positions_frame.grid(row=3, column=0,  sticky="nsew", ) # 7x2
        #self.importnat_info.grid(row=4, column=0, )
        self.important_info_msg.grid(row=4, column=0, pady=4)
        
    def init_gui_of_VitalData(self) -> None:
        # - CONTENTS VITAL- #
        # Ttitulos
        self.Motors_title.grid(row=0, column=0,columnspan=2,)
        self.servo_title.grid(row=0,column=2,columnspan=2)
        self.perifercials_title.grid(row=0,column=4,columnspan=2)
        self.status_label.grid(row=0,column=6,columnspan=4)
        
        # Elementos Motor
        self.direction.grid(row=1,column=0, columnspan=2, rowspan=2)
        
        # Servo
        self.cam_scale.grid(row=1,column=2,columnspan=2,padx=5)
        
        # Perifericos
        self.buz_but.grid(row=1,column=4, padx=10)
        self.lamp_but.grid(row=2,column=4, padx=10, pady=5)
        self.buz_on_label.grid(row=1,column=5, padx=3)
        self.lamp_on_label.grid(row=2,column=5, padx=3)
        
        # Status
        self.statuts1_label.grid(row=2,column=6, padx=10)
        
        self.status1.grid(row=1,column=8, padx=10)
        self.status2.grid(row=1,column=7, padx=10)
        self.status3.grid(row=1,column=6, padx=10)
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
        self.empty_space_positions.grid(row=1, column=0, padx=20)
        # Giroscopio
        self.X_Label.grid(row=1, column=1, pady=5, ipadx=15)
        self.Y_Label.grid(row=2, column=1, pady=5)
        
        self.X_Data.grid(row=1,column=2, )
        self.Y_Data.grid(row=2,column=2, )
        
        # Coordenadas
        self.Latitud_Label.grid(row=1, column=3, )
        self.Longitud_Label.grid(row=2,column=3, )
        
        self.Latitud_Data.grid(row=1,column=4, columnspan=2)
        self.Longitud_Data.grid(row=2,column=4, columnspan=2)
        
        self.Google_maps_But.grid(row=1,column=6, padx=20)
        
    def init_gui_of_RecvData(self) -> None:
        # - CONTENTS DATA - #
        self.empty_space_recv.grid(row=0,column=0, padx=45)
        #self.empty_space_recv2.grid(row=0,column=10, padx=15)
        self.empty_space_recv3.grid(row=0,column=3, padx=17)
        self.empty_space_recv4.grid(row=0,column=7, padx=17)
        # Titulos
        self.dist_front_title.grid(row=0, column=1, columnspan=2,)
        self.dist_back_title.grid(row=0, column=4, columnspan=2,)
        self.sensors_title.grid(row=0, column=8, columnspan=2, )
        
        # Etiquetas
        self.frontal_Ultr.grid(row=1, column=1, pady=10,)
        self.frontal_Infr.grid(row=2, column=1, )
        
        self.back_Ultr.grid(row=1,column=4)
        self.back_Infr.grid(row=2,column=4)
        
        self.temp_label.grid(row=1,column=8,)
        self.Hum_label.grid(row=2,column=8)
        self.Gas_label.grid(row=3,column=8, pady=10)
        
        # Data
        self.data_Dist_UltrF.grid(row=1, column=2)
        self.data_Dist_InfrF.grid(row=2, column=2)
        self.data_Dist_UltrB.grid(row=1,column=5)
        self.data_Dist_InfrB.grid(row=2,column=5)
        
        self.data_temp.grid(row=1,column=9)
        self.data_Hum.grid(row=2,column=9)
        
        self.gas_levels.grid(row=3,column=9)
        
    # - Atributos y elementos de aplicacion - #
    # - TITULO - #
    def _Create_title(self) -> Label:
        return Label(
            master=self,
            text='Robot Control and Data',
            foreground='black',
            font=("Z003", 20, "bold")
        )
    
    # - Sub Frames -#
    def _create_VitalData(self) -> LabelFrame:
        return LabelFrame(
            self,
            text="Vital Data",
            font=("Z003", 17, 'bold'),
            
        )
    def _create_Pos(self) -> LabelFrame:
        return LabelFrame(
            self,
            text="Actual Positions",
            font=("Z003", 17, 'bold'),
        )
    def _create_Data(self) -> LabelFrame:
        return LabelFrame(
            self,
            text="General Data",
            font=("Z003", 17, 'bold'),
            
        )
    
    # - CONTENIDOS SUBFRAMES - #
    # - Vital Data - #
    # Slider
    def _create_joystick_slider(self) -> Scale:
        return Scale(self.vital_Data_frame, from_=-1, to=1, 
                     resolution=0.01, orient='horizontal',sliderlength=20, length=200)
    
    # Perifericos
    def _button_Buz(self) -> Button:
        return Button(self.vital_Data_frame, 
                      font=('Z003', 13, 'bold'), text="Lamp",width=7,
                      command=self.send_buttons_info(topic='Buzzer'))
    def _button_lamp(self) -> Button:
        return Button(self.vital_Data_frame, 
                      font=('Z003', 13, 'bold'), text="Buzzer",width=7,
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
        return Button(self.positions_frame, width=35,
                      font=('Z003', 15, 'bold'), text="Open on Google Maps",
                      command=self.get_and_launch_MAPS)
    # Obtener las coordenadas en google maps
    def get_and_launch_MAPS(self):
        pass
    
    # - Data - #    
    def ultr_label(self) -> Label:
        return Label(self.recv_data_frame, text=" Distance:", font=('Z003', 15, 'bold'))
    def infr_label(self) -> Label:
        return Label(self.recv_data_frame, text="Collision:", font=('Z003', 15, 'bold'))
    def data_label(self) -> Label:
        return Label(self.recv_data_frame, text="0000", font=('Z003', 15,))
    
    # -- OPERATIVO -- #
    def update_vals(self):        
        # Verificamos que haya un control Conectado
        if not ps4.check_ps4_connection():
            pass        
        else:
            # Obtenemos los valores y redondeamos los necesarios
            controller_state = ps4.get_controller_state()
            # Redondeamos los valores de los ejes necesarios
            xl = round(controller_state['axes'].get('xL', 0), 2)
            yl = round(controller_state['axes'].get('yL', 0), 2)
            xr = round(controller_state['axes'].get('xR', 0), 2)
            yr = round(controller_state['axes'].get('yR', 0), 2)
        
            # Obtenemos los valores del control y enviamos x MQTT
            self.cam_scale.set(xr)
            # Hacia Abajo
            if yl >= 0.25:
                self.direction.create_image((0,0),image=self.GDown, anchor='nw')
                try:
                    mqtt_esp_Data.publish_message('Down')
                except Exception as e:
                    print(f"Failed to send info due to: {e}")
            
            # Hacia Arriba
            if yl <= -0.25:
                self.direction.create_image((0,0),image=self.GUp, anchor='nw')
                try:
                    mqtt_esp_Data.publish_message('Up')
                except Exception as e:
                    print(f"Failed to send info due to: {e}")
            
            # Derecha
            if xl >= 0.25:
                self.direction.create_image((0,0),image=self.GRight, anchor='nw')
                try:
                    mqtt_esp_Data.publish_message('Right')
                except Exception as e:
                    print(f"Failed to send info due to: {e}")
            
            # Izquierda
            if xl <= -0.25:
                self.direction.create_image((0,0),image=self.GLeft, anchor='nw')
                try:
                    mqtt_esp_Data.publish_message('Left')
                except Exception as e:
                    print(f"Failed to send info due to: {e}")
            
            # Sin Movimiento
            """if xl == 0 and yl == 0:
                self.direction.create_image((0,0),image=self.Still, anchor='nw')
                try:
                    mqtt_esp_Data.publish_message('Left')
                except Exception as e:
                    print(f"Failed to send info due to: {e}")"""
            
            #self.motorX_data.config(text=xl)
            
            # Chequear botones específicos y enviar info por MQTT
            buttons = controller_state['buttons']
            if buttons.get('X', 0):  # Por ejemplo, 'X' activa la lámpara
                self.send_buttons_info('Lamp')
            if buttons.get('O', 0):  # 'O' activa el buzzer
                self.send_buttons_info('Buzzer')
            
            # Llamada recursiva para actualizar cada 50ms
            self.after(50, self.update_vals)
            
    # - MQTT PROTOCOL - #     
    # Envio       
    def send_buttons_info(self, topic):
        try:
            if topic == 'Lamp':
                mqtt_esp_Perif.publish_message('lamp')
            elif topic == 'Buzzer':
                pass
                #mqtt_esp_Buzzer.publish_message('buzz')
        except Exception as e:
            print(f"Failed to send info due to: {e}")
    
    # Recepcion        
    def get_response(self):
        # Perifericos
        self.mensaje_Perifs = mqtt_esp_Perif.last_message

        # Giroscopio y Coordenadas
        self.mensaje_Locations = mqtt_esp_Locations.last_message
        
        # Respuesta del ESP
        self.response = mqtt_esp_Servo.last_message
        # Sensores del ESP
        self.response_Data = mqtt_esp_Data.last_message
        
        # -- DATA -- #
        if self.response_Data:
            value = self.response_Data.split(",")
            # Sensores de temperatura y ultrasonico
            self.data_temp.config(text=value[0])
            self.data_Hum.config(text=value[1])
            self.data_Dist_UltrF.config(text=value[2])
            self.data_Dist_UltrB.config(text=value[3])
            # verifciamos colision 1
            if value[4] == 'collision':
                self.data_Dist_InfrF.config(text='Danger', foreground='red')
            if value[4] == 'clear':
                self.data_Dist_InfrF.config(text='Safe', foreground='Green')
            # Verificamos colision 2
            if value[5] == 'collision':
                self.data_Dist_InfrB.config(text='Danger', foreground='red')
            if value[5] == 'clear':
                self.data_Dist_InfrB.config(text='Safe', foreground='Green')
            
            # Giroscopios
            self.X_Data.config(text=value[6])
            self.Y_Data.config(text=value[7])
            
            # Coordenadas
            self.Latitud_Data.config(text=value[9])
            self.Longitud_Data.config(text=value[10])
            
        # Verificar respuesta en lampara
        if self.mensaje_Perifs:
            if self.mensaje_Perifs == 'LPOn':
                self.buz_on_label.config(text='On', foreground='green')
            elif self.mensaje_Perifs == 'LPOff':
                self.lamp_on_label.config(text='Off',foreground='red')
            
        # Lectura de los valores del giroscopio
        if self.mensaje_Locations:
            self.X_Data.config(text=self.mensaje_Locations)
            
        self.parent.after(500, self.get_response)
            
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
        self.but_colors.grid(row=1, column=0, padx=10, pady=5,)
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
                      width=24,
                      borderwidth=1,
                      command=self.detect_colors,
                      text='Colors',
                      font=('Z003', 15, 'bold'))
    
    def _but_contors(self) -> Button:
        return Button(self,
                      width=24,
                      borderwidth=1,
                      command=self.detect_contorns,
                      text='Contorns',
                      font=('Z003', 15, 'bold'))
    
    def _but_save(self) -> Button:
        return Button(self,
                      width=24,
                      borderwidth=1,
                      command=self.save_photo,
                      text='Save',
                      font=('Z003', 15, 'bold'))
        
    def _but_faces(self) -> Button:
        return Button(self,
                      width=24,
                      borderwidth=1,
                      command=self.face_detect,
                      text='Faces',
                      font=('Z003', 15, 'bold'))
        
    # -- OPERATIVO -- #
    # Colores 
    def detect_colors(self):
        # Crear ventana de OpenCV
        cap = cv2.VideoCapture(self.stream_url)
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
        
        cv2.namedWindow('Contorns detection')
        
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
            
            cv2.imshow('Contorns detection', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            
        cap.release()
        cv2.destroyAllWindows()
    
    # Deteccion de rsotros
    def face_detect(self):
        """
        Originally scripted by: Gabriela Solano
        """
        # Modelo de dibujo y deteccion de rostros
        mp_face_detection = mp.solutions.face_detection
        mp_drawing = mp.solutions.drawing_utils

        # Toma de captrua de stream
        cap = cv2.VideoCapture(self.stream_url)

        # Todos los resultados mayores a 50% de asertividad
        with mp_face_detection.FaceDetection(
            min_detection_confidence=0.5) as face_detection:

            # Leemos el stream
            while True:
                ret, frame = cap.read()
                if ret == False:
                    break
                #frame = imutils.resize(frame, width=720)
                frame = cv2.flip(frame, 1)
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)        

                results = face_detection.process(frame_rgb)

                # Dibujamos en la imagen los resultados
                if results.detections is not None:
                    for detection in results.detections:
                        mp_drawing.draw_detection(frame, detection,
                            mp_drawing.DrawingSpec(color=(0, 255, 255), circle_radius=2),
                            mp_drawing.DrawingSpec(color=(255, 0, 255)))

                cv2.imshow("Frame", frame)
                # Cerramos la ventana
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        cap.release()
        cv2.destroyAllWindows()
        
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
        self.out: Label = self._out_label()
        self.send: Button = self._comman_send_button()
        self.cmd_out: Entry = self._command_output()
        self.command: Entry = self._commands()
        
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
                     width=60)
        
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
                     width=60)
    
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
        self.notebook_set = self._create_settings_Notebook()
        
        # - IPs - #
        self.content =     Label(self, text="Actual IPs", font=("Z003", 15, "bold"))
        self.HIP_label =   Label(self, text="        Host Ip: ", font=("Z003", 15))
        self.EsIP_label =  Label(self, text="     ESP32 Ip: ", font=("Z003", 15))
        self.RasIP_label = Label(self, text="Raspberry Ip: ", font=("Z003", 15))    
        
        self.host_ip: Entry = self.options_entry()
        self.esp_ip: Entry = self.options_entry()
        self.rasp_ip: Entry = self.options_entry()
        
        # - SERVER -#
        self.server_label = Label(self, text="URL stream: ", font=("Z003", 15))
        self.server_URL: Entry = self.options_entry()
        
        # - D-PAD - #
        self.title_joys = Label(master=self, text='Joystick', foreground='black', font=("Z003", 15, "bold"))
        
        self.lable_name =    Label(self, text="         Name: ", font=("Z003", 15))
        self.lable_id =      Label(self, text="     ID on PC: ", font=("Z003", 15))
        self.lable_power =   Label(self, text="       Power: ", font=("Z003", 15))
        self.lable_buttons = Label(self, text="Total Buttons: ", font=("Z003", 15))
        self.lable_axes =    Label(self, text="   Total Axes: ", font=("Z003", 15))
        
        self.name: Entry = self.options_entry()
        self.id: Entry = self.options_entry()
        self.power: Entry = self.options_entry()
        self.buttons: Entry = self.options_entry()
        self.axes: Entry = self.options_entry()
        
        self.actions_label = Label(self, text="Quick Actions", font=("Magneto", 20, "bold"))
        self.joys_updated: Button = self.but_refresh()
        self.dev_button: Button = self._button_Open_Dev()
        self.TSP_Button: Button = self._button_Open_TSP()
        
        # Command Prompt
        self.frame_CMD_promt = Frame_CMD(self)
        self.frame_CMD_promt.config(bg='black')
        
        # Creamos los objetos
        self.init_gui()
        self.update_configs_connect()
        self.get_joy_stats()
        
    # - Colocamos los elementos visuales - #
    def init_gui(self)-> None:
        # - JOYSTICKS AND NETWORK - #
        self.title.grid(row=0, column=0, columnspan=2)
        self.notebook_set.grid(row=0,column=2, rowspan=15,padx=20, pady=10 ,sticky='nsew')
        
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
        self.actions_label.grid(row=13, column=0, columnspan=2, pady=3)
        self.joys_updated.grid(row=14, column=0, columnspan=2, pady=3)
        self.dev_button.grid(row=15,column=0,columnspan=2, pady=3)
        self.TSP_Button.grid(row=16,column=0, columnspan=2, pady=3)
        
        self.frame_CMD_promt.grid(row=15,column=2, rowspan=2, padx=20, sticky='nsew')
        
        # - INFO AND HELP - #
    
    # - JOYSTICKS AND NETWORK - #
    # - VISUALS - #
    # - TITULO - #
    def _Create_title(self) -> Label:
        return Label(
            master=self,
            text='Connectivity',
            foreground='black',
            font=("Magneto", 20, "bold")
        )
    
    # - Notebook - #
    def _create_settings_Notebook(self):
        # Creación del Notebook y sus pestañas
        notebook = Notebook(self)
        tab1 = Frame(notebook)
        tab2 = Frame(notebook)
        notebook.add(tab1, text='Help')
        notebook.add(tab2, text='About')
        
        # ---------- TAB 1 ---------- #
        # - Titulos - #
        Label(tab1, text="Commands", foreground='black', 
              font=("Magneto", 20, "bold"), justify='left',).grid(row=0, column=0, padx=15,)
        
        # - Text - #
        commands = Text(tab1, width=90,height=19,
                        font=('consolas', 14), state='disabled' )

        commands.grid(row=1,column=0, padx=15)
        
        # ---------- TAB 2 ---------- #
        Label(tab2, text="About us", foreground='black', 
              font=("Magneto", 20, "bold")).grid(row=0, column=0, 
                                                 columnspan=2, padx=15)
        
        about = Text(tab2, width=90,height=19,
                        font=('consolas', 14), state='disabled' )
        about.grid(row=1,column=0, padx=15)

        # Lee el contenido para commands
        file_commands= os.path.join(os.path.dirname(__file__), './sprites/commands.txt')
        commands.config(state='normal')
        try:
            with open(file_commands, "r") as archivo:
                contenido = archivo.read()
                # Inserta el contenido en el Text
                commands.delete("1.0", 'end')  # Limpia el Text antes de insertar texto
                commands.insert('end', contenido)
        except FileNotFoundError:
            commands.insert('end', "Archivo no encontrado.")
        
        commands.config(state='disabled')
        
        # Lee el contenido para about us

        
        return notebook 
    
    # - Valores - #
    def options_entry(self) -> Entry:
        return Entry(self, 
                     font=('consolas', 14),  
                     justify='left',
                     state='readonly',
                     width=40)
    
    # - OPERATIVO - #
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
    
    # - BOTONES - #
    def but_refresh(self) -> Button:
        return Button(self,
                      width=40,
                      command=self.get_joy_stats,
                      text='Refresh Control',
                      font=('Z003', 15, 'bold'))
    # - Obtenemos los valores del control - #
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
    
    # - Open web debugger - #
    def _button_Open_Dev(self) -> Button:
        return Button(self, 
                      text='Open Web Debugger', 
                      font=("Z003", 15, 'bold'),
                      width=40,
                      command= self.open_debugger)
    # - Abrimos el navegador - #
    def open_debugger(self):
        nav1 = webbrowser.get()
        nav1.open(f"http://{ip}:1880/ui")
        
    # - Open ThingSpeak - #
    def _button_Open_TSP(self) -> Button:
        return Button(self, 
                  text='Open ThingSpeak', 
                  font=("Z003", 15, 'bold'),
                  width=40,
                  command= self.open_TSP)
    # - Abrimos el navegador - #
    def open_TSP(self):
        nav1 = webbrowser.get()
        nav1.open('https://thingspeak.mathworks.com/channels/2739749')
           
# ------------------------------------------------------ #
# -------------- Inicializacion de la app -------------- #
# ------------------------------------------------------ #
root = Tk()

if __name__ == '__main__':
    ex = App(root)
    root.mainloop()
    