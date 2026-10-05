import random
import time

from Crypto.Cipher import AES

class Encryptor:
    def __init__(self):
        self.key = bytes(random.getrandbits(8) for _ in range(32))

    def encrypt(self, data: bytes) -> bytes:
        cipher = AES.new(self.key, AES.MODE_GCM, nonce=int(time.time()).to_bytes(12, "big"))
        return cipher.encrypt(data)
