from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def encrypt(key, data: bytes, nonce) -> bytes:
    return AESGCM(key).encrypt(nonce, data, None)
