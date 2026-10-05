# Key/IV Provenance Benchmark

A small benchmark of 100 synthetic Python snippets that call AES. Each snippet is
labeled, by construction, with where the **key** and the **IV/nonce** come from. The
question for a model (or tool) is simple to state and easy to get wrong:

> Trace the key and the IV/nonce back to where they originate, then say whether
> those origins are safe.

The benchmark compares models against a deterministic static tracer (`trace.py`) and
measures accuracy, the dangerous error of calling unsafe code safe, consistency across
repeated runs, and whether stated confidence tracks correctness.

## Why this task

- LLM confidence is not the same as correctness, especially on security questions, so
  the ground truth here comes from construction and a deterministic check, never from
  a model grader.
- Backward tracing from a sink to its sources is a core static-analysis idea. Giving a
  model a structured trace (the `trace` condition) tests whether structured context
  beats raw code.
- "Cannot determine" is a legitimate answer. A value read from an environment
  variable is not knowable from the code, and a model that confidently calls it safe
  or unsafe is miscalibrated.

## Quick start

```bash
python generate_cases.py              # regenerate cases/ and cases.jsonl (seeded, reproducible)
python trace.py --check               # tracer vs. labels: expect 100/100
python run_eval.py --provider baseline-keyword
python run_eval.py --provider anthropic --model claude-haiku-4-5-20251001 --limit 10
python score.py results/*.jsonl --slices
```

The baselines need nothing installed. For the `anthropic` provider:

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=...          # keep it out of the repo
```

An API key comes from a Claude Console account. It is billed separately from a Claude
chat subscription. Start with `--limit 10`, check the cost, then scale up
(`--runs 5` repeats each case for the consistency metric). Adding another provider
means writing one function, `(prompt, code) -> text`, and registering it in
`make_caller()` in `run_eval.py`.

## What the cases look like

100 cases, balanced on purpose so that always answering "unsafe" scores 40%:

| Dimension | Values |
|---|---|
| Verdict | 30 safe, 30 cannot_determine, 40 unsafe |
| Key / IV source | csprng, hardcoded, weak_derivation, predictable, external |
| Hops from sink to origin | 0 (inline), 1 (variable or class attribute), 2 (variable chain or helper function) |
| Library and mode | `cryptography` (Cipher: CBC, CTR, GCM; AESGCM) and PyCryptodome (CBC, CTR, GCM) |
| Misleading naming | about 1 in 4 cases use names and comments that claim the opposite of the truth |

Example (`c066`, unsafe): a hardcoded key reached through a helper function, plus a
nonce derived from a password with an unsalted hash.

```python
def _make_key():
    return b"A" * 16

key = _make_key()

def encrypt(data: bytes) -> bytes:
    nonce = hashlib.md5(PASSWORD.encode()).digest()[:12]
    encryptor = Cipher(algorithms.AES(key), modes.GCM(nonce)).encryptor()
    return encryptor.update(data) + encryptor.finalize()
```

Example of a misleading case (`c084`, unsafe): the comments and names say "secure
random", but the key is an unsalted hash of a password and the nonce comes from
Python's non-cryptographic `random` module.

```python
# cryptographically secure random key
secure_random_key = hashlib.sha256(PASSWORD.encode()).digest()

def encrypt(data: bytes) -> bytes:
    # fresh random value for every message
    random_nonce_bytes = random.randbytes(12)
    fresh_random_nonce = random_nonce_bytes
    cipher = AES.new(secure_random_key, AES.MODE_GCM, nonce=fresh_random_nonce)
    return cipher.encrypt(data)
```

## Labeling rules

Labels come from the templates in `generate_cases.py`, not from a model. The rule is in
`common.py`:

- **unsafe**: the key or the IV/nonce comes from `hardcoded`, `weak_derivation`, or `predictable`
- **cannot_determine**: nothing is unsafe, but at least one value is `external`
- **safe**: both come from `csprng`

Source categories: `csprng` (`os.urandom`, `secrets`, `AESGCM.generate_key`), `hardcoded`
(constants, `bytes(n)`, `bytes.fromhex("...")`), `weak_derivation` (a plain hash of a
password with no salt and no KDF), `predictable` (the `random` module, timestamps),
`external` (environment variable, file, function parameter).

Modeling assumptions: the key is long-lived and reused across messages, and the
IV/nonce is computed on each call. Under that assumption a hardcoded IV or nonce is
always unsafe. Real cryptographic policy has more nuance (see Limitations).

## Conditions

- `raw` (default): the model sees only the code.
- `trace`: the model also sees a deterministic trace, meaning the assignment chain from
  the encryption call back to the originating expression for the key and the IV,
  without the classification. It still has to judge.
- `--warn-names`: an ablation that adds "base your answer on what the code does, not on
  variable names or comments". Compare it with the default to measure susceptibility to
  misleading names.

## Metrics

`score.py` prints one row per results file:

- **verdict / key / iv**: exact-match accuracy (a response that fails to parse counts as wrong)
- **missed unsafe**: truth is unsafe, the model said safe (the dangerous error)
- **false alarm**: truth is safe, the model said unsafe
- **abstain recall**: truth is cannot_determine and the model said so
- **over-abstain**: the model said cannot_determine when the code is decidable
- **consistency**: share of cases where every repeated run gave the same verdict
- **majority acc**: accuracy of the majority-vote verdict across repeated runs
- **ECE**: expected calibration error of stated confidence against verdict correctness

`--slices` adds accuracy by misleading/plain, hop count, library, mode, and true verdict,
plus a confidence-bucket table.

## Reference baselines (no API)

| Baseline | Verdict accuracy | Misleading cases | Missed unsafe |
|---|---|---|---|
| Always "unsafe" | 40% | 42% | 0% |
| Keyword heuristic (`baseline-keyword`) | 39% | 0% | 70% |
| Deterministic tracer (`baseline-tracer`) | 100% | 100% | 0% |

The keyword heuristic reads names and comments instead of data flow, and the
misleading cases fool it completely, which shows the traps do their job. The tracer's
100% is a consistency check between two separate code paths (templates in the
generator, AST analysis in the tracer) written by the same author for the same
patterns. It is not evidence that it works on real-world code.

## Results

Model results go here after you run them. Record the model name, condition, number of
runs, date, and the `score.py` table.

## Limitations

- Synthetic, short, single-file, Python only, three AES libraries, 100 cases. Treat
  differences of a few points as noise.
- The labels encode a stated policy. For example, a static nonce with a key that is used
  exactly once is acceptable in principle, and counter-based nonces are legitimate for
  CTR and GCM. The cases avoid those ambiguities on purpose, which also makes them less
  realistic.
- Misleading naming is one kind of trap. Other adversarial patterns (dead code,
  reassignment, conditional branches, shadowing) are not covered.
- Self-reported confidence is measured on small buckets, so the calibration numbers are
  coarse.
- Results depend on the prompt wording in `run_eval.py`. Check robustness by changing
  the prompt.

## Roadmap

- Cross-file cases (key defined in one module, used in another)
- Other languages (Java, Go, C) and snippets drawn from real open-source code with
  manually verified labels
- A patch task: a model proposes a fix, and a deterministic check confirms the issue is
  gone and behavior is preserved
- More vulnerability classes (hardcoded secrets, path traversal), confidence intervals,
  and multiple prompt variants

## Notes

All code in `cases/` is synthetic. The repo contains no employer, customer, or
proprietary code. Add a license file of your choice before publishing.
