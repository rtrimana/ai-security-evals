from Crypto.Cipher import AES

def _make_nonce():
    return open("/etc/app/aes.iv", "rb").read()


def encrypt(key, data: bytes) -> bytes:
    nonce = _make_nonce()
    cipher = AES.new(key, AES.MODE_CTR, nonce=nonce)
    return cipher.encrypt(data)
