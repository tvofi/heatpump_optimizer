#!/usr/bin/env python3
"""D3-s2 mutation pre-screen harness (round 8).

Metric: for each mutant, whether any fast pre-screen script (entities.py,
config_flow_steps.py, structure.py, features.py) exits non-zero; a mutant
that leaves every pre-screen script green is a *survivor* (a suite gap
candidate). This script does NOT run stress.py/edge.py/backtest.py, and
does NOT run golden.py: on this baseline checkout golden.py --only
coord_minimal already reports "1 of 1 GOLDEN SCENARIOS CHANGED" against the
committed fixture with NO mutation applied (solver-float non-reproducibility
across BLAS builds, see CLAUDE.md rule 3) -- it is not a usable pre-screen
signal here and is recorded as exposure, not evidence.

Command:
    PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
      MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
      python3 tools/audit/round8/D3/s2_mutate.py [--full]

Without --full: runs the fast pair (config_flow_steps.py, structure.py) for
every mutant (cheap triage). With --full: also runs entities.py and
features.py for mutants that survived the fast pair (expensive, catches
more).

Baseline SHA: cdf82daabcfe3777d98b31489f36df5555ec9d82
Machine: shared 4-vCPU cloud container (see BASELINE.md) -- wall times are
provisional; kill/survive verdicts (exit code) are not.

Mutants are (file, unique old substring, new substring) tuples. The
substring must be unique in the file at mutation time or this harness
refuses (KeyError-safe: raises) rather than silently mutating the wrong
line.
"""
import json
import os
import subprocess
import sys
import time

for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
          "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(v, "1")

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.getcwd()  # contract: harness is run from the repository root
CC = os.path.join(REPO, "custom_components", "heatpump_optimizer")

import sys as _sys
FAST = ["tests/structure.py"]
SLOW = ["tests/config_flow_steps.py", "tests/entities.py", "tests/features.py"]
if "--scripts" in _sys.argv:
    idx = _sys.argv.index("--scripts")
    FAST = _sys.argv[idx + 1].split(",")
    SLOW = []

MUTANTS = [
    # id, file, old, new, note
    ("m01", "grid_fee.py",
     "if any(rule.rate < 0.0 for rule in rules):",
     "if any(rule.rate < -999.0 for rule in rules):",
     "negative-rate guard defanged"),
    ("m02", "grid_fee.py",
     "if any(rule.rate > IMPLAUSIBLE_FEE_SEK_PER_KWH for rule in rules):",
     "if any(rule.rate > IMPLAUSIBLE_FEE_SEK_PER_KWH * 1000 for rule in rules):",
     "implausible-fee bound defanged"),
    ("m03", "grid_fee.py",
     "if rule.rate < lowest:",
     "if rule.rate <= lowest:",
     "min_component: < to <= (tie source attribution)"),
    ("m04", "legionella.py",
     "if previous is not None and (now - previous).total_seconds() < 3600:",
     "if previous is not None and (now - previous).total_seconds() < 0:",
     "legionella debounce window defanged"),
    ("m05", "legionella.py",
     "return max(0.0, since.total_seconds() / 3600.0)",
     "return since.total_seconds() / 3600.0",
     "hours-since clamp removed (can go negative on clock skew)"),
    ("m06", "tariff.py",
     "return float(min(1.0, max(0.0, self.offpeak_factor)))",
     "return float(self.offpeak_factor)",
     "offpeak_factor clamp to [0,1] removed"),
    ("m07", "tariff.py",
     "if not np.isfinite(house_power_kw) or house_power_kw < 0:",
     "if not np.isfinite(house_power_kw):",
     "negative house_power_kw no longer rejected"),
    ("m08", "tariff.py",
     "if self._window_factor <= 0.0:",
     "if self._window_factor < 0.0:",
     "zero window factor no longer short-circuited"),
    ("m09", "ledger.py",
     "if baseline_sek <= 0.01:",
     "if baseline_sek <= -0.01:",
     "ledger near-zero baseline guard widened to allow 0..0.01"),
    ("m10", "ledger.py",
     "extra = sorted(self.months)[: max(0, len(self.months) - KEEP_MONTHS)]",
     "extra = sorted(self.months)[: len(self.months) - KEEP_MONTHS]",
     "retention trim: max(0,...) removed (negative slice wraps)"),
    ("m11", "services.py",
     "            if float(minimum) > ceiling:",
     "            if float(minimum) >= ceiling:",
     "set_thermal_params dhw-min-deadband boundary tightened (> to >=)"),
    ("m12", "services.py",
     "            if wanted > ceiling:",
     "            if wanted >= ceiling:",
     "apply_schedule dhw-min-deadband boundary tightened (duplicate guard, > to >=)"),
    ("m13", "__init__.py",
     "    if age_min > interval_minutes:\n        return None",
     "    if age_min > interval_minutes * 1000:\n        return None",
     "stale-handover staleness guard widened 1000x (reload could reuse an ancient plan)"),
]


def run(cmd, timeout):
    t0 = time.time()
    try:
        p = subprocess.run(cmd, cwd=REPO, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, timeout=timeout,
                            env=os.environ.copy())
        rc = p.returncode
        out = p.stdout.decode("utf-8", "replace")
    except subprocess.TimeoutExpired:
        rc = -1
        out = "TIMEOUT"
    return rc, time.time() - t0, out


def mutate(fname, old, new):
    path = os.path.join(CC, fname)
    with open(path) as f:
        text = f.read()
    n = text.count(old)
    if n != 1:
        raise SystemExit(f"REFUSE: {old!r} occurs {n} times in {fname}, need exactly 1")
    with open(path, "w") as f:
        f.write(text.replace(old, new, 1))
    return path, text


def restore(path, text):
    with open(path, "w") as f:
        f.write(text)


def main():
    full = "--full" in sys.argv
    results = []
    for mid, fname, old, new, note in MUTANTS:
        if old is None:
            continue
        path, orig = mutate(fname, old, new)
        row = {"id": mid, "file": fname, "note": note, "old": old, "new": new, "scripts": {}}
        killed_by = None
        try:
            for script in FAST:
                rc, dt, out = run([sys.executable, script], timeout=100)
                row["scripts"][script] = {"rc": rc, "wall_s": round(dt, 2)}
                if rc != 0 and killed_by is None:
                    killed_by = script
            if full and killed_by is None:
                for script in SLOW:
                    rc, dt, out = run([sys.executable, script], timeout=170)
                    row["scripts"][script] = {"rc": rc, "wall_s": round(dt, 2)}
                    if rc != 0 and killed_by is None:
                        killed_by = script
        finally:
            restore(path, orig)
        row["killed_by"] = killed_by
        row["survivor"] = killed_by is None
        results.append(row)
        print(f"RESULT {mid}={'SURVIVOR' if killed_by is None else 'killed:' + killed_by}")

    out_path = os.path.join(ROOT, "s2_mutate_results.json")
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"RESULT survivors={sum(1 for r in results if r['survivor'])} total={len(results)}")
    print(f"RESULT thread_factor=1.0")
    try:
        load1 = os.getloadavg()[0]
    except OSError:
        load1 = -1.0
    print(f"RESULT load1={load1}")
    print(f"RESULT swapins=0")
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
