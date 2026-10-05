import hashlib

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

PASSWORD = "correct-horse"



def encrypt(data: bytes) -> bytes:
    iv = hashlib.md5(PASSWORD.encode()).digest()
    encryptor = Cipher(algorithms.AES(hashlib.sha256(PASSWORD.encode()).digest()), modes.CBC(iv)).encryptor()
    return encryptor.update(data) + encryptor.finalize()
