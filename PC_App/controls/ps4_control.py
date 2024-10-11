import pygame

def get_available_controllers():
    pygame.init()
    pygame.joystick.init()
    
    controllers = []
    
    # Obtener la cantidad de joysticks conectados
    joystick_count = pygame.joystick.get_count()
    
    if joystick_count == 0:
        print("No hay controles conectados")
    else:
        print(f"Se detectaron {joystick_count} controles")
        
        for i in range(joystick_count):
            joystick = pygame.joystick.Joystick(i)
            joystick.init()
            
    return controllers


def get_control_info(controller_id):
    if controller_id < pygame.joystick.get_count():
        joystick = pygame.joystick.Joystick(controller_id)
        joystick.init()
        
        controller_info = {
            "id": controller_id,
            "name": joystick.get_name(),
            "num_axes": joystick.get_numaxes(),
            "num_buttons": joystick.get_numbuttons(),
            "num_hats": joystick.get_numhats(),
        }
        return controller_info
    else:
        print(f"No existe control con ID {controller_id}")
        return None

# Llamar a la función y mostrar los controles disponibles
available_controllers = get_available_controllers()
