"""D14.M3/M5 sweep (D14-s2, round 11): run every detector/barriered class's own detector at the baseline.

Metric, per class: the detector command's exit code at the export root (0 =
the class's detector lists no live seam it refuses at the baseline), its wall
and children-CPU seconds (M5: the barrier's cost in gate seconds; provisional,
the judge's quiet re-runner re-takes them), and the CI wiring: which CI
entry point (.github/workflows/*.yml, tests/run.sh, tools/ci/gate.py, or a
suite script that spawns it) names the command's script.

Classes come from the ledger itself (status detector or barriered), so a class
added to bugclasses.json without a row here prints `NOROW`; the command per
class is the ledger's detector (or barrier, where detector is null), reduced
to its runnable in-tree form; a command that needs GitHub's API or a cloud
session is replaced by its offline --self-test, and says so.

Run: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D14/s2/sweep.py [--only CLASS,...] [--skip-heavy]
Expected at 92d38ecb640bd462f2e19c0814d0f0b7df1ee692: RESULT classes=36, RESULT norow=0;
per-class rc in the ROW lines (exact); seconds provisional (load1 printed).
"""
import os

for _threads in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_threads, "1")

import argparse
import glob
import json
import resource
import subprocess
import sys
import time

PY = sys.executable
HT = {"PYTHONPATH": "tests/hastub"}
STK = {"PYTHONPATH": "tests/hastub", "HASTUB_TZ": "Europe/Stockholm"}

# class -> (argv, extra env, script whose CI wiring is checked, note)
ROWS = {
    "R9-ROW-STALE": ([PY, "tools/audit/seat/record_row.py", "--self-test"], {}, "record_row.py", "delivery_status.py reads the live PR list (gh); the barrier's guard self-test instead"),
    "P1": ([PY, "tests/finite_boundary.py"], HT, "finite_boundary.py", ""),
    "P2": ([PY, "tests/entities.py"], HT, "entities.py", "section 'P2: one fact, one owner'"),
    "P3": ([PY, "tests/features.py"], HT, "features.py", "block R9-P3"),
    "P4": ([PY, "tests/optimality.py"], HT, "optimality.py", ""),
    "P5": (None, None, "features.py", "same run as P3 (R9-P5 block)"),
    "P6": (None, None, "entities.py", "same run as P2 (P6 section)"),
    "P7": ([PY, "tests/dst_checks.py"], STK, "dst_checks.py", "features.py spawns it"),
    "P9": (["node", "tests/card_browser.mjs"], {}, "card_browser.mjs", "needs Playwright/Chromium"),
    "I1": ([PY, "tests/mutation_table.py", "--help"], {}, "mutation_table.py", "--scope changed needs an origin/main diff; argv parse only"),
    "I2": ([PY, "tests/closure.py", "selftest"], {}, "closure.py", "check --in-dir needs a strace recording; self-test"),
    "I3": (["node", "tools/policy/field_coverage.mjs"], {}, "field_coverage.mjs", ""),
    "I4": (["node", "tools/policy/agreement.mjs", "--self-test"], {}, "agreement.mjs", ""),
    "I5": ([PY, "tests/doc_claims.py"], HT, "doc_claims.py", ""),
    "N-future-instant": (None, None, "finite_boundary.py", "same run as P1 (instant arm)"),
    "P11": ([PY, "tests/ha_contract.py"], HT, "ha_contract.py", ""),
    "N-restart": (None, None, "features.py", "same run as P3 (RC2 block)"),
    "N-solve-recompute": ([PY, "tests/stress.py"], HT, "stress.py", "production-call channel"),
    "N-structure-blind": ([PY, "tests/structure.py"], HT, "structure.py", ""),
    "N-shared-config": ([PY, "tests/arch_score_head.py"], HT, "arch_score_head.py", ""),
    "N-staleness": (None, None, "features.py", "same run as P3 (R10 N-staleness block)"),
    "N-silent-zero": (["node", "tools/policy/field_coverage.mjs", "--only", "census"], {}, "field_coverage.mjs", ""),
    "N-body-lint-bounce": (["bash", "tools/pr/prepr.sh", "--self-test"], {}, "prepr.sh", ""),
    "N-train-only-predicate": ([PY, "tools/policy/budget_raise_gate.py", "--self-test"], {}, "budget_raise_gate.py", ""),
    "N-no-expiry": (None, None, "entities.py", "same run as P2"),
    "N-log-flood": (None, None, "entities.py", "same run as P2"),
    "N-move-stale-path": (None, None, "entities.py", "same run as P2"),
    "N-vocabulary-drift": ([PY, "tools/audit/seat/roster_sync.py", "--self-test"], {}, "roster_sync.py", "roster_edit.py --self-test is its second half"),
    "R10-TOPIC-FAMILY": ([PY, "tools/audit/seat/topic_grammar.py", "--self-test"], {}, "topic_grammar.py", ""),
    "R10-SELFTEST-RED-INTRODUCED": ([PY, "tools/audit/seat/merge_train.py", "--self-test"], {}, "merge_train.py", "introduced needs CI runs at a head; self-test"),
    "N-provisional-gate-red-read-final": (None, None, "merge_train.py", "same run as R10-SELFTEST-RED-INTRODUCED"),
    "R10-SELFTEST-TABLE-SHRINK": (["bash", "tools/ci/selftest_scope_mutants.sh"], {}, "selftest_scope", "check re-measures every step; the mutants are the barrier's pin"),
    "N-silent-stop": ([PY, "tools/audit/seat/pulse.py", "--self-test"], {}, "pulse.py", "live mode reads origin; self-test"),
    "N-unmetered-reference": ([PY, "dev/audit/harnesses/r10_rca_sav_estimate.py", "census"], {"PYTHONPATH": "tests/hastub:tests:custom_components"}, "r10_rca_sav_estimate.py", ""),
    "N-livehead-operator-cancel": ([PY, "dev/audit/harnesses/livehead_cancels.py", "--help"], {}, "livehead_cancels.py", "--fetch needs the Actions API (gh forbidden to finders)"),
    "N-relay-handoff-starvation": ([PY, "-I", "dev/audit/rca/relay_handoff_lag.py", "--self-test"], {}, "relay_handoff_lag.py", ""),
}
HEAVY = {"N-solve-recompute", "P9", "P4"}


