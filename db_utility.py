import psycopg2
import logging

def get_connection():
    """
    Establishes and returns a connection to the PostgreSQL database.
    Modify the parameters below to match your database settings.
    """
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="first_db",
            user="postgres",
            password="Pavankandi7680$", 
            port=5432
        )
        logging.info("Database connection established.")
        return conn
    except Exception as e:
        logging.error(f"Error connecting to the database: {e}")
        raise
