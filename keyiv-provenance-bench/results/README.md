# Results

Last updated: 2026-10-05

Status: the reference baselines and a first full run with Claude Haiku 4.5 (100 cases,
3 runs each) are complete, with an error analysis. The `trace` and `--warn-names`
comparisons have not been run. Error analysis found two ambiguous labels (see "Label
issues found"); a corrected v1.1 is planned and will change the numbers.

## Summary

Claude Haiku 4.5 nearly saturates this version of the benchmark. With the default
prompt it scores 99-100% on every metric, including the cases with misleading names and
comments, where a keyword heuristic scores 0%. The four wrong responses come from two
cases, and both trace in part to ambiguity in my labeling policy, not only to model
error. This version cannot separate the model from a perfect score, so the next steps
are fixing the labels (v1.1) and then a harder set (v2).

## Results (100 cases)

| Run | Records | Verdict | Key | IV | Missed unsafe | False alarm | Abstain recall | Over-abstain | Consistency | Majority acc | ECE |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Keyword heuristic | 100 | 39% | 52% | 50% | 70% | 23% | 23% | 4% | n/a | n/a | 0.51 |
| Deterministic tracer | 100 | 100% | 100% | 100% | 0% | 0% | 100% | 0% | n/a | n/a | 0.00 |
| Claude Haiku 4.5 (`raw`) | 300 | 100% | 100% | 99% | 0% | 0% | 99% | 0% | 99% | 100% | 0.04 |

Percentages are rounded. Haiku's verdict accuracy is 299 of 300 responses, and its IV
label accuracy is 296 of 300. Always answering "unsafe" scores 40% (it makes no key or
IV claims, so those columns do not apply). The tracer's 100% is a consistency check
between two separate code paths (the generator's templates and AST analysis) written by
the same author for the same patterns. It is not evidence that it works on real-world
code.

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
  verdict (1 of 300 responses) was on a `cannot_determine` case, and it depends on a
  labeling choice discussed below.
- **Misleading names did not fool it.** Without being told to ignore names and
  comments, Haiku scored 99% on the misleading cases. The keyword heuristic scores 0%
  on them.
- **Stable answers.** One case had runs that disagreed. The majority-vote verdict was
  correct on all 100 cases.
- **Key labels were more accurate than IV labels** (100% vs. 99%). All four wrong
  labels were IV labels.

## Wrong responses (4 of 300)

| Case | Runs wrong | Truth (key / IV / verdict) | Model answer | Confidence |
|---|---|---|---|---|
| c042 (PyCryptodome GCM, 2 hops, misleading) | 1 of 3 | external / external / cannot_determine | IV `hardcoded`, verdict `unsafe` | 0.95 |
| c089 (PyCryptodome CBC, 1 hop, plain) | 3 of 3 | predictable / weak_derivation / unsafe | IV `hardcoded`, verdict `unsafe` (correct) | 0.95 |

- **c042.** A comment claims the nonce is "fresh random," but it is read from a fixed
  file path. In two of three runs Haiku answered `external` and `cannot_determine`, as
  labeled. In the third it called the nonce `hardcoded` and the verdict `unsafe`. The
  model was asked for JSON only, so its reasoning is not recorded. That answer is
  defensible, since a nonce read from a fixed file is the same for every message.
- **c089.** The IV is an unsalted MD5 of a password that is a literal in the code. It
  is labeled `weak_derivation`. Haiku called it `hardcoded` on all three runs. The
  verdict was still correct. Since the password is a literal, "hardcoded" is also a
  fair description.
- Both wrong answers were stated with confidence 0.95, the same as most correct ones,
  so the stated confidence carried no signal here.

## Label issues found

1. **External IVs read from a file or environment variable (16 of 100 cases).** The
   benchmark assumes the IV is computed on each call. A value read from a fixed file
   or environment variable is the same for every message, which is static and unsafe.
   Only a caller-supplied parameter is truly undecidable. Thirteen of the 16 cases are
   labeled `cannot_determine`, and Haiku answered `cannot_determine` on 38 of those 39
   records. If those cases were relabeled `unsafe`, its score would fall, not rise, so
   the headline number depends on this policy choice. The prompt also defines
   environment variable and file as `external`, so Haiku was mostly following the
   rubric as written.
2. **`weak_derivation` versus `hardcoded` (18 cases).** Every weak-derivation key or
   IV hashes a password that is a literal in the code, so both labels apply. Haiku
   differed from the label on one of these cases (c089, three runs), and matched on
   the others.

## Other limitations of this reading

- **Heavily scaffolded task.** The prompt spells out the five source categories and the
  verdict rules, so the model is not asked to discover them.
- **Sample size.** Majority-vote accuracy of 100 of 100 cases is consistent with a true
  case-level accuracy as low as about 96% (95% interval). The three runs of a case are
  not independent, so 300 records is not 300 cases.
- **Calibration cannot be assessed.** All 300 stated confidences fell in the 0.9-1.0
  bucket, so there is no spread to compare against accuracy.
- **Synthetic, standard-library patterns** that models may have seen in public code.
- **One model.**

## Not run yet

- `--condition trace` and `--warn-names`. At 99-100% there is almost no headroom to
  measure whether structured context or a warning about names helps.
- Other models. The model is a flag (`--model`), so this is a one-line change.

## Next

1. **v1.1, fix the labels.** Generate external IVs only as caller-supplied parameters,
   and take weak-derivation passwords from an environment variable instead of a
   literal. This regenerates the cases, so the numbers above stay valid for v1 (tag the
   commit `v1.0`) and v1.1 needs its own run.
2. **v2, harder cases.** Dead code, reassignment, conditional branches, wrappers and
   re-exports, cross-file keys, a CSPRNG value generated once and reused across
   messages, and sources that look safe but are not (for example a seeded generator).
3. Then run `trace` and `--warn-names` on a set where the model makes errors.

## Reproduce

```bash
python generate_cases.py
python trace.py --check
python run_eval.py --provider baseline-keyword
python run_eval.py --provider baseline-tracer
python run_eval.py --provider anthropic --model claude-haiku-4-5-20251001 --runs 3
python score.py results/*.jsonl --slices
python list_errors.py results/claude-haiku-4-5-20251001_raw.jsonl --show 3
```

`--limit N` runs a class-balanced subset with a fixed seed. It is a smoke test, not a
result.

See the Limitations section of the README for what this benchmark does not cover.
