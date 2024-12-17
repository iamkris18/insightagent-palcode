import json
import psycopg2

# Connect to PostgreSQL database
conn = psycopg2.connect(
    host="localhost",  # e.g., "localhost" or an IP address
    database="palcode_db",  # the database you want to connect to
    user="postgres",  # your PostgreSQL username
    password="password"  # your PostgreSQL password
)
cursor = conn.cursor()

# Load data from the simplified JSON
with open('data.json', 'r') as file:
    invoices = json.load(file)

# Insert data into the PostgreSQL database
for invoice in invoices:
    cursor.execute('''
    INSERT INTO invoices (id, project_id, billing_date, vendor_name, invoice_number,
                          total_claimed_amount, payment_date, status, balance_to_finish_including_retainage,
                          completed_work_retainage_amount, contract_sum_to_date, current_payment_due)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ''', (
        invoice['id'], invoice['project_id'], invoice['billing_date'], invoice['vendor_name'], invoice['invoice_number'],
        invoice['total_claimed_amount'], invoice['payment_date'], invoice['status'], 
        invoice['summary']['balance_to_finish_including_retainage'], 
        invoice['summary']['completed_work_retainage_amount'],
        invoice['summary']['contract_sum_to_date'], invoice['summary']['current_payment_due']
    ))

# Commit changes and close the connection
conn.commit()
conn.close()
