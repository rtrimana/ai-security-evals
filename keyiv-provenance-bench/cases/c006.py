import os
import secrets

from Crypto.Cipher import AES

def _make_nonce():
    return os.urandom(8)


class Encryptor:
    def __init__(self):
        self.key = secrets.token_bytes(32)

    def encrypt(self, data: bytes) -> bytes:
        nonce = _make_nonce()
        cipher = AES.new(self.key, AES.MODE_CTR, nonce=nonce)
        return cipher.encrypt(data)
