import requests
import json
from hashlib import sha1
import colorama
from colorama import Fore, Style

url_user = "http://localhost:5050/"
url_file = "http://localhost:5051/"

# Inicializamos colorama
colorama.init(autoreset=True)

# Definición del tick verde
tick = "✓"
frase_exito = "Operación exitosa"

# Definición de la "X" roja
x_roja = "X"
frase_fracaso = "Operación fallida"


############# TEST DE USER #############

print()
print(" >>> EMPIEZA EL TEST DE user.py <<<")

print()
print("$$$$$$$$$  Creando usuario Beatriz con password supersecreta1234...  $$$$$$$$$")
print()
print("Debe devolver Operación exitosa")

url = url_user + "create_user"
headers = {"Content-Type": "application/json"}
data = {"name": "Beatriz", "password": "supersecreta1234"}
response = requests.post(url, headers=headers, data=json.dumps(data))
if response.status_code == 200:
    print(response.json())
    # Imprimimos el tick en verde y la frase_exito
    print(f"{Fore.GREEN}{tick} {frase_exito}{Style.RESET_ALL}")
else:
    print(f"{Fore.RED}{x_roja} {frase_fracaso}{Style.RESET_ALL}")
    print(response.json())
    raise Exception("Error al crear el usuario")
    
print()
print("$$$$$$$$$    Iniciando sesion...  $$$$$$$$$")
print()
print("Debe devolver Operación exitosa y además su UID")

url = url_user + "login"
headers = {"Content-Type": "application/json"}
data = {"name": "Beatriz", "password": "supersecreta1234"}
response = requests.post(url, headers=headers, data=json.dumps(data))
if response.status_code == 200:
    print(response.json())
    # Imprimimos el tick en verde y la frase_exito
    print(f"{Fore.GREEN}{tick} {frase_exito}{Style.RESET_ALL}")

    UID = response.json()["UID"]
    token = response.json()["token"]
else:
    print(f"{Fore.RED}{x_roja} {frase_fracaso}{Style.RESET_ALL}")
    raise Exception("Error al iniciar sesion")
    
print()
print(" >>> TERMINA EL TEST DE user.py <<<")


############# TEST DE FILE #############


print()
print(" >>> EMPIEZA EL TEST DE file.py <<<")

print()
print("$$$$$$$$$    Probando la subida de archivos...  $$$$$$$$$")
print()
print("Creando el fichero fichero_001.txt con el contenido 'texto de prueba del fichero'")
print("Debe devolver Operación exitosa")

url = url_file + "subir"
headers = {}
headers["Content-Type"] = "application/json"
headers["Authorization"] = "Bearer " + token
data = {}
data["uid"] = UID
data["filename"] = "fichero_001.txt"
data["content"] = "texto de prueba del fichero"
response = requests.post(url, headers=headers, data=json.dumps(data))
if response.status_code == 200:
    print(response.json())
    # Imprimimos el tick en verde y la frase_exito
    print(f"{Fore.GREEN}{tick} {frase_exito}{Style.RESET_ALL}")
else:
    print(f"{Fore.RED}{x_roja} {frase_fracaso}{Style.RESET_ALL}")
    raise Exception("Error al subir el archivo")
    
    
print()
print("$$$$$$$$$    Probando la obtención de archivos...  $$$$$$$$$")
print()
print("Debe devolver Operación exitosa y el contenido del fichero")

url = url_file + "leer"
data = {}
data["uid"] = UID
data["filename"] = "fichero_001.txt"
response = requests.get(url, headers=headers, data=json.dumps(data))
if response.status_code == 200:
    print("{"+ response.text + "}")
    # Imprimimos el tick en verde y la frase_exito
    print(f"{Fore.GREEN}{tick} {frase_exito}{Style.RESET_ALL}")
    
else:
    print(f"{Fore.RED}{x_roja} {frase_fracaso}{Style.RESET_ALL}")
    raise Exception("Error al leer el archivo")


