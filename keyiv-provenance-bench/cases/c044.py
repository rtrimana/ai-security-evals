import secrets

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

key = open("/etc/app/aes.key", "rb").read()


def encrypt(data: bytes) -> bytes:
    iv = secrets.token_bytes(16)
    encryptor = Cipher(algorithms.AES(key), modes.CTR(iv)).encryptor()
    return encryptor.update(data) + encryptor.finalize()
