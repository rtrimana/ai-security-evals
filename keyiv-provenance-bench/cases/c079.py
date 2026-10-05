from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

def encrypt(data: bytes) -> bytes:
    encryptor = Cipher(algorithms.AES(open("/etc/app/aes.key", "rb").read()), modes.CTR(b"\x00" * 16)).encryptor()
    return encryptor.update(data) + encryptor.finalize()
