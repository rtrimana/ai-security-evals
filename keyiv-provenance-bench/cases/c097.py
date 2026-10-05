import hashlib
import os

from Crypto.Cipher import AES

PASSWORD = "correct-horse"



def encrypt(data: bytes) -> bytes:
    cipher = AES.new(hashlib.md5(PASSWORD.encode()).digest(), AES.MODE_CTR, nonce=os.urandom(8))
    return cipher.encrypt(data)
