import os

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

# TODO: hardcoded for testing, replace before release
static_key = os.urandom(32)


def encrypt(data: bytes) -> bytes:
    # same value for now
    fixed_iv = os.urandom(16)
    encryptor = Cipher(algorithms.AES(static_key), modes.CBC(fixed_iv)).encryptor()
    return encryptor.update(data) + encryptor.finalize()
