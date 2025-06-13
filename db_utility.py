#importing necessary packages 
import psycopg2
def get_db_connection():
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="first_db",
            user="postgres",
            password="Pavankandi7680$", 
            port=5432
        )
        return conn
    except:
        print("Error connecting to the database")
        return None
