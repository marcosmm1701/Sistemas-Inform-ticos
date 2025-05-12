import requests
import json

# Configuración del servidor
API_URL = "http://localhost:5000/borraCiudad"


def test_borra_ciudad(city, use_wrong_order=False, commit_before_error=False):
    """
    Envía una solicitud POST al servidor para probar el endpoint borraCiudad.
    
    Args:
        city (str): Ciudad cuyos clientes se desean borrar.
        use_wrong_order (bool): Si se usa el orden incorrecto de borrado.
        commit_before_error (bool): Si se realiza un COMMIT intermedio antes del error.
    """
    data = {
        "city": city,
        "use_wrong_order": use_wrong_order,
        "commit_before_error": commit_before_error
    }

    print(f"\n=== Probando borrado para ciudad: '{city}' ===")
    print(f"Parámetros: Orden incorrecto: {use_wrong_order}, Commit intermedio: {commit_before_error}")

    try:
        response = requests.post(API_URL, json=data)
        print("Respuesta del servidor:", response.json())
        if response.status_code == 200:
            print("✔ Éxito: ", response.json()["message"])
        else:
            print("✘ Error: ", response.json()["error"])
    except requests.RequestException as e:
        print(f"Error de conexión con el servidor: {e}")


def menu():
    """
    Menú principal para probar las funcionalidades del cliente.
    """
    while True:
        print("\n--- Cliente de Pruebas para borraCiudad ---")
        print("1. Borrar clientes con orden correcto")
        print("2. Borrar clientes con orden incorrecto (provocar error)")
        print("3. Borrar clientes con COMMIT intermedio y luego error")
        print("4. Salir")
        
        choice = input("Seleccione una opción: ")

        if choice == "1":
            city = input("Ingrese la ciudad: ").strip()
            test_borra_ciudad(city, use_wrong_order=False, commit_before_error=False)

        elif choice == "2":
            city = input("Ingrese la ciudad: ").strip()
            test_borra_ciudad(city, use_wrong_order=True, commit_before_error=False)

        elif choice == "3":
            city = input("Ingrese la ciudad: ").strip()
            test_borra_ciudad(city, use_wrong_order=True, commit_before_error=True)

        elif choice == "4":
            print("Saliendo del cliente.")
            break

        else:
            print("Opción no válida. Por favor, elija una opción del menú.")


if __name__ == "__main__":
    print("Iniciando cliente para pruebas de API...")
    menu()
