import hashlib
import os

from Crypto.Cipher import AES

PASSWORD = "letmein-2024"



def encrypt(data: bytes) -> bytes:
    nonce = hashlib.md5(PASSWORD.encode()).digest()[:8]
    cipher = AES.new(os.urandom(32), AES.MODE_CTR, nonce=nonce)
    return cipher.encrypt(data)
