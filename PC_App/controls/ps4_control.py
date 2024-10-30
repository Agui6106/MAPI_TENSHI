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
def get_controller_state():
    """
    Devuelve el estado de los botones y posiciones de las palancas del control.
    """
    buttons = {}
    axes = {}
    
    for event in pygame.event.get():
        if event.type == pygame.JOYBUTTONDOWN or event.type == pygame.JOYBUTTONUP:
            # Mapear botones con sus nombres
            buttons = {
                'X': pygame.joystick.Joystick(0).get_button(0),
                'O': pygame.joystick.Joystick(0).get_button(1),
                'SQR': pygame.joystick.Joystick(0).get_button(2),
                'TRI': pygame.joystick.Joystick(0).get_button(3),
                'D_UP': pygame.joystick.Joystick(0).get_button(11),
                'D_DWN': pygame.joystick.Joystick(0).get_button(12),
                'D_LFT': pygame.joystick.Joystick(0).get_button(13),
                'D_RGT': pygame.joystick.Joystick(0).get_button(14)
            }
        
        if event.type == pygame.JOYAXISMOTION:
            # Mapear posiciones de las palancas
            axes = {
                'xL': pygame.joystick.Joystick(0).get_axis(0),
                'yL': pygame.joystick.Joystick(0).get_axis(1),
                'xR': pygame.joystick.Joystick(0).get_axis(2),
                'yR': pygame.joystick.Joystick(0).get_axis(3)
            }
    
    return {'buttons': buttons, 'axes': axes}

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
    if check_ps4_connection():
        while True:
            state = get_controller_state()
            print(state)
        