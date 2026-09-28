"""Issue #1725, the knife-edge harness: the two optimizer comparisons whose
VERDICT (not just their numbers) moves with the OpenBLAS DYNAMIC_ARCH kernel's
summation order, isolated from the 18-minute suite runs they live in.

Metric, one line: the stop-rule gap of tests/optimality.py's ftol check and
the shipped-vs-seeded margin of tests/features.py's R9-F2.1 P3 storage check,
per BLAS kernel, on the exact scenario each check uses.

  stop-rule arms (tests/optimality.py, challenger 7, #921):
    prod     -- the production solve (ftol 1e-6 at both sites), scored by
                optimality.py's own cost rule (sum(pr*pw*DT), comfort floor
                16.5 C). Expected ROBUST across kernels: 61.24-61.28 SEK on
                every x86 kernel and CI; 61.70 on Accelerate.
    loose_1e3 / loose_1e2 -- the pre-#1725 single-site arm (multi-start
                refinement loosened, restart tight) at ftol 1e-3 and 1e-2.
                loose_1e3 is the CHAOTIC quantity #1725 is about: measured
                63.47 Haswell / 63.48 Sandybridge / 61.09 Nehalem (the kernel
                Rosetta actually selects) / 60.54 Accelerate / 63.47 CI
                (mined from green Tests logs) -- sign of its gap vs prod
                flips, against a 0.1% bound.
    both_1e3 / both_1e2 -- the same loosening applied to BOTH ftol sites
                (multi-start refinement and restart polish). both_1e2 is the
                kernel-STABLE arm the fix adopts: cost 64.97 SEK
                bit-identically in every environment, gap +5.04 (Accelerate)
                to +5.74 (Haswell); the check keys on it with a 2.5% bound.
    tight_1e8 -- both sites tightened to 1e-8. Candidate comparator that
                measurement REJECTED: it lands in different basins per kernel
                (59.11-60.44 SEK, objective sign flips), so no check can key
                on it. Kept as data for that decision.
  null controls:
    repeat    -- the prod arm solved twice in one process; the schedules must
                be bit-identical (if not, "kernel" is not the only mover).
    flat      -- the prod arm's cost across kernels is the null the whole
                attribution rests on: it must not move materially between
                kernels of the same wheels.
  R9-F2.1 P3 (tests/features.py, D2-s2-81): margin = j_seeded + 0.1 - j_plain
    per zone arm, on the 750 L storage house. Positive margin = check passes.
    Single-zone is the check's own null arm. Measured +0.0904..+0.1000 on
    every Linux kernel (the fix leaves it untouched); -0.2070 on Accelerate.

Run from the repository root, once per kernel:

    PYTHONPATH=tests/hastub python3 tools/audit/harnesses/k1725_blas_kernel_gap.py

Select the kernel with OPENBLAS_CORETYPE (Haswell, Sandybridge, ...; SkylakeX
SIGILLs under Rosetta -- no AVX-512). The AVX-512/CI-class data point comes
from mining `gh run view --log` of green Tests runs for optimality.py's
" stop-prod /" and " stop-rule:" lines; this hardware cannot reach it.

Expected values, tolerance, baseline: see the table in issue #1725 and the
PR this harness ships with. Baseline SHA and machine are printed by the run.

It prints one RESULT line per number, and thread_factor/load1/swapins at the
end per the harness contract (tools/audit/README.md).
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import subprocess  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from datetime import datetime  # noqa: E402
from unittest import mock  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))
os.chdir(ROOT)
for _part in ("custom_components", os.path.join("tests", "hastub"), "tests"):
    sys.path.insert(0, os.path.join(ROOT, _part))

import numpy as np  # noqa: E402

from profiles import DT, N, house, prices, weather  # noqa: E402
from heatpump_optimizer import optimizer as optm  # noqa: E402
from heatpump_optimizer.optimizer import (  # noqa: E402
    HeatPumpOptimizer, OptimizationConfig)
from heatpump_optimizer.thermal_model import (  # noqa: E402
    ThermalModel, ThermalParameters, ThermalState)


def env_line():
    """The kernel/CPU line the run's numbers are attributed against."""
    core = os.environ.get("OPENBLAS_CORETYPE") or ""
    env = dict(os.environ, OPENBLAS_VERBOSE="2")
    try:
        p = subprocess.run([sys.executable, "-c", "import numpy"],
                           env=env, capture_output=True, text=True, timeout=60)
        for line in p.stderr.splitlines():
            if "Core:" in line:
                core = line.split("Core:", 1)[1].strip()
                break
    except Exception as exc:  # noqa: BLE001 -- attribution, fail-soft
        core = core or f"unknown ({exc.__class__.__name__})"
    cpu = "unknown"
    try:
        if sys.platform == "darwin":
            cpu = subprocess.run(["sysctl", "-n", "machdep.cpu.brand_string"],
                                 capture_output=True, text=True,
                                 timeout=10).stdout.strip() or cpu
        else:
            with open("/proc/cpuinfo") as fh:
                for line in fh:
                    if line.startswith(("model name", "Hardware")):
                        cpu = line.split(":", 1)[1].strip()
                        break
    except OSError:
        pass
    head = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"],
        capture_output=True, text=True).stdout.strip()
    print(f"environment: core={core} cpu={cpu} numpy={np.__version__} "
          f"python={sys.version.split()[0]} head={head}", flush=True)


