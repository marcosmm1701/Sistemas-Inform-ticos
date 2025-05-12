from quart import Quart, request, jsonify
from sqlalchemy.ext.asyncio import create_async_engine, AsyncConnection
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.sql import text

app = Quart(__name__)

# Configuración de la base de datos
DATABASE_URI = "postgresql+asyncpg://alumnodb:1234@localhost:5432/si1"
engine = create_async_engine(DATABASE_URI, execution_options={"autocommit": False})


@app.route("/borraCiudad", methods=["POST"])
async def borra_ciudad():
    """
    Punto de acceso que borra todos los clientes de una ciudad y su información asociada.
    """
    data = await request.json
    city = data.get("city")
    use_wrong_order = data.get("use_wrong_order", False)  # Para usar orden incorrecto
    commit_before_error = data.get("commit_before_error", False)  # Para usar commit intermedio

    if not city:
        return jsonify({"error": "Falta el parámetro 'city'"}), 400
    
    # Verificamos si hay clientes en la ciudad especificada
    async with engine.connect() as conn:
        result = await conn.execute(
            text("SELECT COUNT(*) FROM customers WHERE city = :city"),
            {"city": city}
        )
        count = result.scalar()  # Obtiene el valor de la primera columna de la primera fila

        if count == 0:
            return jsonify({"error": f"No hay clientes en la ciudad '{city}'"}), 404

    async with engine.connect() as conn:  # Usamos conexión asíncrona
        trans = await conn.begin()  # Iniciamos la transacción
        try:
            print(f"Iniciando transacción para borrar clientes de la ciudad '{city}'")

            if commit_before_error:
                print("Haciendo un COMMIT intermedio...")
                await trans.commit()
                trans = await conn.begin()

            if use_wrong_order:
                # Intento de borrado en orden incorrecto para forzar un error
                print("Usando orden incorrecto para el borrado.")
                await conn.execute(
                    text("DELETE FROM customers WHERE city = :city"),
                    {"city": city}
                )

                # Esto debería fallar si hay restricciones de claves foráneas
                await conn.execute(
                    text("DELETE FROM orders WHERE customerid IN (SELECT customerid FROM customers WHERE city = :city)"),
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

                
                await conn.execute(
                    text("DELETE FROM orders WHERE customerid IN (SELECT customerid FROM customers WHERE city = :city)"),
                    {"city": city}
                )
                await conn.execute(
                    text("DELETE FROM customers WHERE city = :city"),
                    {"city": city}
                )

            # Commit de la transacción si todo salió bien
            await trans.commit()
            print("Transacción completada con éxito.")
            return jsonify({"message": f"Clientes de la ciudad '{city}' borrados con éxito."}), 200

        except IntegrityError as ie:
            print(f"Error de integridad detectado: {ie}")
            await trans.rollback()
            print("Rollback realizado debido a un error de integridad.")
            return jsonify({"error": "Error de integridad durante el borrado, cambios deshechos."}), 400

        except SQLAlchemyError as e:
            print(f"Error de la base de datos detectado: {e}")
            await trans.rollback()
            print("Rollback realizado debido a un error en la base de datos.")
            return jsonify({"error": "Error en la base de datos, cambios deshechos."}), 500

        except Exception as e:
            print(f"Error desconocido: {e}")
            await trans.rollback()
            print("Rollback realizado debido a un error desconocido.")
            return jsonify({"error": "Error desconocido, cambios deshechos."}), 500


if __name__ == "__main__":
    app.run(debug=True)
