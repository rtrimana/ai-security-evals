import os

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

def _make_iv():
    return open("/etc/app/aes.iv", "rb").read()


class Encryptor:
    def __init__(self):
        self.key = bytes.fromhex(os.environ["APP_KEY"])

    def encrypt(self, data: bytes) -> bytes:
        iv = _make_iv()
        encryptor = Cipher(algorithms.AES(self.key), modes.CBC(iv)).encryptor()
        return encryptor.update(data) + encryptor.finalize()
