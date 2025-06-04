import pygame

import const2


class Boton:
    def __init__(self,texto, fuente, color_normal, color_hover, y_pos):
       self.texto = texto
       self.fuente = fuente
       self.color_normal = color_normal
       self.color_efecto = color_hover
       self.y_pos = y_pos
       self.color_actual = color_normal
       self.posicion = self._calcular_posicion_centrada()

    def _calcular_posicion_centrada(self):
        texto_temp = self.fuente.render(self.texto, True, self.color_normal)
        x_centrado = (const2.width - texto_temp.get_width()) // 2
        return (x_centrado, self.y_pos)

    def dibujar(self, ventana, posicion_mouse):
        # Color al pasar el mouse
        self.color_actual = self.color_efecto if self.clic(posicion_mouse) else self.color_normal

        # Sombra (5px abajo/derecha)
        sombra = self.fuente.render(self.texto, True, const2.negro)
        ventana.blit(sombra, (self.posicion[0] - const2.DESPLAZAMIENTO_SOMBRA,
                              self.posicion[1] + const2.DESPLAZAMIENTO_SOMBRA))

        # Texto principal
        texto = self.fuente.render(self.texto, True, self.color_actual)
        ventana.blit(texto, self.posicion)

    def clic(self, posicion_mouse):
        texto_rect = self.fuente.render(self.texto, True, self.color_actual).get_rect(
            topleft=self.posicion
        )
        return texto_rect.collidepoint(posicion_mouse)
