import pygame
import time

pygame.init()
pygame.joystick.init()

joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
    
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

def get_joys_left():
    """
    Nos regresa las posiciones de la palanca Izquierda
    """
    x = 0
    y = 0
    while True:
        for event in pygame.event.get():
            if event.type == pygame.JOYAXISMOTION:
                x = pygame.joystick.Joystick(0).get_axis(0)
                y = pygame.joystick.Joystick(0).get_axis(1)
                return x, y
            
def get_joys_right():
    """
    Nos regresa las posiciones de la palanca Derecha
    """
    x = 0
    y = 0
    while True:
        for event in pygame.event.get():
            if event.type == pygame.JOYAXISMOTION:
                x = pygame.joystick.Joystick(0).get_axis(2)
                y = pygame.joystick.Joystick(0).get_axis(3)
                return x, y

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
    # - Info - #
    """ print(f'\nName: {get_pad_info(0,'name')}')
    print(f'Id: {get_pad_info(0,'id')}')
    print(f'Power: {get_pad_info(0,'power')}')
    print(f'Total Buttons: {get_pad_info(0,'buttons')}')
    print(f'Total Axes: {get_pad_info(0,'axes')}')
    
    # - Butons - #
    while True:
        button = get_buttons()
        xval_left, yval_left = get_joys_left()
        xval_right, yval_right = get_joys_right()
        print(button)
        print('')
        print(f'X Left: {xval_left}, Y Left: {yval_left} \n')
        print(f'X right: {xval_right}, Y right: {yval_right} \n')"""