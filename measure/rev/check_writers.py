"""Item 5: who writes a check run at a PR head, and when the code-scanning
`CodeQL` check (app github-advanced-security) lands against the analyses and
against `pr-contract`.

    python3 -I measure/rev/check_writers.py measure/p2/raw > measure/rev/check_writers.txt

Per saved head (raw/checks_<sha>.json, GET commits/<sha>/check-runs):
  writers   every (app slug) that wrote a check run, with its names;
  analyses  how many `Analyze (*)` check runs concluded success/failure (a leg
            that ran) and the newest completion among them;
  codescan  the CodeQL code-scanning check: conclusion, its completed_at minus
            the newest analysis job's completion (LAG), and minus the earliest's;
  contract  the newest `pr-contract` completion minus the code-scanning check's
            (negative = the contract concluded BEFORE the red it owed an answer).
Prints the distribution of LAG over heads with a code-scanning check, which is
the wait pr-contract must allow for.
"""
import json, sys
from datetime import datetime
from pathlib import Path

def t(s): return datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").timestamp() if s else None
raw = Path(sys.argv[1]); lags = []; firsts = []; before = []; apps = {}
for f in sorted(raw.glob("checks_*.json")):
    runs = json.loads(f.read_text())["check_runs"]
    for r in runs: apps.setdefault(r["app"]["slug"], set()).add(r["name"] if r["app"]["slug"] != "github-actions" else "<workflow jobs>")
    an = [r for r in runs if r["app"]["slug"] == "github-actions" and r["name"].startswith("Analyze (") and r["conclusion"] in ("success", "failure")]
    cs = [r for r in runs if r["app"]["slug"] == "github-advanced-security" and r["name"] == "CodeQL"]
    pc = [r for r in runs if r["name"] == "pr-contract" and r["completed_at"]]
    last_an = max((t(r["completed_at"]) for r in an if r["completed_at"]), default=None)
    first_an = min((t(r["completed_at"]) for r in an if r["completed_at"]), default=None)
    last_pc = max((t(r["completed_at"]) for r in pc), default=None)
    head = f.stem[7:17]
    if not cs:
        print(f"{head} analyses {len(an):2d}  codescan ABSENT"); continue
    c = max(cs, key=lambda r: r["completed_at"] or "")
    lag = t(c["completed_at"]) - last_an if last_an and c["completed_at"] else None
    lag1 = t(c["completed_at"]) - first_an if first_an and c["completed_at"] else None
    if lag1 is not None: firsts.append(lag1)
    gap = last_pc - t(c["completed_at"]) if last_pc and c["completed_at"] else None
    if lag is not None: lags.append(lag)
    if gap is not None and gap < 0: before.append((head, c["conclusion"]))
    print(f"{head} analyses {len(an):2d}  codescan {c['conclusion']:8s} lag {lag if lag is not None else '-':>6} s (vs first analysis {lag1 if lag1 is not None else '-':>5} s)"
          f"  pr-contract-minus-codescan {gap if gap is not None else '-':>6} s")
print("\nwriters at the sampled PR heads:")
for a, n in sorted(apps.items()): print(f"  {a}: {', '.join(sorted(n))}")
lags.sort()
print(f"\ncode-scanning check present at {len(lags)} heads; lag after the newest analysis, s: "
      f"min {lags[0]:.0f} median {lags[len(lags)//2]:.0f} max {lags[-1]:.0f}" if lags else "no code-scanning check")
firsts.sort()
if firsts: print(f"lag after the EARLIEST analysis job completed, s: min {firsts[0]:.0f} median {firsts[len(firsts)//2]:.0f} max {firsts[-1]:.0f}"
                 " (negative: the check concluded while the uploading job was still finishing)")
print(f"heads whose last pr-contract concluded before the code-scanning check: {len(before)} {before}")
