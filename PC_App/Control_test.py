# - Pygame and Pyseria - #       
import pygame
#import serial

# - PS4 CONTROLLER - #
import controls.ps4_control as ps4
# Inicializar Pygame
pygame.init()

# Establecer dimensiones de la pantalla
screen = pygame.display.set_mode((800, 600))

# Título de la ventana
pygame.display.set_caption('Control Test')

# Colores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)

# Posición inicial del círculo
x, y = 400, 300
radius = 30
speed = 5

# Fuente para escribir un texto
font = pygame.font.Font(None, 32)
input_box = pygame.Rect(20, 50, 700, 32)
color_inactive = pygame.Color('lightskyblue3')
color_active = pygame.Color('dodgerblue2')
color = color_inactive
active = False
text = ''

# Función para leer datos del puerto serial
def read_ps4():
    var = ps4.get_buttons
    return var

# Función para mostrar el texto recibido del puerto serial
def display_serial_text(screen, font, text, position):
    if text:
        serial_disp_txt = font.render(text, True, 'blue')
        screen.blit(serial_disp_txt, position)

# Solicitar un comando. Mostrar texto
text_surface = font.render("Input a command:", True, 'white')

# Texto recibido. Mostar texto fijo
recv_txt = font.render("Response:", True, 'white')

# Lo que recibi. Texto variable por la lectura serial
"""serial_text = read_ps4()
serial_disp_txt = font.render(serial_text, True, 'blue')"""

# - Reaccion a botones - #
# Start
strt_text_surface = font.render("X", True, 'white')
show_start_text = False  # Variable de estado para controlar la visibilidad del tstrt
# Escape
escape_text_surface = font.render("[]", True, 'white')
show_escape_text = False  # Variable de estado para controlar la visibilidad del texto
# Jump
jump_text_surface = font.render("O", True, 'white')
show_jump_text = False  # Variable de estado para controlar la visibilidad del texto
# Shoot
shoot_text_surface = font.render("<|", True, 'white')
show_shoot_text = False  # Variable de estado para controlar la visibilidad del texto

# Bucle principal del juego
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            if input_box.collidepoint(event.pos):
                active = not active
            else:
                active = False
            color = color_active if active else color_inactive
            
        if event.type == pygame.KEYDOWN:
            if active:
                if event.key == pygame.K_RETURN:
                    text = ''
                elif event.key == pygame.K_BACKSPACE:
                    text = text[:-1]
                else:
                    text += event.unicode
    
    # Rellenar la pantalla con negro
    screen.fill(BLACK)

    # Dibujar el círculo
    pygame.draw.circle(screen, 'white', (x, y), radius)

    # Renderizar el texto de entrada
    txt_surface = font.render(text, True, color)
    width = max(200, txt_surface.get_width() + 10)
    input_box.w = width
    screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
    pygame.draw.rect(screen, color, input_box, 2)

    # - Mostrar texto en la pantalla - #
    # Input a command:
    screen.blit(text_surface, (20, 20))
    # Response:
    screen.blit(recv_txt, (500, 20))
    # Leer y mostrar datos del puerto serial
    command = read_ps4()
    #display_serial_text(screen, font, command, (500, 50))
    
    # Reaccion a botones
    if show_start_text:
        screen.blit(strt_text_surface, (20, 100))
    if show_escape_text:
        screen.blit(escape_text_surface, (20, 200))
    if show_jump_text:
        screen.blit(jump_text_surface, (20, 300)) 
    if show_shoot_text:
        screen.blit(shoot_text_surface, (20, 400))
    # Actualizar la pantalla
    pygame.display.flip()

    # - Reaccionamos a la input recibida - #
    if command:
        # Inputs Joystick
        if command == 'I':
            x -= speed
        elif command == 'D':
            x += speed
        elif command == 'A':
            y -= speed
        elif command == 'a':
            y += speed
        # Inputs Botones
        elif command == 'X':
            show_start_text = True
            show_escape_text = False
            show_jump_text = False
            show_shoot_text = False
        elif command == 'SQR':
            show_start_text = False
            show_escape_text = True
            show_jump_text = False
            show_shoot_text = False
        elif command == 'O':
            show_start_text = False
            show_escape_text = False
            show_jump_text = True
            show_shoot_text = False
        elif command == 'TRI':
            show_start_text = False
            show_escape_text = False
            show_jump_text = False
            show_shoot_text = True
            
    """
        Received command list:
        - Movement
            Izquierda = I
            Derecha = D
            Arriba = A
            Abajo = a
            
        - Acciones
            Start On = Str
            Escape On = Esc
            Jump On = Jmp
            Shoot On = Sho
            
            Start Off = st0
            Escape Off = es0
            Jump Off = jm0
            Shoot Off = sh0
        
        Sent command list:
        die -> Should do sth in control
    """
    
    # Controlar la velocidad del bucle
    pygame.time.Clock().tick(60)

# Salir de Pygame
pygame.quit()
