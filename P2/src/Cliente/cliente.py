import requests
import colorama
from colorama import Fore, Style

BASE_URL = "http://127.0.0.1:5000"

# 1. Registra y autentica al usuario
def register_user(address, email, creditcard, username, password):
    data = {
        "username": username,
        "email": email,
        "password": password,
        "address": address,
        "creditcard": creditcard    
    }
    response = requests.post(f"{BASE_URL}/register", json=data)
    print("Register Response:", response.json())
    return response

# 2. Inicio de sesión del usuario
def login_user(username, password):
    data = {
        "username": username,
        "password": password
    }
    response = requests.post(f"{BASE_URL}/login", json=data)
    print("Login Response:", response.json())
    return response

# 3. Añadir saldo a la cuenta del usuario
def add_balance(customer_id, amount):
    data = {
        "customerid": customer_id,
        "amount": amount
    }
    response = requests.post(f"{BASE_URL}/add_balance", json=data)
    print("Add Balance Response:", response.json())
    return response

# 4. Añadir productos al carrito
def add_to_cart(customer_id, product_id, quantity):
    data = {
        "customerid" : customer_id,
        "prod_id": product_id,
        "quantity": quantity
    }
    response = requests.post(f"{BASE_URL}/add_to_cart", json=data)
    print("Add TO Cart Response:", response.json())
    return response

# 5. Ver carrito actual
def view_cart(customer_id):
    data = {
        "user_id": customer_id
    }
    response = requests.post(f"{BASE_URL}/cart_products", json=data)
    print("View Cart Response:", response.json())
    return response

# 6. Realizar el pago del carrito
def checkout(customer_id):
    data = {
        "customerid": customer_id
    }
    response = requests.post(f"{BASE_URL}/pay_cart",  json=data)
    print("Checkout Response:", response.json())
    return response

# 7. Eliminar el usuario
def customer_delete(customer_id):
    data = {
        "customerid": customer_id
    }
    response = requests.delete(f"{BASE_URL}/delete_user", json=data)
    print("Delete User Response:", response.json())
    return response


# Función principal de pruebas exhaustivas
def main():
    
    # Inicializamos colorama
    colorama.init(autoreset=True)

    # Definición del tick verde
    tick = "✓"
    frase_exito = "Operación exitosa"

    # Definición de la "X" roja
    x_roja = "X"
    frase_fracaso = "Operación fallida"

    
    # Usuario de prueba
    username = "Javier"
    email = "LaSemanaDeJavier@uam.com"
    password = "securepassword123"
    address = "1234 Main St, Springfield, IL"
    creditcard = "1234-5678-9012-3456"
    initial_balance = 10000  # Para garantizar que se pueden hacer las compras
    product_quantity = 2  # Cantidad por producto en las pruebas
    customer_id = None
    products = [1,2,3,4,5]  # Lista de ids de productos a añadir al carrito

    # Prueba 1: Registrar usuario
    print("\n=== Registration Test ===")
    register_response = register_user(address, email, creditcard, username, password)
    
    if register_response.status_code == 200:
        print(f"{Fore.GREEN}{tick} {frase_exito}{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}{x_roja} {frase_fracaso}{Style.RESET_ALL}")
        raise Exception("Error al crear el usuario")

    # Prueba 2: Iniciar sesión
    print("\n=== Login Test ===")
    login_response = login_user(username, password)
    if login_response.status_code == 200:
        print(f"{Fore.GREEN}{tick} {frase_exito}{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}{x_roja} {frase_fracaso}{Style.RESET_ALL}")
        raise Exception("Error al iniciar sesión")
    customer_id = login_response.json().get("customerid")

    # Prueba 3: Añadir saldo al usuario
    print("\n=== Add Balance Test ===")
    add_balance_response = add_balance(customer_id, initial_balance)
    if add_balance_response.status_code == 200:
        print(f"{Fore.GREEN}{tick} {frase_exito}{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}{x_roja} {frase_fracaso}{Style.RESET_ALL}")
        raise Exception("Error al añadir saldo al usuario")

    # Prueba 4: Añadir productos al carrito
    print("\n=== Add Products to Cart Test ===")
    for prod_id in products:  # Seleccionamos hasta 3 productos para la prueba
        add_to_cart_response = add_to_cart(customer_id, prod_id, product_quantity)
        if add_to_cart_response.status_code == 200:
            print(f"{Fore.GREEN}{tick} {frase_exito}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}{x_roja} {frase_fracaso}{Style.RESET_ALL}")
            raise Exception("Error al añadir productos al carrito. Producto: ", prod_id)

    # Prueba 5: Verificar el carrito actual
    print("\n=== View Cart Test ===")
    view_cart_response = view_cart(customer_id)
    if view_cart_response.status_code == 200:
        print(f"{Fore.GREEN}{tick} {frase_exito}{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}{x_roja} {frase_fracaso}{Style.RESET_ALL}")
        raise Exception("Error al ver el carrito")

    # Prueba 6: Realizar el pago del carrito
    print("\n=== Checkout Test ===")
    checkout_response = checkout(customer_id)
    if checkout_response.status_code == 200:
        print(f"{Fore.GREEN}{tick} {frase_exito}{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}{x_roja} {frase_fracaso}{Style.RESET_ALL}")
        raise Exception("Error al realizar el pago del carrito")


    # Prueba 7: Eliminar el usuario
    print("\n=== Delete User Test ===")
    delete_response = customer_delete(customer_id)
    if delete_response.status_code == 200:
        print(f"{Fore.GREEN}{tick} {frase_exito}{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}{x_roja} {frase_fracaso}{Style.RESET_ALL}")
        raise Exception("Error al eliminar el usuario")
if __name__ == "__main__":
    main()
