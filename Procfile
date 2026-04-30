# ──────────────────────────────────────────────────────────────
# Procfile — Instrucciones de arranque para producción
# Render y otras plataformas como Heroku leen este archivo
# para saber cómo iniciar la aplicación.
#
# Formato: <tipo_de_proceso>: <comando>
# ──────────────────────────────────────────────────────────────

# web → indica que es un proceso web que recibe tráfico HTTP
# gunicorn → servidor WSGI de producción (reemplaza al servidor de Flask)
# app:app → primer "app" es el archivo app.py, segundo "app" es la instancia Flask
web: python init.py && gunicorn app:app