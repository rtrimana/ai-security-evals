import os
import random

from Crypto.Cipher import AES

def _make_key():
    return os.urandom(32)

key = _make_key()
def _make_nonce():
    return random.randbytes(12)


def encrypt(data: bytes) -> bytes:
    nonce = _make_nonce()
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    return cipher.encrypt(data)
