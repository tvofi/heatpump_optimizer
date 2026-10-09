"""Reviewer's targeted drive of PR #2074's refusal path (defect-root-cause.md
"A detector must be shown to detect"): the defect night's shape and the
ordinary-failure night's shape, both through the tree's own baseline_refusal().

Inputs are fabricated ScriptRuns (a stale committed recording + a timed-out
baseline); nothing runs a driver, so this is seconds-scale.
"""
import io
import sys
from contextlib import redirect_stdout

sys.path.insert(0, "/Users/timmalmstrom/hpo-seats/review-2074/wt/tests")
import mutation_table as mt  # noqa: E402

SR = mt.ScriptRun
STALE = {"tests/boost_drift_replay.py": {"seconds": 800.2, "rc": 0}}


def show(title, baseline, scope, recorded):
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = mt.baseline_refusal(baseline, scope, recorded)
    out = buf.getvalue()
    print(f"\n===== {title}  (scope={scope}) -> return {rc} =====")
    print(out.rstrip())
    return rc, out


results = []

# --- the defect night: baseline TIMED OUT, committed recording says rc 0 ---
t1 = SR(rc=124, failed=0, seconds=2401.0, stdout="",
        stderr="timed out after 2401s\n", timed_out=True)
rc, out = show("DEFECT NIGHT: timeout + committed rc:0", {"tests/boost_drift_replay.py": t1},
               "full", STALE)
for want in ["2401", "STALE", "800.2", "3 x", "pool", "TIMED OUT"]:
    hit = want in out
    results.append((f"defect-night mentions {want!r}", hit))
bad = "Fix the suite first" in out
results.append(("defect-night does NOT say 'Fix the suite first'", not bad))

# --- same, but the bound not recoverable from stderr (elapsed fallback) ---
t2 = SR(rc=124, failed=0, seconds=2401.0, stdout="", stderr="killed\n", timed_out=True)
rc, out = show("DEFECT NIGHT: timeout, no 'timed out after Ns' in stderr", {"x.py": t2},
               "full", STALE)
results.append(("elapsed-seconds fallback prints a bound", "x.py: pool cost reached the 2401s bound" in out))

# --- the ordinary red: a failing check, NOT a timeout ---
t3 = SR(rc=1, failed=3, seconds=140.0, stdout="  FAIL a16:debug_inline  [boom]\n", stderr="")
rc, out = show("ORDINARY RED: failing check", {"tests/entities.py": t3}, "full", STALE)
results.append(("ordinary red still says 'Fix the suite first'", "Fix the suite first" in out))
results.append(("ordinary red still names the check", "a16:debug_inline" in out))
results.append(("ordinary red does NOT say STALE", "STALE" not in out))

# --- mixed: one timeout, one real failure ---
rc, out = show("MIXED: a timeout AND a real failure", {"x.py": t1, "y.py": t3}, "full", STALE)
results.append(("mixed: both arms printed", "TIMED OUT in x.py" in out and "already red in y.py" in out))

# --- timeout with no green solo recording (rc != 0 arm) ---
NOREC = {"x.py": {"seconds": 800.2, "rc": 1}}
rc, out = show("TIMEOUT, committed rc != 0", {"x.py": t1}, "full", NOREC)
results.append(("no-green-recording arm says so", "no green solo recording" in out))

# --- timeout, driver absent from the table entirely ---
rc, out = show("TIMEOUT, no committed recording at all", {"x.py": t1}, "full", {})
results.append(("absent recording is named as such", "no committed recording" in out))

# --- green baseline: nothing fires ---
g = SR(rc=0, failed=0, seconds=100.0, stdout="", stderr="")
rc, out = show("GREEN baseline", {"x.py": g}, "full", STALE)
results.append(("green baseline returns None", rc is None))

# --- the return-code arm is unchanged from the base ---
rc_full, _ = show("RETURN ARM: full", {"x.py": t1}, "full", STALE)
rc_changed, _ = show("RETURN ARM: changed", {"x.py": t1}, "changed", STALE)
results.append(("full -> 1", rc_full == 1))
results.append(("changed -> 0", rc_changed == 0))

print("\n---------------- RESULT LINES ----------------")
fails = 0
for name, ok in results:
    print(f"{'ok  ' if ok else 'FAIL'} {name}")
    fails += 0 if ok else 1
print(f"RESULT refusal-path-drive: {len(results) - fails} of {len(results)} assertions hold"
      + ("" if not fails else f" — {fails} FAILED"))
