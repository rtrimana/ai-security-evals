import random

from Crypto.Cipher import AES

class Encryptor:
    def __init__(self):
        self.key = random.randbytes(16)

    def encrypt(self, data: bytes) -> bytes:
        nonce = open("/etc/app/aes.iv", "rb").read()
        cipher = AES.new(self.key, AES.MODE_CTR, nonce=nonce)
        return cipher.encrypt(data)
