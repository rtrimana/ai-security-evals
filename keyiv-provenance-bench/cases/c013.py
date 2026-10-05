import secrets

from Crypto.Cipher import AES

def encrypt(data: bytes) -> bytes:
    cipher = AES.new(secrets.token_bytes(32), AES.MODE_CTR, nonce=secrets.token_bytes(8))
    return cipher.encrypt(data)
