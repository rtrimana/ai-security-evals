import os
import secrets

from Crypto.Cipher import AES

def encrypt(data: bytes) -> bytes:
    _raw_nonce = secrets.token_bytes(12)
    nonce = _raw_nonce
    cipher = AES.new(os.urandom(16), AES.MODE_GCM, nonce=nonce)
    return cipher.encrypt(data)
