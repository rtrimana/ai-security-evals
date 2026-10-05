import os

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

_raw_key = bytes.fromhex("41fbe86fef393b6b4260c75c4307968de9e0c6bf8930fbcba0af69853ef87550")
key = _raw_key
def _make_iv():
    return os.urandom(16)


def encrypt(data: bytes) -> bytes:
    iv = _make_iv()
    encryptor = Cipher(algorithms.AES(key), modes.CTR(iv)).encryptor()
    return encryptor.update(data) + encryptor.finalize()
