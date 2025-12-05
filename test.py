import psycopg2

conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="genai_db",
    user="postgres",
    password="krushna123"
)

print("Connected successfully!")
