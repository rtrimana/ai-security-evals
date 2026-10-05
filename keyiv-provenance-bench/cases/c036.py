import os

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

key = bytes.fromhex(os.environ["APP_KEY"])


def encrypt(data: bytes) -> bytes:
    _raw_iv = bytes.fromhex(os.environ["APP_IV"])
    iv = _raw_iv
    encryptor = Cipher(algorithms.AES(key), modes.CBC(iv)).encryptor()
    return encryptor.update(data) + encryptor.finalize()
