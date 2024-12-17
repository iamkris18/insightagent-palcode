import json
import psycopg2

if __name__ == '__main__':
    conn = psycopg2.connect(
        host="localhost",  
        database="palcode_db",
        user="postgres", 
        password="password"
    )
    cursor = conn.cursor()

    create_table_query = '''
        CREATE TABLE IF NOT EXISTS invoices (
            id SERIAL PRIMARY KEY,
            project_id INTEGER NOT NULL,
            billing_date DATE NOT NULL,
            vendor_name VARCHAR(255) NOT NULL,
            invoice_number INTEGER NOT NULL,
            total_claimed_amount NUMERIC(10, 2) NOT NULL,
            payment_date DATE,
            status VARCHAR(50),
            balance_to_finish_including_retainage NUMERIC(10, 2),
            completed_work_retainage_amount NUMERIC(10, 2),
            contract_sum_to_date NUMERIC(10, 2),
            current_payment_due NUMERIC(10, 2),
            created_by_id INTEGER,
            created_by_name VARCHAR(255),
            created_by_login VARCHAR(255),
            created_by_company_name VARCHAR(255)
        );
    '''

    cursor.execute(create_table_query)
    conn.commit()

    with open('data.json', 'r') as file:
        invoices = json.load(file)

    insert_query = '''
        INSERT INTO invoices (
            id, project_id, billing_date, vendor_name, invoice_number, 
            total_claimed_amount, payment_date, status, balance_to_finish_including_retainage, 
            completed_work_retainage_amount, contract_sum_to_date, current_payment_due,
            created_by_id, created_by_name, created_by_login, created_by_company_name
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    '''

    for i in invoices:
        cursor.execute(insert_query, (
            i['id'], i['project_id'], i['billing_date'], i['vendor_name'], i['invoice_number'],
            i['total_claimed_amount'], i['payment_date'], i['status'], 
            i['summary']['balance_to_finish_including_retainage'], 
            i['summary']['completed_work_retainage_amount'], 
            i['summary']['contract_sum_to_date'], 
            i['summary']['current_payment_due'],
            i['created_by']['id'], i['created_by']['name'], i['created_by']['login'], i['created_by']['company_name']
        ))

    conn.commit()
    conn.close()

    print("Data inserted successfully!")
