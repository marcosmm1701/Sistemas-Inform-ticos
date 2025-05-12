# Permite construir consultas SQL utilizando SQLAlchemy
from sqlalchemy import select
# Importa los elementos principales de Quart
from quart import Quart, request, jsonify
#  Importa herramientas para manejar conexiones y sesiones de base de datos
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
# Facilita la creación de sesiones para interactuar con la base de datos
from sqlalchemy.orm import sessionmaker
# Importa los modelos de la base de datos, que representan las tablas y relaciones.
from models import User, Product, Order, OrderDetail, Inventory, Base
# Importa la cadena de conexión a la base de datos.
from config import SQLALCHEMY_DATABASE_URI
# Se utiliza para verificar las contraseñas de los usuarios de forma segura.
from werkzeug.security import check_password_hash
#Se importa para manejar la programación asincrónica en Python.
import asyncio
# Se importa para manejar números decimales con precisión.
from decimal import Decimal
# Se importa para manejar excepciones de integridad en la base de datos.
from sqlalchemy.exc import IntegrityError
# Se importa para usar funciones SQL como max.
from sqlalchemy.sql import func
# Se importa para manejar fechas y horas.
from datetime import datetime

app = Quart(__name__)

# Configuración de la base de datos
engine = create_async_engine(SQLALCHEMY_DATABASE_URI, echo=True, future=True)
SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Crea las tablas en la base de datos al iniciar el servidor, sincronizándolas con los modelos
@app.before_serving
async def startup():
    # Crear las tablas en la base de datos
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Genera una sesión de base de datos asincrónica
async def get_db():
    async with SessionLocal() as session:
        yield session

@app.route('/login', methods=['POST'])
async def login():
    data = await request.get_json()
    username = data.get('username')
    password = data.get('password')

    # Crea una sesión asincrónica con la base de datos usando SessionLocal
    async with SessionLocal() as session:
        # Ejecuta una consulta usando SQLAlchemy
        result = await session.execute(select(User).filter_by(username=username))
        user = result.scalar_one_or_none()  # Devuelve un solo resultado si existe, o None si no
    
    # Verifica si el usuario existe y si la contraseña es correcta    
    if user and user.password == password:
        customer_id = user.customerid
        return jsonify({"message": "Login successful", "customerid": customer_id}), 200
    else:
        return jsonify({"message": "Invalid username or password"}), 401

@app.route('/add_balance', methods=['POST'])
async def add_balance():
    data = await request.get_json()
    customer_id = data.get('customerid')
    amount = data.get('amount')
    
    # Crea una sesión asincrónica con la base de datos usando SessionLocal y la asigna a session
    async with SessionLocal() as session:
        user = await session.get(User, customer_id)
        if user:    # Si el usuario con ese id existe
            if user.balance is None:
                user.balance = Decimal('0.00')
            user.balance = user.balance + Decimal(amount)
            await session.commit()
            return jsonify({"message": "Balance added successfully"}), 200
        else:
            return jsonify({"message": "User not found"}), 404

@app.route('/add_to_cart', methods=['POST'])
async def add_to_cart():
    data = await request.get_json()
    customer_id = data.get('customerid')
    prod_id = data.get('prod_id')
    quantity = data.get('quantity')
   
    # Crea una sesión asincrónica con la base de datos usando SessionLocal y la asigna a session
    async with SessionLocal() as session:
        
        product = await session.get(Product, prod_id)
        inventory = await session.get(Inventory, prod_id)
        
        if not product or inventory.stock < quantity:
            return jsonify({"message": "Product not available"}), 400

        # Busca el carrito pendiente del usuario
        order = await session.execute(select(Order).filter_by(customerid=customer_id, status='Pending'))
        order = order.scalar_one_or_none()

        # Creamos un carrito si no existe
        if not order:
            # Obtiene el siguiente valor disponible para orderid
            result = await session.execute(select(func.max(Order.orderid)))
            max_orderid = result.scalar() or 0  # Si no hay registros, comienza desde 0
            new_orderid = max_orderid + 1
            # Obtiene la fecha actual en formato 'YYYY-MM-DD'
            fecha_actual = func.current_date()
            
            order = Order(orderid = new_orderid, orderdate = fecha_actual,customerid = customer_id, netamount = 0, tax = 21, totalamount = 0, status='Pending')
            session.add(order)
            await session.commit()

        order_detail = OrderDetail(orderid=order.orderid, prod_id=prod_id, quantity=quantity, price=product.price)
        session.add(order_detail)
        await session.commit()
        
    return jsonify({"message": "Product added to cart"}), 200

@app.route('/pay_cart', methods=['POST'])
async def pay_cart():
    data = await request.get_json()
    customer_id = data.get('customerid')
    
    async with SessionLocal() as session:
        order = await session.execute(select(Order).filter_by(customerid=customer_id, status='Pending'))
        order = order.scalar_one_or_none()

        if not order:
            return jsonify({"message": "No pending order found for this customer"}), 400

        user = await session.get(User, customer_id)
        if order.totalamount > user.balance:
            return jsonify({"message": "Insufficient balance"}), 400

        order.status = 'Paid'
        await session.commit()

    return jsonify({"message": "Payment successful"}), 200


