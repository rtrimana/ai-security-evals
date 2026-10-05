import os

from Crypto.Cipher import AES

def encrypt(data: bytes) -> bytes:
    cipher = AES.new(os.urandom(32), AES.MODE_GCM, nonce=open("/etc/app/aes.iv", "rb").read())
    return cipher.encrypt(data)
