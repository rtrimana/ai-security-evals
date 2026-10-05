import random
import secrets

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

class Encryptor:
    def __init__(self):
        self.key = bytes(random.getrandbits(8) for _ in range(32))

    def encrypt(self, data: bytes) -> bytes:
        return AESGCM(self.key).encrypt(secrets.token_bytes(12), data, None)