print()
print("$$$$$$$$$    Probando la lista de archivos...  $$$$$$$$$")
print()
print("Debe devolver Operación exitosa y la lista de archivos del usuario") 

url = url_file + "listar"
headers = {}
headers["Content-Type"] = "application/json"
headers["Authorization"] = "Bearer " + token
data = {}
data["uid"] = UID
response = requests.get(url, headers=headers, data=json.dumps(data))
if response.status_code == 200:
    print(response.json())
    # Imprimimos el tick en verde y la frase_exito
    print(f"{Fore.GREEN}{tick} {frase_exito}{Style.RESET_ALL}")
    
else:
    print(f"{Fore.RED}{x_roja} {frase_fracaso}{Style.RESET_ALL}")
    raise Exception("Error al listar los archivos")
    

print()
print("$$$$$$$$$    Probando la eliminación de archivos...  $$$$$$$$$")
print()
print("Debe devolver Operación exitosa")

url = url_file + "eliminar"
headers = {}
headers["Content-Type"] = "application/json"
headers["Authorization"] = "Bearer " + token
data = {}
data["uid"] = UID
data["filename"] = "fichero_001.txt"
response = requests.delete(url, headers=headers, data=json.dumps(data))
if response.status_code == 200:
    print(response.json())
    # Imprimimos el tick en verde y la frase_exito
    print(f"{Fore.GREEN}{tick} {frase_exito}{Style.RESET_ALL}")
    
else:
    print(f"{Fore.RED}{x_roja} {frase_fracaso}{Style.RESET_ALL}")
    raise Exception("Error al eliminar el archivo")

print()
print(" >>> TERMINA EL TEST DE file.py <<<")

print()
print()

############# TEST DE ERRORES #############


print(" >>> EMPIEZA EL TEST DE CONTROL DE ERRORES <<<")
print()

print("$$$$$$$$$  Creando usuario duplicado (Beatriz)...  $$$$$$$$$")
print()
print("Debe devolver un error (409 Usuario ya existe)")

url = url_user + "create_user"
data = {"name": "Beatriz", "password": "supersecreta1234"}
response = requests.post(url, headers=headers, data=json.dumps(data))
if response.status_code == 409:
    print("Error esperado:", response.json())
    # Imprimimos el tick en verde y la frase_exito
    print(f"{Fore.GREEN}{tick} {frase_exito}{Style.RESET_ALL}")
else:
    print("Error no esperado")
    print(f"{Fore.RED}{x_roja} {frase_fracaso}{Style.RESET_ALL}")


print()
print("$$$$$$$$$  Iniciar sesión con credenciales incorrectas...  $$$$$$$$$")
print()
print("Debe devolver un error (401 Credenciales incorrectas)")

url = url_user + "login"
data = {"name": "Beatriz", "password": "wrongpassword"}
response = requests.post(url, headers=headers, data=json.dumps(data))
if response.status_code == 401:
    print("Error esperado:", response.json())
    # Imprimimos el tick en verde y la frase_exito
    print(f"{Fore.GREEN}{tick} {frase_exito}{Style.RESET_ALL}")
else:
    print("Error no esperado")
    print(f"{Fore.RED}{x_roja} {frase_fracaso}{Style.RESET_ALL}")


print()
print("$$$$$$$$$  Subir archivo sin autenticación...  $$$$$$$$$")
print()
print("Debe devolver un error (403 Sin autorización)")

url = url_file + "subir"
headers = {"Content-Type": "application/json"}  # Sin token
data = {"uid": UID, "filename": "fichero_002.txt", "content": "nuevo contenido"}
response = requests.post(url, headers=headers, data=json.dumps(data))
if response.status_code == 403:
    print("Error esperado:", response.json())
    # Imprimimos el tick en verde y la frase_exito
    print(f"{Fore.GREEN}{tick} {frase_exito}{Style.RESET_ALL}")
else:
    print("Error no esperado")
    print(f"{Fore.RED}{x_roja} {frase_fracaso}{Style.RESET_ALL}")



