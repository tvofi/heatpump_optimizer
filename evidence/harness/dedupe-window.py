#!/usr/bin/env python3
"""Reproduce the committed CI figures at their own measured instant, then apply
the shipped dedupe rule to the same window.

Run: python3 -I dedupe-window.py <repo>
Prints RESULT lines only. Network: one check-runs call per merged tree.
"""
import datetime as dt
import json
import subprocess
import sys

repo = sys.argv[1]
CUT = dt.datetime(2026, 10, 20, 16, 52, 44, tzinfo=dt.timezone.utc)
WANT = ("closures",)

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


rows = []          # (commit, started, ended, minutes, job), API order preserved
for sha in merges:
    out = subprocess.run(
        ["gh", "api", f"repos/tvofi/heatpump_optimizer/commits/{sha}/check-runs",
         "--paginate", "-q",
         ".check_runs[] | [.name,.id,.started_at,.completed_at,.conclusion] | @tsv"],
        capture_output=True, text=True)
    for line in out.stdout.strip().split("\n"):
        if not line:
            continue
        name, job, began, ended, concl = line.split("\t")
        if name != "closures" or began in ("", "null") or ended in ("", "null"):
            continue
        if p(ended) > CUT:      # not complete at the measurement instant
            continue
        rows.append((sha, began, ended, round((p(ended) - p(began)).total_seconds() / 60, 1), int(job)))


def med(xs):
    xs = sorted(xs)
    n = len(xs)
    return xs[n // 2] if n % 2 else (xs[n // 2 - 1] + xs[n // 2]) / 2.0


committed = json.load(open(f"{repo}/tools/plan/durations.json"))["ci"]["closures"]
by_commit = {}
for r in rows:
    by_commit.setdefault(r[0], []).append(r)

first_listed, earliest = [], []
for sha, rs in by_commit.items():
    first_listed.append(rs[0][3])                      # the shipped rule
    earliest.append(min(rs, key=lambda x: x[1])[3])    # its stated intent

print(f"RESULT window_merges={len(merges)} closures_rows_complete={len(rows)} "
      f"distinct_commits={len(by_commit)}")
print(f"RESULT rows_without_dedupe n={len(rows)} median={med([r[3] for r in rows])} "
      f"| committed n={committed['n']} median={committed['median_minutes']}")
dups = {s: v for s, v in by_commit.items() if len(v) > 1}
for sha, rs in dups.items():
    print(f"RESULT duplicate commit={sha[:12]} api_order="
          f"{[(r[1], r[3], r[4]) for r in rs]}")
print(f"RESULT shipped_rule_first_listed n={len(first_listed)} median={med(first_listed)}")
print(f"RESULT stated_intent_first_attempt n={len(earliest)} median={med(earliest)}")

fast = json.load(open(f"{repo}/tools/plan/durations.json"))["ci"]["fast (3.14)"]["median_minutes"]
ana = json.load(open(f"{repo}/tools/plan/durations.json"))["ci"]["Analyze (python)"]["median_minutes"]
rate = json.load(open(f"{repo}/tools/plan/durations.json"))["ci"]["Analyze (python)"]["cancelled_rate"]
for label, m in (("committed", committed["median_minutes"]),
                 ("shipped_rule", med(first_listed)),
                 ("stated_intent", med(earliest))):
    gate = fast + m + ana * (1.0 + rate)
    print(f"RESULT gate_if_closures_median={label} gate={gate:.4f} ci_51={51 * gate:.1f}")
