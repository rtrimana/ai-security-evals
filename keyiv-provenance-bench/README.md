# Results

Last updated: 2026-10-05

Status: the reference baselines are complete (n = 100). One **preliminary smoke test**
with Claude Haiku 4.5 on a 12-case subset is included below. Full model runs are pending.

## Reference baselines (no API, n = 100)

| Baseline | Verdict | Key | IV | Missed unsafe | False alarm | Abstain recall | Misleading cases |
|---|---|---|---|---|---|---|---|
| Always "unsafe" | 40% | n/a | n/a | 0% | 100% | 0% | 42% |
| Keyword heuristic | 39% | 52% | 50% | 70% | 23% | 23% | 0% |
| Deterministic tracer | 100% | 100% | 100% | 0% | 0% | 100% | 100% |

- The set cannot be gamed by always answering "unsafe" (40%).
- A heuristic that reads names and comments instead of data flow scores 0% on the
  misleading cases and misses 70% of unsafe code, which is what those cases are built
  to catch.
- The tracer's 100% is a consistency check between two separate code paths (the
  generator's templates and AST analysis) written by the same author for the same
  patterns. It is not evidence that it works on real-world code.

## Preliminary: Claude Haiku 4.5 smoke test

This is a pipeline check on a small subset, not a benchmark result.

| Setting | Value |
|---|---|
| Model | `claude-haiku-4-5-20251001` |
| Condition | `raw` (code only), default prompt (no instruction to ignore names or comments) |
| Temperature | not set (provider default) |
| Cases | 12, a class-balanced seeded subset (`--limit 12`): 4 safe, 4 cannot_determine, 4 unsafe; 5 misleading |
| Runs per case | 3 (36 records) |
| Case IDs | c004, c011, c018, c019, c034, c035, c040, c043, c068, c069, c072, c084 |
| Commit | add the git commit hash here |

| Verdict | Key | IV | Missed unsafe | False alarm | Abstain recall | Over-abstain | Consistency | Majority acc | ECE |
|---|---|---|---|---|---|---|---|---|---|
| 100% | 100% | 100% | 0% | 0% | 100% | 0% | 100% | 100% | 0.04 |

Verdict accuracy by slice: 100% in every slice (misleading and plain cases; 0, 1, and
2 hops; all three libraries and modes; all three true verdicts).

What it shows:

- With the default prompt, Haiku classified every key and IV correctly, including the
  five misleading cases, where the keyword heuristic scores 0%.
- Its answers were identical across the three runs of every case.
- All 36 responses parsed.

What it does not show:

- **Sample size.** With 12 cases, a perfect score is consistent with a true accuracy
  as low as roughly 74% (95% interval at the case level). The three runs of a case are
  not independent, so 36 records is not 36 cases.
- **Calibration.** An ECE of 0.04 only reflects that a confident model was right every
  time. It means little until there are errors to calibrate against.
- **Discrimination.** If models score near 100% on the full set, this version of the
  benchmark is saturated and cannot separate models or conditions.

## Full runs (pending)

| Date | Model | Condition | Cases | Runs | Verdict | Missed unsafe | Abstain recall | Consistency | ECE |
|---|---|---|---|---|---|---|---|---|---|
| | | raw | 100 | 3 | | | | | |
| | | trace | 100 | 3 | | | | | |
| | | raw, `--warn-names` | 100 | 3 | | | | | |

Plan: run `raw` on all 100 cases first. If errors appear, run `trace` and
`--warn-names` to test whether structured context helps and how much misleading names
and comments matter. If the model is near 100%, the set is saturated and the next step
is a harder v2 (dead code, reassignment, conditional branches, wrappers, cross-file
keys, a CSPRNG value generated once and reused).

## Reproduce

```bash
python generate_cases.py
python trace.py --check
python run_eval.py --provider baseline-keyword
python run_eval.py --provider baseline-tracer
python run_eval.py --provider anthropic --model claude-haiku-4-5-20251001 --limit 12 --runs 3
python score.py results/*.jsonl --slices
```

`--limit` takes a class-balanced subset with a fixed seed, so the 12 cases above are
the same on every machine.

## Reading the numbers

- With n = 100, accuracy near 80% carries roughly +/- 8 points of sampling noise.
  Treat smaller differences between models or conditions as noise.
- Check **missed unsafe** (calling unsafe code safe) and **abstain recall** (saying
  "cannot determine" when the code really is undecidable) before accuracy.
- Consistency and majority accuracy need at least 2 runs per case.
- Calibration buckets are small, so ECE is coarse.
- Do not report a run made with `--limit` as a result. It is a smoke test.

See the Limitations section of the README for what this benchmark does not cover.
