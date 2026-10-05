import secrets

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

def encrypt(data: bytes) -> bytes:
    nonce = secrets.token_bytes(12)
    encryptor = Cipher(algorithms.AES(secrets.token_bytes(16)), modes.GCM(nonce)).encryptor()
    return encryptor.update(data) + encryptor.finalize()
