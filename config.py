import os

DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", "5432")
DB_NAME = os.environ.get("DB_NAME", "todo_app")
DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "")

print(f"DB_HOST leído: {DB_HOST}")
print(f"DB_PORT leído: {DB_PORT}")
print(f"DB_NAME leído: {DB_NAME}")
print(f"DB_USER leído: {DB_USER}")

DB_CONFIG = {
    "host": DB_HOST,
    "port": int(DB_PORT),
    "database": DB_NAME,
    "user": DB_USER,
    "password": DB_PASSWORD
}