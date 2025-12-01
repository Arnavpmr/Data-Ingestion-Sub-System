import os
import psycopg
from psycopg import OperationalError
from dotenv import load_dotenv
import pandas as pd

# Load environment variables from .env file
load_dotenv()

def test_postgresql_connection():
    try:
        # Use environment variables for database configuration
        with psycopg.connect(
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT")),
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        ) as conn:
            with conn.cursor() as cur:
                # do db stuff in here
                pass
        return True

    except OperationalError as e:
        print(f"Error connecting to PostgreSQL: {e}")
        return False

if __name__ == "__main__":
    test_postgresql_connection()