import os
import urllib.parse

# 1. Intentamos obtener la URL de Render
DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()

if DATABASE_URL:
    # --- CONFIGURACIÓN PARA LA NUBE (RENDER) ---
    result = urllib.parse.urlparse(DATABASE_URL)
    query_params = urllib.parse.parse_qs(result.query)
    
    # Mantenemos DB_CONFIG por si lo usas en otra parte
    DB_CONFIG = {
        "host": result.hostname,
        "port": result.port or 5432,
        "database": result.path[1:],
        "user": result.username,
        "password": result.password,
        "sslmode": query_params.get("sslmode", ["require"])[0]
    }
    print(f"Conectando a Render: {result.hostname}")

else:
    # --- CONFIGURACIÓN PARA TU PC (LOCAL) ---
    # Aquí es vital poner tu contraseña real de Postgres local o usar la variable de entorno
    LOCAL_PASS = os.environ.get("DB_PASSWORD", "4024") 
    
    DB_CONFIG = {
        "host": "localhost",
        "port": 5432,
        "database": "Gestor-Tareas",
        "user": "postgres",
        "password": LOCAL_PASS,
        "sslmode": "disable"
    }
    
    # Creamos una DATABASE_URL artificial para que psycopg2.connect(DATABASE_URL) no falle
    DATABASE_URL = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}?sslmode=disable"
    
    print("Usando base de datos local en localhost")