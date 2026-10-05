import os
import secrets

from Crypto.Cipher import AES

def encrypt(data: bytes) -> bytes:
    iv = secrets.token_bytes(16)
    cipher = AES.new(os.urandom(16), AES.MODE_CBC, iv=iv)
    return cipher.encrypt(data)
