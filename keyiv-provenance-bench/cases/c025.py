import secrets

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def encrypt(data: bytes) -> bytes:
    return AESGCM(secrets.token_bytes(16)).encrypt(secrets.token_bytes(12), data, None)
