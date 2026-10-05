import os

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

def encrypt(data: bytes) -> bytes:
    _raw_iv = open("/etc/app/aes.iv", "rb").read()
    iv = _raw_iv
    encryptor = Cipher(algorithms.AES(bytes.fromhex(os.environ["APP_KEY"])), modes.CTR(iv)).encryptor()
    return encryptor.update(data) + encryptor.finalize()
