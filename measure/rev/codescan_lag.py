"""Round-2 item 5: when the code-scanning `CodeQL` check lands against the
analysis jobs that UPLOADED, and whether the review's check-run predicate could
ever hold.

    python3 -I measure/rev/codescan_lag.py measure/p2/raw > measure/rev/codescan_lag.txt

Per saved head (raw/checks_<sha>.json, GET commits/<sha>/check-runs):
  uploading legs  `Analyze (*)` check runs of github-actions that concluded success
                  or cancelled after running at least UPLOAD_MIN s (a scope
                  stand-down ends in 2-5 s and uploads nothing);
  first / last    the code-scanning check's completed_at minus the first and the
                  last uploading leg's completion;
  predicate       the review's option 1: the check is completed with completed_at
                  AFTER the newest `Analyze (*)` job's completion.
check_writers.py measured the lag against the first ANY leg, stand-downs included;
this one separates the legs that uploaded, which is what decides whether the
check's completed_at tracks the last upload or only the first.
"""
import json
import sys
from datetime import datetime
from pathlib import Path

UPLOAD_MIN = 20


def t(s):
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").timestamp() if s else None


raw = Path(sys.argv[1])
firsts, lasts, holds, n = [], [], [], 0
print(f"{'head':10s} {'uploading':>9s} {'check':8s} {'vs first upload s':>17s} {'vs last upload s':>16s}  option-1 predicate")
for f in sorted(raw.glob("checks_*.json")):
    runs = json.loads(f.read_text())["check_runs"]
    cs = [r for r in runs if r["app"]["slug"] == "github-advanced-security" and r["name"] == "CodeQL"]
    an = [r for r in runs if r["app"]["slug"] == "github-actions" and r["name"].startswith("Analyze (")
          and r["completed_at"] and r["started_at"]]
    up = [r for r in an if r["conclusion"] in ("success", "cancelled")
          and t(r["completed_at"]) - t(r["started_at"]) >= UPLOAD_MIN]
    head = f.stem[7:17]
    if not cs:
        print(f"{head} {len(up):9d} {'ABSENT':8s}")
        continue
    c = max(cs, key=lambda r: r["completed_at"] or "")
    cc = t(c["completed_at"])
    newest_any = max(t(r["completed_at"]) for r in an)
    ok = c["status"] == "completed" and cc > newest_any
    n += 1
    holds.append(ok)
    a = cc - min(t(r["completed_at"]) for r in up) if up else None
    b = cc - max(t(r["completed_at"]) for r in up) if up else None
    if a is not None:
        firsts.append(a)
        lasts.append(b)
    print(f"{head} {len(up):9d} {c['conclusion']:8s} {a if a is not None else '-':>17} {b if b is not None else '-':>16}  "
          f"{'holds' if ok else 'never holds'}")
firsts.sort(); lasts.sort()
print(f"\nheads with a code-scanning check: {n}")
print(f"completed_at minus the FIRST uploading leg's end, s: min {firsts[0]:.0f} max {firsts[-1]:.0f}")
print(f"completed_at minus the LAST uploading leg's end, s: min {lasts[0]:.0f} max {lasts[-1]:.0f}")
print(f"heads where it concluded before the last upload ended: {sum(x < 0 for x in lasts)} of {len(lasts)}")
print(f"option 1 (completed_at after the newest Analyze job) holds at {sum(holds)} of {n} heads; "
      f"at the rest it never holds, and the wait would time out and fail closed")
