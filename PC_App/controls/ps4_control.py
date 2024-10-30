import pygame
import time

pygame.init()
pygame.joystick.init()

joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]

# - Verificacion - #
def check_ps4_connection():
    """
    Verifica si hay un control de PS4 conectado
    """
    joystick_count = pygame.joystick.get_count()
    if joystick_count == 0:
        print("No hay control PS4 conectado. Por favor, conecta un control.")
        return False
    else:
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
        #print(f"Control conectado: {joystick.get_name()}")
        return True
    
def refresh_joys():
    # - Reescanemos los controles - #
    pygame.joystick.quit()  
    pygame.joystick.init() 
    
    joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
    
    # Reiniciamos los joysticks
    for joystick in joysticks:
        joystick.init()  
        
    print(f"{len(joysticks)} joystick(s) connected: {joysticks}")
    return joysticks  # Devuelve la lista de joysticks

# - BOTONES Y JOYSTICKS - #
def get_buttons():
    """
    Nos regresa todos los botones del control
    
    """
    while True:
        for event in pygame.event.get():
            if event.type == pygame.JOYBUTTONDOWN:
                if event.button == 0:
                    return 'X'

                if event.button == 1:
                    return 'O'

                if event.button == 2:
                    return 'SQR'

                if event.button == 3:
                    return 'TRI'
                
                if event.button == 11:
                    return 'D_UP'
                
                if event.button == 12:
                    return 'D_DWN'
                
                if event.button == 13:
                    return 'D_LFT'
                
                if event.button == 14:
                    return 'D_RGT'

def get_joys():
    """
    Nos regresa las posiciones de la palanca Izquierda
    """
    # Joystick Izquierdo
    xL = 0
    yL = 0
    # Joystick Derecho
    xR = 0
    yR = 0
    
    while True:
        for event in pygame.event.get():
            # Joysticks
            if event.type == pygame.JOYAXISMOTION:
                xL = pygame.joystick.Joystick(0).get_axis(0)
                yL = pygame.joystick.Joystick(0).get_axis(1)
                xR = pygame.joystick.Joystick(0).get_axis(2)
                yR = pygame.joystick.Joystick(0).get_axis(3)
                return xL, yL, xR, yR

# - INFORMACION DEL PAD - #
def get_pad_info(id_pad, val):
    """
    Obtener la informacion del control.
    val = name, id, power, buttons, axes
    """
    joystick = pygame.joystick.Joystick(id_pad)

    if val == 'name':
        return joystick.get_name()

    if val == 'id':
        return joystick.get_id()
    
    if val == 'power':
        return joystick.get_power_level()
    
    if val == 'buttons':
        return joystick.get_numbuttons()
    
    if val == 'axes':
        return joystick.get_numaxes()       
                    
if __name__ == "__main__":
    while True:
        print(get_buttons())
        