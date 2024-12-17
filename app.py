from flask import Flask, jsonify, request
from openai import OpenAI
import config, helpers

app = Flask(__name__)
client = OpenAI(api_key=config.OPENAI_API_KEY)

@app.route('/custom_question', methods=['POST'])
def ask_openai():
    try:
        invoices = helpers.load_invoice_data()
        if not invoices:
            return generate_response(500, "No invoice data found")

        user_query = request.json.get("query", "")
        if not user_query:
            return generate_response({400, "Query cannot be empty"})

        invoice_summary = "\n\n".join([
            f"Invoice ID: {inv.get('id', 'N/A')}\n"
            f"Vendor: {inv.get('vendor_name', 'Unknown')}\n"
            f"**Total Claimed Amount:** ${inv.get('total_claimed_amount', 0):,.2f}\n"
            f"Invoice Number: {inv.get('invoice_number', 'N/A')}"
            f"status: {inv.get('status','N/A')}\n"
            f"Payment Status: {inv.get('payment_date','N/A')}\n"
            f"**Balance to Finish (Including Retainage):** ${inv.get('summary', {}).get('balance_to_finish_including_retainage', 0):,.2f}\n"
            f"**Current Payment Due:** ${inv.get('summary', {}).get('current_payment_due', 0):,.2f}\n"
            f"Payment Date: {inv.get('payment_date', 'N/A')}"
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
            return generate_response(200, response)

        openai_answer = response
        return generate_response(200, openai_answer)

    except Exception as e:
        print("Error:", e)
        return jsonify({"status": 500, "error": "Something went wrong", "details": str(e)})

@app.route('/invoices', methods=['GET'])
def example():
    data = helpers.load_invoice_data()
    return jsonify(data)

@app.route('/top_invoices', methods=['GET'])
def top_invoices():
    conn = helpers.get_db_connection()
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
    conn = helpers.get_db_connection()
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
            "status": 200,
            "Invoice ID": invoice[0],
            "Vendor Name": invoice[1],
            "Balance Pending": f"${invoice[2]:,.2f}"
        }
    else:
        return generate_response(200,"no invoice found")

    return jsonify(response)

@app.route('/')  # Define a route for the home page
def home():
    return "Hello, World!"

def generate_response(status_code, message, data=None):
    response = {
        "status": status_code,
        "message": message
    }

    return jsonify(response), status_code

if __name__ == '__main__':
    app.run(debug=True)
