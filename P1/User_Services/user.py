# Importamos las librerías necesarias
import os  # Para operaciones del sistema, como crear directorios
import uuid  # Para generar identificadores únicos
import json  # Para trabajar con archivos JSON
from quart import Quart, request, jsonify  # Importamos Quart y sus funciones para crear la API
import shutil

# Creamos una instancia de la aplicación Quart
app = Quart(__name__)

# Directorio donde se almacenarán los datos de los usuarios
USER_DIR = "User_data"

# Función para guardar la información del usuario en un archivo JSON
def guardar_usuario_json(name, password, uid, token):
    # Creamos un diccionario con la información del usuario
    user_data = {
        'name': name,  # Nombre del usuario
        'password': password,  # Contraseña del usuario
        'uid': uid,  # UID único del usuario
        'token': token,  # Token de acceso generado
    }

    # Creamos la ruta específica para el archivo JSON del usuario
    particular_dir = os.path.join(USER_DIR, name)
    
    # Creamos el directorio del usuario si no existe
    os.makedirs(particular_dir, exist_ok=True)
    
    # Definimos la ruta del archivo JSON donde se guardará la información del usuario
    user_file_path = os.path.join(particular_dir, f'{name}.json')

    # Abrimos el archivo en modo escritura y guardamos los datos del usuario en formato JSON
    with open(user_file_path, 'w') as user_file:
        json.dump(user_data, user_file)  # Escribimos el diccionario en el archivo JSON


# Ruta para crear un nuevo usuario, se usa el método POST
@app.route('/create_user', methods=['POST'])

async def crear_usuario():
    # Esperamos a que se envíe un JSON en la solicitud y lo almacenamos en 'data'
    data = await request.json

    # Verificamos si la contraseña se ha proporcionado en el JSON
    if 'name' not in data or 'password' not in data:
        return jsonify({"error": "Faltan campos obligatorios (name or password)"}), 400  # Devolvemos un error si falta la contraseña
    
    # Asignamos el nombre recibido a la variable 'name'
    name = data['name']  
    # Asignamos la contraseña recibida a la variable 'password'
    password = data['password']

    # Verificamos si el usuario ya existe
    user_file_path = os.path.join(USER_DIR, name, f'{name}.json')
    if os.path.exists(user_file_path):
        return jsonify({"error": "Usuario ya existe"}), 409


    # Generamos un UID único para el usuario
    uid = str(uuid.uuid4())
    # Definimos un UUID secreto, que se usará para generar el token
    secret_uuid = uuid.UUID('00010203-0405-0607-0809-0a0b0c0d0e0f')
    # Generamos el token usando el UUID secreto y el UID del usuario
    token = str(uuid.uuid5(secret_uuid, uid))

    # Llamamos a la función para guardar la información del usuario en un archivo JSON
    guardar_usuario_json(name, password, uid, token)

    # Respondemos con un mensaje de éxito y devolvemos el UID y el token
    return jsonify({
        "message": "Usuario creado",  # Mensaje de éxito
        "uid": uid,  # UID del usuario
        "token": token,  # Token de acceso del usuario
        #"secret_uid": str(secret_uuid)  # UID secreto (opcional en la respuesta)
    }), 200  # Código de estado 200 indica que se ha creado un recurso

# Ruta para iniciar sesión, se usa el método GET
@app.route('/login', methods=['POST']) #unque el objetivo del login es "obtener" un token o confirmar las credenciales, el proceso de autenticar a un usuario implica enviar datos sensibles (como el nombre de usuario y la contraseña). 
                                       #Estos deben ser enviados en el cuerpo de la solicitud, no como parámetros de URL, que es lo que hace un GET.
async def login():
    # Obtenemos la contraseña desde el JSON de la solicitud
    data = await request.json
    if 'name' not in data or 'password' not in data:
        return jsonify({"error": "Faltan campos obligatorios (name, password)"}), 400

    name = data['name']
    password = data['password']
    
    # Verificar si el archivo del usuario existe
    user_file_path = os.path.join(USER_DIR, name, f'{name}.json')
    print(user_file_path)
    if not os.path.exists(user_file_path):
        return jsonify({"error": "Usuario no existe"}), 404
    
    # Abrimos el archivo del usuario en modo lectura para cargar los datos
    with open(user_file_path, 'r') as user_file:
        user_data = json.load(user_file)  # Cargamos los datos del usuario desde el archivo JSON

    # Verificamos si la contraseña ingresada es correcta
    if user_data['password'] != password:
        return jsonify({"error": "Contraseña incorrecta"}), 401  # Error si la contraseña es incorrecta

    # Respuesta exitosa con UID y token
    return jsonify({"message": "Login exitoso", "UID": user_data['uid'], "token": user_data['token']}), 200  # Código de estado 200 para éxito

@app.route('/eliminar_usuario', methods=['DELETE'])
async def eliminar_usuario():
    # Obtenemos el nombre del usuario del cuerpo de la solicitud
    data = await request.json
    if 'name' not in data:
        return jsonify({"error": "Falta el campo 'name' en la solicitud"}), 400

    name = data['name']
    
    # Establecemos la ruta del archivo JSON del usuario
    user_file_path = os.path.join(USER_DIR, name)

    # Comprobamos si el archivo existe
    if not os.path.isdir(user_file_path):
        return jsonify({"error": "El usuario no existe"}), 404  # Usuario no encontrado

    # Eliminamos el archivo
    shutil.rmtree(user_file_path)
    return jsonify({"message": "Usuario eliminado"}), 200  # El usuario fue eliminado con éxito




# Inicia la aplicación en el puerto 5050
if __name__ == '__main__':
    app.run(host = '0.0.0.0',port=5050)  # Cambiar 'localhost' a '0.0.0.0' si se desea accesible externamente
