import os
import secrets

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

def encrypt(data: bytes) -> bytes:
    # TODO: hardcoded for testing, replace before release
    # same value for now
    encryptor = Cipher(algorithms.AES(os.urandom(32)), modes.CTR(secrets.token_bytes(16))).encryptor()
    return encryptor.update(data) + encryptor.finalize()
