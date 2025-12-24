from cryptography.fernet import Fernet

# Automatically generates/loads key
KEY_FILE = "secret.key"

def load_or_create_key():
    try:
        with open(KEY_FILE, "rb") as f:
            return f.read()
    except FileNotFoundError:
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as f:
            f.write(key)
        return key


fernet = Fernet(load_or_create_key())


def encrypt_file(input_path, output_path):
    with open(input_path, "rb") as f:
        data = f.read()
    encrypted = fernet.encrypt(data)
    with open(output_path, "wb") as f:
        f.write(encrypted)


def decrypt_file(input_path, output_path):
    with open(input_path, "rb") as f:
        data = f.read()
    decrypted = fernet.decrypt(data)
    with open(output_path, "wb") as f:
        f.write(decrypted)
