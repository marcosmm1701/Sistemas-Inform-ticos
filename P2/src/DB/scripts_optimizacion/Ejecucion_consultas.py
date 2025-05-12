#Archivo extra: no se solicitaba en la práctica, pero se incluye para facilitar la ejecución de consultas SQL
import psycopg2

def ejecutar_consulta(anio, pais):
    # Configura los parámetros de conexión a la base de datos
    conexion = psycopg2.connect(
        host="127.0.0.1",  # Dirección de la base de datos (localhost en este caso)
        port="5433",       # Puerto, de la segunda base de datos
        database="si2",    # Nombre de la base de datos
        user="alumnodb",   # Usuario de la base de datos
        password="1234"    # Contraseña de la base de datos
    )
    
    # Define el cursor
    cursor = conexion.cursor()

    # Define la consulta SQL con placeholders
    consulta_sql = """
        EXPLAIN
        SELECT COUNT(DISTINCT state) 
        FROM customers AS c 
        JOIN orders AS o ON c.customerid = o.customerid 
        WHERE EXTRACT(YEAR FROM o.orderdate) = %s AND c.country = %s;
    """
    
    try:
        # Ejecuta la consulta con los valores dados para anio y pais
        cursor.execute(consulta_sql, (anio, pais))
        
        # Recupera el resultado
        resultado = cursor.fetchone()[0]
        print(f"El número de estados distintos: {resultado}")
        
    except Exception as e:
        print(f"Error al ejecutar la consulta: {e}")
        
    finally:
        # Cierra el cursor y la conexión
        cursor.close()
        conexion.close()

# Llama a la función con los parámetros deseados
ejecutar_consulta(2017, 'Perú')
