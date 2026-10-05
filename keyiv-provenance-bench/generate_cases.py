"""Generate labeled AES key/IV provenance cases.

Every snippet is synthetic. The label is known by construction (the template
decides where the key and the IV/nonce come from), so no model is involved in
producing ground truth.

Usage:
    python generate_cases.py            # writes cases/ and cases.jsonl
    python generate_cases.py --seed 7   # a different but reproducible set
"""
import argparse
import ast
import json
import random
import re
import string
from pathlib import Path

from common import SOURCES, verdict_from

# (library, mode) combinations; cycled across the cases.
LIB_MODES = [
    ("cryptography", "CBC"),
    ("cryptography", "CTR"),
    ("cryptography", "GCM"),
    ("aesgcm", "GCM"),
    ("pycryptodome", "CBC"),
    ("pycryptodome", "CTR"),
    ("pycryptodome", "GCM"),
]

# How the value reaches the encryption call, grouped by number of hops between the
# sink and the originating expression.
HOPS = {"direct": 0, "param": 0, "var": 1, "cls": 1, "chain": 2, "helper": 2}
KEY_BY_HOP = {0: ["direct"], 1: ["var", "cls"], 2: ["chain", "helper"]}
IV_BY_HOP = {0: ["direct"], 1: ["var"], 2: ["chain", "helper"]}

# Class sizes. Balanced on purpose: a model that always answers "unsafe" should
# not be able to score well.
N_SAFE, N_UNKNOWN, N_UNSAFE = 30, 30, 40

PASSWORDS = ["hunter2", "correct-horse", "letmein-2024", "P@ssw0rd!", "changeme"]


def rand_literal(rng, n):
    alphabet = string.ascii_letters + string.digits
    return "".join(rng.choice(alphabet) for _ in range(n))


def key_expr(rng, source, n, lib):
    """Expression producing a key of n bytes. None means 'function parameter'."""
    if source == "csprng":
        opts = [f"os.urandom({n})", f"secrets.token_bytes({n})"]
        if lib == "aesgcm" and n == 32:
            opts.append("AESGCM.generate_key(bit_length=256)")
        return rng.choice(opts)
    if source == "hardcoded":
        return rng.choice([
            f'b"{rand_literal(rng, n)}"',
            f'bytes.fromhex("{rng.getrandbits(n * 8):0{n * 2}x}")',
            f'b"A" * {n}',
        ])
    if source == "weak_derivation":
        if n == 32:
            return "hashlib.sha256(PASSWORD.encode()).digest()"
        return "hashlib.md5(PASSWORD.encode()).digest()"
    if source == "predictable":
        return rng.choice([
            f"random.randbytes({n})",
            f"bytes(random.getrandbits(8) for _ in range({n}))",
        ])
    if source == "external":
        return rng.choice([
            'bytes.fromhex(os.environ["APP_KEY"])',
            'open("/etc/app/aes.key", "rb").read()',
            None,
        ])
    raise ValueError(source)


def iv_expr(rng, source, n):
    """Expression producing an IV/nonce of n bytes. None means 'function parameter'."""
    if source == "csprng":
        return rng.choice([f"os.urandom({n})", f"secrets.token_bytes({n})"])
    if source == "hardcoded":
        return rng.choice([
            f'b"{rand_literal(rng, n)}"',
            f'b"\\x00" * {n}',
            f"bytes({n})",
        ])
    if source == "weak_derivation":
        base = "hashlib.md5(PASSWORD.encode()).digest()"
        return base if n == 16 else f"{base}[:{n}]"
    if source == "predictable":
        return rng.choice([
            f"random.randbytes({n})",
            f'int(time.time()).to_bytes({n}, "big")',
        ])
    if source == "external":
        return rng.choice([
            'bytes.fromhex(os.environ["APP_IV"])',
            'open("/etc/app/aes.iv", "rb").read()',
            None,
        ])
    raise ValueError(source)


def plain_names(is_nonce):
    iv = "nonce" if is_nonce else "iv"
    return dict(key="key", iv=iv, kfn="_make_key", ifn=f"_make_{iv}",
                kraw="_raw_key", iraw=f"_raw_{iv}")


def misleading_names(verdict, is_nonce):
    """Names and comments that claim the opposite of the truth."""
    iv = "nonce" if is_nonce else "iv"
    if verdict == "safe":
        names = dict(key="static_key", iv=f"fixed_{iv}", kfn="get_hardcoded_key",
                     ifn=f"get_fixed_{iv}", kraw="default_key", iraw=f"default_{iv}")
        return names, "TODO: hardcoded for testing, replace before release", "same value for now"
    names = dict(key="secure_random_key", iv=f"fresh_random_{iv}", kfn="generate_secure_key",
                 ifn=f"generate_random_{iv}", kraw="random_key_bytes", iraw=f"random_{iv}_bytes")
    return names, "cryptographically secure random key", "fresh random value for every message"


