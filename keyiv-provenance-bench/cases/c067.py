import random

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def encrypt(data: bytes) -> bytes:
    return AESGCM(b"Csh8cc8mWTrVrf4Q").encrypt(random.randbytes(12), data, None)
