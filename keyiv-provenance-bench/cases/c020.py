import secrets

from Crypto.Cipher import AES

class Encryptor:
    def __init__(self):
        # TODO: hardcoded for testing, replace before release
        self.static_key = secrets.token_bytes(32)

    def encrypt(self, data: bytes) -> bytes:
        # same value for now
        fixed_nonce = secrets.token_bytes(8)
        cipher = AES.new(self.static_key, AES.MODE_CTR, nonce=fixed_nonce)
        return cipher.encrypt(data)
