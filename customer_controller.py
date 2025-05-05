import csv
import os
import shutil
import logging
from flask import Flask, jsonify
from db_utility import get_connection

shutil.rmtree("__pycache__", ignore_errors=True)

# -------------------- Logging Configuration --------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# -------------------- Flask App Initialization --------------------
app = Flask(__name__)


# -------------------- GET Endpoint: Get Customer Details --------------------
@app.route('/get_customer_details', methods=['GET'])
def get_customer_details():
    """
    GET /get_customer_details
    Fetches all customer records from the database and returns as JSON.
    """
    customers = []
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT name, email_id, phone_no FROM customer")
        rows = cur.fetchall()

        for name, email, phone in rows:
            customers.append({
                "name": name,
                "email_id": email,
                "phone_no": phone
            })

        logging.info("Fetched customer data successfully.")

    except Exception as e:
        logging.error(f"Error retrieving customer data: {e}")
    finally:
        if 'cur' in locals(): cur.close()
        if 'conn' in locals(): conn.close()
        logging.info("Database connection closed after retrieval.")

    return jsonify(customers)


# -------------------- POST Endpoint: Insert Customer Data from CSV --------------------
@app.route('/insert_customer_data', methods=['POST'])
def insert_customer_data():
    """
    POST /insert_customer_data
    Inserts customer data from a predefined CSV file into the database.
    """
    csv_path = 'C:/Users/Pavan/Desktop/Projects/Documents/First_Flask_poc/Unprocessed/test.csv'
    try:
        conn = get_connection()
        cur = conn.cursor()
        logging.info(f"Inserting customer data from: {csv_path}")

        with open(csv_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                cur.execute(
                    "INSERT INTO customer (name, email_id, phone_no) VALUES (%s, %s, %s)",
                    (row['Name'], row['Email_Id'], row['Phone_No'])
                )

        conn.commit()
        logging.info("Customer data inserted successfully.")

    except FileNotFoundError:
        logging.error(f"CSV file not found: {csv_path}")
    except KeyError as e:
        logging.error(f"Missing column in CSV: {e}")
    except Exception as e:
        logging.error(f"Database error: {e}")
    finally:
        if 'cur' in locals(): cur.close()
        if 'conn' in locals(): conn.close()
        logging.info("Database connection closed after insertion.")

    return jsonify({"message": "Customer data inserted from CSV."})





# -------------------- App Runner --------------------
if __name__ == '__main__':
    app.run(debug=True)  