# --- the stop-rule scenario: optimality.py's _dhw_setup, verbatim -----------

def dhw_setup(start=datetime(2026, 1, 15)):
    cfg = house(two_zone=True)
    p = ThermalParameters.from_config(cfg)
    p.dhw_enabled = True
    m = ThermalModel(p)
    o = HeatPumpOptimizer(m, OptimizationConfig(
        horizon_hours=24, time_step_minutes=15,
        target_temp=21.0, min_temp=17.0, max_temp=23.0))
    pr = prices("winter_typical", start)
    ot, wi, ra, so = weather("winter_cold", start)
    st = ThermalState(
        room_temperature=21.0, slab_temperature=22.0,
        outdoor_temperature=float(ot[0]), upper_floor_temperature=21.0,
        lower_floor_temperature=21.0, buffer_tank_temperature=40.0,
        dhw_temperature=48.0)
    return o, m, pr, ot, wi, ra, so, st, start


def score(m, pw, st, ot, wi, ra, so, pr, min_t=16.5):
    room, _, _, _, _, _, _ = m.simulate_trajectory(st, pw, ot, wi, ra, so, DT)
    return (float(np.sum(pr * pw * DT)),
            float(np.maximum(0, min_t - room[1:]).sum()))


full_scoped = optm._scoped_minimize
full_ms = optm._multi_start_minimize
full_restart = optm._lbfgsb_restart


def _ftol_scoped(ftol):
    def wrap(*a, **kw):
        kw = dict(kw)
        opts = dict(kw.get("options") or {})
        opts["ftol"] = ftol
        kw["options"] = opts
        return full_scoped(*a, **kw)
    return wrap


def _restart_tight(*a, **kw):
    with mock.patch.object(optm, "_scoped_minimize", full_scoped):
        return full_restart(*a, **kw)


def _loose_ms(ftol):
    # The check's single-site arm: multi-start refinement loosened, restart
    # restored to the production ftol (optimality.py's _loose_ms_7).
    def wrap(objective, starts, bounds, *a, **kw):
        with mock.patch.object(optm, "_lbfgsb_restart", _restart_tight):
            with mock.patch.object(optm, "_scoped_minimize", _ftol_scoped(ftol)):
                return full_ms(objective, starts, bounds, *a, **kw)
    return wrap


def _both_ms(ftol):
    # The refused both-sites arm: everything funneling through
    # _scoped_minimize runs at the loosened ftol, restart included.
    def wrap(objective, starts, bounds, *a, **kw):
        with mock.patch.object(optm, "_scoped_minimize", _ftol_scoped(ftol)):
            return full_ms(objective, starts, bounds, *a, **kw)
    return wrap


env_line()
o7, m7, pr7, ot7, wi7, ra7, so7, st7, start7 = dhw_setup()

arms = [("prod", None), ("loose_1e3", _loose_ms(1e-3)),
        ("loose_1e2", _loose_ms(1e-2)), ("both_1e3", _both_ms(1e-3)),
        ("both_1e2", _both_ms(1e-2)), ("tight_1e8", _both_ms(1e-8))]

results = {}
for name, ms_patch in arms:
    t0 = time.perf_counter()
    if ms_patch is None:
        r = o7.optimize(st7, pr7, ot7, wi7, ra7, so7, start7)
    else:
        with mock.patch.object(optm, "_multi_start_minimize", ms_patch):
            r = o7.optimize(st7, pr7, ot7, wi7, ra7, so7, start7)
    pw = np.asarray(r.power_schedule, dtype=float)
    c, v = score(m7, pw, st7, ot7, wi7, ra7, so7, pr7)
    results[name] = (c, v, pw)
    print(f"RESULT stop_{name}_cost={c:.2f} SEK viol={v:.4f} "
          f"objective={float(r.objective_value):.4f} "
          f"wall={time.perf_counter() - t0:.1f}s", flush=True)

