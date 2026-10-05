import os
import secrets

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

class Encryptor:
    def __init__(self):
        # cryptographically secure random key
        self.secure_random_key = bytes.fromhex(os.environ["APP_KEY"])

    def encrypt(self, data: bytes) -> bytes:
        # fresh random value for every message
        fresh_random_iv = secrets.token_bytes(16)
        encryptor = Cipher(algorithms.AES(self.secure_random_key), modes.CBC(fresh_random_iv)).encryptor()
        return encryptor.update(data) + encryptor.finalize()
