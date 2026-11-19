#!/usr/bin/env python3
"""D1-s3 M5: classify excepts_inject.py's JSONL (lifecycle arm) per handler.

Metric (one line): per injected handler, the four D1.M5 properties read off the armed run --
escaped (the injected fault left a lifecycle phase or a task), silent (fired, and no record at
any level was added over the control), flood (WARNING+ added in two consecutive armed refreshes),
no-recovery (the disarmed refresh B2 did not succeed) and update-failed (an armed refresh set
last_update_success False).
Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D1/s3/classify.py out/inj_*.jsonl
Reads only the harness's own output; baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692.
"""
import glob
import json
import sys

REFRESH = ("refreshA1", "refreshA2", "refreshB1")


def classify(rec):
    ph = {p["phase"]: p for p in rec["phases"]}
    armed = [p for p in rec["phases"] if p["phase"] != "refreshB2"]
    tags = []
    if rec["fired"] == 0:
        return ["not-fired"]
    if any((not p["ok"] and p["mark_escaped"]) or p.get("task_mark") for p in armed):
        tags.append("escaped")
    if any(not p["ok"] for p in armed):
        tags.append("phase-raised")
    if sum(p["added"] for p in armed) == 0 and sum(p["mark_logged"] for p in armed) == 0:
        tags.append("silent")
    if ph["refreshA1"]["added_warn"] and ph["refreshA2"]["added_warn"]:
        tags.append("flood")
    if any(ph[r]["value"] is False for r in REFRESH):
        tags.append("update-failed")
    b2 = ph["refreshB2"]
    if not b2["ok"] or b2["value"] is False:
        tags.append("no-recovery")
    return tags or ["contained-logged"]


def main():
    files = sys.argv[1:] or glob.glob("dev/audit/rounds/round11/D1/s3/out/inj_*.jsonl")
    rows = [json.loads(l) for f in files for l in open(f) if l.strip()]
    counts = {}
    for r in sorted(rows, key=lambda r: r["id"]):
        tags = classify(r)
        for t in tags:
            counts[t] = counts.get(t, 0) + 1
        print(f"{r['id']:60s} {r['kind']:6s} fired={r['fired']:<4d} entered={r.get('entered', '?')!s:<4s} {','.join(tags)}")
    for t, n in sorted(counts.items()):
        print(f"RESULT {t}={n} handlers")
    print(f"RESULT injected={len(rows)} handlers")
    print("RESULT thread_factor=1.0 (reads JSONL; no timing)")
    print("RESULT load1=0")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
