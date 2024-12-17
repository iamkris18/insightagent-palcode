import json
import psycopg2

conn = psycopg2.connect(
    host="localhost",  
    database="palcode_db",
    user="postgres", 
    password="password"
)
cursor = conn.cursor()

with open('data.json', 'r') as file:
    invoices = json.load(file)

for i in invoices:
    cursor.execute('''
    INSERT INTO invoices (id, project_id, billing_date, vendor_name, invoice_number,total_claimed_amount, payment_date, status, balance_to_finish_including_retainage,completed_work_retainage_amount, contract_sum_to_date, current_payment_due)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ''', (
        i['id'], i['project_id'], i['billing_date'], i['vendor_name'], i['invoice_number'],i['total_claimed_amount'], i['payment_date'], i['status'], i['summary']['balance_to_finish_including_retainage'], i['summary']['completed_work_retainage_amount'],i['summary']['contract_sum_to_date'], i['summary']['current_payment_due']
    )
)

conn.commit()
conn.close()
