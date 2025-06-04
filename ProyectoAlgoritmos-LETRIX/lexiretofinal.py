import pygame
import math
import random
import const2

def main ():

    pygame.init()
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
    FUENTE_TIEMPO = pygame.font.Font("letras/letraproyecto.ttf", 30)

    ventana = pygame.display.get_surface()
    if ventana is None:
        ventana = pygame.display.set_mode((ANCHO, ALTO))

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


    # cargar letras validas
    LETRAS, LETRA_CENTRAL, palabras_validas = generar_letras_validas("diccionario_sin_acentos.txt")
    if not LETRAS:
        print("No se pudo generar un conjunto valido de letras")
        return

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

    def calcular_puntos(palabra): #calcula cantidad de puntos totales
        if set(palabra) == set(LETRAS):  # Heptacrack: contiene las 7 letras
            return 10
        elif len(palabra) == 3:
            return 1
        elif len(palabra) == 4:
            return 2
        elif len(palabra) >= 5:
            return len(palabra)
        return 0

    # Calcular el puntaje máximo posible
    puntaje_total = sum(calcular_puntos(p) for p in palabras_validas)
    puntaje_actual = 0

    def aplicar_palabra():
        palabra = "".join(seleccionados)


        if len(palabra) < 3:
            mostrar_mensaje("Palabra demasiado corta", ROJO)
            return False

        if LETRA_CENTRAL not in palabra:
            mostrar_mensaje("Falta la letra central", NARANJA)
            return False

        if palabra_es_valida(palabra) and palabra not in todas_encontradas:
            letra_inicial = palabra[0]
            palabras_encontradas[letra_inicial]['palabras'].append(palabra)
            todas_encontradas.add(palabra)
            lista_palabras_encontradas.append(palabra)
            seleccionados.clear()
            puntos = calcular_puntos(palabra)
            nonlocal puntaje_actual
            puntaje_actual += puntos

            mostrar_mensaje("¡Palabra aceptada!", VERDE)
            return True

        mostrar_mensaje("Palabra no valida", (200, 0, 0))
        return False


    def dibujar_palabras_encontradas(scroll_offset):
        x_inicio, y_inicio = ANCHO - 350, ALTO - 680
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

    def mostrar_mensaje(mensaje, color):
        global mensaje_actual, color_mensaje, tiempo_mensaje_inicio
        mensaje_actual = mensaje
        color_mensaje = color
        tiempo_mensaje_inicio = pygame.time.get_ticks()


    def dibujar_botones(cx, y_botones, mx, my):
        ancho_boton = 219
        alto_boton = 50
        espacio_entre_boton = 20

        x_aplicar = cx - ancho_boton / 2
        x_borrar_palabra = x_aplicar - ancho_boton - espacio_entre_boton
        x_borrar_letra = x_aplicar + ancho_boton + espacio_entre_boton

        boton_borrar_palabra = dibujar_boton("Borrar palabra", x_borrar_palabra, y_botones, ancho_boton, alto_boton,
                                             (mx, my))
        boton_aplicar = dibujar_boton("Aplicar", x_aplicar, y_botones, ancho_boton, alto_boton, (mx, my))
        boton_borrar_letra = dibujar_boton("Borrar letra", x_borrar_letra, y_botones, ancho_boton, alto_boton, (mx, my))

        # Dibujar botón Volver al menú
        boton_menu = pygame.Rect(12, ANCHO - 300, 170, 45)
        hover_menu = boton_menu.collidepoint(mx,my)
        color_menu = (200, 200, 200) if hover_menu else BLANCO
        pygame.draw.rect(ventana, color_menu, boton_menu)
        pygame.draw.rect(ventana, NEGRO, boton_menu, 2)

        texto_menu = FUENTE.render("Volver", True, NEGRO)
        ventana.blit(texto_menu, (boton_menu.centerx - texto_menu.get_width() // 2,
                                 boton_menu.centery - texto_menu.get_height() // 2))

        return boton_borrar_palabra, boton_aplicar, boton_borrar_letra,boton_menu


    # juego
    cx, cy = ANCHO / 2, 260  # centro de los hexagonos
    radio = 80
    distancia = radio * 2 * math.cos(math.radians(30)) + 3.5
    posiciones = obtener_posiciones_hexagonos(cx, cy, distancia)
    hexagonos = [obtener_puntos_hexagono(x, y, radio) for (x, y) in posiciones]
    tiempo_inicio = pygame.time.get_ticks()
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
        boton_borrar_palabra, boton_aplicar, boton_borrar_letra,boton_menu = dibujar_botones(cx, 550, mx, my)
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
        texto_tiempo = FUENTE_TIEMPO.render(f"{tiempo_transcurrido // 60:02d}:{tiempo_transcurrido % 60:02d}", True, NEGRO)
        ventana.blit(texto_tiempo, (ANCHO - 1330, ALTO - 680))  # posicion del tiempo
        # linea base fija debajo de la palabra
        linea_largo = 400  # largor de la linea
        linea_alto = 3
        x_linea = cx - linea_largo / 2
        y_linea = cy + 265  # un poco debajo del texto
        pygame.draw.line(ventana, NEGRO, (x_linea, y_linea), (x_linea + linea_largo, y_linea), linea_alto)
        # Mostrar progreso de puntuación
        porcentaje = int((puntaje_actual / puntaje_total) * 100) if puntaje_total > 0 else 0
        texto_puntos = FUENTE.render(f"Puntos:{puntaje_actual}/{puntaje_total} ({porcentaje}%)", True, NEGRO)
        ventana.blit(texto_puntos, (ANCHO - 420, ALTO - 30))  # Ajusta la posición si hace falta

        # Mostrar mensajes

        if mensaje_actual and pygame.time.get_ticks() - tiempo_mensaje_inicio < duracion_mensaje:
            texto = FUENTE.render(mensaje_actual, True, color_mensaje)
            ventana.blit(texto, (ANCHO // 2 - texto.get_width() // 2, 30))

        # Manejo de eventos
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                run = False
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                    if boton_borrar_palabra.collidepoint(mx, my):
                        seleccionados.clear()
                    elif boton_borrar_letra.collidepoint(mx, my) and seleccionados:
                        seleccionados.pop()
                    elif boton_aplicar.collidepoint(mx, my):
                        aplicar_palabra()
                    elif boton_menu.collidepoint(mx, my):
                        return
                    else:
                        for i, poligono in enumerate(hexagonos):
                            if punto_en_poligono(mx, my, poligono):
                                seleccionados.append(LETRAS[i])
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
    main()