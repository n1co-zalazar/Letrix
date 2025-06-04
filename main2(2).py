from juego2 import Juego
from login import pantalla_login

if pantalla_login():  # Solo continúa si se inicia sesión correctamente
    g = Juego()
    while g.run:
        g.play = True
        g.bucle_juego()
else:
    print("Login cancelado o fallido.")