def indent(lines, n):
    pad = " " * n
    return [pad + ln if ln else ln for ln in lines]


def commented(lines, comment):
    return ([f"# {comment}"] if comment else []) + lines


def render(spec, password):
    """Turn a spec into Python source text."""
    lib, mode = spec["lib"], spec["mode"]
    nm = spec["names"]
    kexpr, iexpr = spec["key_expr"], spec["iv_expr"]
    kstruct, istruct = spec["key_struct"], spec["iv_struct"]
    kcom, icom = spec["key_comment"], spec["iv_comment"]

    module, pre, cls_init = [], [], []
    kparam = iparam = None

    # ---- key: reused across messages, so it lives at module/class level ----
    if kstruct == "direct":
        kref = kexpr
        if kcom:
            pre.append(f"# {kcom}")
    elif kstruct == "var":
        module += commented([f"{nm['key']} = {kexpr}"], kcom)
        kref = nm["key"]
    elif kstruct == "chain":
        module += commented([f"{nm['kraw']} = {kexpr}", f"{nm['key']} = {nm['kraw']}"], kcom)
        kref = nm["key"]
    elif kstruct == "helper":
        module += commented([f"def {nm['kfn']}():", f"    return {kexpr}", "",
                             f"{nm['key']} = {nm['kfn']}()"], kcom)
        kref = nm["key"]
    elif kstruct == "cls":
        cls_init = commented([f"self.{nm['key']} = {kexpr}"], kcom)
        kref = f"self.{nm['key']}"
    elif kstruct == "param":
        kparam = nm["key"]
        kref = kparam
    else:
        raise ValueError(kstruct)

    # ---- IV/nonce: computed per call inside encrypt() ----
    ivn = nm["iv"]
    if istruct == "direct":
        iref = iexpr
        if icom:
            pre.append(f"# {icom}")
    elif istruct == "var":
        pre += commented([f"{ivn} = {iexpr}"], icom)
        iref = ivn
    elif istruct == "chain":
        pre += commented([f"{nm['iraw']} = {iexpr}", f"{ivn} = {nm['iraw']}"], icom)
        iref = ivn
    elif istruct == "helper":
        module += commented([f"def {nm['ifn']}():", f"    return {iexpr}"], icom)
        pre.append(f"{ivn} = {nm['ifn']}()")
        iref = ivn
    elif istruct == "param":
        iparam = ivn
        iref = iparam
    else:
        raise ValueError(istruct)

    # ---- the sink ----
    if lib == "cryptography":
        third_party = ["from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes"]
        sink = [f"encryptor = Cipher(algorithms.AES({kref}), modes.{mode}({iref})).encryptor()",
                "return encryptor.update(data) + encryptor.finalize()"]
    elif lib == "aesgcm":
        third_party = ["from cryptography.hazmat.primitives.ciphers.aead import AESGCM"]
        sink = [f"return AESGCM({kref}).encrypt({iref}, data, None)"]
    else:
        third_party = ["from Crypto.Cipher import AES"]
        if mode == "CBC":
            ctor = f"AES.new({kref}, AES.MODE_CBC, iv={iref})"
        elif mode == "CTR":
            ctor = f"AES.new({kref}, AES.MODE_CTR, nonce={iref})"
        else:
            ctor = f"AES.new({kref}, AES.MODE_GCM, nonce={iref})"
        sink = [f"cipher = {ctor}", "return cipher.encrypt(data)"]

    # ---- function / class wrapper ----
    sig = ([kparam] if kparam and kstruct != "cls" else []) + ["data: bytes"] + ([iparam] if iparam else [])
    if kstruct == "cls":
        sig = ["self"] + ["data: bytes"] + ([iparam] if iparam else [])
        wrapper = (["class Encryptor:", "    def __init__(self):"] + indent(cls_init, 8) + [""]
                   + [f"    def encrypt({', '.join(sig)}) -> bytes:"] + indent(pre + sink, 8))
    else:
        wrapper = [f"def encrypt({', '.join(sig)}) -> bytes:"] + indent(pre + sink, 4)

    # PASSWORD constant if anything references it
    body = "\n".join(module + wrapper + cls_init)
    if "PASSWORD" in body:
        module = [f'PASSWORD = "{password}"', ""] + module

    # standard-library imports inferred from usage
    body = "\n".join(module + wrapper)
    std = [f"import {m}" for m in ("hashlib", "os", "random", "secrets", "time")
           if re.search(rf"\b{m}\.", body)]

    parts = []
    if std:
        parts += std + [""]
    parts += third_party + [""]
    if module:
        parts += module + [""]
    parts += [""] if module else []
    parts += wrapper
    return "\n".join(parts).rstrip() + "\n"


