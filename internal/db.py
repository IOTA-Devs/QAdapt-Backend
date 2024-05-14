from psycopg2 import pool
from os import getenv

db_credentials = {
    "database": getenv("DB_NAME"),
    "user": getenv("DB_USER"),
    "password": getenv("DB_PASSWORD"),
}

# TODO: Update to use SQLAlchemy instead of psycopg2
pool = pool.SimpleConnectionPool(
    1, 
    20, 
    database=db_credentials.get("database"), 
    host="localhost", 
    user=db_credentials.get("user"), 
    password=db_credentials.get("password"), 
    port=5432
)
def get_conn():
    return pool.getconn()

def release_conn(conn):
    pool.putconn(conn)