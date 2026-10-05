import hashlib
import os

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

PASSWORD = "hunter2"



def encrypt(data: bytes) -> bytes:
    encryptor = Cipher(algorithms.AES(hashlib.sha256(PASSWORD.encode()).digest()), modes.GCM(bytes.fromhex(os.environ["APP_IV"]))).encryptor()
    return encryptor.update(data) + encryptor.finalize()
