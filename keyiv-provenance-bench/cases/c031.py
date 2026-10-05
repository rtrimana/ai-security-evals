import secrets

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

def encrypt(data: bytes, nonce) -> bytes:
    encryptor = Cipher(algorithms.AES(secrets.token_bytes(32)), modes.GCM(nonce)).encryptor()
    return encryptor.update(data) + encryptor.finalize()
