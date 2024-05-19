from psycopg2 import pool
from os import getenv
from contextlib import contextmanager
from psycopg2.extras import RealDictCursor

db_credentials = {
    "database": getenv("DB_NAME"),
    "user": getenv("DB_USER"),
    "password": getenv("DB_PASSWORD"),
    "host": getenv("DB_HOST")
}

pool = pool.SimpleConnectionPool(
    1, 
    20, 
    database=db_credentials.get("database"), 
    host=db_credentials.get("host") or "localhost", 
    user=db_credentials.get("user"), 
    password=db_credentials.get("password"), 
    port=5432
)
def get_conn():
    return pool.getconn()

def release_conn(conn):
    pool.putconn(conn)

@contextmanager
def get_db_cursor():
    conn = None
    try:
        conn = get_conn()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        yield cur
        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()

        raise e
    finally:
        if cur:
            cur.close()
        if conn:
            release_conn(conn)