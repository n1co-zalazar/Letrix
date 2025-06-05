import json
import os
from pathlib import Path

PARTIDAS_DIR = Path("partidas_guardadas")
PARTIDAS_ARCHIVO = PARTIDAS_DIR / "partidas.json"


def inicializar_sistema_guardado():
    """Crea el directorio y archivo si no existen"""
    try:
        PARTIDAS_DIR.mkdir(exist_ok=True)
        if not PARTIDAS_ARCHIVO.exists():
            with open(PARTIDAS_ARCHIVO, 'w') as f:
                json.dump({"usuarios": {}}, f)
        return True
    except Exception as e:
        print(f"Error inicializando sistema de guardado: {e}")
        return False


def guardar_partida(username, juego, datos):
    """Guarda los datos de la partida para un usuario específico"""
    try:
        # Cargar datos existentes
        with open(PARTIDAS_ARCHIVO, 'r') as f:
            partidas = json.load(f)

        # Asegurar estructura
        if "usuarios" not in partidas:
            partidas["usuarios"] = {}
        if username not in partidas["usuarios"]:
            partidas["usuarios"][username] = {}

        # Actualizar datos
        partidas["usuarios"][username][f"partida_{juego}"] = datos

        # Guardar
        with open(PARTIDAS_ARCHIVO, 'w') as f:
            json.dump(partidas, f, indent=2)

        return True
    except Exception as e:
        print(f"Error al guardar partida: {e}")
        return False


def cargar_partida(username, juego):
    """Carga los datos de la partida para un usuario específico"""
    try:
        with open(PARTIDAS_ARCHIVO, 'r') as f:
            partidas = json.load(f)
            return partidas["usuarios"].get(username, {}).get(f"partida_{juego}", None)
    except (FileNotFoundError, json.JSONDecodeError):
        return None
    except Exception as e:
        print(f"Error al cargar partida: {e}")
        return None


# Inicializar el sistema al importar el módulo
inicializar_sistema_guardado()
