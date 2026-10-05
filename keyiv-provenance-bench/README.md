# Results

Last updated: 2026-10-05

Status: the reference baselines and a first full run with Claude Haiku 4.5 (100 cases,
3 runs each) are complete. The `trace` and `--warn-names` comparisons have not been run.

## Summary

Claude Haiku 4.5 nearly saturates this version of the benchmark. With the default
prompt it scores 99-100% on every metric, including the cases with misleading names and
comments, where a keyword heuristic scores 0%. This version cannot separate the model
from a perfect score, so the next step is a harder v2, not more runs of v1.

## Results (100 cases)

| Run | Records | Verdict | Key | IV | Missed unsafe | False alarm | Abstain recall | Over-abstain | Consistency | Majority acc | ECE |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Keyword heuristic | 100 | 39% | 52% | 50% | 70% | 23% | 23% | 4% | n/a | n/a | 0.51 |
| Deterministic tracer | 100 | 100% | 100% | 100% | 0% | 0% | 100% | 0% | n/a | n/a | 0.00 |
| Claude Haiku 4.5 (`raw`) | 300 | 100% | 100% | 99% | 0% | 0% | 99% | 0% | 99% | 100% | 0.04 |

Percentages are rounded. Haiku's verdict accuracy is 299 of 300 responses. Always
answering "unsafe" scores 40% (it makes no key or IV claims, so those columns do not
apply). The tracer's 100% is a consistency check between two separate code paths (the
generator's templates and AST analysis) written by the same author for the same
patterns. It is not evidence that it works on real-world code.

## Setup for the Haiku run

| Setting | Value |
|---|---|
| Model | `claude-haiku-4-5-20251001` |
| Condition | `raw` (code only), default prompt (no instruction to ignore names or comments) |
| Temperature | not set (provider default) |
| Cases and runs | 100 cases, 3 runs each (300 records) |
| Parse rate | 100% |
| Date | 2026-10-05 |
| Commit | add the git commit hash here |

## Haiku accuracy by slice (verdict)

| Slice | Accuracy |
|---|---|
| Plain cases (76) | 100% |
| Misleading names and comments (24) | 99% |
| 0 hops (35) / 1 hop (33) / 2 hops (32) | 100% / 100% / 99% |
| `cryptography` (44) / AESGCM (14) / PyCryptodome (42) | 100% / 100% / 99% |
| CBC (29) / CTR (29) / GCM (42) | 100% / 100% / 99% |
| True verdict: safe (30) / unsafe (40) / cannot_determine (30) | 100% / 100% / 99% |

## What the results show

- **No dangerous errors.** Missed unsafe and false alarm are both 0%. The only wrong
  verdict (1 of 300 responses) was on a `cannot_determine` case.
- **Misleading names did not fool it.** Without being told to ignore names and
  comments, Haiku scored 99% on the misleading cases. The keyword heuristic scores 0%
  on them.
- **Stable answers.** One case had runs that disagreed. The majority-vote verdict was
  correct on all 100 cases.
- **Key labels were slightly more accurate than IV labels** (100% vs. 99%).

## What they do not show

- **The task is heavily scaffolded.** The prompt spells out the five source categories
  and the verdict rules. The model is not asked to discover them, which makes the task
  easier than an open-ended code review.
- **Sample size.** Majority-vote accuracy of 100 of 100 cases is consistent with a true
  case-level accuracy as low as about 96% (95% interval). The three runs of a case are
  not independent, so 300 records is not 300 cases.
- **Calibration cannot be assessed.** All 300 stated confidences fell in the 0.9-1.0
  bucket, so there is no spread to compare against accuracy. The one wrong verdict was
  also stated with confidence of at least 0.9, but a single error is an anecdote, not a
  calibration result.
- **Synthetic, standard-library patterns.** `os.urandom`, `secrets`, and AES library
  calls are common in public code, so models may have seen similar patterns.
- **One model.** Nothing here compares models.

## Wrong responses

Not yet written up. List them with the ground truth next to each:

```bash
python list_errors.py results/claude-haiku-4-5-20251001_raw.jsonl --show 3
```

The summary above says the single wrong verdict was on a `cannot_determine` case. The
write-up of which case and why belongs here once it has been read.

## Not run yet

- `--condition trace` and `--warn-names`. At 99-100% there is almost no headroom to
  measure whether structured context or a warning about names helps. They become
  informative on a harder set.
- Other models. The model is a flag (`--model`), so a larger or smaller model is a
  one-line change.

## Next: a harder v2

Dead code, reassignment, conditional branches, wrappers and re-exports, cross-file
keys, a CSPRNG value generated once and reused across messages, and sources that look
safe but are not (for example a seeded generator). The goal is a set where a strong
model makes errors, so that the `trace` and `--warn-names` comparisons mean something.

## Reproduce

```bash
python generate_cases.py
python trace.py --check
python run_eval.py --provider baseline-keyword
python run_eval.py --provider baseline-tracer
python run_eval.py --provider anthropic --model claude-haiku-4-5-20251001 --runs 3
python score.py results/*.jsonl --slices
```

`--limit N` runs a class-balanced subset with a fixed seed. It is a smoke test, not a
result.

See the Limitations section of the README for what this benchmark does not cover.
