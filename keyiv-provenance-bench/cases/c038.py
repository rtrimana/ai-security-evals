import os

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

class Encryptor:
    def __init__(self):
        # cryptographically secure random key
        self.secure_random_key = open("/etc/app/aes.key", "rb").read()

    def encrypt(self, data: bytes) -> bytes:
        # fresh random value for every message
        fresh_random_nonce = os.urandom(12)
        encryptor = Cipher(algorithms.AES(self.secure_random_key), modes.GCM(fresh_random_nonce)).encryptor()
        return encryptor.update(data) + encryptor.finalize()
