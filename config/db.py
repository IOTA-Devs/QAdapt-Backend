import psycopg2

conn = psycopg2.connect(
    database="qadaptdb",
    host="localhost",
    user="postgres",
    password="1234",
    port="5432"
)