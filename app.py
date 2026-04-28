from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2
import psycopg2.extras
from config import DB_CONFIG

app = Flask(__name__)
app.secret_key = "clave_secreta_Gestor-Tareas-Personal"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# ── Base de datos ──────────────────────────────────────────
def get_db():
    conn = psycopg2.connect(**DB_CONFIG)
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id SERIAL PRIMARY KEY,
            username VARCHAR(100) UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
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
    conn.close()

# ── Modelo de usuario ──────────────────────────────────────
class Usuario(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

@login_manager.user_loader
def load_user(user_id):
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM usuarios WHERE id = %s", (user_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row:
        return Usuario(row["id"], row["username"])
    return None

# ── Rutas de autenticación ─────────────────────────────────
@app.route("/")
@login_required
def index():
    return render_template("index.html", username=current_user.username)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        data = request.get_json()
        username = data.get("username", "").strip()
        password = data.get("password", "").strip()

        conn = get_db()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT * FROM usuarios WHERE username = %s", (username,))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user and check_password_hash(user["password"], password):
            login_user(Usuario(user["id"], user["username"]))
            return jsonify({"ok": True})
        return jsonify({"error": "Usuario o contraseña incorrectos"}), 401

    return render_template("login.html")

@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        data = request.get_json()
        username = data.get("username", "").strip()
        password = data.get("password", "").strip()

        if not username or not password:
            return jsonify({"error": "Completa todos los campos"}), 400

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
            conn.close()
            return jsonify({"ok": True})
        except:
            return jsonify({"error": "El usuario ya existe"}), 409

    return render_template("registro.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

# ── Rutas de tareas ────────────────────────────────────────
@app.route("/tareas", methods=["GET"])
@login_required
def get_tareas():
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(
        "SELECT * FROM tareas WHERE usuario_id = %s ORDER BY id DESC",
        (current_user.id,)
    )
    tareas = cur.fetchall()
    cur.close()
    conn.close()
    # Convertir fecha a string para JSON
    resultado = []
    for t in tareas:
        t = dict(t)
        if t["fecha_limite"]:
            t["fecha_limite"] = t["fecha_limite"].strftime("%Y-%m-%d")
        resultado.append(t)
    return jsonify(resultado)

@app.route("/tareas", methods=["POST"])
@login_required
def crear_tarea():
    data = request.get_json()
    titulo = data.get("titulo", "").strip()
    fecha_limite = data.get("fecha_limite") or None
    prioridad = data.get("prioridad", "media")
    categoria = data.get("categoria", "personal")
    if not titulo:
        return jsonify({"error": "El título no puede estar vacío"}), 400
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO tareas (titulo, fecha_limite, prioridad, categoria, usuario_id) VALUES (%s, %s, %s, %s, %s)",
        (titulo, fecha_limite, prioridad, categoria, current_user.id)
    )
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"mensaje": "Tarea creada"}), 201

@app.route("/tareas/<int:id>", methods=["PUT"])
@login_required
def completar_tarea(id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "UPDATE tareas SET completada = TRUE WHERE id = %s AND usuario_id = %s",
        (id, current_user.id)
    )
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"mensaje": "Tarea actualizada"})

@app.route("/tareas/<int:id>", methods=["PATCH"])
@login_required
def editar_tarea(id):
    data = request.get_json()
    titulo = data.get("titulo", "").strip()
    if not titulo:
        return jsonify({"error": "El título no puede estar vacío"}), 400
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "UPDATE tareas SET titulo = %s WHERE id = %s AND usuario_id = %s",
        (titulo, id, current_user.id)
    )
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"mensaje": "Tarea actualizada"})

@app.route("/tareas/<int:id>", methods=["DELETE"])
@login_required
def eliminar_tarea(id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "DELETE FROM tareas WHERE id = %s AND usuario_id = %s",
        (id, current_user.id)
    )
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"mensaje": "Tarea eliminada"})

if __name__ == "__main__":
    init_db()
    #app.run(debug=True) ##Con esto en true hace que se corra en local pero para 
    # ## producción se recomienda dejarlo en false
    app.run(debug=False)
    
    