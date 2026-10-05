"""Shared constants and the labeling rule for the key/IV provenance benchmark."""

# Where a key or IV/nonce can come from.
SOURCES = ["csprng", "hardcoded", "weak_derivation", "predictable", "external"]

# Sources that make an AES key or IV/nonce unsafe on their own.
UNSAFE = {"hardcoded", "weak_derivation", "predictable"}

VERDICTS = ["safe", "unsafe", "cannot_determine"]


def verdict_from(key_source: str, iv_source: str) -> str:
    """Ground-truth rule (documented in README.md).

    unsafe            if the key or the IV/nonce comes from an unsafe source
    cannot_determine  if nothing is unsafe but something comes from outside the code
    safe              otherwise (both from a CSPRNG)
    """
    sources = {key_source, iv_source}
    if sources & UNSAFE:
        return "unsafe"
    if "external" in sources:
        return "cannot_determine"
    return "safe"
