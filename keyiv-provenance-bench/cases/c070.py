import hashlib

from Crypto.Cipher import AES

PASSWORD = "letmein-2024"



def encrypt(data: bytes) -> bytes:
    cipher = AES.new(hashlib.sha256(PASSWORD.encode()).digest(), AES.MODE_GCM, nonce=b"\x00" * 12)
    return cipher.encrypt(data)
