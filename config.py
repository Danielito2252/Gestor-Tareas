import os

DATABASE_URL = os.environ.get("DATABASE_URL", None)

if DATABASE_URL:
    import urllib.parse
    result = urllib.parse.urlparse(DATABASE_URL)
    DB_CONFIG = {
        "host": result.hostname,
        "port": result.port or 5432,
        "database": result.path[1:],
        "user": result.username,
        "password": result.password
    }
    print(f"Conectando a: {result.hostname}")
else:
    DB_CONFIG = {
        "host": "localhost",
        "port": 5432,
        "database": "Gestor-Tareas",
        "user": "postgres",
        "password": os.environ.get("DB_PASSWORD", "")
    }
    print("Usando base de datos local")