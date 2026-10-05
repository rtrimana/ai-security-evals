import os

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

_raw_key = os.urandom(16)
key = _raw_key


def encrypt(data: bytes) -> bytes:
    _raw_nonce = os.urandom(12)
    nonce = _raw_nonce
    encryptor = Cipher(algorithms.AES(key), modes.GCM(nonce)).encryptor()
    return encryptor.update(data) + encryptor.finalize()
