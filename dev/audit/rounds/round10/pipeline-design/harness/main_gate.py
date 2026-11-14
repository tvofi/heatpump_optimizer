#!/usr/bin/env python3
"""Baseline step 6: main's `gate` after each first-parent merge; red streak starts are the scoped-green/FULL-red exposure."""
import os as _os
_HERE = _os.path.dirname(_os.path.abspath(__file__))
PD_DATA = _os.environ.get("PD_DATA", _os.path.join(_HERE, "..", "data")) + "/"
PD_REPO = _os.environ.get("PD_REPO", _os.path.abspath(_os.path.join(_HERE, "..", "..", "..", "..", "..", "..")))
PD_STATE = _os.environ.get("PD_STATE", _os.path.expanduser("~/.local/state/hpo"))
import json, collections, datetime
D = PD_DATA
j = json.load(open(D + "main_gate.json")); seq = []
for l in reversed(j["log"]):
    sha, ct, subj = l.split(" ", 2); g = []
    for s in j["suites"].get(sha, []):
        wr = s.get("workflowRun") or {}
        if wr.get("event") == "push" and (wr.get("workflow") or {}).get("name") == "CI":
            for c in s["checkRuns"]["nodes"]: g.append((c["conclusion"] or "PENDING", s["conclusion"]))
    seq.append((g[-1][0] if g else "NONE", sha[:10], subj, int(ct), g[-1][1] if g else None))
c = collections.Counter(k for k, *_ in seq)
print("first-parent commits", len(seq), "gate on the push run:", dict(c))
print("gate SUCCESS while the run concluded otherwise:", sum(1 for k, _, _, _, rc in seq if k == "SUCCESS" and rc != "SUCCESS"), "of", c["SUCCESS"])
prev = "SUCCESS"; streaks = []
for k, sha, subj, ct, rc in seq:
    if k in ("SUCCESS", "FAILURE"):
        if k == "FAILURE" and prev == "SUCCESS": streaks.append([sha, subj[:78], ct, ct, 1])
        elif k == "FAILURE": streaks[-1][3] = ct; streaks[-1][4] += 1
        prev = k
judged = c["SUCCESS"] + c["FAILURE"]
print(f"gate-red streak starts: {len(streaks)} over {judged} judged merges ({len(streaks)/judged:.3f}); red merges {c['FAILURE']} ({c['FAILURE']/judged:.3f})")
for sha, subj, a, b, n in streaks:
    print("  ", datetime.datetime.fromtimestamp(a, datetime.timezone.utc).strftime("%m-%d %H:%M"), sha, subj, "| reds", n, "span h", round((b - a) / 3600, 1))
