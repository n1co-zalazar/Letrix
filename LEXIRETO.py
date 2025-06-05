import pygame
import math
import random
import const2
import sys
import os
import json


def cargar_partida(usuario):
    from guardado import cargar_partida as cp
    partida = cp(usuario, "lexireto")
    print(f"Intentando cargar partida para {usuario}: {partida}")  # Debug
    return partida

def guardar_partida(usuario, estado):
    from guardado import guardar_partida as gp
    return gp(usuario, "lexireto", estado)

mensaje_actual = ""
color_mensaje = const2.negro
tiempo_mensaje_inicio = 0

def mostrar_mensaje(mensaje, color):
    """Función independiente para mostrar mensajes"""
    global mensaje_actual, color_mensaje, tiempo_mensaje_inicio
    mensaje_actual = mensaje
    color_mensaje = color
    tiempo_mensaje_inicio = pygame.time.get_ticks()


def mostrar_menu_inicial(username, ventana, ANCHO, ALTO, FUENTE, FUENTE_BOTON):
    """Muestra el menú inicial con opciones de nueva partida o continuar"""
    fondo = pygame.image.load("imágenes/fondo3.png").convert()
    fondo = pygame.transform.scale(fondo, (ANCHO, ALTO))

    # Verificar si hay partida guardada usando la función correcta
    partida_guardada = None
    if username:
        from guardado import cargar_partida
        partida_guardada = cargar_partida(username, "lexireto")

    tiene_partida_guardada = partida_guardada is not None

    # Crear botones
    boton_nueva = pygame.Rect(ANCHO // 2 - 150, ALTO // 2 - 50, 300, 50)
    boton_cargar = pygame.Rect(ANCHO // 2 - 150, ALTO // 2 + 30, 300, 50)

    while True:
        ventana.blit(fondo, (0, 0))

        # Título
        titulo = FUENTE.render("LEXIRETO", True, const2.negro)
        ventana.blit(titulo, (ANCHO // 2 - titulo.get_width() // 2, ALTO // 3))

        # Dibujar botones
        mouse_pos = pygame.mouse.get_pos()

        # Botón Nueva Partida
        color_nueva = const2.gris if boton_nueva.collidepoint(mouse_pos) else const2.blanco
        pygame.draw.rect(ventana, color_nueva, boton_nueva, border_radius=5)
        pygame.draw.rect(ventana, const2.negro, boton_nueva, 2, border_radius=5)
        texto_nueva = FUENTE_BOTON.render("Nueva Partida", True, const2.negro)
        ventana.blit(texto_nueva, texto_nueva.get_rect(center=boton_nueva.center))

        # Botón Continuar Partida - siempre visible pero con estado diferente
        color_cargar = const2.gris if boton_cargar.collidepoint(mouse_pos) and tiene_partida_guardada else const2.blanco
        pygame.draw.rect(ventana, color_cargar, boton_cargar, border_radius=5)
        pygame.draw.rect(ventana, const2.negro, boton_cargar, 2, border_radius=5)

        # Texto siempre visible, pero con color diferente según el estado
        texto_color = const2.negro if tiene_partida_guardada else const2.gris
        texto_cargar = FUENTE_BOTON.render("Continuar Partida", True, texto_color)
        ventana.blit(texto_cargar, texto_cargar.get_rect(center=boton_cargar.center))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if boton_nueva.collidepoint(mouse_pos):
                    return None  # Nueva partida
                elif boton_cargar.collidepoint(mouse_pos):
                    if tiene_partida_guardada:
                        return partida_guardada  # Partida guardada
                    else:
                        mostrar_mensaje("No hay partida guardada", const2.rojo)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "salir"

def main(estado_partida=None, username=None):
    pygame.init()
    # Verificar que el sistema de guardado esté inicializado
    from guardado import inicializar_sistema_guardado
    if not inicializar_sistema_guardado():
        print("Error: No se pudo inicializar el sistema de guardado")
        return
    # Configuración inicial
    ANCHO = const2.width
    ALTO = const2.length
    # colores
    BLANCO = const2.blanco
    NEGRO = const2.negro
    AMARILLO = const2.amarillo
    GRIS = const2.gris
    AZUL = const2.gris
    ROJO = const2.rojo
    NARANJA = const2.naranja
    VERDE = const2.verde

    scroll_offset = 0
    FUENTE = pygame.font.Font("letras/letraproyecto.ttf", 24)
    FUENTE_BOTON = pygame.font.Font("letras/letraproyecto.ttf", 15)
    FUENTE_ERROR = pygame.font.Font("letras/letraproyecto.ttf", 22)  # Fuente más grande solo para el error
    FUENTE_TIEMPO = pygame.font.Font("letras/letraproyecto.ttf", 30)

    ventana = pygame.display.get_surface()
    if ventana is None:
        ventana = pygame.display.set_mode((ANCHO, ALTO))

    # Mostrar menú inicial si no se proporciona estado_partida
    if username:
        estado_partida = mostrar_menu_inicial(username, ventana, ANCHO, ALTO, FUENTE, FUENTE_BOTON)
        if estado_partida == "salir":
            return

    fondo = pygame.image.load("imágenes/fondo3.png").convert()
    fondo = pygame.transform.scale(fondo, (ANCHO, ALTO))
    pygame.display.set_caption("Lexireto")
    seleccionados = []
    reloj = pygame.time.Clock()

    # variables para mensajes
    mensaje_actual = ""
    color_mensaje = NEGRO
    tiempo_mensaje_inicio = 0
    duracion_mensaje = 2000

    # Variable específica para mensaje de palabra no válida
    mensaje_error_palabra = ""
    color_error_palabra = ROJO


    # ------------------------funciones generar letras y palabras validas----------------------------------------------------
    def generar_letras_validas(diccionario_path, min_palabras=30, max_intentos=100):
        with open(diccionario_path, "r", encoding="utf-8") as f:
            palabras = [line.strip().upper() for line in f if len(line.strip()) >= 3 and line.strip().isalpha()]

        pangramas = [p for p in palabras if len(set(p)) >= 7]
        if not pangramas:
            return None, None, set()

        for _ in range(max_intentos):
            pangrama = random.choice(pangramas)
            letras = list(set(pangrama))
            random.shuffle(letras)
            letras = letras[:7]

            if len(letras) < 7:
                continue

            letra_central = random.choice(letras)
            letras_set = set(letras)

            palabras_validas_ = {
                p for p in palabras
                if len(p) >= 3 and letra_central in p and set(p).issubset(letras_set)
            }

            # Asegurar que haya al menos una palabra que empiece con cada letra del conjunto
            cubre_todas_las_letras = all(
                any(p.startswith(letra) for p in palabras_validas_)
                for letra in letras
            )

            if len(palabras_validas_) >= min_palabras and cubre_todas_las_letras:
                return letras, letra_central, palabras_validas_

        return None, None, set()

    if estado_partida and estado_partida.get("letras_panal"):
        LETRAS = estado_partida["letras_panal"]
        LETRA_CENTRAL = estado_partida["letra_central"]
        palabras_validas = set(estado_partida.get("palabras_validas", []))
        puntaje_actual = estado_partida.get("puntaje", 0)
        tiempo_transcurrido_guardado = estado_partida.get("tiempo_transcurrido", 0)
        tiempo_inicio = pygame.time.get_ticks() - (tiempo_transcurrido_guardado * 1000)
    else:
        LETRAS, LETRA_CENTRAL, palabras_validas = generar_letras_validas("diccionario_sin_acentos.txt")
        if not LETRAS:
            print("No se pudo generar un conjunto válido de letras")
            return

        tiempo_inicio = pygame.time.get_ticks()
        puntaje_actual = 0


    # asegurar que la letra central este en la primera posicion
    if LETRA_CENTRAL in LETRAS:
        LETRAS.remove(LETRA_CENTRAL)
        LETRAS.insert(0, LETRA_CENTRAL)

    # mostrar letras y palabras validas al inicio
    print("\n=== Palabras validas para esta ronda ===")
    print(f"Letras disponibles: {', '.join(LETRAS)}")
    print(f"Letra central requerida: {LETRA_CENTRAL}\n")
    print("Lista completa de palabras válidas:")
    for i, palabra in enumerate(sorted(palabras_validas), 1):
        print(f"{i}. {palabra}")
    print(f"\nTotal: {len(palabras_validas)} palabras válidas.\n")

    # inicializar palabras encontradas
    palabras_encontradas = {
        letra: {'palabras': [], 'contador': 0, 'total': 0} for letra in LETRAS
    }

    for letra in LETRAS:
        palabras_encontradas[letra]['total'] = sum(
            1 for palabra in palabras_validas
            if palabra.startswith(letra) and LETRA_CENTRAL in palabra
        )

    todas_encontradas = set()
    lista_palabras_encontradas = []

    if estado_partida:
        for letra, info in estado_partida.get("palabras_encontradas", {}).items():
            if letra in palabras_encontradas:
                palabras_encontradas[letra]['palabras'] = info.get('palabras', [])
                palabras_encontradas[letra]['contador'] = info.get('contador', 0)

        todas_encontradas = set(estado_partida.get("palabras_encontradas_todas", []))
        lista_palabras_encontradas = estado_partida.get("lista_palabras_encontradas", [])

    # -------------------------------funciones de dibujar hexagonos-------------------------------------------------------
    def obtener_puntos_hexagono(cx, cy, radio):
        return [
            ((cx + radio * math.cos(math.radians(60 * i - 30)),
              cy + radio * math.sin(math.radians(60 * i - 30)))
            ) for i in range(6)
        ]

    def obtener_posiciones_hexagonos(cx, cy, distancia):
        return [
            (cx, cy),  # centro
            (cx + distancia, cy),  # derecha
            (cx - distancia, cy),  # izquierda
            (cx + distancia / 2, cy - distancia * math.sin(math.radians(60))),  # arriba derecha
            (cx - distancia / 2, cy - distancia * math.sin(math.radians(60))),  # arriba izquierda
            (cx + distancia / 2, cy + distancia * math.sin(math.radians(60))),  # abajo derecha
            (cx - distancia / 2, cy + distancia * math.sin(math.radians(60))),  # abajo izquierda
        ]

    def punto_en_poligono(px, py, poligono):
        dentro = False
        j = len(poligono) - 1
        for i in range(len(poligono)):
            xi, yi = poligono[i]
            xj, yj = poligono[j]
            if ((yi > py) != (yj > py)) and (px < (xj - xi) * (py - yi) / (yj - yi + 1e-10) + xi):
                dentro = not dentro
            j = i
        return dentro

    def dibujar_boton(texto, x, y, ancho, alto, mouse_pos):
        rect = pygame.Rect(x, y, ancho, alto)
        color = AZUL if rect.collidepoint(mouse_pos) else BLANCO
        pygame.draw.rect(ventana, color, rect, border_radius=5)
        pygame.draw.rect(ventana, NEGRO, rect, 2, border_radius=5)
        texto_render = FUENTE_BOTON.render(texto, True, NEGRO)
        ventana.blit(texto_render, texto_render.get_rect(center=rect.center))
        return rect

    # -------------------------------fin funciones de dibubar hexagonos-------------------------------------------------------------
    # ----------------------funciones de logica del juego----------------------------------------------------------------
    def palabra_es_valida(palabra):
        if len(palabra) < 3:
            return False
        if palabra[0] not in LETRAS:
            return False
        if LETRA_CENTRAL not in palabra:
            return False
        if not set(palabra).issubset(set(LETRAS)):
            return False
        if palabra not in palabras_validas:
            return False
        return True

    def calcular_puntos(palabra):  # calcula cantidad de puntos totales
        if set(palabra) == set(LETRAS):  # Heptacrack: contiene las 7 letras
            return 10
        elif len(palabra) == 3:
            return 1
        elif len(palabra) == 4:
            return 2
        elif len(palabra) >= 5:
            return len(palabra)
        return 0

    # Calcular el puntaje maximo posible
    puntaje_total = sum(calcular_puntos(p) for p in palabras_validas)

    def aplicar_palabra():
        nonlocal mensaje_error_palabra, color_error_palabra
        palabra = "".join(seleccionados)

        if len(palabra) < 3:
            mostrar_mensaje("Palabra demasiado corta", ROJO)
            mensaje_error_palabra = ""
            return False

        if LETRA_CENTRAL not in palabra:
            mostrar_mensaje("Falta la letra central", NARANJA)
            mensaje_error_palabra = ""
            return False

        if not set(palabra).issubset(set(LETRAS)):
            mostrar_mensaje("Letras no validas", ROJO)
            mensaje_error_palabra = ""
            return False

        if palabra not in palabras_validas:
            mensaje_error_palabra = "Palabra no valida"
            color_error_palabra = ROJO
            mostrar_mensaje("", NEGRO)  # Limpiar mensaje superior
            return False

        if palabra in todas_encontradas:
            mostrar_mensaje("Palabra ya encontrada", NARANJA)
            mensaje_error_palabra = ""
            return False

        # Si pasa todas las validaciones
        letra_inicial = palabra[0]
        palabras_encontradas[letra_inicial]['palabras'].append(palabra)
        todas_encontradas.add(palabra)
        lista_palabras_encontradas.append(palabra)
        seleccionados.clear()
        puntos = calcular_puntos(palabra)
        nonlocal puntaje_actual
        puntaje_actual += puntos
        mensaje_error_palabra = ""  # Limpiar mensaje de error

        mostrar_mensaje("¡Palabra aceptada!", VERDE)
        return True

    def dibujar_palabras_encontradas(scroll_offset):
        x_inicio, y_inicio = ANCHO - 180, ALTO - 510
        area_altura = ALTO - y_inicio
        contenido_altura = sum(30 + len(info['palabras']) * 25 + 15 for info in palabras_encontradas.values())

        scroll_offset = max(0, min(scroll_offset, contenido_altura - area_altura))
        superficie_contenido = pygame.Surface((200, contenido_altura))
        superficie_contenido = pygame.Surface((200, contenido_altura), pygame.SRCALPHA)
        superficie_contenido.fill((0, 0, 0, 0))  # Transparente total

        offset_y = -scroll_offset

        for letra, info in palabras_encontradas.items():
            texto = FUENTE.render(f"{letra}: {len(info['palabras'])}/{info['total']}", True, NEGRO)
            superficie_contenido.blit(texto, (0, offset_y))
            offset_y += 30

            for palabra in info["palabras"]:
                texto_palabra = FUENTE_BOTON.render(palabra, True, NEGRO)
                superficie_contenido.blit(texto_palabra, (20, offset_y))
                offset_y += 25
            offset_y += 15

        ventana.blit(superficie_contenido, (x_inicio, y_inicio), (0, scroll_offset, 200, area_altura))

        if contenido_altura > area_altura:
            barra_height = int((area_altura ** 2) / contenido_altura)
            barra_pos = int((scroll_offset * (area_altura - barra_height)) / (contenido_altura - area_altura))
            pygame.draw.rect(ventana, NEGRO, (x_inicio - 20, y_inicio + barra_pos, 8, barra_height))

        return scroll_offset

    def mostrar_reglas():
        reglas_fondo = pygame.Surface((ANCHO, ALTO))
        reglas_fondo.fill(NEGRO)
        fuente = pygame.font.Font('letras/letraproyecto.ttf', 20)
        instruccionesventana = [
            "---------------------------------------------------------------------------",
            "                        REGLAS DEL LEXIRETO                            ",
            "---------------------------------------------------------------------------",
            "-Forma palabras de al menos 3 letras. Puedes repetir las letras,pero",
            " siempre incluyendo la letra central.",
            "-Encuentra palabras que incluyan las 7 letras (¡Heptacrack!) y ",
            "subirás de posición en Cómo va tu juego y mejorarás tus estadísticas.",
            "----------------------------PUNTUACION---------------------------------------",
            "-las palabras de 3 letras dan 1 punto y las de 4 letras, 2 puntos.",
            "A partir de 5 letras, obtendrás tantos puntos como letras tenga la",
            "palabra. Los heptacracks valen 10 puntos."
        ]

        boton_cerrar = pygame.Rect(ANCHO // 2 - 80, ALTO - 100, 160, 50)
        esperando = True
        while esperando:
            ventana.blit(reglas_fondo, (0, 0))
            y = 30
            for linea in instruccionesventana:
                texto = fuente.render(linea, True, VERDE)
                ventana.blit(texto, (20, y))
                y += 55

            mouse_pos = pygame.mouse.get_pos()
            hover_cerrar = boton_cerrar.collidepoint(mouse_pos)
            color_cerrar = (200, 200, 200) if hover_cerrar else (255, 255, 255)
            pygame.draw.rect(ventana, color_cerrar, boton_cerrar)
            pygame.draw.rect(ventana, NEGRO, boton_cerrar, 2)

            texto_cerrar = fuente.render("Cerrar", True, NEGRO)
            ventana.blit(texto_cerrar, (boton_cerrar.centerx - texto_cerrar.get_width() // 2,
                                        boton_cerrar.centery - texto_cerrar.get_height() // 2))


            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if boton_cerrar.collidepoint(event.pos):
                        esperando = False  # Salir del bucle al hacer clic en "Cerrar"


    def mostrar_pausa(fondo_pausa=None):
        #ventana de pausa
        pausa_ancho = ANCHO // 2
        pausa_alto = ALTO // 2
        pausa_x = (ANCHO - pausa_ancho) // 2
        pausa_y = (ALTO - pausa_alto) // 2

        # Superficie con transparencia
        pausa_ventana = pygame.Surface((pausa_ancho, pausa_alto), pygame.SRCALPHA)
        pausa_ventana.set_alpha(230)

        # Si se proporciona una imagen de fondo, cargarla y escalarla
        if fondo_pausa:
            fondo_img = pygame.image.load(fondo_pausa).convert()
            fondo_img = pygame.transform.scale(fondo_img, (pausa_ancho, pausa_alto))
            pausa_ventana.blit(fondo_img, (0, 0))
        else:
            pausa_ventana.fill(NEGRO)

        fuente = pygame.font.Font('letras/letraproyecto.ttf', 20)

        # Crear botones dentro de la ventana de pausa
        boton_reglaspausa = pygame.Rect(pausa_x + 20, pausa_y + 30, pausa_ancho - 40, 50)
        boton_regresar = pygame.Rect(pausa_x + 20, pausa_y + 110, pausa_ancho - 40, 50)

        esperando = True
        while esperando:
            ventana.blit(fondo, (0, 0))  # redibuja fondo del juego por detrás (si lo usás)
            ventana.blit(pausa_ventana, (pausa_x, pausa_y))

            mouse_pos = pygame.mouse.get_pos()

            # Botón REGLAS
            hover_reglas = boton_reglaspausa.collidepoint(mouse_pos)
            color_reglas = (200, 200, 200) if hover_reglas else (255, 255, 255)
            pygame.draw.rect(ventana, color_reglas, boton_reglaspausa, border_radius=5)
            pygame.draw.rect(ventana, NEGRO, boton_reglaspausa, 2, border_radius=5)
            texto_reglas = fuente.render("Reglas", True, NEGRO)
            ventana.blit(texto_reglas, texto_reglas.get_rect(center=boton_reglaspausa.center))

            # Botón REGRESAR
            hover_regresar = boton_regresar.collidepoint(mouse_pos)
            color_regresar = (200, 200, 200) if hover_regresar else (255, 255, 255)
            pygame.draw.rect(ventana, color_regresar, boton_regresar, border_radius=5)
            pygame.draw.rect(ventana, NEGRO, boton_regresar, 2, border_radius=5)
            texto_regresar = fuente.render("Regresar", True, NEGRO)
            ventana.blit(texto_regresar, texto_regresar.get_rect(center=boton_regresar.center))

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if boton_reglaspausa.collidepoint(event.pos):
                        mostrar_reglas()
                    elif boton_regresar.collidepoint(event.pos):
                        esperando = False

    def mostrar_mensaje(mensaje, color):
        nonlocal mensaje_actual, color_mensaje, tiempo_mensaje_inicio
        mensaje_actual = mensaje
        color_mensaje = color
        tiempo_mensaje_inicio = pygame.time.get_ticks()

    def dibujar_botones(cx, y_botones, mx, my):
        ancho_boton = 219
        alto_boton = 50
        espacio_entre_boton = 20

        x_aplicar = cx - ancho_boton / 2
        x_borrar_palabra = x_aplicar - (ancho_boton + espacio_entre_boton)
        x_borrar_letra = x_aplicar + ancho_boton + espacio_entre_boton
        x_volver = cx - ancho_boton / 2  # debajo de los otros botones

        boton_borrar_palabra = dibujar_boton("Borrar palabra", x_borrar_palabra, y_botones, ancho_boton, alto_boton,
                                             (mx, my))
        boton_aplicar = dibujar_boton("Aplicar", x_aplicar, y_botones, ancho_boton, alto_boton, (mx, my))
        boton_borrar_letra = dibujar_boton("Borrar letra", x_borrar_letra, y_botones, ancho_boton, alto_boton, (mx, my))
        boton_volver = dibujar_boton("Volver", 30, 90, ancho_boton, alto_boton, (mx, my))
        boton_pausa = dibujar_boton("Pausa", 30, 30, ancho_boton, alto_boton, (mx, my))

        boton_guardar = dibujar_boton("Guardar", ANCHO - 250, 30, ancho_boton, alto_boton, (mx, my))
        return boton_borrar_palabra, boton_aplicar, boton_borrar_letra, boton_volver, boton_pausa, boton_guardar

    # juego
    cx, cy = ANCHO / 2, 260  # centro de los hexagonos
    radio = 80
    distancia = radio * 2 * math.cos(math.radians(30)) + 3.5
    posiciones = obtener_posiciones_hexagonos(cx, cy, distancia)
    hexagonos = [obtener_puntos_hexagono(x, y, radio) for (x, y) in posiciones]
    run = True

    while run:
        ventana.blit(fondo, (0, 0))
        mx, my = pygame.mouse.get_pos()
        # Dibujar hexagonos
        for i, (x, y) in enumerate(posiciones):
            puntos = hexagonos[i]
            letra_actual = LETRAS[i]
            if punto_en_poligono(mx, my, puntos):
                color = AZUL
            elif i == 0:  # Hexagono central
                color = AMARILLO
            else:
                color = BLANCO

            pygame.draw.polygon(ventana, color, puntos)
            pygame.draw.polygon(ventana, NEGRO, puntos, 2)
            texto = FUENTE.render(letra_actual, True, NEGRO)
            rect = texto.get_rect(center=(x, y))
            ventana.blit(texto, rect)

        # dibujar botones
        boton_borrar_palabra, boton_aplicar, boton_borrar_letra, boton_volver,boton_pausa, boton_guardar = dibujar_botones(cx, 550,mx, my)

        # Dibujar mensaje de error específico (con fuente grande y posición ajustada)
        if mensaje_error_palabra:
            texto_error = FUENTE_ERROR.render(mensaje_error_palabra, True, color_error_palabra)
            # Posición centrada y más abajo (ajusta el +40 si necesitas más/menos espacio)
            x_pos = boton_aplicar.x + (boton_aplicar.width - texto_error.get_width()) // 2
            y_pos = boton_aplicar.y + boton_aplicar.height + 40
            ventana.blit(texto_error, (x_pos, y_pos))

        # dibujar palabra actual
        letras_renderizadas = [FUENTE.render(letra, True, NEGRO) for letra in seleccionados]
        anchos_letras = [texto.get_width() for texto in letras_renderizadas]
        total_ancho = sum(anchos_letras) + (len(letras_renderizadas) - 1) * 5  # 5px espacio entre letras
        inicio_x = cx - total_ancho / 2
        y_texto = cy + 230
        x_actual = inicio_x
        for i, letra_surface in enumerate(letras_renderizadas):
            ventana.blit(letra_surface, (x_actual, y_texto))
            x_actual += letra_surface.get_width() + 5  # avanzar al siguiente

        # dibujar palabras encontradas
        scroll_offset = dibujar_palabras_encontradas(scroll_offset)
        # mostrar tiempo
        tiempo_actual = pygame.time.get_ticks()
        tiempo_transcurrido = (tiempo_actual - tiempo_inicio) // 1000
        texto_tiempo = FUENTE_TIEMPO.render(f"{tiempo_transcurrido // 60:02d}:{tiempo_transcurrido % 60:02d}", True,
                                            NEGRO)
        ventana.blit(texto_tiempo, (ANCHO - 775, 710))  # posicion del tiempo
        # linea base fija debajo de la palabra
        linea_largo = 400  # largor de la linea
        linea_alto = 3
        x_linea = cx - linea_largo / 2
        y_linea = cy + 265  # un poco debajo del texto
        pygame.draw.line(ventana, NEGRO, (x_linea, y_linea), (x_linea + linea_largo, y_linea), linea_alto)
        # Mostrar progreso de puntuación
        porcentaje = int((puntaje_actual / puntaje_total) * 100) if puntaje_total > 0 else 0
        texto_puntos = FUENTE.render(f"Puntos: {puntaje_actual}/{puntaje_total} ({porcentaje}%)", True, NEGRO)
        ventana.blit(texto_puntos, (ANCHO - 900, 10))  #posicion de la puntuacion

        # Mostrar mensajes generales
        if mensaje_actual and pygame.time.get_ticks() - tiempo_mensaje_inicio < duracion_mensaje:
            texto = FUENTE.render(mensaje_actual, True, color_mensaje)
            ventana.blit(texto, (ANCHO // 2 - texto.get_width() // 2, 650))

        # Manejo de eventos
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                run = False
                sys.exit()
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                if boton_pausa.collidepoint(mx,my):
                    mostrar_pausa()
                elif boton_borrar_palabra.collidepoint(mx, my):
                    seleccionados.clear()
                    mensaje_error_palabra = ""  # Limpiar mensaje de error al borrar
                elif boton_borrar_letra.collidepoint(mx, my) and seleccionados:
                    seleccionados.pop()
                    mensaje_error_palabra = ""  # Limpiar mensaje de error al borrar
                elif boton_aplicar.collidepoint(mx, my):
                    aplicar_palabra()
                elif boton_guardar.collidepoint(mx, my):
                    estado = {
                        "letras_panal": LETRAS,
                        "letra_central": LETRA_CENTRAL,
                        "palabras_validas": list(palabras_validas),
                        "palabras_encontradas": palabras_encontradas,
                        "palabras_encontradas_todas": list(todas_encontradas),
                        "lista_palabras_encontradas": lista_palabras_encontradas,
                        "puntaje": puntaje_actual,
                        "tiempo_transcurrido": (pygame.time.get_ticks() - tiempo_inicio) // 1000
                    }
                    if guardar_partida(username, estado):  # Usa el username real
                        mostrar_mensaje("Partida guardada", VERDE)
                    else:
                        mostrar_mensaje("Error al guardar", ROJO)
                elif boton_volver.collidepoint(mx, my):
                    return
                else:
                    for i, poligono in enumerate(hexagonos):
                        if punto_en_poligono(mx, my, poligono):
                            seleccionados.append(LETRAS[i])
                            mensaje_error_palabra = ""  # Limpiar mensaje de error al agregar letra
            elif evento.type == pygame.MOUSEWHEEL:
                scroll_offset -= evento.y * 30
                scroll_offset = max(0, scroll_offset)
            pygame.display.flip()
            reloj.tick(60)

    # Al salir del juego
    print("\n=== Palabras encontradas ===")
    for palabra in lista_palabras_encontradas:
        print(palabra)
    print(f"\nTotal: {len(lista_palabras_encontradas)} palabras encontradas.")

    palabras_no_encontradas = sorted(palabras_validas - set(lista_palabras_encontradas))
    print("\n=== Palabras NO encontradas ===")
    for palabra in palabras_no_encontradas:
        print(palabra)
    print(f"\nTotal: {len(palabras_no_encontradas)} palabras no encontradas.")

    pygame.display.set_caption("Palabrerío")
    return


if __name__ == "__main__":
    estado_partida = None
    if len(sys.argv) > 1 and sys.argv[1] == "--cargar":
        usuario = sys.argv[2] if len(sys.argv) > 2 else "jugador"
        estado_partida = cargar_partida(usuario)

    main(estado_partida)

