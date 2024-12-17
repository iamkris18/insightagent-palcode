from flask import Flask, jsonify, request
import psycopg2

app = Flask(__name__)

# Connect to the PostgreSQL database
def get_db_connection():
    conn = psycopg2.connect(
        host="localhost",  # e.g., "localhost" or an IP address
        database="palcode_db",  # the database you want to connect to
        user="postgres",  # your PostgreSQL username
        password="password"  # your PostgreSQL password
    )
    return conn

@app.route('/top_invoices', methods=['GET'])
def top_invoices():
    # Fetch top 5 invoices based on the current_payment_due
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, vendor_name, current_payment_due
        FROM invoices
        ORDER BY current_payment_due DESC
        LIMIT 5;
    ''')
    invoices = cursor.fetchall()
    conn.close()

    # Format the response
    response = []
    for invoice in invoices:
        response.append({
            "Invoice ID": invoice[0],
            "Vendor Name": invoice[1],
            "Invoice Amount": invoice[2]
        })

    return jsonify(response)

@app.route('/invoice_summary', methods=['GET'])
def invoice_summary():
    # Fetch the invoice with the highest balance
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, vendor_name, balance_to_finish_including_retainage
        FROM invoices
        ORDER BY balance_to_finish_including_retainage DESC
        LIMIT 1;
    ''')
    invoice = cursor.fetchone()
    conn.close()

    # Format the response
    if invoice:
        response = {
            "Invoice ID": invoice[0],
            "Vendor Name": invoice[1],
            "Balance Pending": f"${invoice[2]:,.2f}"
        }
    else:
        response = {"message": "No invoice found"}

    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
