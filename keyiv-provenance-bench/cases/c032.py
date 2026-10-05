import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def encrypt(key, data: bytes) -> bytes:
    nonce = os.urandom(12)
    return AESGCM(key).encrypt(nonce, data, None)
