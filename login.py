import pygame
import os
import time


def pantalla_login():
    pygame.init()
    screen = pygame.display.set_mode((600, 400))
    pygame.display.set_caption("Sistema de Login")
    font = pygame.font.Font("letras/letraproyecto.ttf", 11)
    small_font = pygame.font.Font("letras/letraproyecto.ttf", 7)
    clock = pygame.time.Clock()

    # Cargar fondo
    NOMBRE_IMAGEN_FONDO = "imágenes/fondo3.png"
    fondo = pygame.image.load(NOMBRE_IMAGEN_FONDO)
    fondo = pygame.transform.scale(fondo, (600, 400))

    # Archivos
    USERS_FILE = "usuarios.txt"

    # Colores
    WHITE = (255, 255, 255)
    GRAY = (200, 200, 200)
    BLACK = (0, 0, 0)
    RED = (255, 100, 100)
    YELLOW = (255, 255, 0)

    # --- Funciones de Ayuda ---

    def cargar_usuarios():
        users = {}
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, "r") as f:
                for line in f:
                    if "," in line:
                        name, pwd = line.strip().split(",", 1)
                        users[name] = pwd
        return users

    def guardar_usuario(username, password):
        with open(USERS_FILE, "a") as f:
            f.write(f"{username},{password}\n")

    def dibujar_texto(texto, x, y, color=WHITE, fuente=font, contorno=True):
        if contorno:
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx != 0 or dy != 0:
                        sombra = fuente.render(texto, True, BLACK)
                        screen.blit(sombra, (x + dx, y + dy))
        render = fuente.render(texto, True, color)
        screen.blit(render, (x, y))

    def dibujar_texto_centrado_en_rect(texto, rect, color=BLACK, fuente=font, contorno=False):
        render = fuente.render(texto, True, color)
        texto_rect = render.get_rect(center=rect.center)
        if contorno:
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx != 0 or dy != 0:
                        sombra = fuente.render(texto, True, BLACK)
                        sombra_rect = sombra.get_rect(center=rect.center)
                        screen.blit(sombra, (sombra_rect.x + dx, sombra_rect.y + dy))
        screen.blit(render, texto_rect)

    def dibujar_texto_input_centrado(texto, rect, color=WHITE, fuente=font):
        render = fuente.render(texto, True, color)
        texto_rect = render.get_rect(center=rect.center)
        screen.blit(render, texto_rect)

    def dibujar_rect_redondeado(surface, color, rect, radius, width=0):
        if radius > rect.width / 2:
            radius = rect.width / 2
        if radius > rect.height / 2:
            radius = rect.height / 2

        pygame.draw.circle(surface, color, (rect.left + radius, rect.top + radius), radius, width)
        pygame.draw.circle(surface, color, (rect.right - radius, rect.top + radius), radius, width)
        pygame.draw.circle(surface, color, (rect.left + radius, rect.bottom - radius), radius, width)
        pygame.draw.circle(surface, color, (rect.right - radius, rect.bottom - radius), radius, width)

        pygame.draw.rect(surface, color, (rect.left + radius, rect.top, rect.width - 2 * radius, rect.height), width)
        pygame.draw.rect(surface, color, (rect.left, rect.top + radius, rect.width, rect.height - 2 * radius), width)

        if width == 0:
            pygame.draw.rect(surface, color, (rect.left + radius, rect.top, rect.width - 2 * radius, rect.height))
            pygame.draw.rect(surface, color, (rect.left, rect.top + radius, rect.width, rect.height - 2 * radius))

    # --- Estado de la Aplicación ---
    estado = "inicio"
    username = ""
    password = ""
    activo = None
    mensaje = ""
    mensaje_temp = ""
    modo = "login"

    input_boxes = {
        "username": pygame.Rect(200, 100, 250, 40),
        "password": pygame.Rect(200, 160, 250, 40),
    }
    boton_login = pygame.Rect(180, 130, 240, 50)
    boton_registro = pygame.Rect(180, 200, 240, 50)
    boton_volver = pygame.Rect(20, 20, 100, 35)

    login_exitoso = False

    running = True
    while running:
        screen.blit(fondo, (0, 0))
        caps = pygame.key.get_mods() & pygame.KMOD_CAPS

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if estado == "inicio":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if boton_login.collidepoint(event.pos):
                        estado = "formulario"
                        modo = "login"
                        mensaje = ""
                        mensaje_temp = ""
                        username = ""
                        password = ""
                        activo = "username"
                    elif boton_registro.collidepoint(event.pos):
                        estado = "formulario"
                        modo = "registro"
                        mensaje = ""
                        mensaje_temp = ""
                        username = ""
                        password = ""
                        activo = "username"

            elif estado == "formulario":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for campo, rect in input_boxes.items():
                        if rect.collidepoint(event.pos):
                            activo = campo
                    if boton_volver.collidepoint(event.pos):
                        estado = "inicio"
                        username = ""
                        password = ""
                        mensaje = ""
                        mensaje_temp = ""
                        activo = None

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_TAB:  # Manejo de TAB para cambiar entre campos
                        if activo == "username":
                            activo = "password"
                        elif activo == "password":
                            activo = "username"
                        # Prevenir el comportamiento por defecto de TAB
                        continue
                    
                    elif event.key == pygame.K_RETURN:
                        usuarios = cargar_usuarios()
                        if modo == "login":
                            if username in usuarios and usuarios[username] == password:
                                mensaje = f"Bienvenido, {username}!"
                                login_exitoso = True
                                running = False
                            else:
                                mensaje = "Usuario o contraseña incorrectos."
                        elif modo == "registro":
                            if username in usuarios:
                                mensaje = "El usuario ya existe."
                            elif len(username) < 3:
                                mensaje = "El nombre debe tener al menos 3 letras."
                            elif len(username) > 14:
                                mensaje = "El nombre no puede tener más de 14 caracteres."
                            elif len(password) < 6:
                                mensaje = "La contraseña debe tener al menos 6 caracteres."
                            else:
                                guardar_usuario(username, password)
                                mensaje = "¡Registrado con éxito!"
                                username = ""
                                password = ""
                                activo = "username"
                    elif event.key == pygame.K_BACKSPACE:
                        if activo == "username":
                            username = username[:-1]
                            mensaje_temp = ""
                        elif activo == "password":
                            password = password[:-1]
                    else:  # Manejo de caracteres normales
                        if activo == "username":
                            if len(username) < 14 and event.unicode.isprintable():
                                username += event.unicode
                                mensaje_temp = ""
                            elif len(username) >= 14:
                                mensaje_temp = "Máx. 14 caracteres"
                        elif activo == "password":
                            if event.unicode.isprintable():
                                password += event.unicode

        if estado == "inicio":
            dibujar_texto("Elige una opción:", 180, 60)
            dibujar_rect_redondeado(screen, BLACK, boton_login, 15)
            dibujar_rect_redondeado(screen, BLACK, boton_registro, 15)
            dibujar_texto_centrado_en_rect("Iniciar Sesión", boton_login, WHITE, font, contorno=False)
            dibujar_texto_centrado_en_rect("Registrarse", boton_registro, WHITE, font, contorno=False)

        elif estado == "formulario":
            dibujar_texto("Usuario:", 80, 110)
            dibujar_texto("Contraseña:", 80, 170)

            for campo, rect in input_boxes.items():
                pygame.draw.rect(screen, BLACK, rect)
                if activo == campo:
                    pygame.draw.rect(screen, WHITE, rect, 2)
                else:
                    pygame.draw.rect(screen, GRAY, rect, 2)

                contenido = username if campo == "username" else "*" * len(password)
                dibujar_texto_input_centrado(contenido, rect, WHITE, font)

            dibujar_rect_redondeado(screen, BLACK, boton_volver, 10)
            dibujar_texto_centrado_en_rect("Volver", boton_volver, WHITE, small_font, contorno=False)

            dibujar_texto("Presiona ENTER para continuar", 150, 230, WHITE)
            dibujar_texto("Usa TAB para cambiar entre campos", 150, 350, WHITE, small_font)
            if caps and activo == "password":
                dibujar_texto("¡Bloq Mayús está activo!", 200, 270, YELLOW, small_font)
            if mensaje:
                dibujar_texto(mensaje, 80, 310, RED)
            if mensaje_temp:
                dibujar_texto(mensaje_temp, 200, 145, RED, small_font)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    return login_exitoso
