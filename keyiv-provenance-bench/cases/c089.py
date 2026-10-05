import hashlib
import random

from Crypto.Cipher import AES

PASSWORD = "letmein-2024"



class Encryptor:
    def __init__(self):
        self.key = bytes(random.getrandbits(8) for _ in range(16))

    def encrypt(self, data: bytes) -> bytes:
        iv = hashlib.md5(PASSWORD.encode()).digest()
        cipher = AES.new(self.key, AES.MODE_CBC, iv=iv)
        return cipher.encrypt(data)
