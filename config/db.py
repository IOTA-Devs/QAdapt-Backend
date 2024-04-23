from psycopg2 import pool

pool = pool.SimpleConnectionPool(1, 20, database="qadaptdb", host="localhost", user="postgres", password="1234", port="5432")

def get_conn():
    return pool.getconn()

def release_conn(conn):
    pool.putconn(conn)