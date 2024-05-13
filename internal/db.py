import os
from psycopg2 import pool

pool = pool.SimpleConnectionPool(1, 20, database="qadapt", host="localhost", user="postgres", password=os.getenv("DB_PASSWORD"), port=5432)
def get_conn():
    return pool.getconn()

def release_conn(conn):
    pool.putconn(conn)