print()
print("$$$$$$$$$  Leer archivo que no existe...  $$$$$$$$$")
print()
print("Debe devolver un error (404 Archivo no encontrado)")

url = url_file + "leer"
data = {"uid": UID, "filename": "archivo_inexistente.txt"}
response = requests.get(url, headers=headers, data=json.dumps(data))
if response.status_code == 404:
    print("Error esperado:", response.json())
    # Imprimimos el tick en verde y la frase_exito
    print(f"{Fore.GREEN}{tick} {frase_exito}{Style.RESET_ALL}")
else:
    print("Error no esperado")
    print(f"{Fore.RED}{x_roja} {frase_fracaso}{Style.RESET_ALL}")

print()
print("$$$$$$$$$  Eliminar archivo que no existe...  $$$$$$$$$")
print()
print("Debe devolver un error (404 Archivo no encontrado)")

url = url_file + "eliminar"
headers = {}
headers["Content-Type"] = "application/json"
headers["Authorization"] = "Bearer " + token
data = {"uid": UID, "filename": "archivo_inexistente.txt"}
response = requests.delete(url, headers=headers, data=json.dumps(data))
if response.status_code == 404:
    print("Error esperado:", response.json())
    # Imprimimos el tick en verde y la frase_exito
    print(f"{Fore.GREEN}{tick} {frase_exito}{Style.RESET_ALL}")
else:
    print("Error no esperado")
    print(f"{Fore.RED}{x_roja} {frase_fracaso}{Style.RESET_ALL}")

print()
print(" >>> TERMINA EL TEST DE CONTROL DE ERRORES <<<")
print()
print()

############# TEST DE ELIMINACION DE USUARIOS #############

print(" >>> EMPIEZA EL TEST DE ELIMINACION DE USUARIOS <<<")
print()
print("$$$$$$$$$  Eliminar usuario Beatriz...  $$$$$$$$$")
print()
print("Debe devolver Operación exitosa y el mensaje 'Usuario eliminado'")

url = url_user + "eliminar_usuario"
data = {"name": "Beatriz"}
response = requests.delete(url, headers=headers, data=json.dumps(data))
if response.status_code == 200:
    print(response.json())
    # Imprimimos el tick en verde y la frase_exito
    print(f"{Fore.GREEN}{tick} {frase_exito}{Style.RESET_ALL}")
else:
    print(f"{Fore.RED}{x_roja} {frase_fracaso}{Style.RESET_ALL}")

print()
print("$$$$$$$$$  Eliminando archivos del usuario Beatriz...  $$$$$$$$$")
print()
print("Debe devolver Operación exitosa y el mensaje 'Directorio del usuario eliminado con exito'")

url = url_file + "eliminar_dir"
data = {"uid": UID}
response = requests.delete(url, headers=headers, data=json.dumps(data))
if response.status_code == 200:
    print(response.json())
    # Imprimimos el tick en verde y la frase_exito
    print(f"{Fore.GREEN}{tick} {frase_exito}{Style.RESET_ALL}")
else:
    print(f"{Fore.RED}{x_roja} {frase_fracaso}{Style.RESET_ALL}")


print()
print("$$$$$$$$$  Eliminar usuario que no existe...  $$$$$$$$$")
print()
print("Debe devolver un error (404 Usuario no encontrado)")

url = url_user + "eliminar_usuario"
data = {"name": "Beatriz"}
response = requests.delete(url, headers=headers, data=json.dumps(data))
if response.status_code == 404:
    print("Error esperado:", response.json())
    # Imprimimos el tick en verde y la frase_exito
    print(f"{Fore.GREEN}{tick} {frase_exito}{Style.RESET_ALL}")
else:
    print("Error no esperado")
    print(f"{Fore.RED}{x_roja} {frase_fracaso}{Style.RESET_ALL}")


print()
print(" >>> TERMINA EL TEST DE ELIMINACION DE USUARIOS <<<")
print()