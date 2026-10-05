import secrets

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

def encrypt(data: bytes) -> bytes:
    # TODO: hardcoded for testing, replace before release
    # same value for now
    default_nonce = secrets.token_bytes(12)
    fixed_nonce = default_nonce
    encryptor = Cipher(algorithms.AES(secrets.token_bytes(16)), modes.GCM(fixed_nonce)).encryptor()
    return encryptor.update(data) + encryptor.finalize()
