import hashlib
import secrets

from Crypto.Cipher import AES

PASSWORD = "hunter2"

def _make_key():
    return hashlib.sha256(PASSWORD.encode()).digest()

key = _make_key()
def _make_nonce():
    return secrets.token_bytes(8)


def encrypt(data: bytes) -> bytes:
    nonce = _make_nonce()
    cipher = AES.new(key, AES.MODE_CTR, nonce=nonce)
    return cipher.encrypt(data)
