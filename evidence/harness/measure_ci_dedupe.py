#!/usr/bin/env python3
"""Reviewer's own harness for `measure_ci`'s (commit, context) dedupe.

Run: python3 -I measure_ci_dedupe.py <path-to-replan.py> [--mutant]

It monkeypatches `replan.subprocess.run` so no network is touched: `git log`
returns three fixed SHAs and `gh api` returns three contexts per SHA. Commit C1
carries TWO `closures` rows, listed newest-first exactly as the live API lists
them (reviewer observed commit 0c298f6b: the later attempt has the higher job id
and comes first). The first row is the rerun (60 min), the second the first
attempt (20 min).

Prints one RESULT line per rule. A median that moves between the rules is the
finding's demonstration.
"""
import importlib.util
import sys
from datetime import datetime, timedelta, timezone

TARGET = sys.argv[1]
MUTANT = "--mutant" in sys.argv

spec = importlib.util.spec_from_file_location("replan_under_test", TARGET)
replan = importlib.util.module_from_spec(spec)
spec.loader.exec_module(replan)

SHAS = ["c1" * 20, "c2" * 20, "c3" * 20]


def stamp(minutes):
    base = datetime(2026, 10, 20, 10, 0, tzinfo=timezone.utc)
    return (base + timedelta(minutes=minutes)).strftime("%Y-%m-%dT%H:%M:%SZ")


# rows[sha][context] = list of (started_offset, duration, conclusion)
# C1's closures: the rerun is FIRST in API order (started later, higher job id).
ROWS = {
    SHAS[0]: {
        "fast (3.14)": [(0, 10, "success")],
        "closures": [(120, 60, "success"), (0, 20, "success")],
        "Analyze (python)": [(0, 30, "success")],
    },
    SHAS[1]: {
        "fast (3.14)": [(0, 12, "success")],
        "closures": [(0, 22, "success")],
        "Analyze (python)": [(0, 32, "success")],
    },
    SHAS[2]: {
        "fast (3.14)": [(0, 14, "success")],
        "closures": [(0, 24, "success")],
        "Analyze (python)": [(0, 34, "success")],
    },
}
JOBS = {}


class Fake:
    returncode = 0
    stderr = ""

    def __init__(self, stdout=""):
        self.stdout = stdout


def fake_run(argv, **kw):
    if argv[:2] == ["git", "-C"] or argv[:1] == ["git"]:
        return Fake("\n".join(SHAS) + "\n")
    url = next(a for a in argv if "/commits/" in a)
    sha = url.rsplit("/", 2)[-2]
    lines = []
    job = 1000
    for ctx, rows in ROWS[sha].items():
        for started, minutes, concl in rows:
            job += 1
            lines.append("\t".join([
                ctx, str(job), stamp(started), stamp(started + minutes), concl]))
    return Fake("\n".join(lines) + "\n")


replan.subprocess.run = fake_run
measured = replan.measure_ci(".", "o/r", 3)
ci = measured["ci"]
print(f"RESULT code_rule closures n={ci['closures']['n']} median={ci['closures']['median_minutes']}")
print(f"RESULT code_rule samples={measured['provenance']['merges']}")
print(f"RESULT code_rule all n={ {k: v['n'] for k, v in ci.items()} }")

# The two counterfactuals, computed from the same fake population.
first_attempt = {c: sorted(rows, key=lambda r: r[0])[0][1] for c, rows in ROWS[SHAS[0]].items()}
naive = []
for sha in SHAS:
    for ctx, rows in ROWS[sha].items():
        if ctx == "closures":
            naive.extend(r[1] for r in rows)


def med(xs):
    xs = sorted(xs)
    n = len(xs)
    return xs[n // 2] if n % 2 else (xs[n // 2 - 1] + xs[n // 2]) / 2.0


correct = [ROWS[SHAS[0]]["closures"][1][1], ROWS[SHAS[1]]["closures"][0][1],
           ROWS[SHAS[2]]["closures"][0][1]]
print(f"RESULT correct_first_attempt closures n={len(correct)} median={med(correct)}")
print(f"RESULT naive_all_attempts closures n={len(naive)} median={med(naive)}")
print(f"RESULT mutant={MUTANT} | code keeps first-listed rerun: "
      f"{ci['closures']['median_minutes'] == 60 or med([60,22,24]) == ci['closures']['median_minutes']}")
