#!/usr/bin/env python3
"""v1_legionella_due.py -- D3 verifier's own measurement of D3-s2-01.

Metric (one line): with LegionellaGuard.last_cycle SKEW hours in the future
(interval 1 day, clock stepped by tests/hastub dt_util.freeze), (a) the published
due_in_hours at t0 and (b) the first clock instant, on a 15-minute grid, at which
due_in_hours <= 0 (the instant the timer is overdue) -- baseline vs the
clamp-removed mutant; plus (c) the optimizer's deadline instant
t0 + (interval - hours_since) that optimizer.py:4140 derives from the state.

Instrumented symbol: custom_components/heatpump_optimizer/legionella.py:
LegionellaGuard.hours_since (and due_in_hours through it).
Perturbation: delete the max(0.0, ...) clamp (one line, restored in finally).
Expected: (a) moves 24.0 -> 26.0 for SKEW=2; (b) overdue instant unchanged
(delta 0.0 h); (c) deadline instant moves +2.0 h but only while now < last_cycle.
Null control: SKEW = -2 (last cycle in the past): all three identical.

Command (tree root):
  PYTHONPATH=tests/hastub python3 tools/audit/round8/D3/v1_legionella_due.py
Baseline cdf82daabcfe3777d98b31489f36df5555ec9d82; machine 4-vCPU container; exact.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import hashlib
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path.cwd()
LEG = ROOT / "custom_components/heatpump_optimizer/legionella.py"
OLD = "        return max(0.0, since.total_seconds() / 3600.0)"
NEW = "        return since.total_seconds() / 3600.0"

PROBE = r'''
import sys, json
sys.path.insert(0, "tests"); sys.path.insert(0, "custom_components")
from datetime import datetime, timedelta, timezone
from homeassistant.util import dt as dt_util
from harness import FakeHass
from heatpump_optimizer.thermal_model import ThermalParameters
from heatpump_optimizer.disinfection import DisinfectionSwitch
from heatpump_optimizer.legionella import LegionellaGuard
skew = float(sys.argv[1])
p = ThermalParameters.from_config({})
p.dhw_legionella_enabled = True
p.dhw_legionella_interval_days = 1
g = LegionellaGuard(FakeHass(), "v1", p, {}, action=lambda: {},
                    disinfect=DisinfectionSwitch({}, None, None), dhw_blocked=lambda: False)
t0 = datetime(2026, 3, 1, 12, 0, tzinfo=timezone.utc)
try:
    dt_util.freeze(t0)
    g.last_cycle = t0 + timedelta(hours=skew)
    due0 = g.due_in_hours()
    since0 = g.hours_since()
    deadline0 = 24.0 - since0
    first = None
    for k in range(0, 4 * 24 * 4):
        dt_util.freeze(t0 + timedelta(minutes=15 * k))
        if g.due_in_hours() <= 0:
            first = k * 0.25
            break
finally:
    dt_util.freeze(None)
print(json.dumps({"due0": due0, "since0": since0, "overdue_at_h": first,
                  "deadline_h": deadline0}))
'''


def probe(skew):
    import json
    env = dict(os.environ, PYTHONPATH="tests/hastub")
    p = subprocess.run([sys.executable, "-c", PROBE, str(skew)], cwd=ROOT, env=env,
                       capture_output=True, text=True, timeout=300)
    if p.returncode:
        raise SystemExit(p.stderr[-2000:])
    return json.loads(p.stdout.strip().splitlines()[-1])


def main():
    orig = LEG.read_text()
    h0 = hashlib.sha256(orig.encode()).hexdigest()
    assert orig.count(OLD) == 1
    t0 = time.process_time(); w0 = time.thread_time()
    res = {}
    try:
        for arm in ("base", "mutant"):
            if arm == "mutant":
                LEG.write_text(orig.replace(OLD, NEW, 1))
            for skew in (2.0, -2.0):
                res[(arm, skew)] = probe(skew)
                print(f"  {arm:6s} skew={skew:+.0f}h {res[(arm, skew)]}")
    finally:
        LEG.write_text(orig)
    restored = hashlib.sha256(LEG.read_bytes()).hexdigest() == h0
    b, m = res[("base", 2.0)], res[("mutant", 2.0)]
    nb, nm = res[("base", -2.0)], res[("mutant", -2.0)]
    print(f"RESULT due_in_hours_t0_base={b['due0']} h")
    print(f"RESULT due_in_hours_t0_mutant={m['due0']} h")
    print(f"RESULT overdue_instant_delta={m['overdue_at_h'] - b['overdue_at_h']} h")
    print(f"RESULT optimizer_deadline_delta={m['deadline_h'] - b['deadline_h']:.6f} h")
    print(f"RESULT null_identical={int(nb == nm)} count")
    print(f"RESULT restored={int(restored)} count")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print(f"RESULT thread_factor={(time.process_time()-t0)/max(time.thread_time()-w0,1e-9):.3f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
