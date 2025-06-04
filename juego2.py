import pygame
import const2
from boton import Boton
import LETRAS
import LEXIRETO


class Juego:
    def __init__(self):
        pygame.init()
        self.run, self.play = True, False
        self.Ancho, self.Largo = const2.width, const2.length
        pygame.display.set_caption('Palabrerío')
        self.ventana = pygame.display.set_mode((self.Ancho, self.Largo))

        # Fondo
        imagen_fon = pygame.image.load('imágenes/fondo3.png') #nombre del archivo imagen
        self.fon = pygame.transform.scale(imagen_fon, (const2.width, const2.length))  # ajustamos la imagen a la ventana

        # Fuente
        self.titulo_fuente = pygame.font.SysFont('PressStart2P-Regular', const2.tamano_letra_titulo)
        self.titulo_opciones = pygame.font.SysFont('PressStart2P-Regular', const2.tamano_letra_subtitulos)
        self.i = 0  # Posicion del fondo

        # Botones
        self.botones = [
            Boton('Lexireto', self.titulo_opciones, const2.blanco,
                  const2.color_opciones, const2.posicion_lexireto),
            Boton('Letras', self.titulo_opciones, const2.blanco,
                  const2.color_opciones, const2.posicion_letras),
            Boton('Cerrar Sesión', self.titulo_opciones, const2.blanco,
                  const2.color_opciones, const2.posicion_salir),
        ]

    def mover_fondo(self):
        """Actualiza la posición del fondo para el efecto de desplazamiento continuo."""
        # Decrementamos el índice para mover hacia la izquierda
        self.i -= 0.5

        # Reiniciar la posición del fondo cuando llegue al final
        if self.i <= -self.Ancho:
            self.i = 0

        # Dibujar el fondo en movimiento
        self.ventana.fill(const2.negro)
        self.ventana.blit(self.fon, (self.i, 0))
        self.ventana.blit(self.fon, (self.Ancho + self.i, 0))

    def bucle_juego (self):
        while self.play:
            self.check_eventos()
            #Mover el fondo
            self.mover_fondo()

            #Dibujar el título
            self.crea_titulo('PressStart2P-Regular', const2.nombre_juego,
                             const2.negro, const2.blanco, const2.posicion_titulo2, const2.posicion_titulo)

            # Obtener posición del mouse
            mouse_pos = pygame.mouse.get_pos()

            #Dibujar los botones
            for boton in self.botones:
                boton.dibujar(self.ventana, mouse_pos)

            pygame.display.update()

    def check_eventos(self):
        for eventos in pygame.event.get():
            if eventos.type == pygame.QUIT:
                self.run, self.play = False, False
                pygame.quit()
                quit()
            if eventos.type == pygame.MOUSEBUTTONDOWN and eventos.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                for boton in self.botones:
                    if boton.clic(mouse_pos):
                        if boton.texto == 'Lexireto':
                            self.ejecutar_lexireto()
                        elif boton.texto == 'Letras':
                            self.ejecutar_letras()
                        elif boton.texto == 'Cerrar Sesión':
                            self.run, self.play = False, False
                            pygame.quit()
                            quit()

    def ejecutar_lexireto(self):
        """Ejecuta el juego Lexireto"""
        self.play = False  # Pausamos el menú principal
        LEXIRETO.main()  # Ejecutamos Lexireto
        self.play = True  # Volvemos al menú principal al terminar
        # Restablecemos la pantalla
        self.ventana = pygame.display.set_mode((self.Ancho, self.Largo))

    def ejecutar_letras(self):
        """Ejecuta el juego Letras"""
        self.play = False  # Pausamos el menú principal
        LETRAS.jugar_sopa_letras()  # Ejecutamos Letras
        self.play = True  # Volvemos al menú principal al terminar
        # Restablecemos la pantalla
        self.ventana = pygame.display.set_mode((self.Ancho, self.Largo))

    def crea_titulo(self,letra, nombrejuego, colorsombra, colortitulo, posicionsombra, posiciontitulo):
        fuente_titulo = pygame.font.SysFont(letra, const2.tamano_letra_titulo)

        titulo1 = fuente_titulo.render(nombrejuego, True, colorsombra)
        self.ventana.blit(titulo1, posicionsombra)

        titulo = fuente_titulo.render(nombrejuego, True, colortitulo)
        self.ventana.blit(titulo, posiciontitulo)

