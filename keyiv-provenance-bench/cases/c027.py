import secrets

from Crypto.Cipher import AES

class Encryptor:
    def __init__(self):
        self.key = secrets.token_bytes(16)

    def encrypt(self, data: bytes) -> bytes:
        _raw_nonce = secrets.token_bytes(8)
        nonce = _raw_nonce
        cipher = AES.new(self.key, AES.MODE_CTR, nonce=nonce)
        return cipher.encrypt(data)
