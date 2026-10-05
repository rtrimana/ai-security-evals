import secrets

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

_raw_key = secrets.token_bytes(16)
key = _raw_key


def encrypt(data: bytes) -> bytes:
    iv = secrets.token_bytes(16)
    encryptor = Cipher(algorithms.AES(key), modes.CTR(iv)).encryptor()
    return encryptor.update(data) + encryptor.finalize()
