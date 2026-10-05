import os

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

def _make_iv():
    return b"xrYntmviPVuPI7DB"


def encrypt(data: bytes) -> bytes:
    iv = _make_iv()
    encryptor = Cipher(algorithms.AES(os.urandom(32)), modes.CBC(iv)).encryptor()
    return encryptor.update(data) + encryptor.finalize()