###########   FUNCIONES ADICIONALES   ###########


@app.route('/cart_products', methods=['POST'])
async def list_cart_products():
    data = await request.get_json()
    customer_id = data.get('user_id')  # Recibe el 'user_id' directamente desde el cuerpo de la solicitud
                                   # Hemos optado por esta opción por seguridad

    if not customer_id:
        return jsonify({"error": "user_id is required"}), 400

    # Crea una sesión asincrónica con la base de datos
    async with SessionLocal() as session:
        # Consulta los productos en el carrito del usuario
        order = await session.execute(select(Order).filter_by(customerid=customer_id, status='Pending'))
        order = order.scalar_one_or_none()
        
        if not order:
            return jsonify({"message": "No pending order found for this customer"}), 400
        
        order_details_result = await session.execute(
            select(OrderDetail, Product)
            .join(Product, Product.prod_id == OrderDetail.prod_id)
            .filter(OrderDetail.orderid == order.orderid)
        )
        
        cart_items = [
            {
                "product_id": product.prod_id,
                "description": product.description,
                "quantity": order_detail.quantity,
                "price_per_unit": order_detail.price,
                "total_price": order_detail.quantity * order_detail.price
            }
            for order_detail, product in order_details_result.fetchall()
        ]


    # Devuelve el carrito en formato JSON
    return jsonify({"cart_items": cart_items}), 200


@app.route('/register', methods=['POST'])
async def register_user():
    data = await request.get_json()
    
    # Extracción y verificación de datos
    required_fields = ["address", "email", "creditcard", "username", "password"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"{field} is required"}), 400

    
    async with SessionLocal() as session:
        # Verifica si el email ya existe
        result = await session.execute(select(User).filter_by(email=data['email']))
        existing_email_user = result.scalar_one_or_none()
        if existing_email_user:
            return jsonify({"error": "Email already exists"}), 409

        # Verifica si el username ya existe
        result = await session.execute(select(User).filter_by(username=data['username']))
        existing_username_user = result.scalar_one_or_none()
        if existing_username_user:
            return jsonify({"error": "Username already exists"}), 409


         # Obtiene el siguiente valor disponible para customerid
        result = await session.execute(select(func.max(User.customerid)))
        max_customerid = result.scalar() or 0  # Si no hay registros, comienza desde 0
        new_customerid = max_customerid + 1

        # Crea nuevo usuario si el email y username no existen
        new_user = User(
            customerid=new_customerid,
            address=data['address'],
            email=data['email'],
            creditcard=data['creditcard'],
            username=data['username'],
            password=data['password'],
            balance=0    #Hemos decidido que el saldo inicial sea 0, ya que solo los usuarios ya registrados tenian la bonificacion de 0 a 200$

        )

        # Guardaa usuario en la base de datos
        session.add(new_user)
        try:
            await session.commit()
            return jsonify({"message": "User registered successfully"}), 200
        except IntegrityError:      # Captura el error de integridad si ocurre otro tipo de conflicto (por ejemplo, el email/username ya existe)
            await session.rollback()
            return jsonify({"error": "Email or username already exists"}), 409
        except Exception as e:
            await session.rollback()
            return jsonify({"error": str(e)}), 500


@app.route('/delete_user', methods=['DELETE'])
async def eliminar_usuario():
    data = await request.get_json()
    user_id = data.get('customerid')
    async with SessionLocal() as session:
        # Buscar al usuario en la base de datos
        result = await session.execute(select(User).filter_by(customerid=user_id))
        user = result.scalars().first()  # Obtener el primer usuario que coincida

        if not user:
            return jsonify({"message": "Usuario no encontrado"}), 404

        
        try:
            # Obtiene todos los pedidos del usuario
            orders = await session.execute(select(Order).filter_by(customerid = user.customerid))
            orders_list = orders.scalars().all()

            # Obtiene los detalles de los pedidos
            orders_details_list = []
            for order in orders_list:
                order_details = await session.execute(select(OrderDetail).filter_by(orderid=order.orderid))
                orders_details_list.extend(order_details.scalars().all())

            # Elimina los detalles de los pedidos
            for order_detail in orders_details_list:
                await session.delete(order_detail)

            # Elimina los pedidos
            for order in orders_list:
                await session.delete(order)

            # Finalmente, elimina el usuario
            await session.delete(user)
            
            # Commit para guardar los cambios
            await session.commit()

            return jsonify({"message": "Usuario, sus pedidos y detalles han sido eliminados"}), 200
        except Exception as e:
            await session.rollback()  # Hace rollback en caso de error
            return jsonify({"message": "Hubo un error al eliminar el usuario", "error": str(e)}), 500
        finally:
            await session.close()
        
        
        
if __name__ == '__main__':
    app.run(debug=True)
