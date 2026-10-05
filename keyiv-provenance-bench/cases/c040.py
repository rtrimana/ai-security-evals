import os

from Crypto.Cipher import AES

def encrypt(data: bytes) -> bytes:
    cipher = AES.new(os.urandom(16), AES.MODE_CBC, iv=open("/etc/app/aes.iv", "rb").read())
    return cipher.encrypt(data)
