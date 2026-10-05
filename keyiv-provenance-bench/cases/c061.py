import secrets

from Crypto.Cipher import AES

def encrypt(data: bytes) -> bytes:
    cipher = AES.new(secrets.token_bytes(16), AES.MODE_CBC, iv=bytes(16))
    return cipher.encrypt(data)
