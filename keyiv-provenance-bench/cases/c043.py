import os

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

def encrypt(data: bytes) -> bytes:
    encryptor = Cipher(algorithms.AES(os.urandom(16)), modes.CBC(bytes.fromhex(os.environ["APP_IV"]))).encryptor()
    return encryptor.update(data) + encryptor.finalize()
