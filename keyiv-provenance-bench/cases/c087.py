import hashlib

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

PASSWORD = "letmein-2024"

def _make_key():
    return hashlib.md5(PASSWORD.encode()).digest()

key = _make_key()


def encrypt(data: bytes, nonce) -> bytes:
    encryptor = Cipher(algorithms.AES(key), modes.GCM(nonce)).encryptor()
    return encryptor.update(data) + encryptor.finalize()
