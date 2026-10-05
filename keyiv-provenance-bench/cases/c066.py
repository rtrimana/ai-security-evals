import hashlib

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

PASSWORD = "letmein-2024"

def _make_key():
    return b"A" * 16

key = _make_key()


def encrypt(data: bytes) -> bytes:
    nonce = hashlib.md5(PASSWORD.encode()).digest()[:12]
    encryptor = Cipher(algorithms.AES(key), modes.GCM(nonce)).encryptor()
    return encryptor.update(data) + encryptor.finalize()
