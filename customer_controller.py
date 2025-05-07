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

@app.route('/insert_customer_and_address_data', methods=['POST'])
def insert_customer_and_address_data():
    """
    POST /insert_customer_and_address_data
    Inserts customer and address data from a predefined CSV file into the database.
    """
    csv_path = 'C:\\Users\\Pavan\\Desktop\\Projects\\Documents\\First_Flask_poc\\Unprocessed\\test.csv'

    try:
        conn = get_connection()
        cur = conn.cursor()
        logging.info(f"Inserting customer and address data from: {csv_path}")

        with open(csv_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                # Insert customer data into the customer table
                cur.execute(
                    """
                    INSERT INTO customer (name, email_id, phone_no)
                    VALUES (%s, %s, %s) RETURNING customer_id
                    """,
                    (row['name'], row['email_id'], row['phone_no'])
                )
                customer_id = cur.fetchone()[0]  # Get the generated customer_id

                # Insert address data into the address table
                cur.execute(
                    """
                    INSERT INTO address (customer_id_fk, street_1, street_2, city, state, pincode)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (
                        customer_id,
                        row['street_1'],
                        row.get('street_2') or None,  # Treat empty street_2 as None
                        row['city'],
                        row['state'],
                        row['pincode']
                    )
                )

        conn.commit()  # Commit all inserts in one go
        logging.info("Customer and address data inserted successfully.")
        return jsonify({"message": "Customer and address data inserted from CSV."}), 201

    except FileNotFoundError:
        logging.error(f"CSV file not found: {csv_path}")
        return jsonify({"error": "CSV file not found."}), 404

    except KeyError as e:
        logging.error(f"Missing column in CSV: {e}")
        return jsonify({"error": f"Missing column in CSV: {e}"}), 400

    except Exception as e:
        logging.error(f"Database error: {e}")
        return jsonify({"error": f"Failed to insert customer and address data: {e}"}), 500

    finally:
        # Ensure the connection is closed
        if 'cur' in locals(): cur.close()
        if 'conn' in locals(): conn.close()
        logging.info("Database connection closed after insertion.")


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

@app.route('/update_address_details', methods=['PUT'])
def update_address_details():
    """
    PUT /update_address_details
    Updates all address details for a customer based on customer_id or email_id.
    Expects JSON payload with address fields and either 'customer_id_fk' or 'email_id'.
    Returns updated address data.
    """
    data = request.get_json()

    # Debugging log to see the received data
    logging.info(f"Received data: {data}")

    # Extract address details from the request
    new_street_1 = data.get('street_1')
    new_street_2 = data.get('street_2')
    new_city = data.get('city')
    new_state = data.get('state')
    new_pincode = data.get('pincode')

    # Extract customer identification details
    customer_id_fk = data.get('customer_id_fk')
    email_id = data.get('email_id')

    # Debugging log for the extracted values
    logging.info(f"Extracted fields - street_1: {new_street_1}, city: {new_city}, state: {new_state}, pincode: {new_pincode}, customer_id_fk: {customer_id_fk}, email_id: {email_id}")

    # Validate required fields
    if not (new_street_1 and new_city and new_state and new_pincode) or (not customer_id_fk and not email_id):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        conn = get_connection()
        cur = conn.cursor()

        # Build WHERE condition dynamically
        if customer_id_fk:
            # Update address based on customer_id_fk
            cur.execute("""
                UPDATE address 
                SET street_1 = %s, street_2 = %s, city = %s, state = %s, pincode = %s
                WHERE customer_id_fk = %s
                RETURNING customer_id_fk, street_1, street_2, city, state, pincode
            """, (new_street_1, new_street_2, new_city, new_state, new_pincode, customer_id_fk))
        else:
            # Update address based on email_id (join customer to get customer_id_fk)
            cur.execute("""
                UPDATE address 
                SET street_1 = %s, street_2 = %s, city = %s, state = %s, pincode = %s
                FROM customer
                WHERE customer.email_id = %s AND address.customer_id_fk = customer.customer_id
                RETURNING address.customer_id_fk, street_1, street_2, city, state, pincode
            """, (new_street_1, new_street_2, new_city, new_state, new_pincode, email_id))

        updated_row = cur.fetchone()
        conn.commit()

        if updated_row:
            result = {
                "customer_id_fk": updated_row[0],
                "street_1": updated_row[1],
                "street_2": updated_row[2],
                "city": updated_row[3],
                "state": updated_row[4],
                "pincode": updated_row[5]
            }
            logging.info("Address details updated successfully.")
            return jsonify(result)
        else:
            logging.warning("No address found with provided identifier.")
            return jsonify({"message": "Address not found"}), 404

    except Exception as e:
        logging.error(f"Error updating address details: {e}")
        return jsonify({"error": "Internal server error"}), 500
    finally:
        if 'cur' in locals(): cur.close()
        if 'conn' in locals(): conn.close()
        logging.info("Database connection closed after update.")



# -------------------- App Runner --------------------
if __name__ == '__main__':
    app.run(debug=True)  