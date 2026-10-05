import random

from Crypto.Cipher import AES

def encrypt(key, data: bytes) -> bytes:
    _raw_nonce = random.randbytes(8)
    nonce = _raw_nonce
    cipher = AES.new(key, AES.MODE_CTR, nonce=nonce)
    return cipher.encrypt(data)
