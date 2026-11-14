#!/usr/bin/env python3
"""Programme replay: tools/plan/replan.py over round 10's whole roster, every group reset to not-started at one
fixed start, under 20 slots. A scenario edits only tools/plan/durations.json's measured terms:
  first: hours taken off every size's first-round hours (per group)
  round: the hours of one extra review round
  rfac : factor on the extra rounds per group (review_rounds - 1)
Null controls: the unedited durations (baseline), and an edit to a term the planner does not read."""
import os as _os
_HERE = _os.path.dirname(_os.path.abspath(__file__))
PD_DATA = _os.environ.get("PD_DATA", _os.path.join(_HERE, "..", "data")) + "/"
PD_REPO = _os.environ.get("PD_REPO", _os.path.abspath(_os.path.join(_HERE, "..", "..", "..", "..", "..", "..")))
PD_STATE = _os.environ.get("PD_STATE", _os.path.expanduser("~/.local/state/hpo"))
import json, subprocess, sys, copy, os, tempfile
S = _os.path.join(_HERE, "..") + "/"; WT = PD_REPO + "/"
ROSTER_REV = _os.environ.get("PD_ROSTER_REV", "2e1845bf11a46c9b893df33a4c80648fc27683f4")  # origin/handoff/audit-r10-roster when the replay was taken
roster = json.loads(subprocess.run(["git", "-C", PD_REPO, "show", ROSTER_REV + ":dev/programme/rosters/wave-r10-groups.json"], capture_output=True, text=True, check=True).stdout)
keep = []
for g in roster["groups"]:
    st = (g.get("resume") or {}).get("stage")
    if g["group"].startswith("R11-") or st in ("absorbed", "deferred", "refused") or not g.get("size"): continue
    g = copy.deepcopy(g); g["resume"] = {"stage": "not-started"}; g["carry"] = []; keep.append(g)
names = {g["group"] for g in keep}
for g in keep: g["after"] = [a for a in g.get("after") or [] if a in names]
roster["groups"] = keep
os.makedirs(S + "out/replay", exist_ok=True)
rf = S + "out/replay/wave-r10-groups.json"; json.dump(roster, open(rf, "w"))
base = json.load(open(WT + "tools/plan/durations.json"))
def run(name, first=0.0, round_h=None, rfac=1.0, slots=20, junk=False):
    d = copy.deepcopy(base)
    for tbl in ("first_round_hours",):
        for k in d[tbl]: d[tbl][k] = round(max(1.0, d[tbl][k] - first), 2)
    for k, cell in d["first_round_by_class_hours"].items():
        for c in cell: cell[c] = round(max(1.0, cell[c] - first), 2)
    if round_h is not None: d["round_hours"] = round_h
    for k in d["review_rounds"]: d["review_rounds"][k] = round(1 + (d["review_rounds"][k] - 1) * rfac, 3)
    for k, cell in d["review_rounds_by_class"].items():
        for c in cell: cell[c] = round(1 + (cell[c] - 1) * rfac, 3)
    for k in d["sizes_hours"]:
        d["sizes_hours"][k] = round(d["first_round_hours"][k] + (d["review_rounds"][k] - 1) * d["round_hours"], 2)
    if junk: d["analyze_cancel_note"] = "edited"
    df = S + f"out/replay/durations-{name}.json"; json.dump(d, open(df, "w"))
    out = S + f"out/replay/plan-{name}.json"
    r = subprocess.run([sys.executable, "-I", WT + "tools/plan/replan.py", "--roster-file", rf, "--durations", df, "--start", "2026-10-20T17:00:00Z",
                        "--out", out, "--slots", str(slots), "--seats", str(slots), "--coordinator-cap", "3"], capture_output=True, text=True, cwd=WT)
    if r.returncode or not os.path.exists(out): return name, None, (r.stderr or r.stdout)[-300:]
    s = json.load(open(out))["summary"]
    return name, s.get("wall_hours"), {k: s.get(k) for k in ("closure", "batches", "ci_minutes")}
if __name__ == "__main__":
    b = None
    for a in [dict(name="baseline (round 10 as measured)"), dict(name="null: unread term edited", junk=True)] + [json.loads(x) for x in sys.argv[1:]]:
        n, w, extra = run(a.pop("name").replace(" ", "_").replace("/", "-")[:60], **a)
        if w is None: print(n, "FAILED", extra); continue
        b = b or w
        print(f"{n:62s} wall {w:8.2f} h  ({(w - b) / b * 100:+6.1f} %)  {extra}")
