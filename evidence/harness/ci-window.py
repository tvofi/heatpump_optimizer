#!/usr/bin/env python3
"""Reproduce every committed CI figure at the durations file's own measured_at,
with the earliest-started_at rule per (commit, context).

Run: python3 -I ci-window.py <repo> <cut-iso> <durations.json>
"""
import datetime as dt
import json
import subprocess
import sys

repo, cut_s, durations = sys.argv[1], sys.argv[2], sys.argv[3]
CUT = dt.datetime.fromisoformat(cut_s.replace("Z", "+00:00"))
WANT = ("fast (3.14)", "closures", "Analyze (python)")
committed = json.load(open(durations))
log = subprocess.run(["git", "-C", repo, "log", "origin/main", "--first-parent",
                      "--merges", "--format=%H %cI"], capture_output=True,
                     text=True).stdout.split("\n")
merges = []
for line in log:
    if not line.strip():
        continue
    sha, when = line.split()
    if dt.datetime.fromisoformat(when) <= CUT:
        merges.append(sha)
    if len(merges) >= 30:
        break


def p(s):
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00"))


def med(xs):
    xs = sorted(xs)
    n = len(xs)
    return xs[n // 2] if n % 2 else (xs[n // 2 - 1] + xs[n // 2]) / 2.0


def q(xs, f):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(round(f * (len(xs) - 1))))]


rows = {w: [] for w in WANT}
samples = 0
for sha in merges:
    out = subprocess.run(
        ["gh", "api", f"repos/tvofi/heatpump_optimizer/commits/{sha}/check-runs",
         "--paginate", "-q",
         ".check_runs[] | [.name,.id,.started_at,.completed_at,.conclusion] | @tsv"],
        capture_output=True, text=True)
    got = {}
    for line in out.stdout.strip().split("\n"):
        if not line:
            continue
        name, job, began, ended, concl = line.split("\t")
        if name not in WANT or began in ("", "null") or ended in ("", "null"):
            continue
        if p(ended) > CUT:
            continue
        m = round((p(ended) - p(began)).total_seconds() / 60, 1)
        prev = got.get(name)
        if prev is None or began < prev["started"]:
            got[name] = {"started": began, "minutes": m, "conclusion": concl}
    for name, r in got.items():
        rows[name].append((r["minutes"], r["conclusion"]))
    if len(got) == 3:
        samples += 1

print(f"RESULT window_merges={len(merges)} samples_all_three={samples}")
for w in WANT:
    xs = [m for m, _ in rows[w]]
    c = committed["ci"][w]
    canc = sum(1 for _, k in rows[w] if k == "cancelled")
    print(f"RESULT {w}: n={len(xs)} median={med(xs)} iqr=[{q(xs, .25)}, {q(xs, .75)}] "
          f"cancelled={canc} rate={round(canc / max(1, len(xs)), 3)} "
          f"| committed n={c['n']} median={c['median_minutes']} iqr={c['iqr']} "
          f"cancelled={c.get('cancelled')} rate={c.get('cancelled_rate')}")
