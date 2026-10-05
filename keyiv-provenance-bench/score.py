"""Score one or more results files against cases.jsonl. No model is used for grading.

    python score.py results/*.jsonl
    python score.py results/claude-haiku-4-5-20251001_raw.jsonl --slices

Metrics
  verdict / key / iv accuracy   exact match with the ground truth (parse failures count as wrong)
  missed unsafe                 truth = unsafe but the model said safe (the dangerous error)
  false alarm                   truth = safe but the model said unsafe
  abstain recall                truth = cannot_determine and the model said so
  over-abstain                  truth is safe/unsafe but the model said cannot_determine
  consistency                   share of cases where every repeated run gave the same verdict
  majority acc                  accuracy of the majority-vote verdict across repeated runs
  ECE                           expected calibration error of the stated confidence vs. verdict correctness
"""
import argparse
import collections
import json
from pathlib import Path

BUCKETS = [(0.0, 0.5), (0.5, 0.7), (0.7, 0.9), (0.9, 1.0001)]


def load_results(path):
    return [json.loads(line) for line in open(path)]


def pct(num, den):
    return None if den == 0 else num / den


def fmt(x):
    return "n/a" if x is None else f"{100 * x:.0f}%"


def evaluate(records, truth):
    n = len(records)
    parsed_ok = sum(1 for r in records if r.get("parsed"))
    per = []
    for r in records:
        t = truth[r["id"]]
        p = r.get("parsed") or {}
        per.append(dict(
            id=r["id"], truth=t, pred=p.get("verdict"),
            verdict_ok=p.get("verdict") == t["verdict"],
            key_ok=p.get("key_source") == t["key_source"],
            iv_ok=p.get("iv_source") == t["iv_source"],
            conf=p.get("confidence"),
        ))

    def rate(rows, field):
        return pct(sum(1 for x in rows if x[field]), len(rows))

    unsafe = [x for x in per if x["truth"]["verdict"] == "unsafe"]
    safe = [x for x in per if x["truth"]["verdict"] == "safe"]
    unknown = [x for x in per if x["truth"]["verdict"] == "cannot_determine"]
    decided = unsafe + safe

    by_case = collections.defaultdict(list)
    for x in per:
        by_case[x["id"]].append(x)
    multi = {k: v for k, v in by_case.items() if len(v) > 1}
    consistency = pct(sum(1 for v in multi.values() if len({x["pred"] for x in v}) == 1), len(multi))
    majority = None
    if multi:
        correct = 0
        for v in multi.values():
            top = collections.Counter(x["pred"] for x in v).most_common(1)[0][0]
            correct += top == v[0]["truth"]["verdict"]
        majority = correct / len(multi)

    # calibration of stated confidence vs. verdict correctness
    with_conf = [x for x in per if x["conf"] is not None]
    cal, ece = [], None
    if with_conf:
        ece = 0.0
        for lo, hi in BUCKETS:
            rows = [x for x in with_conf if lo <= x["conf"] < hi]
            if rows:
                acc = sum(x["verdict_ok"] for x in rows) / len(rows)
                mean_conf = sum(x["conf"] for x in rows) / len(rows)
                ece += abs(acc - mean_conf) * len(rows) / len(with_conf)
                cal.append(dict(bucket=f"{lo:.1f}-{min(hi, 1.0):.1f}", n=len(rows),
                                mean_conf=round(mean_conf, 3), accuracy=round(acc, 3)))

    summary = dict(
        n=n, parse_rate=pct(parsed_ok, n),
        verdict_acc=rate(per, "verdict_ok"), key_acc=rate(per, "key_ok"), iv_acc=rate(per, "iv_ok"),
        missed_unsafe=pct(sum(1 for x in unsafe if x["pred"] == "safe"), len(unsafe)),
        false_alarm=pct(sum(1 for x in safe if x["pred"] == "unsafe"), len(safe)),
        abstain_recall=pct(sum(1 for x in unknown if x["pred"] == "cannot_determine"), len(unknown)),
        over_abstain=pct(sum(1 for x in decided if x["pred"] == "cannot_determine"), len(decided)),
        consistency=consistency, majority_acc=majority, ece=ece, calibration=cal,
    )

    slices = {}
    for field in ("trap", "hops_max", "lib", "mode"):
        slices[field] = {}
        for value in sorted({x["truth"][field] for x in per}, key=str):
            rows = [x for x in per if x["truth"][field] == value]
            slices[field][str(value)] = rate(rows, "verdict_ok")
    slices["truth_verdict"] = {}
    for value in ("safe", "unsafe", "cannot_determine"):
        rows = [x for x in per if x["truth"]["verdict"] == value]
        slices["truth_verdict"][value] = rate(rows, "verdict_ok")
    return summary, slices


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("results", nargs="+")
    ap.add_argument("--slices", action="store_true", help="also print accuracy by slice")
    ap.add_argument("--json", default="results/summary.json")
    args = ap.parse_args()

    truth = {r["id"]: r for r in map(json.loads, open("cases.jsonl"))}
    all_summaries, all_slices = {}, {}
    for path in args.results:
        if Path(path).name == "summary.json":
            continue
        s, sl = evaluate(load_results(path), truth)
        all_summaries[path], all_slices[path] = s, sl

    cols = [("verdict_acc", "verdict"), ("key_acc", "key"), ("iv_acc", "iv"),
            ("missed_unsafe", "missed unsafe"), ("false_alarm", "false alarm"),
            ("abstain_recall", "abstain recall"), ("over_abstain", "over-abstain"),
            ("consistency", "consistency"), ("majority_acc", "majority acc")]
    print("| results file | n | " + " | ".join(c[1] for c in cols) + " | ECE |")
    print("|---|---|" + "---|" * (len(cols) + 1))
    for path, s in all_summaries.items():
        ece = "n/a" if s["ece"] is None else f"{s['ece']:.2f}"
        print(f"| {Path(path).name} | {s['n']} | " + " | ".join(fmt(s[c[0]]) for c in cols) + f" | {ece} |")

    if args.slices:
        for path, sl in all_slices.items():
            print(f"\n{Path(path).name}: verdict accuracy by slice")
            for field, vals in sl.items():
                print(f"  {field}: " + ", ".join(f"{k}={fmt(v)}" for k, v in vals.items()))
            cal = all_summaries[path]["calibration"]
            if cal:
                print("  calibration (confidence bucket -> accuracy): " +
                      ", ".join(f"{c['bucket']}: {fmt(c['accuracy'])} (n={c['n']})" for c in cal))

    Path(args.json).parent.mkdir(parents=True, exist_ok=True)
    with open(args.json, "w") as f:
        json.dump({"summaries": all_summaries, "slices": all_slices}, f, indent=2)


if __name__ == "__main__":
    main()
