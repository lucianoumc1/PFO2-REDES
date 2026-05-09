import datetime
import os
import sqlite3

import bcrypt
from flask import Flask, jsonify, render_template_string, request, session

app = Flask(__name__)
app.secret_key = "tu_clave_secreta_super_segura"  # cambiar en produccion

DB_NAME = "tareas.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT UNIQUE NOT NULL,
            contraseña_hash TEXT NOT NULL,
            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS tareas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER,
            titulo TEXT NOT NULL,
            descripcion TEXT,
            completada BOOLEAN DEFAULT FALSE,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
        )
        """
    )
    conn.commit()
    conn.close()


def hash_password(password):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


@app.route("/")
def index():
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Sistema de tareas</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            .container { background: #f4f4f4; padding: 20px; border-radius: 5px; }
            .endpoint { background: white; margin: 10px 0; padding: 15px; border-radius: 3px; }
            .method { color: white; padding: 5px 10px; border-radius: 3px; font-weight: bold; }
            .post { background: #4CAF50; }
            .get { background: #2196F3; }
            code { background: #f0f0f0; padding: 2px 5px; border-radius: 2px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Sistema de gestion de tareas (API REST)</h1>
            <p>Registro, login y una pagina de presentacion en /tareas.</p>

            <h2>Endpoints</h2>

            <div class="endpoint">
                <span class="method post">POST</span>
                <strong>/registro</strong>
                <p>Alta de usuario.</p>
                <p><strong>Body:</strong> <code>{"usuario": "nombre", "contraseña": "1234"}</code></p>
            </div>

            <div class="endpoint">
                <span class="method post">POST</span>
                <strong>/login</strong>
                <p>Inicio de sesion.</p>
                <p><strong>Body:</strong> <code>{"usuario": "nombre", "contraseña": "1234"}</code></p>
            </div>

            <div class="endpoint">
                <span class="method get">GET</span>
                <strong>/tareas</strong>
                <p>Pagina HTML publica (sin login).</p>
            </div>

            <div class="endpoint">
                <span class="method post">POST</span>
                <strong>/logout</strong>
                <p>Cierra la sesion.</p>
            </div>

            <h2>Uso rapido</h2>
            <ol>
                <li><code>POST /registro</code></li>
                <li><code>POST /login</code></li>
                <li><code>GET /tareas</code> (vista de presentacion)</li>
            </ol>

            <h2>Estado</h2>
            <p><strong>Base de datos:</strong> SQLite ({{ db_status }})</p>
            <p><strong>Usuarios:</strong> {{ user_count }}</p>
            <p><strong>Stack:</strong> Flask y bcrypt.</p>
        </div>
    </body>
    </html>
    """

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM usuarios")
    user_count = cur.fetchone()[0]
    conn.close()

    db_status = "conectada" if os.path.exists(DB_NAME) else "no encontrada"

    return render_template_string(
        html_template, user_count=user_count, db_status=db_status
    )


@app.route("/registro", methods=["POST"])
def registro():
    try:
        data = request.get_json()
        if not data or "usuario" not in data or "contraseña" not in data:
            return (
                jsonify({"error": "Faltan usuario o contraseña."}),
                400,
            )

        usuario = data["usuario"].strip()
        contraseña = data["contraseña"]

        if len(usuario) < 3:
            return jsonify({"error": "El usuario debe tener al menos 3 caracteres."}), 400
        if len(contraseña) < 4:
            return jsonify({"error": "La contraseña debe tener al menos 4 caracteres."}), 400

        contraseña_hash = hash_password(contraseña)
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO usuarios (usuario, contraseña_hash) VALUES (?, ?)",
                (usuario, contraseña_hash),
            )
            conn.commit()
            return (
                jsonify(
                    {
                        "mensaje": "Usuario registrado.",
                        "usuario": usuario,
                        "fecha_registro": datetime.datetime.now().isoformat(),
                    }
                ),
                201,
            )
        except sqlite3.IntegrityError:
            return jsonify({"error": "Ese usuario ya existe."}), 409
        finally:
            conn.close()

    except Exception as e:
        return jsonify({"error": f"Error del servidor: {str(e)}"}), 500


@app.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json()
        if not data or "usuario" not in data or "contraseña" not in data:
            return jsonify({"error": "Faltan credenciales."}), 400

        usuario = data["usuario"].strip()
        contraseña = data["contraseña"]

        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute(
            "SELECT id, usuario, contraseña_hash FROM usuarios WHERE usuario = ?",
            (usuario,),
        )
        user_data = cur.fetchone()
        conn.close()

        if not user_data:
            return jsonify({"error": "Usuario no encontrado"}), 404

        user_id, db_usuario, contraseña_hash = user_data
        if not verify_password(contraseña, contraseña_hash):
            return jsonify({"error": "Contraseña incorrecta"}), 401

        session["usuario_id"] = user_id
        session["usuario"] = db_usuario

        return (
            jsonify(
                {
                    "mensaje": "Sesion iniciada.",
                    "usuario": db_usuario,
                    "sesion_iniciada": datetime.datetime.now().isoformat(),
                }
            ),
            200,
        )

    except Exception as e:
        return jsonify({"error": f"Error del servidor: {str(e)}"}), 500


@app.route("/tareas", methods=["GET"])
def tareas():
    """Pagina publica, solo presentacion."""
    return """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="utf-8">
    <title>Tareas</title>
    <style>
        body { font-family: Georgia, serif; max-width: 520px; margin: 48px auto; padding: 0 20px;
               color: #222; line-height: 1.6; }
        h1 { font-size: 1.4rem; font-weight: normal; border-bottom: 1px solid #ccc; padding-bottom: 8px; }
        p { margin: 1em 0; }
        a { color: #345; }
    </style>
</head>
<body>
    <h1>Gestion de tareas</h1>
    <p>Vista de presentacion del proyecto. La API REST esta descrita en la pagina principal.</p>
    <p><a href="/">Inicio</a></p>
</body>
</html>"""


@app.route("/logout", methods=["POST", "GET"])
def logout():
    usuario = session.get("usuario", "Usuario")
    session.clear()
    return (
        jsonify(
            {
                "mensaje": f"Sesion cerrada ({usuario}).",
                "fecha_logout": datetime.datetime.now().isoformat(),
            }
        ),
        200,
    )


@app.route("/status")
def status():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM usuarios")
    user_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM tareas")
    task_count = cur.fetchone()[0]
    conn.close()

    return jsonify(
        {
            "status": "OK",
            "database": "SQLite conectada",
            "usuarios_registrados": user_count,
            "tareas_totales": task_count,
            "timestamp": datetime.datetime.now().isoformat(),
            "version": "1.0",
        }
    )


if __name__ == "__main__":
    init_db()
    print("Servidor Flask en marcha.")
    print("Base de datos lista.")
    print("http://localhost:5000")
    app.run(debug=True, host="0.0.0.0", port=5000)
