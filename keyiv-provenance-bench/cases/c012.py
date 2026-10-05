import os

from Crypto.Cipher import AES

# same value for now
def get_fixed_iv():
    return os.urandom(16)


def encrypt(data: bytes) -> bytes:
    # TODO: hardcoded for testing, replace before release
    fixed_iv = get_fixed_iv()
    cipher = AES.new(os.urandom(32), AES.MODE_CBC, iv=fixed_iv)
    return cipher.encrypt(data)
