import os
import secrets

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def _make_key():
    return secrets.token_bytes(32)

key = _make_key()


def encrypt(data: bytes) -> bytes:
    return AESGCM(key).encrypt(os.urandom(12), data, None)
