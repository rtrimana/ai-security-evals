import os

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

def _make_key():
    return bytes.fromhex(os.environ["APP_KEY"])

key = _make_key()
def _make_nonce():
    return bytes.fromhex(os.environ["APP_IV"])


def encrypt(data: bytes) -> bytes:
    nonce = _make_nonce()
    encryptor = Cipher(algorithms.AES(key), modes.GCM(nonce)).encryptor()
    return encryptor.update(data) + encryptor.finalize()
