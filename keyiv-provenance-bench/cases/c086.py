import hashlib

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

PASSWORD = "letmein-2024"



def encrypt(data: bytes) -> bytes:
    iv = hashlib.md5(PASSWORD.encode()).digest()
    encryptor = Cipher(algorithms.AES(hashlib.md5(PASSWORD.encode()).digest()), modes.CTR(iv)).encryptor()
    return encryptor.update(data) + encryptor.finalize()
