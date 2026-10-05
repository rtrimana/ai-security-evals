import secrets

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

def _make_key():
    return secrets.token_bytes(16)

key = _make_key()


def encrypt(data: bytes) -> bytes:
    _raw_iv = secrets.token_bytes(16)
    iv = _raw_iv
    encryptor = Cipher(algorithms.AES(key), modes.CBC(iv)).encryptor()
    return encryptor.update(data) + encryptor.finalize()
