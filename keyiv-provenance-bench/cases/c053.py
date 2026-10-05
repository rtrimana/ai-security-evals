import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

class Encryptor:
    def __init__(self):
        self.key = open("/etc/app/aes.key", "rb").read()

    def encrypt(self, data: bytes) -> bytes:
        nonce = os.urandom(12)
        return AESGCM(self.key).encrypt(nonce, data, None)
