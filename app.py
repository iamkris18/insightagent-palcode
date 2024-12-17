from flask import Flask, jsonify, request
from openai import OpenAI
import config, helpers
from psycopg2.extras import DictCursor
import logging
logging.basicConfig(level=logging.ERROR)

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


        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant analyzing invoice data."},
                {"role": "system", "content": f"The following is the invoice data:{invoice_summary}"},
                {"role": "user", "content": user_query}
            ],
        )

        if not response.choices:
            return generate_response(500, "OpenAI response error: No choices found.")
        
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
        logging.error(f"Error occurred: {str(e)}")
        print("Error:", e)
        return jsonify({"status": 500, "error": "Something went wrong", "details": str(e)})

@app.route('/invoices', methods=['GET'])
def example():
    return jsonify(helpers.load_invoice_data())

@app.route('/top_invoices', methods=['GET'])
def top_invoices():
    try:
        conn = helpers.get_db_connection()
        cursor = conn.cursor(cursor_factory=DictCursor)
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
                "Invoice ID": invoice["id"],
                "Vendor Name": invoice["vendor_name"],
                "Invoice Amount": invoice["current_payment_due"]
            })

        return jsonify(response)
    
    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")
        return generate_response(500, f"Database error: {str(e)}")

@app.route('/invoice_summary', methods=['GET'])
def invoice_summary():
    try:
        conn = helpers.get_db_connection()
        cursor = conn.cursor(cursor_factory=DictCursor)
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
                "Invoice ID": invoice["id"],
                "Vendor Name": invoice["vendor_name"],
                "Balance Pending": invoice["balance_to_finish_including_retainage"]
            }
        else:
            return generate_response(200,"no invoice found")

        return jsonify(response)
    
    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")
        return generate_response(500, f"Database error: {str(e)}")
    
@app.route('/')
def home():
    return "Hello, World!"

def generate_response(status_code, message, data=None):
    response = {
        "status": status_code,
        "message": message
    }

    return jsonify(response), status_code

def main() -> None:
    app.run(debug=True)

if __name__ == '__main__':
    main()

