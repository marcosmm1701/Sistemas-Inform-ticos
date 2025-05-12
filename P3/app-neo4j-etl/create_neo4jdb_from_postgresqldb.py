
"""Module to transform the movie database from relational to a graph database"""
import time

from neo4j import GraphDatabase
from consultas import SQL

class EtlFromPostgresToNeo4j:
    """Class to Transform Movie relational data to graph database"""

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.delete_all_nodes()
        self.create_all_constraints()
        self.sql = SQL()

    def transform_postgres_to_neo4j(self):
        """
        Transform Movie Relational database to Graph database
        """
        # Get all the data from PostgreSQL
        # get the 20 most selling movies from USA
        db_result = self.best_selling_movies_usa()
        print("Processing DB rows ...")
        start_time = time.time()
        
        for row_movie in db_result:
            dict_movie = row_movie
            node_movie = self.create_and_return_movie(dict_movie)
            if not node_movie:
                print(f"[ERROR] No se pudo crear el nodo para la película: {dict_movie}")
                continue

            self.insert_all_actors(dict_movie, node_movie)
            self.insert_all_directors(dict_movie, node_movie)
    
        print("End ETL process...")
        f_string_order = f"Process finished --- {time.time() - start_time} seconds ---"
        print(f_string_order)
    
    def insert_all_actors(self, dict_movie, node_movie):
        """Inserta todos los actores que participaron en la película"""
        # TO-DO SQL
        db_actors = []
        query = """
            SELECT a.actorid, a.actorname
            FROM imdb_actors a
            JOIN imdb_actormovies am ON a.actorid = am.actorid
            WHERE am.movieid = :movieid
        """
        db_actors = self.sql.execute_query(query, {"movieid": dict_movie["movieid"]})

        # Insert all actors
        for row_actor in db_actors:
            dict_actor = row_actor
            self.create_and_return_actor(dict_actor, node_movie)

    def insert_all_directors(self, dict_movie, node_movie):
        """Insert the directors that directed the movie"""
        # TO-DO SQL
        db_directors = []
        query = """
            SELECT d.directorid, d.directorname
            FROM imdb_directors d
            JOIN imdb_directormovies dm ON d.directorid = dm.directorid
            WHERE dm.movieid = :movieid
        """
        db_directors = self.sql.execute_query(query, {"movieid": dict_movie["movieid"]})

        # Insert all directors
        for row_director in db_directors:
            dict_director = row_director
            self.create_and_return_director(dict_director, node_movie)

    def create_and_return_director(self, dict_director, node_movie):
        """ Create Node Person Director"""
        with self.driver.session() as session:
            # Creamos nodo Person
            person_node = session.execute_write(self._create_and_return_person, dict_director["directorid"], dict_director["directorname"])
            if not person_node:
                print("[ERROR] No se pudo crear el nodo Person.")
                return None
            
            # Creamos nodo Director
            node_director = session.execute_write(self._create_and_return_director, dict_director)
            if not node_director:
                print("[ERROR] No se pudo crear el nodo Director.")
                return None
            
            # Relacionamos Person con Movie
            if person_node and node_director:
                session.execute_write(self._create_person_director_relationship, node_movie, node_director)
    
            #Create Relationship DIRECTED
                session.execute_write(self._create_and_return_directed, node_movie, node_director)
                
                
            return node_director

    def create_and_return_actor(self, dict_actor, node_movie):
        with self.driver.session() as session:
            # Creamos nodo Person
            person_node = session.execute_write(self._create_and_return_person, dict_actor["actorid"], dict_actor["actorname"])
            if not person_node:
                print("[ERROR] No se pudo crear el nodo Person.")
                return None
        
            # Creamos nodo Actor
            node_actor = session.execute_write(self._create_and_return_actor, dict_actor)

            if not node_actor:
                print("[ERROR] No se pudo crear el nodo Actor.")
                return None
            
            # Relacionar Person con Actor
            if person_node and node_actor:
                session.execute_write(self._create_person_actor_relationship, node_movie, node_actor)


            # Creamos relación ACTED_IN solo si el nodo_movie es válido
            if node_movie:
                session.execute_write(self._create_and_return_acted_in, node_movie, node_actor)
            return node_actor

    
    def create_and_return_movie(self, dict_movie: dict):
        """ Create Node Movie """
        with self.driver.session() as session:
            movie = session.execute_write(self._create_and_return_movie, dict_movie)
            return movie

    def delete_all_nodes(self):
        """Delete all nodes from database"""
        with self.driver.session() as session:
            session.execute_write(self._delete_all_nodes)

    def create_all_constraints(self):
        """ Create Genre Node """
        with self.driver.session() as session:
            # Creación de constraints UNIQUE
            session.run(
                "CREATE CONSTRAINT actor_id_unique IF NOT EXISTS FOR (a:Actor) REQUIRE a.actorid IS UNIQUE"
            )
            session.run(
                "CREATE CONSTRAINT director_id_unique IF NOT EXISTS FOR (d:Director) REQUIRE d.directorid IS UNIQUE"
            )
            session.run(
                "CREATE CONSTRAINT movie_id_unique IF NOT EXISTS FOR (m:Movie) REQUIRE m.movieid IS UNIQUE"
            )
        
            # Creación de índices
            session.run(
                "CREATE INDEX actor_id IF NOT EXISTS FOR (a:Actor) ON (a.actorid)"
            )
            session.run(
                "CREATE INDEX director_id IF NOT EXISTS FOR (d:Director) ON (d.directorid)"
            )
            session.run(
                "CREATE INDEX movie_id IF NOT EXISTS FOR (m:Movie) ON (m.movieid)"
            )
          
    @staticmethod
    def _create_and_return_directed(tx, node_movie, node_director):
        if not node_movie or not node_director:
            print("[ERROR] node_movie o node_director es None.")
            return None

        # Accedemos directamente a las propiedades del nodo
        movieid = node_movie["movieid"]
        directorid = node_director["directorid"]

        if not movieid or not directorid:
            print(f"[ERROR] Faltan datos en node_movie o node_director: movieid={movieid}, directorid={directorid}")
            return None

        query = """
            MATCH (d:Director {directorid: $directorid}), (m:Movie {movieid: $movieid})
            MERGE (d)-[:DIRECTED]->(m)
            RETURN d, m
        """
        result = tx.run(query, directorid=directorid, movieid=movieid)
        return result.single()

   
    @staticmethod
    def _create_and_return_acted_in(tx, node_movie, node_actor):
        if not node_movie or not node_actor:
            print("[ERROR] node_movie o node_actor es None.")
            return None

        # Accede directamente a las propiedades del nodo
        movieid = node_movie.get("movieid")
        actorid = node_actor.get("actorid")

        if not movieid or not actorid:
            print(f"[ERROR] Faltan datos en node_movie o node_actor: movieid={movieid}, actorid={actorid}")
            return None

        query = """
            MATCH (a:Actor {actorid: $actorid}), (m:Movie {movieid: $movieid})
            MERGE (a)-[:ACTED_IN]->(m)
            RETURN a, m
        """
        result = tx.run(query, actorid=actorid, movieid=movieid)
        return result.single()


    @staticmethod
    def _create_person_actor_relationship(tx, node_movie, node_actor):
        """Create ACTED_IN relationship between Person and Movie"""
        if not node_movie or not node_actor:
            print("[ERROR] node_movie o node_actor es None.")
            return None
        
        # Accede directamente a las propiedades del nodo
        movieid = node_movie["movieid"]
        person_id = node_actor["actorid"]
        
        if not movieid or not person_id:
            print(f"[ERROR] Faltan datos en node_movie o person_id: movieid={movieid}, directorid={person_id}")
            return None
        
        query = """
            MATCH (p:Person {personid: $personid}), (m:Movie {movieid: $movieid})
            MERGE (p)-[:ACTED_IN]->(m)
        """
        result = tx.run(query, personid=person_id, movieid=movieid)
        return result.single()

        
        
        
    @staticmethod
    def _create_person_director_relationship(tx, node_movie, node_director):
        """Create DIRECTED relationship between Person and Movie"""
        if not node_movie or not node_director:
            print("[ERROR] node_movie o node_director es None.")
            return None
        
        # Accede directamente a las propiedades del nodo
        movieid = node_movie["movieid"]
        person_id = node_director["directorid"]
        
        if not movieid or not person_id:
            print(f"[ERROR] Faltan datos en node_movie o person_id: movieid={movieid}, directorid={person_id}")
            return None
        
        query = """
            MATCH (p:Person {personid: $personid}), (m:Movie {movieid: $movieid})
            MERGE (p)-[:DIRECTED]->(m)
        """
        result = tx.run(query, personid=person_id, movieid=movieid)
        return result.single()




    @staticmethod
    def _create_and_return_actor(tx, dict_actor):
        query = """
            MERGE (a:Actor {actorid: $actorid})
            SET a.name = $name
            RETURN a
        """
        result = tx.run(query, actorid=dict_actor["actorid"], name=dict_actor["actorname"])
        
        # Obtener el primer resultado (registro)
        record = result.single()  # Devuelve un solo registro si existe
        if record:
            return record["a"]  # Devuelve el nodo
        else:
            print(f"[ERROR] No se pudo crear o encontrar el nodo Actor para {dict_actor}")
            return None

    

    @staticmethod
    def _create_and_return_director(tx, dict_director):
        
        # Verificar que las claves existen
        if "directorid" not in dict_director or "directorname" not in dict_director:
            raise KeyError("Faltan claves necesarias en dict_director: 'directorid' o 'directorname'")

        # Extraemos los valores
        directorid = dict_director["directorid"]
        name = dict_director["directorname"]

        # Consulta Cypher para crear o encontrar al director
        query = """
            MERGE (d:Director {directorid: $directorid})
            SET d.name = $name
            RETURN d
        """
    
        # Ejecutar la consulta
        result = tx.run(query, directorid=directorid, name=name)
        # Devuelve directamente el nodo en lugar del Record
        record = result.single()
        if record:
            return record["d"]  # 'd' es el alias del nodo en la consulta
        else:
            print(f"[ERROR] No se pudo crear o encontrar el nodo Actor para {dict_director}")
            return None


    @staticmethod
    def _create_and_return_movie(tx, dict_movie):
        """Crea un nodo Movie"""
        # Consulta para crear o encontrar una película
        query = """
            MERGE (m:Movie {movieid: $movieid})
            SET m.title = $title, m.year = $year, m.genre = $genre
            RETURN m
        """

        result = tx.run(query, 
                        movieid=dict_movie["movieid"], 
                        title=dict_movie["movietitle"], 
                        year=dict_movie["year"], 
                        genre=dict_movie.get("genre"))
        
        
        # Obtener el primer resultado (registro)
        record = result.single()  # Devuelve un solo registro si existe
        if record:
            return record["m"]  # Devuelve el nodo
        else:
            print(f"[ERROR] No se pudo crear o encontrar el nodo Movie para {dict_movie}")
            return None


    @staticmethod
    def _create_and_return_person(tx, person_id, name):
        """Create or return a Person node"""
        query = """
            MERGE (p:Person {personid: $personid})
            SET p.name = $name
            RETURN p
        """
        result = tx.run(query, personid=person_id, name=name)
        record = result.single()
        if record:
            return record["p"]
        else:
            print(f"[ERROR] No se pudo crear o encontrar el nodo Person para {person_id}")
            return None


    @staticmethod
    def _delete_all_nodes(tx):
        tx.run("MATCH (n) DETACH DELETE n")

    def best_selling_movies_usa(self):
        """Method that execute the query on the database to get 20 most selling USA movies"""
        # TO-DO SQL 
        query = """
            SELECT DISTINCT 
                m.movieid, 
                m.movietitle, 
                m.year, 
                c.country,
                SUM(i.sales) AS total_sales
            FROM imdb_movies m
            JOIN imdb_moviecountries c ON m.movieid = c.movieid
            JOIN products p ON m.movieid = p.movieid
            JOIN inventory i ON p.prod_id = i.prod_id
            WHERE c.country = 'USA'  -- Filtrar películas de USA
            GROUP BY m.movieid, m.movietitle, m.year, c.country
            ORDER BY total_sales DESC -- Ordenar por ventas totales
            LIMIT 20; -- Seleccionar las 20 películas más vendidas


        """
        result = self.sql.execute_query(query)
        return result


    def close(self):
        """
        Close driver connection
        """
        self.driver.close()


if __name__ == "__main__":
    # Neoj Configuration
    URI = "bolt://127.0.0.1:7687"
    USER = "neo4j"
    PASSWORD = "si1-password"
    convert = EtlFromPostgresToNeo4j(URI, USER, PASSWORD)
    try:
        convert.transform_postgres_to_neo4j()
    finally:
        convert.close()