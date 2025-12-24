from flask import Flask, render_template, request, send_file, redirect, url_for
from crypto_utils import encrypt_file, decrypt_file
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
ENCRYPT_FOLDER = os.path.join(BASE_DIR, "encrypt")
DECRYPT_FOLDER = os.path.join(BASE_DIR, "decrypt")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(ENCRYPT_FOLDER, exist_ok=True)
os.makedirs(DECRYPT_FOLDER, exist_ok=True)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/encrypt", methods=["POST"])
def encrypt_route():
    file = request.files["file"]
    filename = secure_filename(file.filename)

    uploaded_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(uploaded_path)

    encrypted_filename = filename + ".enc"
    encrypted_path = os.path.join(ENCRYPT_FOLDER, encrypted_filename)

    encrypt_file(uploaded_path, encrypted_path)

    return send_file(encrypted_path, as_attachment=True)


@app.route("/decrypt", methods=["POST"])
def decrypt_route():
    file = request.files["file"]
    filename = secure_filename(file.filename)

    uploaded_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(uploaded_path)

    decrypted_filename = filename + ".enc"
    decrypted_path = os.path.join(DECRYPT_FOLDER, decrypted_filename)
    decrypt_file(uploaded_path, decrypted_path)

    return send_file(decrypted_path, as_attachment=True)


@app.route("/download/<folder>/<filename>")
def download_file(folder, filename):
    # Sanitize folder parameter
    if folder not in ["encrypt", "decrypt"]:
        return "Invalid folder", 400

    folder_path = ENCRYPT_FOLDER if folder == "encrypt" else DECRYPT_FOLDER
    file_path = os.path.join(folder_path, filename)

    if not os.path.isfile(file_path):
        return "File not found", 404

    return send_file(file_path, as_attachment=True)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)


# python install 

#  flask cryptography
# python app.py

# http://127.0.0.1:5000
# run here 
