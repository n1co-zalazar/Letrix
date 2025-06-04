import sys
import pygame
import math
import random
import itertools
import const

pygame.init()
# Configuración inicial
ANCHO = 800
ALTO = 600
BLANCO = const2.blanco
NEGRO = const2.negro
AMARILLO = const2.amarillo
GRIS = const2.gris
AZUL = const2.azul
ROJO = const2.rojo
NARANJA = const2.naranja
VERDE = const.verde
scroll_offset = 0
FUENTE = pygame.font.Font("PressStart2P-Regular.ttf", 17)
FUENTE_BOTON = pygame.font.Font("PressStart2P-Regular.ttf", 12)
ventana = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Lexireto")
seleccionados = []
reloj = pygame.time.Clock()

def generar_letras_validas(diccionario_path):
    # Cargar el diccionario una sola vez
    with open(diccionario_path, "r", encoding="utf-8") as f:
        palabras = [line.strip().upper() for line in f if len(line.strip()) >= 3 and line.strip().isalpha()]

    # Precalcular letras usadas en palabras pangramáticas
    pangramas = [p for p in palabras if len(set(p)) >= 7]
    if not pangramas:
        return None, None, set()

    # Tomar un pangrama aleatorio como base
    pangrama = random.choice(pangramas)
    letras = list(set(pangrama))
    random.shuffle(letras)
    letras = letras[:7]  # Asegurar que sean exactamente 7 letras

    # Elegir una letra central (que aparezca en la mayoría de palabras)
    letra_central = max(letras, key=lambda l: sum(l in p for p in palabras))

    # Filtrar palabras válidas
    letras_set = set(letras)
    palabras_validas_ = {
        p for p in palabras
        if len(p) >= 3 and letra_central in p and set(p).issubset(letras_set)
    }

    return letras, letra_central, palabras_validas_

# Cargar letras válidas
LETRAS, LETRA_CENTRAL, palabras_validas = generar_letras_validas("diccionario_sin_acentos.txt")
if not LETRAS:
    print("No se pudo generar un conjunto válido de letras.")
    sys.exit()

# Asegurar que la letra central esté en la primera posición
if LETRA_CENTRAL in LETRAS:
    LETRAS.remove(LETRA_CENTRAL)
    LETRAS.insert(0, LETRA_CENTRAL)

# Mostrar letras y palabras válidas al inicio
print("\n=== Palabras válidas para esta ronda ===")
print(f"Letras disponibles: {', '.join(LETRAS)}")
print(f"Letra central requerida: {LETRA_CENTRAL}\n")
print("Lista completa de palabras válidas:")
for i, palabra in enumerate(sorted(palabras_validas), 1):
    print(f"{i}. {palabra}")
print(f"\nTotal: {len(palabras_validas)} palabras válidas.\n")


# Inicializar palabras encontradas
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

# Funciones de dibujo
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

# Funciones de lógica del juego
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
        mostrar_mensaje("¡Palabra aceptada!", VERDE)
        return True

    mostrar_mensaje("Palabra no válida", (200, 0, 0))
    return False

def dibujar_palabras_encontradas():
    global scroll_offset
    x_inicio, y_inicio = 680, 20
    area_altura = 500
    contenido_altura = sum(30 + len(info['palabras']) * 25 + 15 for info in palabras_encontradas.values())
    
    scroll_offset = max(0, min(scroll_offset, contenido_altura - area_altura))
    superficie_contenido = pygame.Surface((200, contenido_altura))
    superficie_contenido.fill(BLANCO)
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
        pygame.draw.rect(ventana, GRIS, (880, y_inicio + barra_pos, 10, barra_height))

# Variables para mensajes
mensaje_actual = ""
color_mensaje = NEGRO
tiempo_mensaje_inicio = 0
duracion_mensaje = 2000

def mostrar_mensaje(mensaje, color):
    global mensaje_actual, color_mensaje, tiempo_mensaje_inicio
    mensaje_actual = mensaje
    color_mensaje = color
    tiempo_mensaje_inicio = pygame.time.get_ticks()

def main():
    global scroll_offset, mensaje_actual, color_mensaje, tiempo_mensaje_inicio
    
    cx, cy = ANCHO // 2, ALTO // 2
    radio = 60
    distancia = radio * 2 * math.cos(math.radians(30))
    posiciones = obtener_posiciones_hexagonos(cx, cy, distancia)
    hexagonos = [obtener_puntos_hexagono(x, y, radio) for (x, y) in posiciones]
    tiempo_inicio = pygame.time.get_ticks()
    run = True

    while run:
        ventana.fill(BLANCO)
        mx, my = pygame.mouse.get_pos()

        # Dibujar palabra actual
        texto_palabra = FUENTE.render("Palabra: " + "".join(seleccionados), True, NEGRO)
        ventana.blit(texto_palabra, (70, 90))

        # Dibujar hexágonos
        for i, (x, y) in enumerate(posiciones):
            puntos = hexagonos[i]
            letra_actual = LETRAS[i]
            
            if punto_en_poligono(mx, my, puntos):
                color = AZUL
            elif i == 0:  # Hexágono central
                color = AMARILLO
            else:
                color = BLANCO

            pygame.draw.polygon(ventana, color, puntos)
            pygame.draw.polygon(ventana, NEGRO, puntos, 2)
            texto = FUENTE.render(letra_actual, True, NEGRO)
            rect = texto.get_rect(center=(x, y))
            ventana.blit(texto, rect)

        # Dibujar botones
        boton_borrar_palabra = dibujar_boton("Borrar palabra", 130, 500, 180, 40, (mx, my))
        boton_borrar_letra = dibujar_boton("Borrar letra", 490, 500, 160, 40, (mx, my))
        boton_aplicar = dibujar_boton("Aplicar", 340, 500, 120, 40, (mx, my))
        
        # Dibujar palabras encontradas
        dibujar_palabras_encontradas()

        # Mostrar tiempo
        tiempo_actual = pygame.time.get_ticks()
        tiempo_transcurrido = (tiempo_actual - tiempo_inicio) // 1000
        texto_tiempo = FUENTE.render(f"Tiempo: {tiempo_transcurrido // 60:02d}:{tiempo_transcurrido % 60:02d}", True, NEGRO)
        ventana.blit(texto_tiempo, (10, 570))

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

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()