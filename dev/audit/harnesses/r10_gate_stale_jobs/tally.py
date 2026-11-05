#!/usr/bin/env python3
"""Tally reasons.jsonl: classify each red gate attempt by its reason lines."""
import collections
import json
import re
import sys

STALE = re.compile(r"^(?:FAIL )?.+: PENDING \(this run\)$")
PRE = re.compile(r"^FAIL prelude: None$")
ABS = re.compile(r"^(?:FAIL )?.+: ABSENT \(this run\)$")
recs = [json.loads(x) for x in open(sys.argv[1])]
errs = [r for r in recs if r.get("error")]
scanned = sum(1 for r in recs if r.get("scanned"))
gates = [r for r in recs if "why" in r]
kind = collections.Counter()
byday = collections.defaultdict(collections.Counter)
only, mixed = [], []
for r in gates:
    w = r["why"]
    d = (r["read_at"] or r["gate_end"])[:10]
    if not w:
        k = "no-verdict-line"
    elif all(STALE.match(x) or PRE.match(x) for x in w):
        k = "only-prelude-None" if PRE.match(w[0]) else "only-PENDING-this-run"
    elif any(STALE.match(x) for x in w):
        k = "PENDING-plus-other"
    elif any(ABS.match(x) for x in w):
        k = "ABSENT-this-run"
    elif "still being judged" in w[0]:
        k = "deferral"
    else:
        k = "other"
    r["k"] = k
    kind[k] += 1
    byday[d][k] += 1
print("scanned runs", scanned, "red gate attempts", len(gates), "read errors", len(errs))
print(dict(kind))
for d in sorted(byday):
    print(d, sum(byday[d].values()), dict(byday[d]))
print("--- every PENDING / prelude None / ABSENT attempt")
all_lags = []
for r in sorted(gates, key=lambda r: r["read_at"] or ""):
    if r["k"] in ("only-PENDING-this-run", "only-prelude-None", "PENDING-plus-other", "ABSENT-this-run"):
        print(r["run"], "a" + str(r["attempt"]), r["event"], r["read_at"], r["k"], json.dumps(r["lags"]), r["why"][:1] if r["k"] != "only-PENDING-this-run" else "")
        all_lags += [(v["s"], k, v["conclusion"], r["run"]) for k, v in r["lags"].items()]
known = sorted(x for x in all_lags if x[0] is not None)
print("lag lines", len(all_lags), "with a completed_at", len(known))
if known:
    s = [x[0] for x in known]
    print("lag min/median/max", s[0], s[len(s) // 2], s[-1], "negative(genuinely unfinished at read)", sum(1 for x in s if x < 0))
print("red-hidden (job really non-success):", [x for x in all_lags if x[2] not in ("success", None)])
print("--- first 'other' reason shapes")
c = collections.Counter(re.sub(r"\d{6,}", "N", x) for r in gates if r["k"] == "other" for x in r["why"][:1])
for k, v in c.most_common(12):
    print(v, k[:110])
