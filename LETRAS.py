import pygame
import random
import sys
import time
from collections import defaultdict
from const2 import *


def jugar_sopa_letras(palabras=None, filas=7, columnas=7, tam_celda=65):
    """Función principal del juego de Sopa de Letras"""

    # Configuración del juego
    NUM_PALABRAS = 8
    MARGEN_DERECHO = 400
    MARGEN_INFERIOR = 150
    DIRECCIONES = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    # Cargar palabras si no se proporcionan
    def cargar_palabras_desde_archivo(nombre_archivo):
        try:
            with open(nombre_archivo, "r", encoding="utf-8") as f:
                return [linea.strip() for linea in f if linea.strip() and len(linea.strip()) >= 3]
        except FileNotFoundError:
            print(f"Error: No se encontró el archivo {nombre_archivo}")
            return ["PYTHON", "PROGRAMA", "SERPIENTE", "JUEGO", "CODIGO", "TECLADO", "VENTANA",
                    "COMPUTADORA"]  # Palabras por defecto

    if palabras is None:
        palabras = cargar_palabras_desde_archivo("diccionario_sin_acentos.txt")

    if len(palabras) < NUM_PALABRAS:
        print(f"Error: No hay suficientes palabras de 3+ letras. Necesitas al menos {NUM_PALABRAS}.")
        return

    # Inicializar Pygame
    pygame.init()
    screen = pygame.display.set_mode((width, length))
    fondo = pygame.image.load("imágenes/fondo3.png").convert()
    fondo = pygame.transform.scale(fondo, (width, length))
    reloj = pygame.image.load("imágenes/time.png").convert()
    reloj = pygame.transform.scale(reloj, (140, 130))

    # Configurar márgenes y calcular tamaño de celda dinámico
    MARGEN_DERECHO = 400
    MARGEN_INFERIOR = 150

    tam_celda_w = (width - MARGEN_DERECHO) // columnas
    tam_celda_h = (length - MARGEN_INFERIOR) // filas
    tam_celda = min(tam_celda_w, tam_celda_h)

    # Calcular offset para centrar matriz
    offset_x = (width - MARGEN_DERECHO - columnas * tam_celda) // 2
    offset_y = 30 + (length - MARGEN_INFERIOR - filas * tam_celda) // 2

    fuente = pygame.font.SysFont('Arial', 36)
    fuente_celda = pygame.font.SysFont('Arial', tam_celda - 15)
    clock = pygame.time.Clock()

    # Funciones auxiliares
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

        segundos = int(time.time() - inicio_tiempo)
        tiempo_total = int(time.time() - inicio_tiempo)
        horas = tiempo_total // 3600
        minutos = (tiempo_total % 3600) // 60
        segundos = tiempo_total % 60
        tiempo_formateado = f"{horas:01}:{minutos:02}:{segundos:02}"

        fuente = pygame.font.Font('letras/letraproyecto.ttf', 20)
        texto_tiempo = fuente.render(f"WARNING",
                                     True, rojo)

        fuente_time = pygame.font.Font('letras/letraproyecto.ttf', 10)

        numero_tiempo = fuente_time.render(str(tiempo_formateado), True, negro)
        screen.blit(numero_tiempo, (48, 130))

        texto_encontradas = fuente.render(f"Encontradas: {len(palabras_encontradas)}/{len(PALABRAS)}", True, negro)
        screen.blit(texto_tiempo, (15, 30))
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
                if palabra in palabras_encontradas or resolver:  # Cambio clave aquí
                    texto = fuente.render(palabra, True, verde)
                else:
                    texto = fuente.render(f"{palabra[0]} {'-' * (longitud - 1)}", True, negro)
                screen.blit(texto, (x_base + 20, y_base + 5))
                y_base += 30
            y_base += 20

        # Dibujar botón Resolver con efecto hover


        mouse_pos = pygame.mouse.get_pos()

        boton_menu = pygame.Rect(12, 210, 170, 45)
        hover_menu = boton_menu.collidepoint(mouse_pos)
        color_menu = (200, 200, 200) if hover_menu else blanco
        pygame.draw.rect(screen, color_menu, boton_menu)
        pygame.draw.rect(screen, negro, boton_menu, 2)

        texto_menu = fuente.render("Pausa", True, negro)
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
        return  boton_menu, boton_SALIR

    def mostrar_pausa_con_resolver():
        pausa_ancho = width // 2
        pausa_alto = length // 2
        pausa_x = (width - pausa_ancho) // 2
        pausa_y = (length - pausa_alto) // 2

        pausa_ventana = pygame.Surface((pausa_ancho, pausa_alto), pygame.SRCALPHA)
        pausa_ventana.set_alpha(240)
        pausa_ventana.fill((220, 220, 220))  # gris claro

        fuente = pygame.font.Font('letras/letraproyecto.ttf', 24)

        boton_resolver = pygame.Rect(pausa_x + 30, pausa_y + 30, pausa_ancho - 60, 50)
        boton_reglas = pygame.Rect(pausa_x + 30, pausa_y + 100, pausa_ancho - 60, 50)
        boton_volver = pygame.Rect(pausa_x + 30, pausa_y + 170, pausa_ancho - 60, 50)

        resolviendo = False
        esperando = True
        while esperando:
            screen.blit(fondo, (0, 0))
            screen.blit(pausa_ventana, (pausa_x, pausa_y))

            mouse_pos = pygame.mouse.get_pos()

            # Dibujar botones
            for boton, texto in [(boton_resolver, "Resolver"),
                                 (boton_reglas, "Reglas"),
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
                        # Dibujar la pantalla con todas las palabras en verde
                        for _ in range(30):  # Mostrar durante aproximadamente 1 segundo (30 frames)
                            dibujar(matriz, seleccionadas, resolver=True)
                            pygame.display.flip()
                            pygame.time.delay(110)  # ~30 FPS

                        # Luego ir a la pantalla final
                        resultado = pantalla_fin()
                        if resultado == "salir":
                            pygame.quit()
                            sys.exit()
                        else:
                            corriendo = False
                            break
                    elif boton_volver.collidepoint(mouse_pos):
                        esperando = False



    def mostrar_reglas():
        reglas_fondo = pygame.Surface((width, length))
        reglas_fondo.fill(negro)
        fuente = pygame.font.Font('letras/letraproyecto.ttf', 20)
        fuente2 = pygame.font.Font('letras/letraproyecto.ttf', 20)
        instruccionesventana = [
            "---------------------------------------------------------------------------",
            "                      REGLAS DEL JUEGO LETRAS                              "
            ,"---------------------------------------------------------------------------"
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
            for linea in instruccionesventana:
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
    def obtener_celda(pos):
        x, y = pos
        col = (x - offset_x) // tam_celda
        fila = (y - offset_y) // tam_celda
        if fila < 0 or col < 0 or fila >= filas or col >= columnas:
            return None
        return fila, col

    def menu_inicio():
        screen.blit(fondo, (0, 0))
        pygame.display.flip()
        return True

    def pantalla_fin():
        screen.blit(fondo, (0, 0))
        tiempo_final = int(time.time() - inicio_tiempo)
        fuente_grande = pygame.font.Font('letras/letraproyecto.ttf', 30)
        fuente_mediana = pygame.font.Font('letras/letraproyecto.ttf', 20)
        fuente_pequena = pygame.font.Font('letras/letraproyecto.ttf', 16)

        mensaje = fuente_grande.render("¡FELICIDADES!", True, verde)
        subtitulo = fuente_mediana.render("Encontraste todas las palabras", True, negro)
        tiempo = fuente_mediana.render(f"Tiempo total: {tiempo_final} segundos", True, negro)
        instruccion = fuente_pequena.render("¿Quieres volver a jugar?", True, negro)

        # Posiciones de los textos
        screen.blit(mensaje, (width // 2 - mensaje.get_width() // 2, length // 2 - 120))
        screen.blit(subtitulo, (width // 2 - subtitulo.get_width() // 2, length // 2 - 70))
        screen.blit(tiempo, (width // 2 - tiempo.get_width() // 2, length // 2 - 30))
        screen.blit(instruccion, (width // 2 - instruccion.get_width() // 2, length // 2 + 20))

        # Crear botones
        boton_si = pygame.Rect(width // 2 - 150, length // 2 + 60, 120, 50)
        boton_no = pygame.Rect(width // 2 + 30, length // 2 + 60, 120, 50)

        esperando = True
        while esperando:
            mouse_pos = pygame.mouse.get_pos()
            hover_si = boton_si.collidepoint(mouse_pos)
            hover_no = boton_no.collidepoint(mouse_pos)

            # Dibujar fondo nuevamente para limpiar los botones anteriores
            screen.blit(fondo, (0, 0))
            # Volver a dibujar todos los elementos estáticos
            screen.blit(mensaje, (width // 2 - mensaje.get_width() // 2, length // 2 - 120))
            screen.blit(subtitulo, (width // 2 - subtitulo.get_width() // 2, length // 2 - 70))
            screen.blit(tiempo, (width // 2 - tiempo.get_width() // 2, length // 2 - 30))
            screen.blit(instruccion, (width // 2 - instruccion.get_width() // 2, length // 2 + 20))

            # Dibujar botones con efecto hover actualizado
            color_boton_si = (200, 200, 200) if hover_si else blanco
            color_boton_no = (200, 200, 200) if hover_no else blanco

            pygame.draw.rect(screen, color_boton_si, boton_si)
            pygame.draw.rect(screen, negro, boton_si, 2)
            pygame.draw.rect(screen, color_boton_no, boton_no)
            pygame.draw.rect(screen, negro, boton_no, 2)

            texto_si = fuente_pequena.render("Sí", True, negro)
            texto_no = fuente_pequena.render("No", True, negro)

            screen.blit(texto_si, (boton_si.centerx - texto_si.get_width() // 2,
                                   boton_si.centery - texto_si.get_height() // 2))
            screen.blit(texto_no, (boton_no.centerx - texto_no.get_width() // 2,
                                   boton_no.centery - texto_no.get_height() // 2))

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "salir"
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if boton_si.collidepoint(mouse_pos):
                        return "reiniciar"
                    elif boton_no.collidepoint(mouse_pos):
                        return "salir"


            clock.tick(30)

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
            print(f"Advertencia: Solo se colocaron {len(rutas)} de {cantidad_objetivo} palabras")

        rellenar_espacios(matriz)
        return matriz, rutas

    def son_adyacentes(celdas):
        for i in range(len(celdas) - 1):
            f1, c1 = celdas[i]
            f2, c2 = celdas[i + 1]
            if abs(f1 - f2) + abs(c1 - c2) != 1:
                return False
        return True

    # Bucle principal del juego
    while True:
        # Iniciar el juego
        if not menu_inicio():
            pygame.quit()
            sys.exit()

        try:
            matriz, rutas_palabras = generar_sopa_serpiente_superpuesta(palabras, NUM_PALABRAS)
            PALABRAS = list(rutas_palabras.keys())
        except Exception as e:
            print(f"Error al generar la sopa de letras: {e}")
            pygame.quit()
            sys.exit()

        seleccionadas = []
        palabras_encontradas = []
        inicio_tiempo = time.time()

        corriendo = True
        while corriendo:
            boton_menu,boton_SALIR= dibujar(matriz, seleccionadas, resolver=False)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if boton_menu.collidepoint(event.pos):
                        mostrar_pausa_con_resolver()
                    elif boton_SALIR.collidepoint(event.pos):
                        return
                    celda = obtener_celda(pygame.mouse.get_pos())
                    if celda and celda not in seleccionadas:
                        if not seleccionadas or any(
                                abs(celda[0] - f) + abs(celda[1] - c) == 1 for f, c in [seleccionadas[-1]]):
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

            if len(palabras_encontradas) == len(PALABRAS):
                # Mostrar todas las palabras encontradas primero
                for _ in range(30):  # Mostrar durante aproximadamente 1 segundo (30 frames)
                    dibujar(matriz, seleccionadas, resolver=True)
                    pygame.display.flip()
                    pygame.time.delay(110)  # ~30 FPS

                resultado = pantalla_fin()
                if resultado == "salir":
                    pygame.quit()
                    sys.exit()
                else:
                    corriendo = False
                    continue

            clock.tick(30)


