from psycopg2.extras import DictCursor
import logging
import psycopg2

def invoice_summary(invoices):
    try:
        invoice_summary =  "\n\n".join([
                "\n".join([
                    f"Invoice ID: {i.get('id', 'N/A')}",
                    f"Vendor: {i.get('vendor_name', 'Unknown')}",
                    f"**Total Claimed Amount:** ${i.get('total_claimed_amount', 0)}",
                    f"Invoice Number: {i.get('invoice_number', 'N/A')}",
                    f"Status: {i.get('status', 'N/A')}",
                    f"Payment Status: {i.get('payment_date', 'N/A')}",
                    f"**Balance to Finish (Including Retainage):** ${i.get('summary', {}).get('balance_to_finish_including_retainage', 0)}",
                    f"**Current Payment Due:** ${i.get('summary', {}).get('current_payment_due', 0):,.1f}",
                    f"Payment Date: {i.get('payment_date', 'N/A')}",
                    f"Created By ID: {i.get('created_by', {}).get('id', 'N/A')}",
                    f"Created By Name: {i.get('created_by', {}).get('name', 'N/A')}",
                    f"Created By Login: {i.get('created_by', {}).get('login', 'N/A')}",
                    f"Created By Company: {i.get('created_by', {}).get('company_name', 'N/A')}"
                ]) 
                for i in invoices
            ])
        return invoice_summary
    except Exception as e:
        return []
        

def load_invoice_data(): 
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=DictCursor)
        cursor.execute('''
            SELECT *
            FROM invoices
            ORDER BY current_payment_due DESC
        ''')
        invoices = cursor.fetchall()
        conn.close()
        return invoices
    except Exception as e:
        return []

def get_db_connection():
    try: 
        conn = psycopg2.connect(
            host="localhost",
            database="palcode_db",
            user="postgres",
            password="password"
        )
        return conn
    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")
        print("Error loading data.json:", e)
        return []
