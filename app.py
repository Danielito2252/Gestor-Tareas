# ──────────────────────────────────────────────────────────────
# app.py — Archivo principal del backend
# Contiene la configuración de Flask, la conexión a la base de
# datos y todas las rutas (endpoints) de la aplicación.
# ──────────────────────────────────────────────────────────────

import os  # Para leer variables de entorno

# Importaciones de Flask para manejar rutas, plantillas y respuestas
from flask import Flask, render_template, request, jsonify, redirect, url_for

# Importaciones de Flask-Login para manejar sesiones de usuario
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

# Werkzeug para encriptar y verificar contraseñas de forma segura
from werkzeug.security import generate_password_hash, check_password_hash

# Psycopg2 es el conector de Python para PostgreSQL
import psycopg2
import psycopg2.extras  # Permite obtener resultados como diccionarios
import psycopg2.pool    # Para manejar el pool de conexiones
import psycopg2.errors  # Para atrapar errores específicos de PostgreSQL

# Importamos la URL de conexión desde config.py
from config import DATABASE_URL

# ── Configuración de la aplicación ────────────────────────────

# Inicializar la aplicación Flask
app = Flask(__name__)

# MEJORA 1 — Leer la secret_key desde variable de entorno
# En producción agregar SECRET_KEY en Render → Environment Variables
# En local usa el valor por defecto "clave_local_desarrollo"
app.secret_key = os.environ.get("SECRET_KEY", "clave_local_desarrollo")

# Inicializar el manejador de login
login_manager = LoginManager()
login_manager.init_app(app)

# Si el usuario no está autenticado, lo redirige a /login
login_manager.login_view = "login"

# ── Valores válidos para prioridad y categoría ─────────────────

# MEJORA 5 — Definir los valores permitidos como constantes
# Esto evita que se guarden valores inválidos en la base de datos
PRIORIDADES_VALIDAS = {"alta", "media", "baja"}
CATEGORIAS_VALIDAS = {"trabajo", "estudios", "personal"}

# ── Base de datos ──────────────────────────────────────────────

# MEJORA 3 — Pool de conexiones
# En lugar de abrir y cerrar una conexión en cada request,
# el pool mantiene conexiones reutilizables.
# minconn=1 → mínimo 1 conexión activa
# maxconn=10 → máximo 10 conexiones simultáneas
connection_pool = psycopg2.pool.SimpleConnectionPool(1, 10, DATABASE_URL)

def get_db():
    """
    Obtiene una conexión disponible del pool.
    Es más eficiente que crear una conexión nueva en cada request.
    """
    return connection_pool.getconn()

def close_db(conn):
    """
    Devuelve la conexión al pool para que pueda ser reutilizada.
    Siempre debe llamarse después de terminar con la conexión.
    """
    connection_pool.putconn(conn)

def init_db():
    """
    Crea las tablas de la base de datos si no existen.
    Se ejecuta al iniciar la aplicación a través de init.py.

    Tablas:
    - usuarios: almacena las cuentas de usuario con contraseñas encriptadas
    - tareas: almacena las tareas de cada usuario (relacionadas por usuario_id)
    """
    conn = get_db()
    cur = conn.cursor()

    # Tabla de usuarios — almacena credenciales de acceso
    cur.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id SERIAL PRIMARY KEY,
            username VARCHAR(100) UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    # Tabla de tareas — cada tarea pertenece a un usuario específico
    # usuario_id es una llave foránea que referencia a la tabla usuarios
    cur.execute('''
        CREATE TABLE IF NOT EXISTS tareas (
            id SERIAL PRIMARY KEY,
            titulo TEXT NOT NULL,
            completada BOOLEAN DEFAULT FALSE,
            fecha_limite DATE,
            prioridad VARCHAR(10) DEFAULT 'media',
            categoria VARCHAR(20) DEFAULT 'personal',
            usuario_id INTEGER NOT NULL REFERENCES usuarios(id)
        )
    ''')

    conn.commit()
    cur.close()
    close_db(conn)

# ── Modelo de usuario ──────────────────────────────────────────

class Usuario(UserMixin):
    """
    Modelo de usuario requerido por Flask-Login.
    UserMixin agrega los métodos necesarios como is_authenticated,
    is_active, get_id, etc.
    """
    def __init__(self, id, username):
        self.id = id
        self.username = username

