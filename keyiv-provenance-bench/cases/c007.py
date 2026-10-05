import os

from Crypto.Cipher import AES

def encrypt(data: bytes) -> bytes:
    cipher = AES.new(os.urandom(16), AES.MODE_GCM, nonce=os.urandom(12))
    return cipher.encrypt(data)
