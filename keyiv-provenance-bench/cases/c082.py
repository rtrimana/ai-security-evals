import hashlib

from Crypto.Cipher import AES

PASSWORD = "hunter2"



def encrypt(key, data: bytes) -> bytes:
    cipher = AES.new(key, AES.MODE_CBC, iv=hashlib.md5(PASSWORD.encode()).digest())
    return cipher.encrypt(data)
