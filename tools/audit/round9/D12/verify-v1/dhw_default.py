"""D12 verify-v1 (round 9): D12-s1-01 one-line production perturbation and a
start-state control, over the finder's own s1/state_seed.py run_arm().

Metric (one line): arm A (dhw_temp_entity omitted) window-hours the model-truth
tank spends below dhw_min_temperature, and the count of solves whose initial
_solve_snapshot dhw_temperature differs >1 K from that truth tank, over 24 hourly cycles.
Count key: the ThermalState the production _solve_snapshot hands the solver.

Arms:
  base       finder's harness as is (truth starts 50 C, ThermalState default 55 C)
  truth55    control: truth tank starts AT the 55 C default (no initial offset baked in)
  default45  one-line production perturbation in memory: ThermalState.dhw_temperature
             default 55 -> 45 (= dhw_min_temperature); the solver must plan more DHW,
             so window-hours below min must fall (direction DOWN) if the solver reads it.
Run:  PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D12/verify-v1/dhw_default.py
Expected: base reproduces the finder (23, 6.25 h); default45 window-hours < base.
Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1 (+ round9 evidence tree 6f51db2c).
Machine: G2-V1 cloud container, 4 vCPU, Python 3.14. Counts only, frozen clock.
Root rule: cwd (repository root).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import dataclasses
import sys
import time

sys.path.insert(0, "tools/audit/round9/D12/s1")
import state_seed as ss  # noqa: E402
from heatpump_optimizer.thermal_model import ThermalState  # noqa: E402


def _set_default(value):
    names = [f.name for f in dataclasses.fields(ThermalState) if f.init]
    dflt = list(ThermalState.__init__.__defaults__)
    idx = names.index("dhw_temperature") - (len(names) - len(dflt))
    old = dflt[idx]
    dflt[idx] = value
    ThermalState.__init__.__defaults__ = tuple(dflt)
    return old


def main():
    t0p, t0t = time.process_time(), time.thread_time()
    arms = {}
    arms["base"] = ss.run_arm(False)
    ss.TRUTH0 = 55.0
    arms["truth55"] = ss.run_arm(False)
    ss.TRUTH0 = 50.0
    old = _set_default(45.0)
    assert ThermalState().dhw_temperature == 45.0
    try:
        arms["default45"] = ss.run_arm(False)
    finally:
        _set_default(old)
    for k, r in arms.items():
        print(f"ARM {k} {r}")
        print(f"RESULT {k}_dhw_init_mismatch_gt1K={r['mismatch']['dhw']} count")
        print(f"RESULT {k}_dhw_window_hours_below_min={r['window_hours_below_min']} h")
        print(f"RESULT {k}_dhw_kwh_executed={r['dhw_kwh']} kWh")
    proc, thr = time.process_time() - t0p, time.thread_time() - t0t
    print(f"RESULT thread_factor={proc / max(thr, 1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    sw = 0
    try:
        sw = int([ln for ln in open("/proc/vmstat") if ln.startswith("pswpin ")][0].split()[1])
    except Exception:  # noqa: BLE001
        pass
    print(f"RESULT swapins={sw}")


if __name__ == "__main__":
    main()
