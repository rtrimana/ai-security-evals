import hashlib
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

PASSWORD = "P@ssw0rd!"



def encrypt(data: bytes) -> bytes:
    nonce = hashlib.md5(PASSWORD.encode()).digest()[:12]
    return AESGCM(os.urandom(32)).encrypt(nonce, data, None)
