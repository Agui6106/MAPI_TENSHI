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

from tkinter.ttk import Combobox
from tkinter.ttk import Notebook

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

# Mqtt client
mqtt_client = mqtt_coms(ip, 1883, "Rasp/CmdOut", "Rasp/CmdIn")
mqtt_client.start()

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
        
    # - Creacion del Notebook con pestañas - #
    def _Create_notebook(self) -> Notebook:
        notebook = Notebook(self)
        
        # Creamos un frame simple para Tab 1
        tab1 = Frame(notebook)
        tab2 = FrameFiles(notebook)
        tab3 = FrameOptions(notebook)
        tab4 = FrameWebControl(notebook)
        tab5 = FrameAbout(notebook)
        # Agregamos las pestañas al Notebook
        notebook.add(tab1, text='Main')
        notebook.add(tab2, text='File')
        notebook.add(tab3, text='Options')
        notebook.add(tab4, text='Web Control')
        notebook.add(tab5, text='About')
        
        # - Atributos y elementos de aplicacion - #
        # - TITULO - #
        Label(tab1, text="Control Panel. Robot 01",
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
        frame_mqtt_control = Frame_Main_MQTT_Control(tab1)  # Instanciar el frame aquí
        frame_mqtt_control.grid(row=2, column=0)

        # Camara sin proceso
        frame_Raw_camera = Frame_Main_Raw_Camera(tab1)  # Instanciar el frame aquí
        frame_Raw_camera.grid(row=2, column=1)
        
        # Camara procesada
        frame_pros_camera = Frame_Main_Pros_Camera(tab1)
        frame_pros_camera.grid(row=3, column=1)
        
        # Command Prompt
        frame_CMD_promt = Frame_CMD(tab1)
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
            text='Camara sin procesar',
            foreground='black',
            font=("Z003", 20, "bold")
        )
    
    def _content(self) -> Label:
        return Label(self, text="Enviada desde el bot")

# -- Camara procesada -- #
class Frame_Main_Pros_Camera(Frame):
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
            text='Camara Procesada',
            foreground='black',
            font=("Z003", 20, "bold")
        )
    
    def _content(self) -> Label:
        return Label(self, text="La procesamos localemtne")
    
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
        
        # - Actualizamos la respuesta - #
        self.update_cmd_output()
        
        # Creamos los objetos
        self.init_gui()
        
    # - Colocamos los elementos visuales - #
    def init_gui(self)-> None:
        self.title.grid(column=1,row=0,columnspan=3)
        
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
                     width=70)
        
    def _comman_send_button(self) -> Button:
        return Button(self,
                      width=10,
                      background='black',
                      foreground='green',
                      borderwidth=1,
                      command=self.send_command,
                      text='Send',
                      font=('Magneto', 15))
    
    # - Operativo - #
    def send_command(self):
        cmd_in = self.command.get()
        # - Envio - #
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
                     width=70)
    
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
        
        espi = ''
        raspi = ''
    
        # - Creacion de objetos TKinter - #
        self.title: Label = self._Create_title()
        
        self.content: Label = self._Ip_Opt_Label()
        self.HIP_label: Label = self._hostIP_Label()
        self.EsIP_label: Label = self._espIP_Label()
        self.RasIP_label: Label = self._raspIP_Label()
        
        self.host_ip: Label = self._ip_host()
        self.esp_ip: Label = self._ip_esp_in()
        self.rasp_ip: Label = self._ip_rasp_in()
        
        self.esp_ok: Button = self._ok_button_esp()
        self.rasp_ok: Button = self._ok_button_ras()
        
        # Creamos los objetos
        self.init_gui()
        
    # - Colocamos los elementos visuales - #
    def init_gui(self)-> None:
        self.title.grid(row=0, column=0, columnspan=2)

        # - TItulos - #
        self.content.grid(row=1, column=0)
        self.HIP_label.grid(row=2, column=0)
        self.EsIP_label.grid(row=3, column=0)
        self.RasIP_label.grid(row=4, column=0)
        
        # - Labels - #
        self.host_ip.grid(row=2,column=1)
        self.esp_ip.grid(row=3,column=1)
        self.rasp_ip.grid(row=4,column=1)
        
        # - Butons - #
        self.esp_ok.grid(row=3,column=2)
        self.rasp_ok.grid(row=4,column=2)
        
        
    # - Atributos y elementos de aplicacion - #
    # - TITULO - #
    def _Create_title(self) -> Label:
        return Label(
            master=self,
            text='Opciones',
            foreground='black',
            font=("Magneto", 20, "bold")
        )
    
    # - ELEMENTOS VISUALES - #
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
                     
    def _ip_esp_in(self) -> Entry:
        return Entry(self,
                     font=('Z003', 15),
                     width=30)
    
    def _ip_rasp_in(self) -> Entry:
        return Entry(self,
                     font=('Z003', 15),
                     width=30)

    def _ok_button_esp(self) -> Button:
        return Button(self,
                      text='Save',
                      font=('Z003', 15),
                      command= self.get_esp_ip()
                      )
    
    def _ok_button_ras(self) -> Button:
        return Button(self,
                      text='Save',
                      font=('Z003', 15),
                      command= self.get_rasp_ip()
                      )
    
    # - ELEMENTOS OPERATIVOS - #
    def get_esp_ip(self) -> None:
        return self.esp_ip.get()
        
    def get_rasp_ip(self) -> None:
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

if __name__ == '__main__':
    # Inicio de app
    ex = App(root)
    root.mainloop()
    