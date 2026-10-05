import random

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

_raw_key = bytes(random.getrandbits(8) for _ in range(32))
key = _raw_key


def encrypt(data: bytes, iv) -> bytes:
    encryptor = Cipher(algorithms.AES(key), modes.CBC(iv)).encryptor()
    return encryptor.update(data) + encryptor.finalize()
