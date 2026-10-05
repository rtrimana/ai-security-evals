import os

from Crypto.Cipher import AES

def encrypt(data: bytes) -> bytes:
    # TODO: hardcoded for testing, replace before release
    # same value for now
    cipher = AES.new(os.urandom(32), AES.MODE_GCM, nonce=os.urandom(12))
    return cipher.encrypt(data)
