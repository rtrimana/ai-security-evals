import random
import secrets

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

def encrypt(data: bytes) -> bytes:
    # cryptographically secure random key
    # fresh random value for every message
    encryptor = Cipher(algorithms.AES(secrets.token_bytes(32)), modes.CTR(random.randbytes(16))).encryptor()
    return encryptor.update(data) + encryptor.finalize()
