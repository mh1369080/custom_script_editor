from flask import Flask, send_file, jsonify, request
import os

app = Flask(__name__)

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

if __name__ == '__main__':
    app.run(debug=True)
