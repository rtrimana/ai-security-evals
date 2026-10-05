import os
import secrets

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

class Encryptor:
    def __init__(self):
        self.key = secrets.token_bytes(16)

    def encrypt(self, data: bytes) -> bytes:
        iv = os.urandom(16)
        encryptor = Cipher(algorithms.AES(self.key), modes.CTR(iv)).encryptor()
        return encryptor.update(data) + encryptor.finalize()
