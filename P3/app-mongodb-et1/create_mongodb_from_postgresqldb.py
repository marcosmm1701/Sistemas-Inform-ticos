import pymongo
from sqlalchemy import create_engine, text

# Configuración para PostgreSQL
POSTGRES_URL = "postgresql://alumnodb:1234@localhost:5432/si1"

# Configuración para MongoDB
MONGO_URL = "mongodb://localhost:27017/"
DB_NAME = "si1"
COLLECTION_NAME = "france"

# Parte 1: Creamos la base de datos y la colección en MongoDB
def create_mongo():
    # Conexión a MongoDB
    mongo_client = pymongo.MongoClient(MONGO_URL)
    mongo_db = mongo_client[DB_NAME]

    # Crea la colección "France"
    try:
        mongo_db.create_collection(COLLECTION_NAME)
    except pymongo.errors.CollectionInvalid:
        print(f"La colección {COLLECTION_NAME} ya existe.")

    # Define el esquema JSON para la validación de los documentos
    vexpr = {
        "$jsonSchema": {
            "required": ["title", "year", "genres", "directors", "actors"],
            "properties": {
                "title": {"bsonType": "string"},
                "year": {"bsonType": "int"},
                "genres": {"bsonType": "array", "items": {"bsonType": "string"}},
                "directors": {"bsonType": "array", "items": {"bsonType": "string"}},
                "actors": {"bsonType": "array", "items": {"bsonType": "string"}},
                "most_related_movies": {
                    "bsonType": "array",
                    "items": {
                        "bsonType": "object",
                        "properties": {
                            "title": {"bsonType": "string"},
                            "year": {"bsonType": "int"}
                        }
                    }
                },
                "related_movies": {     # Lista de películas relacionadas
                    "bsonType": "array",
                    "items": {
                        "bsonType": "object",
                        "properties": {
                            "title": {"bsonType": "string"},
                            "year": {"bsonType": "int"}
                        }
                    }
                }
            }
        }
    }

    # Comando para aplicar el esquema de validación
    cmd = {
        "collMod": COLLECTION_NAME,
        "validator": vexpr,
        "validationLevel": "moderate"
    }
    mongo_db.command(cmd)   # Aplica el esquema de validación
    print("Validador aplicado correctamente.")

# Parte 2: Extraemos datos de PostgreSQL y cargarlos en MongoDB
def load_mongo():
    # Conexión a PostgreSQL
    engine = create_engine(POSTGRES_URL)

    # Conexión a MongoDB
    mongo_client = pymongo.MongoClient(MONGO_URL)
    mongo_db = mongo_client[DB_NAME]
    collection = mongo_db[COLLECTION_NAME]

    # Consulta para obtener las películas francesas
    query = text("""
        SELECT p.movieid, p.movietitle, p.year, mg.genre, d.directorname AS director, a.actorname AS actor
        FROM imdb_movies p
        JOIN imdb_moviecountries mc ON p.movieid = mc.movieid
        JOIN imdb_moviegenres mg ON p.movieid = mg.movieid
        LEFT JOIN imdb_directormovies dm ON p.movieid = dm.movieid  -- Conexión con la tabla de directores
        LEFT JOIN imdb_directors d ON dm.directorid = d.directorid  -- Conexión con los directores
        LEFT JOIN imdb_actormovies am ON p.movieid = am.movieid     -- Conexión con la tabla intermedia de actores
        LEFT JOIN imdb_actors a ON am.actorid = a.actorid           -- Conexión con los actores
        WHERE mc.country = 'France';
    """)

    # Extrae y transforma los datos
    with engine.connect() as conn:
        result = conn.execute(query)  # Ejecuta la consulta
        movies = {}  # Diccionario para almacenar datos transformados

        # Itera sobre los resultados asegurándote de que sean accesibles como diccionarios
        for row in result.mappings():
            movie_id = row["movieid"]
            if movie_id not in movies:
                
                # El título está en el formato "Nombre de la película (YYYY)"
                title_with_date = row["movietitle"]
                
                # Separar por '(' para aislar la fecha
                parts = title_with_date.split('(')
                
                # El título limpio es la primera parte antes de '('
                clean_title = parts[0].strip()
                
                # Convertimos el año a un número entero
                try:
                    movie_year = int(row["year"])  # Convierte a entero
                except ValueError:
                    print(f"Error: año faltante o no válido: {row}")
                    continue  # Si no se puede convertir, salta este registro

                # Nos aseguramos de que el año sea válido
                if movie_year <= 0:
                    print(f"Error: año faltante o no válido: {row}")
                    continue  # Si el año es inválido, salta este registro

                
                movies[movie_id] = {
                    "title": clean_title,
                    "year": movie_year,
                    "genres": set(),
                    "directors": set(),
                    "actors": set(),
                    "most_related_movies": [],
                    "related_movies": []
                }       
            movies[movie_id]["genres"].add(row["genre"] or "Unknown Genre")
            if row["director"]:
                movies[movie_id]["directors"].add(row["director"])
            if row["actor"]:
                movies[movie_id]["actors"].add(row["actor"])

        # Inserta películas
        for movie in movies.values():
            movie["genres"] = list(movie["genres"])
            movie["directors"] = list(movie["directors"])
            movie["actors"] = list(movie["actors"])

            try:
                collection.insert_one(movie)
            except pymongo.errors.WriteError as e:
                print(f"Error al insertar documento: {movie}")
                print(f"Detalle del error: {e}")




    print("Películas cargadas en MongoDB.")
    
    
    # Parte 3: Detección de películas relacionadas
def calculate_related_movies():
    # Conexión a MongoDB
    mongo_client = pymongo.MongoClient(MONGO_URL)
    mongo_db = mongo_client[DB_NAME]
    collection = mongo_db[COLLECTION_NAME]

    # Obtenemos todas las películas
    all_movies = list(collection.find())

    # Procesamos cada película
    for movie in all_movies:
        title = movie["title"]
        genres_set = set(movie["genres"])
        most_related = []
        related = []

        # Compara con todas las demás películas
        for other_movie in all_movies:
            if movie["_id"] == other_movie["_id"]:  # No comparar consigo misma
                continue

            #Extraemos los géneros de la película que vamos a comparar con la actual
            other_genres_set = set(other_movie["genres"])
            
            # Calculamos la compatibilidad de géneros
            genre_overlap = len(genres_set & other_genres_set) / len(genres_set)

            if genre_overlap == 1.0:  # 100% coincidencia
                most_related.append({"title": other_movie["title"], "year": other_movie["year"]})
            elif genre_overlap >= 0.5:  # 50% o más coincidencia
                related.append({"title": other_movie["title"], "year": other_movie["year"]})

        # Actualizamos las películas relacionadas en la base de datos
        collection.update_one(
            {"_id": movie["_id"]},
            {"$set": {
                "most_related_movies": most_related[:10],  # Máximo 10 películas más relacionadas
                "related_movies": related[:10]  # Máximo 10 películas relacionadas
            }}
        )
        print(f"Películas relacionadas calculadas para '{title}'.")


# Ejecución principal
if __name__ == "__main__":
    create_mongo()
    load_mongo()
    calculate_related_movies()