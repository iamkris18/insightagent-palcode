from flask import Flask, jsonify, request, json
import psycopg2
from openai import OpenAI

app = Flask(__name__)
client = OpenAI(api_key="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")

@app.route('/ask_openai', methods=['POST'])
def ask_openai():
    try:
        invoices = load_invoice_data()
        if not invoices:
            return jsonify({"error": "No invoice data found"}), 500

        user_query = request.json.get("query", "")
        if not user_query:
            return jsonify({"error": "Query cannot be empty"}), 400

        invoice_summary = "\n\n".join([
            f"Invoice ID: {inv.get('id', 'N/A')}\n"
            f"Vendor: {inv.get('vendor_name', 'Unknown')}\n"
            f"**Total Claimed Amount:** ${inv.get('total_claimed_amount', 0):,.2f}\n"
            f"**Balance to Finish (Including Retainage):** ${inv.get('summary', {}).get('balance_to_finish_including_retainage', 0):,.2f}\n"
            f"**Current Payment Due:** ${inv.get('summary', {}).get('current_payment_due', 0):,.2f}\n"
            for inv in invoices
        ])


        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant analyzing invoice data."},
                {"role": "system", "content": f"The following is the invoice data:{invoice_summary}"},
                {"role": "user", "content": user_query}
            ],
        )
        openai_answer = response.choices[0].message.content.strip()

        if "highest balance" in user_query.lower():
            highest_balance_invoice = max(invoices, key=lambda x: x.get('summary', {}).get('balance_to_finish_including_retainage', 0))
            invoice_id = highest_balance_invoice.get('id')
            balance = highest_balance_invoice.get('summary', {}).get('balance_to_finish_including_retainage', 0)

            response = f"Here you go, The invoice with Id {invoice_id} has the highest balance amount pending with an amount ${balance:,.2f}."
        else:
            response = openai_answer

        if "current score" in user_query.lower() or "score of the match" in user_query.lower():
            response = "I am currently unable to provide live match scores. Please check a sports application for real-time updates."
            return jsonify({"response": response})

        openai_answer = response
        return jsonify({"response": openai_answer})

    except Exception as e:
        print("Error:", e)
        return jsonify({"error": "Something went wrong", "details": str(e)}), 500


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

@app.route('/invoices', methods=['GET'])
def example():
    data = load_invoice_data()
    return data

@app.route('/top_invoices', methods=['GET'])
def top_invoices():
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
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, vendor_name, balance_to_finish_including_retainage
        FROM invoices
        ORDER BY balance_to_finish_including_retainage DESC
        LIMIT 3;
    ''')
    invoice = cursor.fetchone()
    conn.close()

    if invoice:
        response = {
            "Invoice ID": invoice[0],
            "Vendor Name": invoice[1],
            "Balance Pending": f"${invoice[2]:,.2f}"
        }
    else:
        response = {"message": "No invoice found"}

    return jsonify(response)

@app.route('/')  # Define a route for the home page
def home():
    return "Hello, World!"

if __name__ == '__main__':
    app.run(debug=True)