def pick_structs(rng, target, kexpr, iexpr):
    """Choose key/IV structures so that the larger hop count equals `target`
    (parameters count as 0 hops and cannot carry the target)."""
    k_param, i_param = kexpr is None, iexpr is None
    if k_param and i_param:
        return "param", "param"
    if k_param:
        return "param", rng.choice(IV_BY_HOP[target])
    if i_param:
        return rng.choice(KEY_BY_HOP[target]), "param"
    if rng.random() < 0.5:
        return rng.choice(KEY_BY_HOP[target]), rng.choice(IV_BY_HOP[rng.randint(0, target)])
    return rng.choice(KEY_BY_HOP[rng.randint(0, target)]), rng.choice(IV_BY_HOP[target])


def source_pairs(rng):
    """(key_source, iv_source) pairs per verdict class, in a fixed order."""
    safe = [("csprng", "csprng")] * N_SAFE
    unknown_pairs = [("csprng", "external"), ("external", "csprng"), ("external", "external")]
    unknown = [unknown_pairs[i % 3] for i in range(N_UNKNOWN)]
    unsafe_pairs = [(k, i) for k in SOURCES for i in SOURCES if verdict_from(k, i) == "unsafe"]
    unsafe = list(unsafe_pairs) + rng.sample(unsafe_pairs, N_UNSAFE - len(unsafe_pairs))
    return [safe, unknown, unsafe]


def build_specs(seed):
    rng = random.Random(seed)
    specs = []
    n = 0
    for group in source_pairs(rng):
        for idx, (ks, is_) in enumerate(group):
            lib, mode = LIB_MODES[n % len(LIB_MODES)]
            n += 1
            trap = "misleading" if idx % 4 == 3 else "none"
            is_nonce = mode == "GCM" or (lib == "pycryptodome" and mode == "CTR")
            key_len = rng.choice([16, 32])
            if lib == "pycryptodome" and mode == "CTR":
                iv_len = 8
            else:
                iv_len = 12 if mode == "GCM" else 16

            kexpr = key_expr(rng, ks, key_len, lib)
            iexpr = iv_expr(rng, is_, iv_len)
            kstruct, istruct = pick_structs(rng, idx % 3, kexpr, iexpr)
            verdict = verdict_from(ks, is_)

            if trap == "misleading":
                names, kcom, icom = misleading_names(verdict, is_nonce)
            else:
                names, kcom, icom = plain_names(is_nonce), None, None

            specs.append(dict(
                id=f"c{n:03d}", lib=lib, mode=mode, names=names,
                key_source=ks, iv_source=is_, verdict=verdict,
                key_expr=kexpr, iv_expr=iexpr,
                key_struct=kstruct, iv_struct=istruct,
                key_comment=kcom, iv_comment=icom, trap=trap,
                password=rng.choice(PASSWORDS),
            ))
    return specs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=1337)
    ap.add_argument("--out", default=".")
    args = ap.parse_args()

    out = Path(args.out)
    cases_dir = out / "cases"
    cases_dir.mkdir(parents=True, exist_ok=True)
    for old in cases_dir.glob("c*.py"):
        old.unlink()

    labels = []
    for spec in build_specs(args.seed):
        source = render(spec, spec["password"])
        ast.parse(source)  # every case must be valid Python
        rel = f"cases/{spec['id']}.py"
        (out / rel).write_text(source)
        labels.append(dict(
            id=spec["id"], file=rel, lib=spec["lib"], mode=spec["mode"],
            key_source=spec["key_source"], iv_source=spec["iv_source"],
            verdict=spec["verdict"], key_struct=spec["key_struct"],
            iv_struct=spec["iv_struct"],
            hops_max=max(HOPS[spec["key_struct"]], HOPS[spec["iv_struct"]]),
            trap=spec["trap"],
        ))

    with open(out / "cases.jsonl", "w") as f:
        for row in labels:
            f.write(json.dumps(row) + "\n")
    print(f"wrote {len(labels)} cases to {cases_dir} and labels to {out / 'cases.jsonl'}")


if __name__ == "__main__":
    main()
