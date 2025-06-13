from db_utility import get_db_connection
from flask import Flask
app=Flask(__name__)

@app.route('/get_patient_details',methods=['GET'])
def get_patient_details():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM patient_medication_details")
    
    # Retrieve column names and all rows
    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    
    cursor.close()
    conn.close()

    if not rows:
        return jsonify({"error": "No patient details found"}), 404

    # Build a list of dicts, e.g. [{col1: val1, col2: val2}, ...]
    data = [dict(zip(columns, row)) for row in rows]
    return jsonify({"patient_details": data}), 200    
if __name__ == '__main__':
    app.run(debug=True)
