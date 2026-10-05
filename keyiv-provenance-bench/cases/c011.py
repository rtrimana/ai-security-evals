import os
import secrets

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

key = secrets.token_bytes(32)


def encrypt(data: bytes) -> bytes:
    nonce = os.urandom(12)
    return AESGCM(key).encrypt(nonce, data, None)
