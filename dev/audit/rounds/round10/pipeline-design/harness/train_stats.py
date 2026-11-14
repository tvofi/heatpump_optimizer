#!/usr/bin/env python3
"""Baseline step 5: train batches, skips, serial routings, refused merges, proofs (merge_throughput.train_batches)."""
import os as _os
_HERE = _os.path.dirname(_os.path.abspath(__file__))
PD_DATA = _os.environ.get("PD_DATA", _os.path.join(_HERE, "..", "data")) + "/"
PD_REPO = _os.environ.get("PD_REPO", _os.path.abspath(_os.path.join(_HERE, "..", "..", "..", "..", "..", "..")))
PD_STATE = _os.environ.get("PD_STATE", _os.path.expanduser("~/.local/state/hpo"))
import sys, collections, re
sys.path.insert(0, sys.argv[1] + "/tools/audit")
import merge_throughput as mt
for name, p in (("state-dir train.log", _os.path.join(_os.environ.get("HPO_STATE_DIR", PD_STATE), "train.log")), ("default-state train.log", _os.path.join(PD_STATE, "merge_train", "train.log"))):
    text = open(p, errors="replace").read(); lines = text.splitlines()
    bs = mt.train_batches(text)
    print("==", name, "batches", len(bs), "from", bs[0]["at"], "to", bs[-1]["at"])
    sizes = [b["queue"] for b in bs]; skips = [len(b["skips"]) for b in bs]
    print("   queue size hist", sorted(collections.Counter(sizes).items()), "mean", round(sum(sizes) / len(sizes), 2))
    print("   entries", sum(sizes), "skips", sum(skips), "skip share", round(sum(skips) / max(1, sum(sizes)), 3))
    rc = collections.Counter(str(s.get("reason") if isinstance(s, dict) else s) for b in bs for s in b["skips"])
    print("   skip reasons", rc.most_common(12))
    for key in ("MERGED", " serial: ", "proof", "merge attempt", "refused", "MAIN-MOVED", "recarry START", "no recarry", "PARK ", "TIMEOUT", "HELD", "STALE ", "INFRA-", "REJOIN", "CURED", "NOT RUN", "UNDRAFT"):
        print(f"   lines containing {key!r}:", sum(1 for l in lines if key in l))
    ser = collections.Counter()
    for l in lines:
        m = re.match(r"#\d+ serial: (.*)", l)
        if m:
            for w in m.group(1).split(","): ser[w.strip()] += 1
    print("   serial routing reasons", ser.most_common(10))
    print("   proof lines sample:", [l[:140] for l in lines if "proof" in l.lower()][:6])
    print("   merge-refused sample:", [l[:160] for l in lines if "refused" in l.lower()][:4])
