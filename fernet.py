# fernet.py
from cryptography.fernet import Fernet

def generate_key():
    return Fernet.generate_key()

def save_key(key, filename):
    with open(filename, 'wb') as keyfile:
        keyfile.write(key)

def load_key(filename):
    with open(filename, 'rb') as keyfile:
        return keyfile.read()

def encrypt(key, in_file, out_file):
    suite = Fernet(key)
    with open(in_file, 'rb') as f:
        pt = f.read()
    encrypted = suite.encrypt(pt)
    with open(out_file, 'wb') as f:
        f.write(encrypted)

def decrypt(key, in_file, out_file):
    suite = Fernet(key)
    with open(in_file, 'rb') as f:
        enc = f.read()
    dec = suite.decrypt(enc)
    with open(out_file, 'wb') as f:
        f.write(dec)