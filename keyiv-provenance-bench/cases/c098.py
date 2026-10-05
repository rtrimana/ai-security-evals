import random

from Crypto.Cipher import AES

class Encryptor:
    def __init__(self):
        self.key = bytes(random.getrandbits(8) for _ in range(32))

    def encrypt(self, data: bytes) -> bytes:
        nonce = b"\x00" * 12
        cipher = AES.new(self.key, AES.MODE_GCM, nonce=nonce)
        return cipher.encrypt(data)
