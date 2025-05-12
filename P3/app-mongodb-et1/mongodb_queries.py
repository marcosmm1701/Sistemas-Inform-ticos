from pymongo import MongoClient
import pandas as pd  # Para manejar los resultados en formato DataFrame

# Configuración para conectarse a MongoDB
MONGO_URL = "mongodb://localhost:27017/"
DB_NAME = "si1"
COLLECTION_NAME = "france"

# Conexión con la colección de MongoDB
def connect_mongodb():
    client = MongoClient(MONGO_URL)
    db = client[DB_NAME]
    return db[COLLECTION_NAME]

# Consulta (a): Películas de ciencia ficción entre 1994 y 1998
def query_sci_fi_movies(collection):
    query = {
        "genres": "Sci-Fi",  # Género: ciencia ficción
        "year": {"$gte": 1994, "$lte": 1998}  # Años entre 1994 y 1998
    }
    results = list(collection.find(query))
    return pd.DataFrame(results)

# Consulta (b): Películas de drama del año 1998 que empiecen por "The"
def query_drama_the_movies(collection):
    query = {
        "genres": "Drama",  # Género: drama
        "year": 1998,  # Año 1998
        "title": {"$regex": r"(^The |, The$)"}  # Títulos que empiezan con "The" o terminan en ", The"
    }
    results = list(collection.find(query))
    return pd.DataFrame(results)

# Consulta (c): Películas en las que Faye Dunaway y Viggo Mortensen hayan compartido reparto
def query_shared_cast_movies(collection):
    query = {
        "actors": {"$all": ["Dunaway, Faye", "Mortensen, Viggo"]}  # Ambos actores deben estar en el reparto
    }
    results = list(collection.find(query))
    return pd.DataFrame(results)

# Ejecución principal
if __name__ == "__main__":
    # Conectar a la colección de MongoDB
    collection = connect_mongodb()

    # Consulta (a)
    print("\nConsulta (a): Películas de ciencia ficción entre 1994 y 1998")
    sci_fi_movies = query_sci_fi_movies(collection)
    print(sci_fi_movies)

    # Consulta (b)
    print("\nConsulta (b): Películas de drama del año 1998 que comienzan con 'The'")
    drama_the_movies = query_drama_the_movies(collection)
    print(drama_the_movies)

    # Consulta (c)
    print("\nConsulta (c): Películas en las que Faye Dunaway y Viggo Mortensen compartieron reparto")
    shared_cast_movies = query_shared_cast_movies(collection)
    print(shared_cast_movies)
