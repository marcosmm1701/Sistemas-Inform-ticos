from sqlalchemy import create_engine, text

class SQL:
    """Class to handle SQL queries with SQLAlchemy"""

    def __init__(self, db_url="postgresql://alumnodb:1234@localhost:5432/si1"):
        """Initialize the SQL class with the database URL"""
        self.engine = create_engine(db_url)

    def execute_query(self, query, params=None):
        """Execute a query and return the results"""
        with self.engine.connect() as connection:
            result = connection.execute(text(query), params or {})
            return [dict(row) for row in result.mappings()]
