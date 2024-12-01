from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from model import * 
import os
import time

app = Flask(__name__)
CORS(app)

# Temporary storage paths
UPLOAD_FOLDER = './uploads'
NET_FOLDER = './net_files'

# Ensure the folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(NET_FOLDER, exist_ok=True)

@app.route('/retrieve-net-file', methods=['POST'])
def retrieve_net_file():
    """
    Accepts data (e.g., form-data) via POST, processes it, 
    and serves a dynamically generated netlist file.
    """
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    # Save the uploaded file
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)
    
    # Generate a netlist file based on the input
    net_file_path = os.path.join(NET_FOLDER, f"{file.filename}.net")
    with open(net_file_path, 'w') as net_file:
        # Example netlist content
        net_file.write(f"(Netlist generated for {file.filename})\n")
        net_file.write("(This is a placeholder. Replace with actual netlist generation logic.)\n")
    
    # Return the generated netlist file
    return send_file("./threading.net", mimetype='text/plain', as_attachment=True)

@app.route('/upload', methods=['POST'])
def upload_file():
    """
    Handles file upload and saves the file in the uploads directory.
    """
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    # Ensure the file is an image
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
    if not ('.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
        return jsonify({"error": "Unsupported file type. Allowed types: png, jpg, jpeg, gif"}), 400
    
    # Save the file
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)
    
    stack = get_component_stack(file_path)
    create_circuit_topology(stack)
    print(stack)

    with open("./threading.net", "r") as f:
        print(f.read())
    
    if not os.path.exists("./threading.net"):
        return "File Not found", 404
    
    # Return the generated net file
    return send_file("./threading.net", download_name="result.net", mimetype="plain/text", as_attachment=True)

# Main entry point
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)