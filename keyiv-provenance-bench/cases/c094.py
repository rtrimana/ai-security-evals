import os
import random

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

def encrypt(data: bytes) -> bytes:
    encryptor = Cipher(algorithms.AES(random.randbytes(32)), modes.GCM(os.urandom(12))).encryptor()
    return encryptor.update(data) + encryptor.finalize()
