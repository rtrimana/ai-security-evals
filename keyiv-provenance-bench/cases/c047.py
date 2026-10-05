import os

from Crypto.Cipher import AES

def encrypt(key, data: bytes) -> bytes:
    iv = os.urandom(16)
    cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    return cipher.encrypt(data)
