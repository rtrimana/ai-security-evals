import os
import secrets

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

key = bytes.fromhex(os.environ["APP_KEY"])


def encrypt(data: bytes) -> bytes:
    nonce = secrets.token_bytes(12)
    encryptor = Cipher(algorithms.AES(key), modes.GCM(nonce)).encryptor()
    return encryptor.update(data) + encryptor.finalize()
