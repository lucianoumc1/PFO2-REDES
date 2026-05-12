# Sistema de Gestión de Tareas - PFO 2

API REST con Flask para registro y login de usuarios, sesiones con cookies y una base SQLite. Incluye un cliente de consola y scripts de ayuda para probar todo sin complicarse.

## Descripción

El servidor expone rutas JSON para dar de alta usuarios, iniciar sesión y cerrarla. Las contraseñas se guardan con bcrypt, no en claro. La ruta `GET /tareas` sirve solo una página HTML mínima de presentación (no pide login). La tabla de tareas en la base está pensada para ampliar el proyecto más adelante.

## Tecnologías utilizadas

- Python 3 y Flask
- SQLite como base embebida
- bcrypt para el hash de contraseñas
- HTML/CSS en las respuestas que devuelve el propio Flask
- requests en el cliente de consola, tests y script de datos de prueba

## Estructura del proyecto

```
├── servidor.py       # App Flask y rutas
├── cliente.py        # Menú en consola contra la API
├── setup_data.py     # Usuarios de ejemplo
├── install.py        # Instalador con venv
├── requirements.txt
├── README.md
└── tareas.db         # Se crea al arrancar el servidor
```

## Instalación y configuración

### 1. Clonar el repositorio

```bash
git clone https://github.com/lucianoumc1/PFO2-REDES.git
cd PFO2-REDES
```
(El nombre de la carpeta puede variar según cómo lo hayas clonado.)

### 2. Entorno virtual (recomendado)

```bash
python -m venv venv
```

En Windows: `venv\Scripts\activate`  
En Linux o macOS: `source venv/bin/activate`

### 3. Dependencias

```bash
pip install -r requirements.txt
```
### 4. Arrancar el servidor

```bash
python servidor.py
```

Por defecto queda escuchando en `http://localhost:5000` (también accesible desde la red local con `0.0.0.0`).

## Uso del sistema

**Navegador**  
Abre `http://localhost:5000` y verás la página con la lista de endpoints. `http://localhost:5000/tareas` muestra la vista de presentación en HTML.

**Cliente de consola**  
Con el servidor en marcha:

```bash
python cliente.py
```

Desde el menú puedes registrar usuario, hacer login, pedir `/tareas` (comprueba que responde), ver `/status`, logout y salir.

## API endpoints

### `POST /registro`

Crea un usuario. Cuerpo JSON con `usuario` (mínimo 3 caracteres) y `contraseña` (mínimo 4).

Respuesta típica **201**:

```json
{
  "mensaje": "Usuario registrado.",
  "usuario": "nombre_usuario",
  "fecha_registro": "2024-01-15T10:30:00.123456"
}
```

Errores habituales: **400** (datos mal o incompletos), **409** (usuario ya existía).

### `POST /login`

Comprueba credenciales y abre sesión Flask (cookie).

Respuesta **200**:

```json
{
  "mensaje": "Sesion iniciada.",
  "usuario": "nombre_usuario",
  "sesion_iniciada": "2024-01-15T10:35:00.123456"
}
```

**400** si faltan campos, **404** si no existe el usuario, **401** si la contraseña no coincide.

### `GET /tareas`

Devuelve **200** y un HTML corto de presentación. **No requiere** estar logueado.

### `POST /logout` (también acepta `GET`)

Cierra la sesión actual.

Ejemplo **200**:

```json
{
  "mensaje": "Sesion cerrada (nombre_usuario).",
  "fecha_logout": "2024-01-15T10:40:00.123456"
}
```

### `GET /status`

JSON con estado del servicio, conteo de usuarios y tareas, y marca de tiempo. Sirve para comprobar que el servidor está vivo.

## Seguridad implementada

Las contraseñas se hashean con **bcrypt** y un salt distinto por registro; en la tabla solo aparece `contraseña_hash`. El login compara con `bcrypt.checkpw`, sin guardar la clave en claro.

Las **sesiones** de Flask se usan para identificar al usuario tras un `POST /login` correcto (por ejemplo si más adelante añades rutas que sí dependan de sesión). La clave `app.secret_key` del ejemplo es solo para desarrollo: en producción deberías cambiarla y usar HTTPS.

## Base de datos SQLite

Al iniciar `servidor.py` se crea `tareas.db` si no existe, con tablas alineadas al código:

```sql
CREATE TABLE usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario TEXT UNIQUE NOT NULL,
    contraseña_hash TEXT NOT NULL,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE tareas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER,
    titulo TEXT NOT NULL,
    descripcion TEXT,
    completada BOOLEAN DEFAULT FALSE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
);
```

Es un solo archivo, fácil de borrar y regenerar en desarrollo si necesitas empezar de cero.

## Casos de prueba

Ejemplos con curl (con el servidor levantado):

Registro correcto (esperado **201**):

```bash
curl -X POST http://localhost:5000/registro \
  -H "Content-Type: application/json" \
  -d '{"usuario": "usuario1", "contraseña": "pass123"}'
```

Mismo usuario otra vez (**409**):

```bash
curl -X POST http://localhost:5000/registro \
  -H "Content-Type: application/json" \
  -d '{"usuario": "usuario1", "contraseña": "otra123"}'
```

Login guardando cookie (**200**):

```bash
curl -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{"usuario": "usuario1", "contraseña": "pass123"}' \
  -c cookies.txt
```

`GET /tareas` sin cookie (**200**, HTML público):

```bash
curl -X GET http://localhost:5000/tareas
```
**
<img width="638" height="952" alt="screen1" src="https://github.com/user-attachments/assets/605d4879-07b0-480f-9563-478bb4893a42" />
**
<img width="577" height="983" alt="screen2" src="https://github.com/user-attachments/assets/e0ad324c-7ad8-461d-afef-4ad13d1e7afa" />
**
<img width="484" height="528" alt="screen3" src="https://github.com/user-attachments/assets/7337c65b-726c-4250-b3ce-2b83e25a7822" />
**
<img width="1586" height="910" alt="screenWeb" src="https://github.com/user-attachments/assets/1f19f279-96b0-4e38-b992-f7f6d45c8d26" />


## Troubleshooting

**No encuentra el módulo `bcrypt` (u otro)**  
Vuelve a activar el venv y ejecuta `pip install -r requirements.txt`.

**El puerto 5000 está ocupado**  
En Linux o macOS algo útil es `lsof -i :5000` y terminar el proceso. En Windows puedes buscar el PID con `netstat -ano | findstr :5000` y cerrarlo desde el administrador de tareas o con `taskkill /PID <número> /F`.

**Base bloqueada o rara**  
Cierra el servidor, borra `tareas.db` si no te importa perder datos locales, y vuelve a arrancar `servidor.py`.

**El cliente no conecta**  
Comprueba que el servidor esté corriendo y prueba `http://localhost:5000/status` en el navegador. Si un sitio usa `127.0.0.1` y otro `localhost`, las cookies pueden no coincidir; mejor unificar la URL.

## Respuestas conceptuales

**¿Por qué hashear contraseñas?**  
Si alguien obtiene una copia de la base, no debería leer las claves tal cual. Un hash con salt (como el de bcrypt) está pensado para eso: verificar la contraseña en el login sin poder “deshacer” el valor almacenado.

**¿Por qué SQLite aquí?**  
Para un trabajo académico o un prototipo va bien: no instala motor aparte, el esquema vive en un archivo y Flask lo abre como cualquier fichero local. Si el proyecto crece, se puede migrar a otro motor manteniendo ideas parecidas.
