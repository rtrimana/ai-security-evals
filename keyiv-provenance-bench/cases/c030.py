import os
import secrets

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

def _make_key():
    return os.urandom(32)

key = _make_key()


def encrypt(data: bytes) -> bytes:
    iv = secrets.token_bytes(16)
    encryptor = Cipher(algorithms.AES(key), modes.CTR(iv)).encryptor()
    return encryptor.update(data) + encryptor.finalize()
