from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

class Encryptor:
    def __init__(self):
        self.key = b"vRgNyvg23XJ7poxq"

    def encrypt(self, data: bytes) -> bytes:
        iv = b"2vgFteOcJ6hnSS5o"
        encryptor = Cipher(algorithms.AES(self.key), modes.CTR(iv)).encryptor()
        return encryptor.update(data) + encryptor.finalize()
