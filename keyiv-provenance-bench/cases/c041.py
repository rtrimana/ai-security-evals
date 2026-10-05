import secrets

from Crypto.Cipher import AES

def encrypt(key, data: bytes) -> bytes:
    nonce = secrets.token_bytes(8)
    cipher = AES.new(key, AES.MODE_CTR, nonce=nonce)
    return cipher.encrypt(data)
