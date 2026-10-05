"""List the responses a model got wrong, with the ground truth next to them.

    python list_errors.py results/claude-haiku-4-5-20251001_raw.jsonl
    python list_errors.py results/claude-haiku-4-5-20251001_raw.jsonl --show 3

--show N also prints the case code and the model's raw answer for the first N errors.
"""
import argparse
import collections
import json
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("results")
    ap.add_argument("--show", type=int, default=0,
                    help="print the case code and raw model answer for the first N errors")
    args = ap.parse_args()

    truth = {r["id"]: r for r in map(json.loads, open("cases.jsonl"))}
    errors, total = [], 0
    for line in open(args.results):
        rec = json.loads(line)
        total += 1
        t, p = truth[rec["id"]], rec.get("parsed")
        want = (t["key_source"], t["iv_source"], t["verdict"])
        got = (p.get("key_source"), p.get("iv_source"), p.get("verdict")) if p else None
        if got != want:
            errors.append((rec, t, p, got, want))

    print(f"{len(errors)} of {total} responses differ from the ground truth\n")
    kinds = collections.Counter()
    for i, (rec, t, p, got, want) in enumerate(errors):
        if got is None:
            wrong = ["unparsed"]
        else:
            wrong = [name for name, g, w in zip(("key_source", "iv_source", "VERDICT"), got, want) if g != w]
        kinds.update(wrong)
        model_txt = "unparsed" if got is None else f"key={got[0]} iv={got[1]} verdict={got[2]}"
        conf = p.get("confidence") if p else None
        print(f"{rec['id']} run {rec['run']}   wrong: {', '.join(wrong)}")
        print(f"   truth: key={want[0]} iv={want[1]} verdict={want[2]}   "
              f"({t['lib']} {t['mode']}, hops={t['hops_max']}, trap={t['trap']})")
        print(f"   model: {model_txt}   confidence={conf}")
        if i < args.show:
            print("   --- code ---")
            for ln in Path(t["file"]).read_text().splitlines():
                print("   " + ln)
            print("   --- model answer ---")
            print("   " + str(rec.get("raw")))
        print()
    if errors:
        print("by kind of error:", dict(kinds))


if __name__ == "__main__":
    main()
