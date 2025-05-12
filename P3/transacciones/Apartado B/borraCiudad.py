from sqlalchemy.ext.asyncio import create_async_engine, AsyncConnection
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.sql import text
import asyncio

# Configuración de la base de datos
DATABASE_URI = "postgresql+asyncpg://alumnodb:1234@localhost:5432/si1"
engine = create_async_engine(DATABASE_URI, execution_options={"autocommit": False})

async def borra_ciudad(city, use_wrong_order=False, commit_before_error=False):
    """
    Función que borra todos los clientes de una ciudad y su información asociada.
    :param city: Ciudad cuyos clientes se desean eliminar.
    :param use_wrong_order: Si se debe usar un orden incorrecto para provocar errores.
    :param commit_before_error: Si se debe hacer un commit intermedio.
    """
    # Verificar si existen clientes en la ciudad
    async with engine.connect() as conn:
        result = await conn.execute(
            text("SELECT COUNT(*) FROM customers WHERE city = :city"),
            {"city": city}
        )
        count = result.scalar()

        if count == 0:
            print(f"No hay clientes en la ciudad '{city}'.")
            return

    async with engine.connect() as conn:  # Iniciamos una conexión
        trans = await conn.begin()  # Iniciamos la transacción
        try:
            print(f"Iniciando transacción para borrar clientes de la ciudad '{city}'")

            if commit_before_error:
                print("Haciendo un COMMIT intermedio...")
                await trans.commit()
                trans = await conn.begin()

            if use_wrong_order:
                # Intento de borrado en orden incorrecto
                print("Usando orden incorrecto para el borrado.")
                await conn.execute(
                    text("DELETE FROM customers WHERE city = :city"),
                    {"city": city}
                )
                await conn.execute(
                    text("DELETE FROM orders WHERE customerid IN "
                         "(SELECT customerid FROM customers WHERE city = :city)"),
                    {"city": city}
                )
            else:
                # Orden correcto de borrado
                print("Usando orden correcto para el borrado.")
                await conn.execute(
                    text("DELETE FROM orderdetail WHERE orderid IN "
                         "(SELECT orderid FROM orders WHERE customerid IN "
                         "(SELECT customerid FROM customers WHERE city = :city))"),
                    {"city": city}
                )

                # Simulamos un retraso con pg_sleep
                print("Simulando latencia con pg_sleep...")
                await conn.execute(text("SELECT pg_sleep(10)"))

                await conn.execute(
                    text("DELETE FROM orders WHERE customerid IN "
                         "(SELECT customerid FROM customers WHERE city = :city)"),
                    {"city": city}
                )
                await conn.execute(
                    text("DELETE FROM customers WHERE city = :city"),
                    {"city": city}
                )

            # Commit de la transacción
            await trans.commit()
            print(f"Clientes de la ciudad '{city}' borrados con éxito.")

        except IntegrityError as ie:
            print(f"Error de integridad detectado: {ie}")
            await trans.rollback()
            print("Rollback realizado debido a un error de integridad.")

        except SQLAlchemyError as e:
            print(f"Error de la base de datos detectado: {e}")
            await trans.rollback()
            print("Rollback realizado debido a un error en la base de datos.")

        except Exception as e:
            print(f"Error desconocido: {e}")
            await trans.rollback()
            print("Rollback realizado debido a un error desconocido.")

# Ejecución principal para realizar pruebas
if __name__ == "__main__":
    # Modificar estos parámetros según los casos de prueba necesarios
    city_to_delete = "timur"
    use_wrong_order = False  # Cambiar a True para usar un orden incorrecto
    commit_before_error = False  # Cambiar a True para probar commit intermedio

    asyncio.run(borra_ciudad(city_to_delete, use_wrong_order, commit_before_error))
