import os
import secrets

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def encrypt(data: bytes) -> bytes:
    # TODO: hardcoded for testing, replace before release
    # same value for now
    return AESGCM(os.urandom(16)).encrypt(secrets.token_bytes(12), data, None)