# Null control 1: in-process determinism of the production arm.
o7b, m7b, pr7b, ot7b, wi7b, ra7b, so7b, st7b, _ = dhw_setup()
r7b = o7b.optimize(st7b, pr7b, ot7b, wi7b, ra7b, so7b, start7)
pw7b = np.asarray(r7b.power_schedule, dtype=float)
identical = bool(np.array_equal(pw7b, results["prod"][2]))
print(f"RESULT stop_repeat_identical={int(identical)}", flush=True)

for arm in ("loose_1e3", "loose_1e2", "both_1e3", "both_1e2", "tight_1e8"):
    c0, _, _ = results["prod"]
    cl = results[arm][0]
    print(f"RESULT stop_{arm}_gap_pct={100.0 * (cl - c0) / cl:+.3f} "
          f"(loosened arm costlier than prod by this much)", flush=True)
# The check as #1725's fix ships it: prod must beat the both-sites 1e-2
# arm by at least 2.5% (half the smallest measured healthy gap, 5.04% on
# Accelerate). A negative or sub-bound value here means the gate goes red.
c0, _, _ = results["prod"]
carm = results["both_1e2"][0]
gap = 100.0 * (carm - c0) / carm
print(f"RESULT stop_check_gap_pct={gap:+.3f} "
      f"(must be >= +2.500 for the gate check to pass)", flush=True)

# --- R9-F2.1 P3: features.py's _f21_storage_solve, verbatim -----------------


def f21_solve(two_zone, seed=None, l1=None):
    cfg = house(two_zone=two_zone, dhw=False, buffer_tank_volume=750.0,
                buffer_max_temperature=70.0, mixing_valve_mode="manual")
    params = ThermalParameters.from_config(cfg)
    params.dhw_enabled = False
    fopt = HeatPumpOptimizer(
        ThermalModel(params),
        OptimizationConfig(
            horizon_hours=24, time_step_minutes=15,
            target_temp=cfg["target_temperature"],
            min_temp=cfg["min_temperature"], max_temp=cfg["max_temperature"]))
    if seed is not None:
        fopt._prev_shipped_plan = np.asarray(seed, dtype=float)
    t0 = datetime(2026, 1, 15, 0, 0)
    out, wind, rain, sun = weather("winter_cold", t0)
    st = ThermalState(
        room_temperature=20.0, upper_floor_temperature=20.0,
        lower_floor_temperature=20.0, slab_temperature=21.0,
        buffer_tank_temperature=25.0, outdoor_temperature=float(out[0]))
    saved = optm._COMFORT_FLOOR_L1
    if l1 is not None:
        optm._COMFORT_FLOOR_L1 = l1
    try:
        res = fopt.optimize(st, prices("winter_typical", t0),
                            out, wind, rain, sun, t0)
    finally:
        optm._COMFORT_FLOOR_L1 = saved
    return np.asarray(res.power_schedule), float(res.objective_value)


for tz in (True, False):
    half_pw, _ = f21_solve(tz, l1=0.5 * optm._COMFORT_FLOOR_L1)
    _, j_plain = f21_solve(tz)
    _, j_seeded = f21_solve(tz, seed=half_pw)
    label = "two_zone" if tz else "single_zone"
    margin = j_seeded + 0.1 - j_plain
    print(f"RESULT f21_p3_{label}_margin={margin:+.4f} "
          f"(check passes when >= 0; j_plain={j_plain:.4f}, "
          f"j_seeded={j_seeded:.4f})", flush=True)

# --- the contract's standing controls ---------------------------------------
import resource  # noqa: E402

factor = (time.process_time() / time.thread_time()) if time.thread_time() else 1.0
print(f"RESULT thread_factor={factor:.3f}", flush=True)
try:
    with open("/proc/loadavg") as fh:
        load1 = fh.read().split()[0]
except OSError:
    out = subprocess.run(["sysctl", "-n", "vm.loadavg"],
                         capture_output=True, text=True, timeout=10).stdout
    load1 = out.split()[1] if len(out.split()) > 1 else "unknown"
print(f"RESULT load1={load1}", flush=True)
print(f"RESULT swapins={resource.getrusage(resource.RUSAGE_SELF).ru_nswap}",
      flush=True)