@login_manager.user_loader
def load_user(user_id):
    """
    Función requerida por Flask-Login.
    Se ejecuta en cada request para cargar el usuario de la sesión activa.
    Busca el usuario en la BD por su id y retorna un objeto Usuario.
    """
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM usuarios WHERE id = %s", (user_id,))
    row = cur.fetchone()
    cur.close()
    close_db(conn)
    if row:
        return Usuario(row["id"], row["username"])
    return None

# ── Rutas de autenticación ─────────────────────────────────────

@app.route("/")
@login_required  # Solo accesible si el usuario está autenticado
def index():
    """
    Ruta principal — muestra la app de tareas.
    Pasa el nombre del usuario actual a la plantilla HTML.
    """
    return render_template("index.html", username=current_user.username)

@app.route("/login", methods=["GET", "POST"])
def login():
    """
    GET  → muestra el formulario de login
    POST → recibe las credenciales en JSON y verifica:
           1. Que el usuario exista en la BD
           2. Que la contraseña coincida con el hash guardado
    Si es correcto, inicia la sesión y retorna {"ok": True}
    Si falla, retorna un error 401
    """
    if request.method == "POST":
        data = request.get_json()
        username = data.get("username", "").strip()
        password = data.get("password", "").strip()

        conn = get_db()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT * FROM usuarios WHERE username = %s", (username,))
        user = cur.fetchone()
        cur.close()
        close_db(conn)

        # Verificar que el usuario existe y la contraseña es correcta
        if user and check_password_hash(user["password"], password):
            login_user(Usuario(user["id"], user["username"]))
            return jsonify({"ok": True})
        return jsonify({"error": "Usuario o contraseña incorrectos"}), 401

    return render_template("login.html")

@app.route("/registro", methods=["GET", "POST"])
def registro():
    """
    GET  → muestra el formulario de registro
    POST → recibe username y password en JSON:
           1. Valida que los campos no estén vacíos
           2. Encripta la contraseña con generate_password_hash
           3. Guarda el nuevo usuario en la BD
    Si el usuario ya existe, retorna error 409
    """
    if request.method == "POST":
        data = request.get_json()
        username = data.get("username", "").strip()
        password = data.get("password", "").strip()

        if not username or not password:
            return jsonify({"error": "Completa todos los campos"}), 400

        # Encriptar la contraseña antes de guardarla — nunca se guarda en texto plano
        hashed = generate_password_hash(password)
        try:
            conn = get_db()
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO usuarios (username, password) VALUES (%s, %s)",
                (username, hashed)
            )
            conn.commit()
            cur.close()
            close_db(conn)
            return jsonify({"ok": True})
        except psycopg2.errors.UniqueViolation:
            # MEJORA 2 — Atrapar solo el error específico de username duplicado
            return jsonify({"error": "El usuario ya existe"}), 409

    return render_template("registro.html")

@app.route("/logout")
@login_required
def logout():
    """
    Cierra la sesión del usuario actual y lo redirige al login.
    """
    logout_user()
    return redirect(url_for("login"))

# ── Rutas de tareas ────────────────────────────────────────────

@app.route("/tareas", methods=["GET"])
@login_required
def get_tareas():
    """
    Retorna todas las tareas del usuario autenticado en formato JSON.
    Las ordena de más reciente a más antigua (ORDER BY id DESC).
    Convierte las fechas a string formato 'YYYY-MM-DD' para el frontend.
    """
    try:
        conn = get_db()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(
            "SELECT * FROM tareas WHERE usuario_id = %s ORDER BY id DESC",
            (current_user.id,)
        )
        tareas = cur.fetchall()
        cur.close()
        close_db(conn)

        # Convertir fecha a string para que JSON pueda serializarla
        resultado = []
        for t in tareas:
            t = dict(t)
            if t["fecha_limite"]:
                t["fecha_limite"] = t["fecha_limite"].strftime("%Y-%m-%d")
            resultado.append(t)
        return jsonify(resultado)
    except Exception as e:
        # MEJORA 4 — Manejo de errores en rutas de tareas
        return jsonify({"error": "Error al obtener las tareas"}), 500

