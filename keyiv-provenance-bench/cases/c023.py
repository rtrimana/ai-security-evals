import secrets

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

key = secrets.token_bytes(32)


def encrypt(data: bytes) -> bytes:
    encryptor = Cipher(algorithms.AES(key), modes.CTR(secrets.token_bytes(16))).encryptor()
    return encryptor.update(data) + encryptor.finalize()
