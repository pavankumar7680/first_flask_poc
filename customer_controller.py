import csv
import os
import shutil
import logging
from flask import Flask, jsonify, request
from db_utility import get_connection
from email_helper import send_success_email
from email_helper import send_name_update_email
from email_helper import send_address_update_email 

shutil.rmtree("__pycache__", ignore_errors=True)

# -------------------- Logging Configuration --------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# -------------------- Flask App Initialization --------------------
app = Flask(__name__)

# --------------------  POST insert_customer_and_address_data --------------------

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
        
        #-------------- Send a success email after data insertion------------------
        send_success_email() 
        #--------------------------------------------------------------------------
        
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
    

# --------------------  GET get_customer_details --------------------

@app.route('/get_customer_details', methods=['GET'])
def get_customer_details():
    """
    GET /get_customer_details
    Retrieves customer details (name, email_id, phone_no) based on optional filters like email_id or phone_no.
    If no filters are provided, returns all customers.
    """
    email_id = request.args.get('email_id')
    phone_no = request.args.get('phone_no')

    try:
        conn = get_connection()
        cur = conn.cursor()

        # Base query
        query = "SELECT name, email_id, phone_no FROM customer"
        params = []

        # Add filter conditions
        if email_id:
            query += " WHERE email_id = %s"
            params.append(email_id)
        elif phone_no:
            query += " WHERE phone_no = %s"
            params.append(phone_no)

        cur.execute(query, params)
        rows = cur.fetchall()

        if not rows:
            return jsonify([]), 200  # Return empty list if no match

        customers = [
            {
                "name": row[0],
                "email_id": row[1],
                "phone_no": row[2]
            }
            for row in rows
        ]

        return jsonify(customers), 200

    except Exception as e:
        logging.error(f"Error fetching customer details: {e}")
        return jsonify({"error": "Internal server error"}), 500

    finally:
        if 'cur' in locals(): cur.close()
        if 'conn' in locals(): conn.close()
        logging.info("Database connection closed after fetching customer details.")
        


# -------------------- PUT Endpoint: Update Customer Name --------------------

@app.route('/update_customer_name', methods=['PUT'])
def update_customer_name():
    """
    PUT /update_customer_name
    Updates a customer's name based on email or phone number.
    Expects JSON payload with 'new_name' and either 'email_id' or 'phone_no'.
    Returns old and updated name with contact details.
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

        # Fetch old name using email or phone
        if email_id:
            cur.execute("SELECT name FROM customer WHERE email_id = %s", (email_id,))
        else:
            cur.execute("SELECT name FROM customer WHERE phone_no = %s", (phone_no,))

        old_row = cur.fetchone()

        if not old_row:
            return jsonify({"message": "Customer not found"}), 404

        old_name = old_row[0]

        # Update the name
        if email_id:
            cur.execute("UPDATE customer SET name = %s WHERE email_id = %s RETURNING name, email_id, phone_no",
                        (new_name, email_id))
        else:
            cur.execute("UPDATE customer SET name = %s WHERE phone_no = %s RETURNING name, email_id, phone_no",
                        (new_name, phone_no))

        updated_row = cur.fetchone()
        conn.commit()

        if updated_row:
            # Send email with old and new names
            send_name_update_email(old_name, updated_row[0])

            result = {
                "old_name": old_name,
                "updated_name": updated_row[0],
                "email_id": updated_row[1],
                "phone_no": updated_row[2]
            }
            logging.info("Customer name updated successfully.")
            return jsonify(result)
        else:
            return jsonify({"message": "Customer not found during update"}), 404

    except Exception as e:
        logging.error(f"Error updating customer name: {e}")
        return jsonify({"error": "Internal server error"}), 500
    finally:
        if 'cur' in locals(): cur.close()
        if 'conn' in locals(): conn.close()
        logging.info("Database connection closed after update.")



# -------------------- PUT Endpoint:update_address_details --------------------

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

        # Fetch old address using customer_id_fk or email_id
        if customer_id_fk:
            cur.execute("""
                SELECT street_1, street_2, city, state, pincode
                FROM address
                WHERE customer_id_fk = %s
            """, (customer_id_fk,))
        else:
            cur.execute("""
                SELECT street_1, street_2, city, state, pincode
                FROM address
                JOIN customer ON address.customer_id_fk = customer.customer_id
                WHERE customer.email_id = %s
            """, (email_id,))

        old_address_row = cur.fetchone()

        if not old_address_row:
            return jsonify({"message": "Address not found"}), 404

        # Update the address
        if customer_id_fk:
            cur.execute("""
                UPDATE address 
                SET street_1 = %s, street_2 = %s, city = %s, state = %s, pincode = %s
                WHERE customer_id_fk = %s
                RETURNING customer_id_fk, street_1, street_2, city, state, pincode
            """, (new_street_1, new_street_2, new_city, new_state, new_pincode, customer_id_fk))
        else:
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
            # Send email with old, new, and updated addresses
            send_address_update_email(
                old_address_row[0], old_address_row[1], old_address_row[2], old_address_row[3], old_address_row[4],  # Old address
                new_street_1, new_street_2, new_city, new_state, new_pincode,  # New address
                updated_row[1], updated_row[2], updated_row[3], updated_row[4], updated_row[5],  # Updated address
                updated_row[0]  # customer_id_fk
            )

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