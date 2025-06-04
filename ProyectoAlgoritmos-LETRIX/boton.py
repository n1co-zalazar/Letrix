import pygame

import const2


class Boton:
    def __init__(self,texto, fuente, color_normal, color_hover, posicion):
       self.texto = texto
       self.fuente = fuente
       self.color_normal = color_normal
       self.color_efecto = color_hover
       self.posicion = posicion
       self.color_actual = color_normal
       self.rect = None

    def dibujar (self, ventana, posicion_mouse):

        if self.clic(posicion_mouse):
            self.color_actual = self.color_efecto
        else:
            self.color_actual = self.color_normal

        """Dibuja el botón y cambia de color si el mouse está encima."""
        # Creacion de la sombra
        sombra_render = self.fuente.render(self.texto, True, const2.negro)
        sombra_rect = sombra_render.get_rect(center=(self.posicion[0] - 5, self.posicion[1] + 5))
        ventana.blit(sombra_render, sombra_rect)

        # Se renderiza el texto con el color actual
        texto_render = self.fuente.render(self.texto, True, self.color_actual)
        texto_rect = texto_render.get_rect(center=self.posicion)
        ventana.blit(texto_render, texto_rect)

    def clic(self, posicion_mouse):

        texto_render = self.fuente.render(self.texto, True, self.color_actual)
        texto_rect = texto_render.get_rect(center=self.posicion)
        return texto_rect.collidepoint(posicion_mouse)