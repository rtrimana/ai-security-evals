import secrets

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

def encrypt(data: bytes, fresh_random_iv) -> bytes:
    # cryptographically secure random key
    encryptor = Cipher(algorithms.AES(secrets.token_bytes(32)), modes.CTR(fresh_random_iv)).encryptor()
    return encryptor.update(data) + encryptor.finalize()
