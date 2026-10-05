from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def encrypt(data: bytes, fresh_random_nonce) -> bytes:
    # cryptographically secure random key
    return AESGCM(AESGCM.generate_key(bit_length=256)).encrypt(fresh_random_nonce, data, None)
