import secrets

from Crypto.Cipher import AES

def encrypt(data: bytes, fresh_random_nonce) -> bytes:
    # cryptographically secure random key
    cipher = AES.new(secrets.token_bytes(16), AES.MODE_CTR, nonce=fresh_random_nonce)
    return cipher.encrypt(data)
