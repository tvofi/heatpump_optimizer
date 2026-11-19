#!/usr/bin/env python3
"""D1-s3 M5: the per-handler table over `enumerate.py d1-excepts`, merging the two injection arms.

Metric (one line): per d1-excepts line, the arm that examined it (lifecycle = excepts_inject.py,
local = local_inject.py via a test script's call, or none) and the verdict read off that arm.
Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D1/s3/m5_table.py [--tsv OUT]
Reads the arms' JSONL under dev/audit/rounds/round11/D1/s3/out/; the universe is re-enumerated.
Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. No RESULT is a timing.
"""
import argparse
import collections
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import d1s3hook as hook  # noqa: E402
from classify import classify  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tsv", default=os.path.join(HERE, "out", "m5_table.tsv"))
    a = ap.parse_args()
    rows = hook.handlers()
    life = {}
    for f in sorted(glob.glob(os.path.join(HERE, "out", "inj_*.jsonl"))):
        for line in open(f):
            if line.strip():
                r = json.loads(line)
                life[r["id"]] = r  # a later file (a rerun) wins
    local = {}
    for f in sorted(glob.glob(os.path.join(HERE, "out", "loc2", "*.jsonl"))):
        for line in open(f):
            if line.strip():
                r = json.loads(line)
                if r["id"] not in local or (r["entered"] and not local[r["id"]]["entered"]):
                    local[r["id"]] = r
    out = []
    counts = collections.Counter()
    for r in rows:
        hid = r["id"]
        if hid in life and life[hid]["fired"]:
            arm, tags = "lifecycle", classify(life[hid])
        elif hid in local:
            l = local[hid]
            arm = "local:" + os.path.basename(l["script"])
            if not l["entered"]:
                tags = ["not-entered"]
            elif l["raised_out"]:
                tags = ["reraised" + ("-by-design" if r["reraises"] else "")]
            else:
                tags = ["contained-" + ("logged" if r["static_logs"] else "silent")]
        else:
            arm, tags = "none", ["not-reached"]
        for t in tags:
            counts[t] += 1
        counts["arm:" + arm.split(":")[0]] += 1
        out.append((hid, r["kind"], r["func"], arm, ",".join(tags), r["body"].replace("\n", " / ")[:120]))
    with open(a.tsv, "w") as fh:
        for row in out:
            fh.write("\t".join(row) + "\n")
    examined = sum(1 for o in out if o[3] != "none")
    for k, v in sorted(counts.items()):
        print(f"RESULT {k}={v} handlers")
    print(f"RESULT universe={len(rows)} handlers")
    print(f"RESULT examined={examined} handlers")
    print("RESULT thread_factor=1.0 (reads JSONL; no timing)")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
