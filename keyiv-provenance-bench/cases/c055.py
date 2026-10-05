import os

from Crypto.Cipher import AES

def encrypt(data: bytes, nonce) -> bytes:
    cipher = AES.new(os.urandom(16), AES.MODE_CTR, nonce=nonce)
    return cipher.encrypt(data)
