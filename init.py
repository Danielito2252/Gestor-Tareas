# ──────────────────────────────────────────────────────────────
# init.py — Inicializador de la base de datos
# Este archivo se ejecuta antes de arrancar el servidor
# tanto en producción (Render) como en local.
#
# En producción se llama desde el Start Command:
#   python init.py && gunicorn app:app
# En local se llama automáticamente desde app.py
# ──────────────────────────────────────────────────────────────

from app import init_db

# MEJORA 1 — Envolver en try/except para detectar errores de conexión
# Si la base de datos no está disponible, el error se muestra claramente
# en los logs en lugar de un traceback confuso
try:
    print("Inicializando base de datos...")
    init_db()
    print("✓ Base de datos lista!")
except Exception as e:
    print(f"✗ Error al inicializar la base de datos: {e}")
    # Relanzamos el error para que Render sepa que el deploy falló
    raise