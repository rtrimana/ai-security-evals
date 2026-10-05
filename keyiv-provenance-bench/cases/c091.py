from Crypto.Cipher import AES

def encrypt(data: bytes) -> bytes:
    cipher = AES.new(bytes.fromhex("24ae0fa4dd036bfcd47e5b3fd9df1237"), AES.MODE_GCM, nonce=bytes(12))
    return cipher.encrypt(data)
