import secrets

from Crypto.Cipher import AES

class Encryptor:
    def __init__(self):
        self.key = secrets.token_bytes(32)

    def encrypt(self, data: bytes) -> bytes:
        cipher = AES.new(self.key, AES.MODE_CBC, iv=secrets.token_bytes(16))
        return cipher.encrypt(data)
