import csv
import os
import shutil
import logging
from flask import Flask, jsonify, request
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
    csv_path = 'C:\\Users\\Pavan\\Desktop\\Projects\\Documents\\First_Flask_poc\\Unprocessed\\test.csv'

    try:
        conn = get_connection()
        cur = conn.cursor()
        logging.info(f"Inserting customer data from: {csv_path}")

        with open(csv_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Make sure the CSV headers and database column names match
                cur.execute(
                    "INSERT INTO customer (name, email_id, phone_no) VALUES (%s, %s, %s)",
                    (row['name'], row['email_id'], row['phone_no'])  
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


# -------------------- PUT Endpoint: Update Customer Name --------------------
@app.route('/update_customer_name', methods=['PUT'])
def update_customer_name():
    """
    PUT //update_customer_name
    Updates a customer's name based on their email or phone number.
    Expects JSON payload with 'new_name' and either 'email_id' or 'phone_no'.
    Returns updated customer data.
    """
    data = request.get_json()
    new_name = data.get('new_name')
    email_id = data.get('email_id')
    phone_no = data.get('phone_no')

    if not new_name or (not email_id and not phone_no):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        conn = get_connection()
        cur = conn.cursor()

        # Build WHERE condition dynamically
        if email_id:
            cur.execute("UPDATE customer SET name = %s WHERE email_id = %s RETURNING name, email_id, phone_no",
                        (new_name, email_id))
        else:
            cur.execute("UPDATE customer SET name = %s WHERE phone_no = %s RETURNING name, email_id, phone_no",
                        (new_name, phone_no))

        updated_row = cur.fetchone()
        conn.commit()

        if updated_row:
            result = {
                "name": updated_row[0],
                "email_id": updated_row[1],
                "phone_no": updated_row[2]
            }
            logging.info("Customer name updated successfully.")
            return jsonify(result)
        else:
            logging.warning("No customer found with provided identifier.")
            return jsonify({"message": "Customer not found"}), 404

    except Exception as e:
        logging.error(f"Error updating customer name: {e}")
        return jsonify({"error": "Internal server error"}), 500
    finally:
        if 'cur' in locals(): cur.close()
        if 'conn' in locals(): conn.close()
        logging.info("Database connection closed after update.")


# -------------------- App Runner --------------------
if __name__ == '__main__':
    app.run(debug=True)  