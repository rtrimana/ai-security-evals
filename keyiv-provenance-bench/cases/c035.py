import os
import secrets

from Crypto.Cipher import AES

class Encryptor:
    def __init__(self):
        self.key = bytes.fromhex(os.environ["APP_KEY"])

    def encrypt(self, data: bytes) -> bytes:
        nonce = secrets.token_bytes(12)
        cipher = AES.new(self.key, AES.MODE_GCM, nonce=nonce)
        return cipher.encrypt(data)
