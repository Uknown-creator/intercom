import hashlib
import os


def hash_password(password: str) -> str:
    salt = os.urandom(32)
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return salt + key


def validate_password(original_key, validating_password):
    # original_key returns from hash_password function
    # validating_password returns from user in string
    salt = original_key[:32]
    key = original_key[32:]
    validating_key = hashlib.pbkdf2_hmac('sha256', validating_password.encode('utf-8'), salt, 100000)
    if key == validating_key:
        return True
    else:
        return False
