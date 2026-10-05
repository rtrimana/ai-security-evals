import os

from Crypto.Cipher import AES

def encrypt(data: bytes) -> bytes:
    cipher = AES.new(os.urandom(16), AES.MODE_CBC, iv=os.urandom(16))
    return cipher.encrypt(data)
