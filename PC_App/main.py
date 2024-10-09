from tkinter import BOTH
from tkinter import RIGHT
from tkinter import LEFT
from tkinter import BOTTOM
from tkinter import X
from tkinter import Button
from tkinter import Frame
from tkinter import Label
from tkinter import messagebox
from tkinter import Tk
from tkinter import Canvas
from tkinter import PhotoImage
from tkinter import Entry
from tkinter import filedialog

from tkinter.ttk import Combobox
from tkinter.ttk import Notebook

import datetime as dt

import os

import cv2
import numpy as np
from PIL import Image, ImageTk

from MQTT_con.MQTT_ex import get_ip_Windows
from MQTT_con.MQTT_ex import mqtt_coms

"""
    Nota: En teoria ya no es encesario entrar a App.
    Puesto que todo se esta modificando dentro de 
    los respecitvos frames
"""
# -- VARIABLES GLOBALES -- #
# Ips
ip_rasp = ''
ip_esp = ''
ip = get_ip_Windows()

# Link servidor
server_stream = "http://192.168.252.18:8000/stream.mjpg"

# Mqtt client
mqtt_client = mqtt_coms(ip, 1883, "Rasp/CmdOut", "Rasp/CmdIn")
mqtt_client.start()

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
        self.parent.title('MAPI-Tenshi Control Software - V1.0')
        # Size del monitor
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        root.geometry(f'{screen_width-50}x{screen_height-50}')
        root.resizable(False, False)

        # -- Colocacion de widgets -- #
        self.pack(fill=BOTH, expand=True)

        # Colocamos el Notebook en la ventana
        self.notebook.pack(fill=BOTH, expand=True)
    
    def load_configuration(self):
        ip_rasp = self.tab3.get_rasp_ip()
        ip_esp = self.tab3.get_esp_ip()
        server_stream = self.tab3.get_URL()
        
    # - Creacion del Notebook con pestañas - #
    def _Create_notebook(self) -> Notebook:
        notebook = Notebook(self)
        
        # Creamos un frame simple para Tab 1
        self.tab1 = Frame(notebook)
        self.tab2 = FrameFiles(notebook)
        self.tab3 = FrameOptions(notebook)
        self.tab4 = FrameWebControl(notebook)
        self.tab5 = FrameAbout(notebook)
        # Agregamos las pestañas al Notebook
        notebook.add(self.tab1, text='Main')
        notebook.add(self.tab2, text='File')
        notebook.add(self.tab3, text='Options')
        notebook.add(self.tab4, text='Web Control')
        notebook.add(self.tab5, text='About')

        # - Atributos y elementos de aplicacion - #
        # - TITULO - #
        Label(self.tab1, text="Control Panel. Robot 01",
              foreground='black',
              font=("Magneto", 20, "bold")).grid(row=1, column=0, columnspan=2)
        """
        Interfaz Esperada:
        
            |   0    |      1        |
            --------------------------
          0 | mqtt   |   Raw Cam     |
            --------------------------
          1 | CMD    |   Pos Cam     |
            --------------------------
        """
        # Control MQTT
        frame_mqtt_control = Frame_Main_MQTT_Control(self.tab1)  # Instanciar el frame aquí
        frame_mqtt_control.grid(row=2, column=0)

        # Camara sin proceso
        frame_Raw_camera = Frame_Main_Raw_Camera(self.tab1)  # Instanciar el frame aquí
        frame_Raw_camera.grid(row=2, column=1)
        
        # Camara procesada
        frame_pros_camera = Frame_Main_Pros_Camera(self.tab1)
        frame_pros_camera.grid(row=3, column=1)
        
        # Command Prompt
        frame_CMD_promt = Frame_CMD(self.tab1)
        frame_CMD_promt.grid(row=4,column=0)
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
            text='UI de control del robot',
            foreground='black',
            font=("Z003", 20, "bold")
        )
    
    def _content(self) -> Label:
        return Label(self, text="Controlled by MQTT")
    
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
        self.but_objects: Button = self._but_save()
        
        # Creamos los objetos
        self.init_gui()
        
    # - Colocamos los elementos visuales - #
    def init_gui(self)-> None:
        self.title.grid(row=0, column=0, columnspan=3)
        
        # Colocamos los botones
        self.but_colors.grid(row=2, column=0, padx=10, pady=10)
        self.but_contours.grid(row=2, column=1, padx=10, pady=10)
        self.but_objects.grid(row=2, column=2, padx=10, pady=10)
        
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
                      width=10,
                      borderwidth=1,
                      command=self.detect_colors,
                      text='Colors',
                      font=('Magneto', 15))
    
    def _but_contors(self) -> Button:
        return Button(self,
                      width=10,
                      borderwidth=1,
                      command=self.detect_contorns,
                      text='Contorns',
                      font=('Magneto', 15))
    
    def _but_save(self) -> Button:
        return Button(self,
                      width=10,
                      borderwidth=1,
                      command=self.save_photo,
                      text='Save',
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
            
            cv2.imshow('Deteccion de contornos', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            
        cap.release()
        cv2.destroyAllWindows()
    
    def save_photo(self):
        cap = cv2.VideoCapture(self.stream_url)
    
        # Leer un solo frame
        ret, frame = cap.read()
    
        if ret:
            # Usar un cuadro de diálogo para seleccionar la ubicación y nombre del archivo
            file_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                     initialfile=f'image_{day}_{month}_{year}_at_{hour}_{minute}.png',
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
        self.content.grid(column=1,row=1)
        self.command.grid(column=2,row=1)
        self.send.grid(column=3,row=1,padx=5, rowspan=2)
        
        # - Recepcion de comandos - # 
        self.out.grid(column=1,row=2)
        self.cmd_out.grid(column=2,row=2)
        
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
        self.parent.after(1000, self.update_cmd_output)

# ----------------------------------- #
# -------- Frames de control -------- #
# ----------------------------------- #

# ---- Clase ventana de archivos ---- #
class FrameFiles(Frame):
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
            text='Titulo Ventana Archivo',
            foreground='black',
            font=("Z003", 20, "bold")
        )
    
    def _content(self) -> Label:
        return Label(self, text="Contenido de la Pestaña 2")
    
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
        
        self.host_ip: Label = self._ip_host()
        self.esp_ip: Label = self._ip_esp_in()
        self.rasp_ip: Label = self._ip_rasp_in()
        
        # - SERVER -#
        self.title_server: Label = self._Server_title()
        self.server_label: Label = self._Server_tag()
        self.server_URL: Entry = self._server_url()
        
        # Creamos los objetos
        self.init_gui()
        
    # - Colocamos los elementos visuales - #
    def init_gui(self)-> None:
        self.title.grid(row=0, column=0, columnspan=2)
        
        # - IP - #
        # - TItulos - #
        self.content.grid(row=1, column=0)
        self.HIP_label.grid(row=2, column=0)
        self.EsIP_label.grid(row=3, column=0)
        self.RasIP_label.grid(row=4, column=0)
        
        # - Entrys - #
        self.host_ip.grid(row=2,column=1)
        self.esp_ip.grid(row=3,column=1)
        self.rasp_ip.grid(row=4,column=1)
        
        # - SERVER - #
        self.title_server.grid(row=1,column=3)
        self.server_label.grid(row=2,column=3)
        self.server_URL.grid(row=2,column=4)

        
    # - Atributos y elementos de aplicacion - #
    # - TITULO - #
    def _Create_title(self) -> Label:
        return Label(
            master=self,
            text='Opciones',
            foreground='black',
            font=("Magneto", 20, "bold")
        )
    
    # - ELEMENTOS VISUALES IPS - #
    def _Ip_Opt_Label(self) -> Label:
        return Label(self, text="Ip Options", font=("Z003", 15, "bold"))
    
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
    def _ip_host(self) -> Label:
        return Label(self, 
                     text=ip,
                     justify='left',
                     font=("Z003", 15))
                     
    def _ip_esp_in(self) -> Label:
        return Label(self,
                     text='',
                     font=('Z003', 15),
                     width=30)
    
    def _ip_rasp_in(self) -> Label:
        return Label(self,
                     text='',
                     font=('Z003', 15),
                     width=30)

    # - ELEMENTOS VISUALES SERVIDOR - #
    def _Server_title(self) -> Label:
        return Label(self, text="Servidor", font=("Z003", 15, "bold"))
    
    def _Server_tag(self) -> Label:
        return Label(self, 
                     text="URL stream: ", 
                     font=("Z003", 15))
    
    def _server_url(self) -> Entry:
        return Entry(self, 
                     justify='left',
                     font=("Z003", 15),
                     width=30)
    
    
    # - ELEMENTOS OPERATIVOS - #        
    def get_URL(self):
        return self.esp_ip.get()

    def get_esp_ip(self):
        return self.esp_ip.get()
        
    def get_rasp_ip(self):
        return self.rasp_ip.get()

        
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
# http://192.168.252.18:8000/stream.mjpg
if __name__ == '__main__':
    #server_stream = input(f'Inserte link de stream')
    # Inicio de app
    ex = App(root)
    root.mainloop()
    