def wiring(script: str) -> list[str]:
    hits = []
    for path in sorted(glob.glob(".github/workflows/*.yml")) + ["tests/run.sh", "tools/ci/gate.py", "tests/features.py", "tests/entities.py"]:
        try:
            with open(path, encoding="utf-8") as f:
                if script in f.read():
                    hits.append(path)
        except OSError:
            pass
    return hits


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    ap.add_argument("--skip-heavy", action="store_true")
    ap.add_argument("--timeout", type=float, default=3600)
    a = ap.parse_args()
    with open("dev/audit/config/bugclasses.json", encoding="utf-8") as f:
        ledger = json.load(f)
    classes = sorted(k for k, v in ledger.items() if not k.startswith("_") and v.get("status") in ("detector", "barriered"))
    print(f"RESULT classes={len(classes)}")
    norow = [k for k in classes if k not in ROWS]
    for k in norow:
        print(f"NOROW {k}")
    print(f"RESULT norow={len(norow)}")
    only = set(filter(None, a.only.split(",")))
    t0, c0 = time.thread_time(), time.process_time()
    for k in classes:
        if k not in ROWS or (only and k not in only):
            continue
        argv, env, script, note = ROWS[k]
        wired = wiring(script)
        if argv is None:
            print(f"ROW {k} rc=shared wired={','.join(wired) or 'NONE'} note={note}")
            continue
        if a.skip_heavy and k in HEAVY:
            print(f"ROW {k} rc=skipped-heavy wired={','.join(wired) or 'NONE'}")
            continue
        e = dict(os.environ)
        e.update(env)
        r0 = resource.getrusage(resource.RUSAGE_CHILDREN)
        w0 = time.monotonic()
        try:
            p = subprocess.run(argv, env=e, capture_output=True, text=True, timeout=a.timeout)
            rc, out = p.returncode, (p.stdout + p.stderr)
        except subprocess.TimeoutExpired as exc:
            rc, out = "timeout", str(exc)
        wall = time.monotonic() - w0
        r1 = resource.getrusage(resource.RUSAGE_CHILDREN)
        cpu = (r1.ru_utime - r0.ru_utime) + (r1.ru_stime - r0.ru_stime)
        tail = " | ".join(l.strip() for l in out.strip().splitlines()[-3:])[:400]
        print(f"ROW {k} rc={rc} wall_s={wall:.1f} cpu_s={cpu:.1f} wired={','.join(wired) or 'NONE'} note={note}")
        print(f"TAIL {k} {tail}")
        sys.stdout.flush()
    tf = (time.process_time() - c0) / max(time.thread_time() - t0, 1e-9)
    print(f"RESULT thread_factor={tf:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        with open("/proc/vmstat") as f:
            print("RESULT swapins=" + next(l.split()[1] for l in f if l.startswith("pswpin")))
    except OSError:
        print("RESULT swapins=unknown")
    return 0


if __name__ == "__main__":
    sys.exit(main())
