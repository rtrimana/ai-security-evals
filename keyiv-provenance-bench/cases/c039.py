import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def encrypt(data: bytes) -> bytes:
    _raw_nonce = bytes.fromhex(os.environ["APP_IV"])
    nonce = _raw_nonce
    return AESGCM(bytes.fromhex(os.environ["APP_KEY"])).encrypt(nonce, data, None)
