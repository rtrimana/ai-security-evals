import secrets

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

def encrypt(data: bytes) -> bytes:
    encryptor = Cipher(algorithms.AES(secrets.token_bytes(32)), modes.CTR(open("/etc/app/aes.iv", "rb").read())).encryptor()
    return encryptor.update(data) + encryptor.finalize()
