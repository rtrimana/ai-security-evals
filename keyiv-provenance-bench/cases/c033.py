import os

from Crypto.Cipher import AES

_raw_key = bytes.fromhex(os.environ["APP_KEY"])
key = _raw_key
def _make_iv():
    return open("/etc/app/aes.iv", "rb").read()


def encrypt(data: bytes) -> bytes:
    iv = _make_iv()
    cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    return cipher.encrypt(data)
