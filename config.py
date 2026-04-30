# ──────────────────────────────────────────────────────────────
# config.py — Configuración de la base de datos
# Detecta automáticamente si está corriendo en producción
# (Render) o en local, y configura la conexión correctamente.
#
# Variables de entorno necesarias:
# - En producción (Render): DATABASE_URL
# - En local: DB_PASSWORD
# ──────────────────────────────────────────────────────────────

import os
import urllib.parse
from urllib.parse import quote_plus  # Para encodear caracteres especiales en la URL
from dotenv import load_dotenv

# Carga las variables del archivo .env al entorno
# Solo funciona en local — en Render las variables
# ya están definidas en Environment Variables
load_dotenv()
# ── Detección del entorno ──────────────────────────────────────

# Intentamos leer DATABASE_URL desde las variables de entorno
# En Render esta variable existe, en local no (a menos que la definas)
DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()

if DATABASE_URL:
    # ── Configuración para producción (Render) ─────────────────
    # Parseamos la URL para extraer cada componente de la conexión
    result = urllib.parse.urlparse(DATABASE_URL)

    # En producción usamos directamente DATABASE_URL con psycopg2.connect()
    # por lo que DB_CONFIG no es necesario en este entorno
    print(f"Conectando a Render: {result.hostname}")

else:
    # ── Configuración para desarrollo local ────────────────────

    # MEJORA 1 — La contraseña se lee obligatoriamente desde variable de entorno
    # Para definirla en Windows CMD: set DB_PASSWORD=tu_contraseña
    # Para definirla en PowerShell:  $env:DB_PASSWORD="tu_contraseña"
    # Nunca hardcodear contraseñas directamente en el código
    LOCAL_PASS = os.environ.get("DB_PASSWORD")
    if not LOCAL_PASS:
        raise ValueError(
            "Falta la variable de entorno DB_PASSWORD. "
            "Defínela antes de correr la aplicación.\n"
            "CMD:        set DB_PASSWORD=tu_contraseña\n"
            "PowerShell: $env:DB_PASSWORD='tu_contraseña'"
        )

    # MEJORA 2 — DB_CONFIG solo existe en local donde realmente se necesita
    DB_CONFIG = {
        "host": "localhost",
        "port": 5432,
        "database": "Gestor-Tareas",
        "user": "postgres",
        "password": LOCAL_PASS,
        "sslmode": "disable"    # SSL no requerido en local
    }

    # MEJORA 3 — Usar quote_plus para encodear la contraseña
    # Esto evita que caracteres especiales como @, /, # rompan la URL
    DATABASE_URL = (
        f"postgresql://{DB_CONFIG['user']}:{quote_plus(DB_CONFIG['password'])}"
        f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}"
        f"/{DB_CONFIG['database']}?sslmode=disable"
    )

    print("Usando base de datos local en localhost")