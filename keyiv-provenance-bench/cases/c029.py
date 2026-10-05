import os

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

key = os.urandom(16)


def encrypt(data: bytes) -> bytes:
    iv = os.urandom(16)
    encryptor = Cipher(algorithms.AES(key), modes.CBC(iv)).encryptor()
    return encryptor.update(data) + encryptor.finalize()
