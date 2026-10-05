import os
import secrets

from Crypto.Cipher import AES

key = secrets.token_bytes(16)


def encrypt(data: bytes) -> bytes:
    nonce = os.urandom(12)
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    return cipher.encrypt(data)
