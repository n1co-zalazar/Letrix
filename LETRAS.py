import pygame
import random
import sys
import time
import os
import json
from collections import defaultdict
from const2 import *
from juego2 import *
from guardado import guardar_partida as guardar_partida_global, cargar_partida as cargar_partida_global


def jugar_sopa_letras(username=None, palabras=None, filas=7, columnas=7, tam_celda=60):
    """Función principal del juego de Sopa de Letras con guardado por usuario"""

    # Configuración del juego
    NUM_PALABRAS = 8
    DIRECCIONES = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    # Cargar palabras si no se proporcionan
    def cargar_palabras_desde_archivo(nombre_archivo):
        try:
            with open(nombre_archivo, "r", encoding="utf-8") as f:
                return [linea.strip() for linea in f if linea.strip() and len(linea.strip()) >= 3]
        except FileNotFoundError:
            print(f"Error: No se encontró el archivo {nombre_archivo}")
            return ["PYTHON", "PROGRAMA", "SERPIENTE", "JUEGO", "CODIGO", "TECLADO", "VENTANA", "COMPUTADORA"]

    if palabras is None:
        palabras = cargar_palabras_desde_archivo("diccionario_sin_acentos.txt")

    if len(palabras) < NUM_PALABRAS:
        print(f"Error: No hay suficientes palabras. Necesitas al menos {NUM_PALABRAS}.")
        return

    # Inicializar Pygame
    pygame.init()
    screen = pygame.display.set_mode((width, length))
    fondo = pygame.image.load("imágenes/fondo3.png").convert()
    fondo = pygame.transform.scale(fondo, (width, length))
    reloj = pygame.image.load("imágenes/time.png").convert()
    reloj = pygame.transform.scale(reloj, (140, 130))

    # Configuración visual
    MARGEN_DERECHO = 400
    MARGEN_INFERIOR = 150
    tam_celda_w = (width - MARGEN_DERECHO) // columnas
    tam_celda_h = (length - MARGEN_INFERIOR) // filas
    tam_celda = min(tam_celda_w, tam_celda_h)
    offset_x = (width - MARGEN_DERECHO - columnas * tam_celda) // 2
    offset_y = 30 + (length - MARGEN_INFERIOR - filas * tam_celda) // 2

    fuente = pygame.font.SysFont('Arial', 36)
    fuente_celda = pygame.font.SysFont('Arial', tam_celda - 15)
    clock = pygame.time.Clock()

    # Funciones auxiliares del juego
    def crear_matriz(filas, columnas):
        return [[" " for _ in range(columnas)] for _ in range(filas)]

    def es_valido(fila, col):
        return 0 <= fila < filas and 0 <= col < columnas

    def puede_colocar(matriz, fila, col, letra):
        return es_valido(fila, col) and (matriz[fila][col] == " " or matriz[fila][col] == letra)

    def buscar_ruta_serpiente(matriz, palabra, index, fila, col, visitados):
        if index == len(palabra):
            return []

        letra = palabra[index]
        for dx, dy in random.sample(DIRECCIONES, len(DIRECCIONES)):
            nf, nc = fila + dx, col + dy
            if puede_colocar(matriz, nf, nc, letra) and (nf, nc) not in visitados:
                visitados.add((nf, nc))
                sub_ruta = buscar_ruta_serpiente(matriz, palabra, index + 1, nf, nc, visitados)
                if sub_ruta is not None:
                    return [(nf, nc)] + sub_ruta
                visitados.remove((nf, nc))
        return None

    def intentar_colocar_palabra(matriz, palabra):
        palabra = palabra.upper()
        for fila in range(filas):
            for col in range(columnas):
                if puede_colocar(matriz, fila, col, palabra[0]):
                    visitados = {(fila, col)}
                    ruta = buscar_ruta_serpiente(matriz, palabra, 1, fila, col, visitados)
                    if ruta is not None:
                        ruta_completa = [(fila, col)] + ruta
                        for (f, c), letra in zip(ruta_completa, palabra):
                            matriz[f][c] = letra
                        return ruta_completa
        return None

    def rellenar_espacios(matriz):
        letras = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        for i in range(filas):
            for j in range(columnas):
                if matriz[i][j] == " ":
                    matriz[i][j] = random.choice(letras)

    def generar_sopa_serpiente_superpuesta(lista_palabras, cantidad_objetivo):
        matriz = crear_matriz(filas, columnas)
        rutas = {}
        usadas = set()
        intentos = 0
        max_intentos = 1000

        while len(rutas) < cantidad_objetivo and intentos < max_intentos:
            palabra = random.choice(lista_palabras).upper()
            if palabra in usadas:
                intentos += 1
                continue

            ruta = intentar_colocar_palabra(matriz, palabra)
            if ruta:
                rutas[palabra] = ruta
                usadas.add(palabra)
            intentos += 1

        if len(rutas) < cantidad_objetivo:
            print(f"Solo se colocaron {len(rutas)} de {cantidad_objetivo} palabras")

        rellenar_espacios(matriz)
        return matriz, rutas

    def son_adyacentes(celdas):
        for i in range(len(celdas) - 1):
            f1, c1 = celdas[i]
            f2, c2 = celdas[i + 1]
            if abs(f1 - f2) + abs(c1 - c2) != 1:
                return False
        return True

    # Funciones de guardado y carga
    def guardar_partida(matriz, palabras_encontradas, PALABRAS, rutas_palabras, inicio_tiempo, username):
        """Guarda la partida actual en un archivo JSON para el usuario"""
        datos = {
            'matriz': matriz,
            'palabras_encontradas': palabras_encontradas,
            'PALABRAS': PALABRAS,
            'rutas_palabras': {k: list(v) for k, v in rutas_palabras.items()},
            'tiempo_transcurrido': time.time() - inicio_tiempo
        }
        return guardar_partida_global(username, "letras", datos)



    def cargar_partida(username):
        """Carga una partida guardada para un usuario específico"""
        estado = cargar_partida_global(username, "letras")
        if estado:
            estado['rutas_palabras'] = {k: [tuple(c) for c in v] for k, v in estado['rutas_palabras'].items()}
        return estado

    # Funciones de interfaz gráfica
    def dibujar(matriz, seleccionadas, resolver=False):
        fuente = pygame.font.Font('letras/letraproyecto.ttf', 20)
        screen.blit(fondo, (0, 0))
        screen.blit(reloj, (17, 60))

        # Dibujar matriz
        for i in range(filas):
            for j in range(columnas):
                letra = matriz[i][j]
                x, y = offset_x + j * tam_celda, offset_y + i * tam_celda
                rect = pygame.Rect(x, y, tam_celda, tam_celda)

                if (i, j) in seleccionadas:
                    pygame.draw.rect(screen, azul, rect)
                else:
                    pygame.draw.rect(screen, negro, rect, 1)

                texto = fuente_celda.render(letra, True, negro)
                text_rect = texto.get_rect(center=rect.center)
                screen.blit(texto, text_rect)

        # Información del juego
        palabra_actual = "".join([matriz[i][j] for i, j in seleccionadas])
        texto_palabra = fuente.render(f"Palabra actual: {palabra_actual}", True, rojo)
        screen.blit(texto_palabra, (200, length - 80))

        # Tiempo transcurrido
        tiempo_total = int(time.time() - inicio_tiempo)
        horas = tiempo_total // 3600
        minutos = (tiempo_total % 3600) // 60
        segundos = tiempo_total % 60
        tiempo_formateado = f"{horas:01}:{minutos:02}:{segundos:02}"

        fuente_time = pygame.font.Font('letras/letraproyecto.ttf', 10)
        numero_tiempo = fuente_time.render(str(tiempo_formateado), True, negro)
        screen.blit(numero_tiempo, (48, 130))

        texto_encontradas = fuente.render(f"Encontradas: {len(palabras_encontradas)}/{len(PALABRAS)}", True, negro)
        screen.blit(texto_encontradas, (850, length - 80))

        # Panel de palabras
        x_base = offset_x + columnas * tam_celda + 40
        y_base = 30
        titulo_panel = fuente.render("Palabras a encontrar:", True, negro)
        screen.blit(titulo_panel, (x_base, y_base))
        y_base += 60

        palabras_por_longitud = defaultdict(list)
        for palabra in PALABRAS:
            palabras_por_longitud[len(palabra)].append(palabra)

        for longitud in sorted(palabras_por_longitud.keys(), reverse=True):
            texto_longitud = fuente.render(f"Palabras de {longitud} letras:", True, negro)
            screen.blit(texto_longitud, (x_base, y_base))
            y_base += 30

            for palabra in palabras_por_longitud[longitud]:
                if palabra in palabras_encontradas or resolver:
                    texto = fuente.render(palabra, True, verde)
                else:
                    texto = fuente.render(f"{palabra[0]} {'-' * (longitud - 1)}", True, negro)
                screen.blit(texto, (x_base + 20, y_base + 5))
                y_base += 30
            y_base += 20

        # Botones
        mouse_pos = pygame.mouse.get_pos()

        boton_menu = pygame.Rect(12, 210, 170, 45)
        hover_menu = boton_menu.collidepoint(mouse_pos)
        color_menu = (200, 200, 200) if hover_menu else blanco
        pygame.draw.rect(screen, color_menu, boton_menu)
        pygame.draw.rect(screen, negro, boton_menu, 2)

        texto_menu = fuente.render("Opciones", True, negro)
        screen.blit(texto_menu, (boton_menu.centerx - texto_menu.get_width() // 2,
                                 boton_menu.centery - texto_menu.get_height() // 2))

        boton_SALIR = pygame.Rect(12, 270, 170, 45)
        hover_SALIR = boton_SALIR.collidepoint(mouse_pos)
        color_SALIR = (200, 200, 200) if hover_SALIR else blanco
        pygame.draw.rect(screen, color_SALIR, boton_SALIR)
        pygame.draw.rect(screen, negro, boton_SALIR, 2)

        texto_SALIR = fuente.render("Volver", True, negro)
        screen.blit(texto_SALIR, (boton_SALIR.centerx - texto_SALIR.get_width() // 2,
                                  boton_SALIR.centery - texto_SALIR.get_height() // 2))

        pygame.display.flip()
        return boton_menu, boton_SALIR

    def mostrar_pausa_con_resolver(username):
        """Muestra el menú de pausa con opciones"""
        pausa_ancho = width // 2
        pausa_alto = length // 2
        pausa_x = (width - pausa_ancho) // 2
        pausa_y = (length - pausa_alto) // 2

        pausa_ventana = pygame.Surface((pausa_ancho, pausa_alto), pygame.SRCALPHA)
        pausa_ventana.set_alpha(240)
        pausa_ventana.fill((220, 220, 220))

        fuente = pygame.font.Font('letras/letraproyecto.ttf', 24)

        boton_resolver = pygame.Rect(pausa_x + 30, pausa_y + 30, pausa_ancho - 60, 50)
        boton_reglas = pygame.Rect(pausa_x + 30, pausa_y + 100, pausa_ancho - 60, 50)
        boton_guardar = pygame.Rect(pausa_x + 30, pausa_y + 170, pausa_ancho - 60, 50)
        boton_volver = pygame.Rect(pausa_x + 30, pausa_y + 240, pausa_ancho - 60, 50)

        esperando = True
        while esperando:
            screen.blit(fondo, (0, 0))
            screen.blit(pausa_ventana, (pausa_x, pausa_y))

            mouse_pos = pygame.mouse.get_pos()

            for boton, texto in [(boton_resolver, "Resolver"),
                                 (boton_reglas, "Reglas"),
                                 (boton_guardar, "Guardar Partida"),
                                 (boton_volver, "Regresar")]:
                hover = boton.collidepoint(mouse_pos)
                color = (200, 200, 200) if hover else blanco
                pygame.draw.rect(screen, color, boton, border_radius=5)
                pygame.draw.rect(screen, negro, boton, 2, border_radius=5)
                texto_render = fuente.render(texto, True, negro)
                screen.blit(texto_render, texto_render.get_rect(center=boton.center))

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if boton_reglas.collidepoint(mouse_pos):
                        mostrar_reglas()
                    elif boton_resolver.collidepoint(mouse_pos):
                        for _ in range(30):
                            dibujar(matriz, seleccionadas, resolver=True)
                            pygame.display.flip()
                            pygame.time.delay(110)
                    elif boton_guardar.collidepoint(mouse_pos):
                        guardar_partida(matriz, palabras_encontradas, PALABRAS, rutas_palabras, inicio_tiempo, username)
                    elif boton_volver.collidepoint(mouse_pos):
                        esperando = False

    def mostrar_reglas():
        """Muestra las reglas del juego"""
        reglas_fondo = pygame.Surface((width, length))
        reglas_fondo.fill(negro)
        fuente = pygame.font.Font('letras/letraproyecto.ttf', 20)

        instrucciones = [
            "---------------------------------------------------------------------------",
            "                      REGLAS DEL JUEGO LETRAS                              ",
            "---------------------------------------------------------------------------",
            "- Encuentra palabras seleccionando letras contiguas",
            "- Puedes usar cada letra en múltiples palabras",
            "- No se permiten diagonales",
            "-----------------------------ATENCIÓN---------------------------------------",
            "No todas las palabras formadas serán válidas",
            "Solo cuentan las palabras propuestas"
        ]

        boton_cerrar = pygame.Rect(width // 2 - 80, length - 100, 160, 50)
        esperando = True

        while esperando:
            screen.blit(reglas_fondo, (0, 0))
            y = 30

            for linea in instrucciones:
                texto = fuente.render(linea, True, verde)
                screen.blit(texto, (20, y))
                y += 55

            mouse_pos = pygame.mouse.get_pos()
            hover_cerrar = boton_cerrar.collidepoint(mouse_pos)
            color_cerrar = (200, 200, 200) if hover_cerrar else (255, 255, 255)

            pygame.draw.rect(screen, color_cerrar, boton_cerrar)
            pygame.draw.rect(screen, negro, boton_cerrar, 2)

            texto_cerrar = fuente.render("Cerrar", True, negro)
            screen.blit(texto_cerrar, (boton_cerrar.centerx - texto_cerrar.get_width() // 2,
                                       boton_cerrar.centery - texto_cerrar.get_height() // 2))

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if boton_cerrar.collidepoint(mouse_pos):
                        esperando = False

    def menu_inicio_con_opciones(username):
        """Muestra el menú inicial con opciones de nueva partida o continuar"""
        fuente = pygame.font.Font('letras/letraproyecto.ttf', 15)
        fuente_botones = pygame.font.Font('letras/letraproyecto.ttf', 15)

        boton_nueva = pygame.Rect(width // 2 - 150, length // 2 - 50, 300, 50)
        boton_cargar = pygame.Rect(width // 2 - 150, length // 2 + 20, 300, 50)

        partida_guardada = cargar_partida(username) if username else None

        while True:
            screen.blit(fondo, (0, 0))

            titulo = fuente.render("SOPA DE LETRAS", True, negro)
            screen.blit(titulo, (width // 2 - titulo.get_width() // 2, length // 3))

            # Dibujar botones
            mouse_pos = pygame.mouse.get_pos()

            for boton, texto, habilitado in [(boton_nueva, "Nueva Partida", True),
                                             (boton_cargar, "Continuar Partida", partida_guardada is not None)]:
                color = (200, 200, 200) if boton.collidepoint(mouse_pos) and habilitado else (
                    blanco if habilitado else (150, 150, 150))
                pygame.draw.rect(screen, color, boton, border_radius=5)
                pygame.draw.rect(screen, negro, boton, 2, border_radius=5)

                texto_render = fuente_botones.render(texto, True, negro if habilitado else (100, 100, 100))
                screen.blit(texto_render, texto_render.get_rect(center=boton.center))

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if boton_nueva.collidepoint(mouse_pos):
                        return None  # Indicar que se quiere una partida nueva
                    elif boton_cargar.collidepoint(mouse_pos) and partida_guardada:
                        return partida_guardada  # Devolver el estado guardado

    def pantalla_fin():
        """Muestra la pantalla de finalización del juego"""
        tiempo_final = int(time.time() - inicio_tiempo)
        fuente_grande = pygame.font.Font('letras/letraproyecto.ttf', 30)
        fuente_mediana = pygame.font.Font('letras/letraproyecto.ttf', 20)

        mensaje = fuente_grande.render("¡FELICIDADES!", True, verde)
        subtitulo = fuente_mediana.render("Encontraste todas las palabras", True, negro)
        tiempo = fuente_mediana.render(f"Tiempo total: {tiempo_final} segundos", True, negro)

        while True:
            screen.blit(fondo, (0, 0))
            screen.blit(mensaje, (width // 2 - mensaje.get_width() // 2, length // 2 - 120))
            screen.blit(subtitulo, (width // 2 - subtitulo.get_width() // 2, length // 2 - 70))
            screen.blit(tiempo, (width // 2 - tiempo.get_width() // 2, length // 2 - 30))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "salir"
                elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    return "continuar"

            pygame.display.flip()
            clock.tick(30)

    def obtener_celda(pos):
        """Obtiene la celda de la matriz basada en la posición del mouse"""
        x, y = pos
        col = (x - offset_x) // tam_celda
        fila = (y - offset_y) // tam_celda
        if fila < 0 or col < 0 or fila >= filas or col >= columnas:
            return None
        return fila, col

    # Bucle principal del juego
    while True:
        # Mostrar menú con opciones (pasando el username)
        estado_guardado = menu_inicio_con_opciones(username)

        if estado_guardado:  # Cargar partida existente
            try:
                matriz = estado_guardado['matriz']
                palabras_encontradas = estado_guardado['palabras_encontradas']
                PALABRAS = estado_guardado['PALABRAS']
                rutas_palabras = estado_guardado['rutas_palabras']
                inicio_tiempo = time.time() - estado_guardado['tiempo_transcurrido']
            except KeyError as e:
                print(f"Error en datos de partida guardada: {e}")
                # Crear nueva partida si hay error
                matriz, rutas_palabras = generar_sopa_serpiente_superpuesta(palabras, NUM_PALABRAS)
                PALABRAS = list(rutas_palabras.keys())
                palabras_encontradas = []
                inicio_tiempo = time.time()
        else:  # Nueva partida
            try:
                matriz, rutas_palabras = generar_sopa_serpiente_superpuesta(palabras, NUM_PALABRAS)
                PALABRAS = list(rutas_palabras.keys())
                palabras_encontradas = []
                inicio_tiempo = time.time()
            except Exception as e:
                print(f"Error al generar la sopa de letras: {e}")
                pygame.quit()
                sys.exit()

        seleccionadas = []
        corriendo = True

        # Bucle del juego
        while corriendo:
            boton_menu, boton_SALIR = dibujar(matriz, seleccionadas, resolver=False)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if boton_menu.collidepoint(event.pos):
                        mostrar_pausa_con_resolver(username)
                    elif boton_SALIR.collidepoint(event.pos):
                        return
                    celda = obtener_celda(pygame.mouse.get_pos())
                    if celda and celda not in seleccionadas:
                        if not seleccionadas or any(abs(celda[0] - f) + abs(celda[1] - c) == 1
                                                    for f, c in [seleccionadas[-1]]):
                            seleccionadas.append(celda)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        palabra_actual = "".join(matriz[i][j] for i, j in seleccionadas)
                        if son_adyacentes(seleccionadas):
                            for palabra, ruta in rutas_palabras.items():
                                if palabra_actual == palabra and palabra not in palabras_encontradas:
                                    palabras_encontradas.append(palabra)
                                    break
                        seleccionadas = []
                    elif event.key == pygame.K_BACKSPACE:
                        if seleccionadas:
                            seleccionadas.pop()

            # Comprobar si se encontraron todas las palabras
            if len(palabras_encontradas) == len(PALABRAS):
                # Mostrar solución
                for _ in range(30):
                    dibujar(matriz, seleccionadas, resolver=True)
                    pygame.display.flip()
                    pygame.time.delay(110)

                resultado = pantalla_fin()
                if resultado == "salir":
                    pygame.quit()
                    sys.exit()
                else:
                    corriendo = False  # Volver al menú principal

            clock.tick(30)
