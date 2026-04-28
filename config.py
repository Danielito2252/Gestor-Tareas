import os
import urllib.parse

DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()   

if DATABASE_URL:
    result = urllib.parse.urlparse(DATABASE_URL)
    # Extraer parámetros de la URL (como sslmode)
    query_params = urllib.parse.parse_qs(result.query)
    
    DB_CONFIG = {
        "host": result.hostname,
        "port": result.port or 5432,
        "database": result.path[1:],
        "user": result.username,
        "password": result.password
    }
    
    # Si la URL tiene sslmode, lo agregamos. Si no, forzamos 'require' para Render.
    DB_CONFIG["sslmode"] = query_params.get("sslmode", ["require"])[0]
    
    print(f"Conectando a: {result.hostname} con sslmode={DB_CONFIG['sslmode']}")
else:
    DB_CONFIG = {
        "host": "localhost",
        "port": 5432,
        "database": "Gestor-Tareas",
        "user": "postgres",
        "password": os.environ.get("DB_PASSWORD", ""),
        "sslmode": "disable" # Localmente usualmente no necesitas SSL
    }
    print("Usando base de datos local")