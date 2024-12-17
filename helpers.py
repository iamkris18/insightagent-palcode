import json
import psycopg2

def load_invoice_data():
    try:
        with open('data.json', 'r') as file:
            data = json.load(file)
        return data
    except Exception as e:
        print("Error loading data.json:", e)
        return []

def get_db_connection():
    conn = psycopg2.connect(
        host="localhost",
        database="palcode_db",
        user="postgres",
        password="password"
    )
    return conn