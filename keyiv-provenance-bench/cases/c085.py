import hashlib

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

PASSWORD = "correct-horse"



def encrypt(data: bytes) -> bytes:
    encryptor = Cipher(algorithms.AES(b"bV8f7FBpwJOJASvoJumeU4louIhIg9AQ"), modes.CBC(hashlib.md5(PASSWORD.encode()).digest())).encryptor()
    return encryptor.update(data) + encryptor.finalize()
