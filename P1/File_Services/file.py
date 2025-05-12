import os
import uuid
import json
from quart import Quart, request, jsonify
import shutil

app = Quart(__name__)

"""# Directorio raíz donde se almacenarán las bibliotecas de los usuarios
ROOT_DIR = "bibliotecas"
FILE_DIR = os.path.join(ROOT_DIR, "file")
USER_DIR = os.path.join(ROOT_DIR, "user")

# Crear el directorio raíz si no existe
os.makedirs(ROOT_DIR, exist_ok=True)
os.makedirs(FILE_DIR, exist_ok=True)"""


# Directorio base donde se almacenarán los archivos de los usuarios
FILE_DIR = "Files_data"


def verificar_token(authorization, uid):
    if authorization is None or uid is None:
        return False
    try:
        # Separamos el token en su formato 'Bearer token'
        tipo, token = authorization.split()
        if tipo != 'Bearer':
            return False
        
        secret_uuid = uuid.UUID('00010203-0405-0607-0809-0a0b0c0d0e0f')
        # Generamos el token esperado usando el UUID secreto y el UID del usuario
        token_esperado = str(uuid.uuid5(secret_uuid, uid))
        # Verificamos si el token enviado coincide con el esperado
        return token == token_esperado
    except ValueError:
        return False

# Ruta para subir un archivo
@app.route('/subir', methods=['POST'])
async def subir_archivo():
    data = await request.json
    if 'uid' not in data or 'filename' not in data or 'content' not in data:
        return jsonify({"error": "Faltan campos obligatorios (uid, filename, content)"}), 400
    
    uid = data['uid']
    filename = data['filename']
    content = data['content']
    
    # Verificar token en la cabecera Authorization
    authorization = request.headers.get('Authorization')
    if not verificar_token(authorization, uid):
        return jsonify({"error": "Token no valido"}), 403
    
    user_dir = os.path.join(FILE_DIR, uid)
    os.makedirs(user_dir, exist_ok=True) # Crear directorio si no existe
    file_path = os.path.join(user_dir, filename)

    with open(file_path, 'w') as f:
        f.write(content)

    return jsonify({"message": f"Archivo {filename} subido con exito"}), 200



# Ruta para obtener un archivo
@app.route('/leer', methods=['GET'])
async def obtener_archivo():
    data = await request.json 
    if 'uid' not in data or 'filename' not in data:
        return jsonify({"error": "Faltan campos obligatorios (uid, filename)"}), 400
    
    uid = data['uid']
    filename = data['filename']
    
    file_path = os.path.join(FILE_DIR, uid, filename)
    if not os.path.exists(file_path):
        return jsonify({"error": "Archivo no encontrado"}), 404

    with open(file_path, 'r') as f:
        data = f.read()

    return data, 200

# Ruta para eliminar un archivo
@app.route('/eliminar', methods=['DELETE'])
async def eliminar_archivo():
    data = await request.json 
    if 'uid' not in data or 'filename' not in data:
        return jsonify({"error": "Faltan campos obligatorios (uid, filename)"}), 400
    
    uid = data['uid']
    filename = data['filename']
    
    # Verificar token en la cabecera Authorization
    authorization = request.headers.get('Authorization')
    if not verificar_token(authorization, uid):
        return jsonify({"error": "Token no valido"}), 403

    file_path = os.path.join(FILE_DIR, uid, filename)
    if not os.path.exists(file_path):
        return jsonify({"error": "Archivo no encontrado"}), 404

    os.remove(file_path)
    return jsonify({"message": f"Archivo {filename} eliminado con exito"}), 200



# Ruta para listar los archivos de un usuario
@app.route('/listar', methods=['GET'])
async def listar_archivos():
    data = await request.json 
    if 'uid' not in data:
        return jsonify({"error": "Faltan campos obligatorios (uid)"}), 400
    
    uid = data['uid']
    # Verificar token en la cabecera Authorization
    authorization = request.headers.get('Authorization')
    if not verificar_token(authorization, uid):
        return jsonify({"error": "Token no valido"}), 403

    # Obtener el directorio del usuario
    user_dir = os.path.join(FILE_DIR, uid)
    if not os.path.exists(user_dir):
        return jsonify({"error": "Usuario no encontrado (UID inexistente)"}), 404

    # Listar los archivos en el directorio del usuario
    archivos = os.listdir(user_dir)
    
    return jsonify({"archivos": archivos}), 200


# Ruta para eliminar un archivo
@app.route('/eliminar_dir', methods=['DELETE'])
async def eliminar_directorio():
    data = await request.json 
    if 'uid' not in data:
        return jsonify({"error": "Faltan campos obligatorios (uid)"}), 400
    
    uid = data['uid']
    
    user_path = os.path.join(FILE_DIR, uid)
    if not os.path.isdir(user_path):
        return jsonify({"error": "Archivo no encontrado"}), 404

    else: 
        shutil.rmtree(user_path)
    return jsonify({"message": f"Directorio del usuario eliminado con exito"}), 200



if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5051)

 
