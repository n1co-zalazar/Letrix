from juego2 import Juego
from login import pantalla_login

login_exitoso, username = pantalla_login()

if login_exitoso:  # Solo continúa si se inicia sesión correctamente
    g = Juego()
    g.username = username  # Asignar el nombre de usuario
    while g.run:
        g.play = True
        g.bucle_juego()
else:
    print("Login cancelado o fallido.")
