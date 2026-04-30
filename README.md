# 📝 Gestor de Tareas Personal

Aplicación web fullstack para gestionar tareas personales, construida con Flask, PostgreSQL y JavaScript vanilla.

![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-3.x-black?logo=flask)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue?logo=postgresql)
![JavaScript](https://img.shields.io/badge/JavaScript-ES6-yellow?logo=javascript)

---

## 📸 Vista previa

### Login
![Login](screenshots/login.png)

### App principal
![App](screenshots/app.png)

---

## ✨ Funcionalidades

- ✅ Registro e inicio de sesión de usuarios
- ✅ Cada usuario ve únicamente sus propias tareas
- ✅ Crear, editar y eliminar tareas
- ✅ Fechas límite y prioridades (Alta, Media, Baja)
- ✅ Categorías (Trabajo, Estudios, Personal)
- ✅ Filtros por estado (Pendientes / Completadas)
- ✅ Búsqueda en tiempo real
- ✅ Ordenamiento por fecha, prioridad o nombre
- ✅ Contador de tareas en tiempo real

---

## 🛠️ Tecnologías utilizadas

| Capa | Tecnología |
|------|-----------|
| Frontend | HTML, CSS, JavaScript (ES6) |
| Backend | Python, Flask, Flask-Login |
| Base de datos | PostgreSQL |
| Seguridad | Werkzeug (hash de contraseñas) |
| Despliegue | Render |

---

## 🚀 Instalación local

### Requisitos previos
- Python 3.x
- PostgreSQL instalado y corriendo
- Git

### Pasos

**1. Clona el repositorio**
```bash
git clone https://github.com/Danielito2252/Gestor-Tareas-.git
cd Gestor-Tareas-Personal
```

**2. Crea y activa el entorno virtual**
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

**3. Instala las dependencias**
```bash
pip install -r requirements.txt
```

**4. Crea la base de datos en PostgreSQL**

Abre pgAdmin o psql y ejecuta:
```sql
CREATE DATABASE "Gestor-Tareas";
```

**5. Crea el archivo de variables de entorno**

Crea un archivo `.env` en la raíz del proyecto con este contenido:
DB_PASSWORD=tu_contraseña_de_postgres

> ⚠️ Este archivo no se sube a GitHub porque contiene información sensible.
> Nunca lo compartas ni lo incluyas en tus commits.

**6. Inicializa la base de datos**
```bash
python init.py
```

Deberías ver:
Usando base de datos local en localhost
Inicializando base de datos...
✓ Base de datos lista!

**7. Corre la aplicación**
```bash
python app.py
```

**8. Abre en tu navegador**
http://127.0.0.1:5000

---

## 📁 Estructura del proyecto
Gestor-Tareas-Personal/
│
├── static/
│   ├── style.css        # Estilos de la aplicación
│   └── script.js        # Lógica del frontend
│
├── templates/
│   ├── index.html       # Página principal
│   ├── login.html       # Página de inicio de sesión
│   └── registro.html    # Página de registro
│
├── screenshots/         # Capturas de pantalla para el README
├── app.py               # Backend principal (Flask)
├── config.py            # Configuración de base de datos
├── init.py              # Inicializador de la base de datos
├── requirements.txt     # Dependencias del proyecto
├── Procfile             # Configuración para despliegue en Render
├── .env                 # Variables de entorno locales (NO incluido en repo)
└── README.md            # Este archivo

---

## 🔐 Variables de entorno

### En local — archivo `.env`
Crea un archivo `.env` en la raíz del proyecto:
DB_PASSWORD=tu_contraseña_de_postgres

### En producción — Render
Configura estas variables en Render → Environment Variables:

| Variable | Descripción |
|----------|-------------|
| `DATABASE_URL` | URL completa de conexión a PostgreSQL |
| `SECRET_KEY` | Clave secreta para las sesiones de Flask |

---

## 🌐 Demo en línea

La app está desplegada en Render:
👉 [https://gestor-tareas-5w65.onrender.com/](https://gestor-tareas-5w65.onrender.com)

> 💤 Al estar en el plan gratuito, la app puede tardar unos segundos en cargar
> si estuvo inactiva. Esto es normal.

---

## 👨‍💻 Autor

**Herberth Daniel Barrios Barrientos** — Estudiante de Ingeniería en Sistemas, 9no ciclo

[![GitHub](https://img.shields.io/badge/GitHub-Danielito2252-black?logo=github)](https://github.com/Danielito2252)

---

## 📌 Nota

Este proyecto fue desarrollado como parte de mi portafolio personal para demostrar habilidades en desarrollo web fullstack.