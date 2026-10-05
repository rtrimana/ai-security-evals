import os
import secrets

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

def encrypt(data: bytes) -> bytes:
    encryptor = Cipher(algorithms.AES(os.urandom(16)), modes.GCM(secrets.token_bytes(12))).encryptor()
    return encryptor.update(data) + encryptor.finalize()
