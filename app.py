from flask import Flask, request, send_from_directory, jsonify, abort
from flask_cors import CORS
import os
import uuid

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

file_links = {}

@app.route('/')
def home():
    return send_from_directory('static', 'index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part", 400
    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400

    unique_id = str(uuid.uuid4())
    save_path = os.path.join(UPLOAD_FOLDER, unique_id + "_" + file.filename)
    file.save(save_path)
    file_links[unique_id] = save_path

    download_link = f"/download/{unique_id}"
    return jsonify({ "message": "File uploaded", "link": download_link ,"fileId": unique_id})

@app.route('/download/<file_id>', methods=['GET'])
def download_file(file_id):
    file_path = file_links.get(file_id)
    if not file_path or not os.path.exists(file_path):
        abort(404)
    filename = os.path.basename(file_path).split("_", 1)[1]
    return send_from_directory(UPLOAD_FOLDER, os.path.basename(file_path), as_attachment=True, download_name=filename)


@app.route('/delete/<file_id>', methods=['DELETE'])
def delete_file(file_id):
    file_path = file_links.get(file_id)
    if not file_path or not os.path.exists(file_path):
        return jsonify({ "error": "File not found" }), 404

    os.remove(file_path)
    del file_links[file_id]
    return jsonify({ "message": "File deleted successfully" })


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
