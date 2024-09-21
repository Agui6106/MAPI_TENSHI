from tkinter import *
from tkinter.ttk import *

# - Clase Principal Aplicacion - #
class App(Frame):
    def __init__(self, parent, *args, **kwargs):       
        Frame.__init__(self, parent, *args, **kwargs)
        self.parent:Tk = parent
        
        # - Inicializacion de objetos TKinter - #
        self.title: Button = self._Create_title()
        
        # - Creacion de los objetos - #
        self.init_gui()
    
    # - Colocamos los elementos visuales - #
    def init_gui(self,)-> None:
        self.title.grid(row=0, column=0, columnspan=2,padx=40)
        
    # - Atributos y elementos de aplicacion - #
    # - TITULO - #
    def _Create_title(self) -> Label:
        return Label(
            master = self,
            text = 'Titulo Ventana Principal',
            foreground = 'black',
            font=("Z003",20,"bold")
        )

# ---- Clase ventana ---- #
class FrameOne(Frame):
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
    
        # - Creacion de objetos TKinter - #
        self.title: Label = self._Create_title()
        
        # Creamos los objetos
        self.init_gui()
        
    # - Colocamos los elementos visuales - #
    def init_gui(self,)-> None:
        self.title.grid(row=0, column=0, columnspan=2,padx=40)
        
    # - Atributos y elementos de aplicacion - #
    # - TITULO - #
    def _Create_title(self) -> Label:
        return Label(
            master = self,
            text = 'Titulo Ventana Archivo',
            foreground = 'black',
            font=("Z003",20,"bold")
        )
    
    
# ------------------------------------------------------ #
# -------------- Inicializacion de la app -------------- #
# ------------------------------------------------------ #
root = Tk()

if __name__ == '__main__':
    # Inicio de app
    ex = App(root)
    root.mainloop()