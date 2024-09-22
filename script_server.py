from flask import Flask, send_file, jsonify, request
import os
import sqlite3
import pandas as pd
app = Flask(__name__)
# Path to your SQLite database
DB_PATH = 'accountingdb.db'

# Path where script files are stored
SCRIPT_DIR = os.path.join(os.path.dirname(__file__), 'scripts')

# Ensure the scripts directory exists
if not os.path.exists(SCRIPT_DIR):
    os.makedirs(SCRIPT_DIR)

@app.route('/get-script/<script_name>', methods=['GET'])
def get_script(script_name):
    try:
        # Build the full path of the script file
        script_path = os.path.join(SCRIPT_DIR, script_name)

        # Return the file content as a downloadable file
        return send_file(script_path, as_attachment=True)
    
    except Exception as e:
        # If the file does not exist or another error occurs
        return jsonify({"error": str(e)}), 404

# Save script endpoint (NEW)
@app.route('/save-script/<script_name>', methods=['POST'])
def save_script(script_name):
    data = request.get_json()

    # Extract the script content
    script_content = data.get("script", "")

    # Save the script content to a file
    try:
        script_path = os.path.join(SCRIPT_DIR, script_name)  # Use full path
        with open(script_path, "w") as script_file:
            script_file.write(script_content)
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/get-table-data/<table_name>', methods=['GET'])
def get_table_data(table_name):
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect('accountingdb.db')
        cursor = conn.execute(f"SELECT * FROM {table_name}")
        records = cursor.fetchall()

        # Get the column names from the cursor description
        columns = [description[0] for description in cursor.description]

        # Return the data and columns as JSON
        return jsonify({"columns": columns, "data": records}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/get-table-structure/<table_name>', methods=['GET'])
def get_table_structure(table_name):
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect('accountingdb.db')
        cursor = conn.cursor()

        # PRAGMA query to get the table structure
        query = f"PRAGMA table_info({table_name})"
        cursor.execute(query)
        structure_info = cursor.fetchall()

        # Extracting relevant details: cid, name, type, notnull, dflt_value, pk
        columns = ['cid', 'name', 'type', 'notnull', 'dflt_value', 'pk']
        structure = [
            {columns[i]: col[i] for i in range(len(columns))}
            for col in structure_info
        ]

        # Close the cursor and connection
        cursor.close()
        conn.close()

        # Return the structure as JSON
        return jsonify({"columns": columns, "structure": structure}), 200
    except sqlite3.OperationalError as oe:
        # This often happens when the table doesn't exist
        return jsonify({"error": f"Table '{table_name}' does not exist. Error: {str(oe)}"}), 404
    except Exception as e:
        # General exception handling for other errors
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

# API endpoint to fetch the list of companies
@app.route('/get-companies', methods=['GET'])
def get_companies():
    try:
        # Connect to your SQLite database
        conn = sqlite3.connect('accountingdb.db')
        cursor = conn.execute("SELECT * from companies")
        records = cursor.fetchall()
        
        # Convert the records to a list of dictionaries
        companies_list = [{"company_code": r[0], "company_name": r[1]} for r in records]
        
        # Return the list as JSON response
        return jsonify(companies_list), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500    
if __name__ == '__main__':
    app.run(debug=True)
