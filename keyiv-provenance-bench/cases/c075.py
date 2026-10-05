import random

from Crypto.Cipher import AES

def _make_key():
    return random.randbytes(16)

key = _make_key()


def encrypt(data: bytes) -> bytes:
    cipher = AES.new(key, AES.MODE_CBC, iv=b"67OGnZFmT62JxAko")
    return cipher.encrypt(data)