@app.route("/tareas", methods=["POST"])
@login_required
def crear_tarea():
    """
    Crea una nueva tarea para el usuario autenticado.
    Recibe en JSON: titulo, fecha_limite, prioridad, categoria.
    Asocia la tarea al usuario actual mediante usuario_id.
    """
    try:
        data = request.get_json()
        titulo = data.get("titulo", "").strip()
        fecha_limite = data.get("fecha_limite") or None
        prioridad = data.get("prioridad", "media")
        categoria = data.get("categoria", "personal")

        if not titulo:
            return jsonify({"error": "El título no puede estar vacío"}), 400

        # MEJORA 6 — Validar largo del título
        if len(titulo) > 200:
            return jsonify({"error": "El título no puede tener más de 200 caracteres"}), 400

        # MEJORA 5 — Validar que prioridad y categoría sean valores permitidos
        if prioridad not in PRIORIDADES_VALIDAS:
            return jsonify({"error": "Prioridad inválida"}), 400
        if categoria not in CATEGORIAS_VALIDAS:
            return jsonify({"error": "Categoría inválida"}), 400

        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO tareas (titulo, fecha_limite, prioridad, categoria, usuario_id) VALUES (%s, %s, %s, %s, %s)",
            (titulo, fecha_limite, prioridad, categoria, current_user.id)
        )
        conn.commit()
        cur.close()
        close_db(conn)
        return jsonify({"mensaje": "Tarea creada"}), 201
    except Exception as e:
        # MEJORA 4 — Manejo de errores en rutas de tareas
        return jsonify({"error": "Error al crear la tarea"}), 500

@app.route("/tareas/<int:id>", methods=["PUT"])
@login_required
def completar_tarea(id):
    """
    Marca una tarea como completada (completada = TRUE).
    Verifica que la tarea pertenezca al usuario autenticado
    usando AND usuario_id = %s para evitar que un usuario
    modifique tareas de otro.
    """
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "UPDATE tareas SET completada = TRUE WHERE id = %s AND usuario_id = %s",
            (id, current_user.id)
        )
        conn.commit()
        cur.close()
        close_db(conn)
        return jsonify({"mensaje": "Tarea actualizada"})
    except Exception as e:
        # MEJORA 4 — Manejo de errores en rutas de tareas
        return jsonify({"error": "Error al completar la tarea"}), 500

@app.route("/tareas/<int:id>", methods=["PATCH"])
@login_required
def editar_tarea(id):
    """
    Actualiza el título de una tarea existente.
    Solo permite editar tareas que pertenezcan al usuario autenticado.
    """
    try:
        data = request.get_json()
        titulo = data.get("titulo", "").strip()

        if not titulo:
            return jsonify({"error": "El título no puede estar vacío"}), 400

        # MEJORA 6 — Validar largo del título
        if len(titulo) > 200:
            return jsonify({"error": "El título no puede tener más de 200 caracteres"}), 400

        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "UPDATE tareas SET titulo = %s WHERE id = %s AND usuario_id = %s",
            (titulo, id, current_user.id)
        )
        conn.commit()
        cur.close()
        close_db(conn)
        return jsonify({"mensaje": "Tarea actualizada"})
    except Exception as e:
        # MEJORA 4 — Manejo de errores en rutas de tareas
        return jsonify({"error": "Error al editar la tarea"}), 500

@app.route("/tareas/<int:id>", methods=["DELETE"])
@login_required
def eliminar_tarea(id):
    """
    Elimina una tarea de la base de datos.
    Solo permite eliminar tareas que pertenezcan al usuario autenticado.
    """
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "DELETE FROM tareas WHERE id = %s AND usuario_id = %s",
            (id, current_user.id)
        )
        conn.commit()
        cur.close()
        close_db(conn)
        return jsonify({"mensaje": "Tarea eliminada"})
    except Exception as e:
        # MEJORA 4 — Manejo de errores en rutas de tareas
        return jsonify({"error": "Error al eliminar la tarea"}), 500

# ── Inicio de la aplicación ────────────────────────────────────

if __name__ == "__main__":
    # Inicializar las tablas de la base de datos al correr localmente
    init_db()
    # debug=False recomendado para producción
    # debug=True muestra errores detallados en desarrollo
    app.run(debug=False)