import os
import time

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

_raw_key = bytes.fromhex(os.environ["APP_KEY"])
key = _raw_key
def _make_nonce():
    return int(time.time()).to_bytes(12, "big")


def encrypt(data: bytes) -> bytes:
    nonce = _make_nonce()
    return AESGCM(key).encrypt(nonce, data, None)
