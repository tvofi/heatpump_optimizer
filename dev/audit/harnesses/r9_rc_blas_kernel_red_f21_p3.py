#!/usr/bin/env python3
"""R9-RC-BLAS-KERNEL-RED: which quantity of tests/features.py's R9-F2.1 P3
storage comparison does NOT move across BLAS kernels.

The check races the production solve against the same solve seeded with the
half-price floor's plan, and keyed its verdict on that race until this
branch: `j_plain <= j_seeded + 0.1`. The margin is a basin-choice quantity,
so the verdict moved with the kernel -- +0.1000/+0.0905/+0.0904 on
Sandybridge/Haswell/Nehalem, -0.2070 on Apple Accelerate (issue #1725,
PR #1726's null control) -- and because `tools/pr/prepr.sh` step 6b records a
closure by RUNNING the scripts a diff reaches, every macOS seat's push
refused. This harness prices the replacement's arm per kernel so the choice
is made by measurement:

  j_plain            -- the production solve (continuation live), no seed.
  j_continuation_off -- the same solve with `_multi_start_minimize`'s
                        `move_starts` forced to its own default identity, i.e.
                        the 934dcb1fc^ route, reached by one parameter rather
                        than by a second copy of the multi-start.
  continuation_gain  -- j_continuation_off - j_plain, BOTH ARMS IN THIS RUN.
                        This is what the re-keyed check reads; its bound is 0
                        and no environment supplies a number for it.
  j_seeded_half_price -- the seeded race's other side, kept as a FIGURE: on
                        Accelerate it reads 110.129674 against a shipped
                        110.436632, so this platform's multi-start leaves 0.307
                        on the table a warm start finds, where the Linux
                        kernels measured the two within 0.0096. Printed, not
                        gated: no bound on that race holds across kernels.
  ladder_scale=<s>   -- the continuation's own 0.5 price scale perturbed to
                        s via a descriptor that intercepts production's
                        assignment; measures whether the gain is a slope (a
                        tolerance would buy detection) or a cliff (it would
                        not).
  bit_identical      -- single-zone j_plain == j_continuation_off AND the two
                        schedules array-equal. Exact by construction, since
                        `move_starts` returns its candidates untouched unless
                        `two_zone_enabled`; this is the null arm and needs no
                        tolerance and no kernel.
  threads_identical  -- every two-zone figure re-solved with the BLAS thread
                        variables pinned to 1, the k1725 harness's own
                        preamble: the mover is the kernel, not run-to-run
                        threading.

SCOPE OF THE KERNEL AXIS, plainly: this box is an Apple M1 with an
Accelerate-backed numpy (2.4.6, python 3.14.7), so `OPENBLAS_CORETYPE` is a
NO-OP here -- there is exactly one locally reachable kernel class, and the
environment line proves it (no OpenBLAS `Core:` line to report). The Linux
rows are cited from the tree, not re-taken: the hpo-ci container this
repository pinned to Sandybridge measured the OLD margin (+0.1000, archived
green at dev/archive/handoff/r9-f2-solver-4/ev/features_head_container.log)
and its pre-continuation shipped plan (111.267, commit 934dcb1fc). The
AVX-512 point is likewise CI's own logs, never this hardware.

Run from the repository root:

    PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r9_rc_blas_kernel_red_f21_p3.py

It prints one RESULT line per number, and thread_factor/load1/swapins at the
end per the harness contract.
"""
def repo_root(start):
    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
    from pathlib import Path
    here = Path(start).resolve()
    if here.is_file():
        here = here.parent
    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
    for cand in (here, *here.parents):
        if (cand / marker).is_file():
            return cand
    raise RuntimeError(f"no repository root above {start}")

import os

PIN = os.environ.get("HPO_F21_PIN_THREADS") == "1"
if PIN:
    for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
               "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
        os.environ[_v] = "1"

import resource  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from datetime import datetime  # noqa: E402
from unittest import mock  # noqa: E402

ROOT = str(repo_root(__file__))
os.chdir(ROOT)
for _part in ("custom_components", os.path.join("tests", "hastub"), "tests"):
    sys.path.insert(0, os.path.join(ROOT, _part))

import numpy as np  # noqa: E402

from profiles import house, prices, solve_inputs, weather  # noqa: E402
from heatpump_optimizer import optimizer as optm  # noqa: E402
from heatpump_optimizer.optimizer import (  # noqa: E402
    HeatPumpOptimizer, OptimizationConfig)
from heatpump_optimizer.thermal_model import (  # noqa: E402
    ThermalModel, ThermalParameters, ThermalState)

FULL_MS = optm._multi_start_minimize


def env_line():
    """The kernel/CPU line every number below is attributed against.

    An Accelerate-backed numpy prints no `Core:` line, so the line says so
    rather than leaving the reader to assume a kernel was selected.
    """
    core = os.environ.get("OPENBLAS_CORETYPE") or "(unset)"
    try:
        p = subprocess.run([sys.executable, "-c", "import numpy"],
                           env=dict(os.environ, OPENBLAS_VERBOSE="2"),
                           capture_output=True, text=True, timeout=60)
        hit = next((ln for ln in p.stderr.splitlines() if "Core:" in ln), None)
        if hit is not None:
            core = hit.split("Core:", 1)[1].strip()
        else:
            core = f"{core} -- no OpenBLAS Core: line (numpy is not OpenBLAS)"
    except Exception as exc:  # noqa: BLE001 -- attribution, fail-soft
        core = f"{core} ({exc.__class__.__name__})"
    blas = "unknown"
    try:
        import numpy.__config__ as _cfg
        blas = str(_cfg.show(mode="dicts")["Build Dependencies"]["blas"]["name"])
    except Exception:  # noqa: BLE001
        pass
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
    head = subprocess.run(["git", "rev-parse", "--short", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    print(f"environment: core={core} blas={blas} cpu={cpu} numpy={np.__version__} "
          f"python={sys.version.split()[0]} head={head} "
          f"threads={'pinned-1' if PIN else 'default'}", flush=True)


def nocont_ms(objective, starts, bounds, *a, **kw):
    """The production multi-start with the continuation removed."""
    kw = dict(kw)
    kw["move_starts"] = lambda cands, maxiter: cands
    return FULL_MS(objective, starts, bounds, *a, **kw)


def scaled_opt(scale):
    """HeatPumpOptimizer whose continuation refines at `scale`, not 0.5.

    Production's `move_starts` assigns `self._floor_l1_scale = 0.5` and
    restores 1.0 in a `finally`. The descriptor keeps that protocol and stores
    `scale` instead, so the objective's floor term reads the perturbed price.
    Nothing else moves: the refine call, the multi-start's budget and the
    cross-candidate minimum that ships are production's.
    """
    class _Scaled(HeatPumpOptimizer):
        _fls = 1.0

        @property
        def _floor_l1_scale(self):
            return self._fls

        @_floor_l1_scale.setter
        def _floor_l1_scale(self, v):
            self._fls = scale if v < 1.0 else 1.0
    return _Scaled


def storage_solve(two_zone, seed=None, l1=None, continuation=True, cls=None):
    """features.py's _f21_storage_solve, verbatim, plus the arms above."""
    cfg = house(two_zone=two_zone, dhw=False, buffer_tank_volume=750.0,
                buffer_max_temperature=70.0, mixing_valve_mode="manual")
    params = ThermalParameters.from_config(cfg)
    params.dhw_enabled = False
    opt = (cls or HeatPumpOptimizer)(
        ThermalModel(params),
        OptimizationConfig(
            horizon_hours=24, time_step_minutes=15,
            target_temp=cfg["target_temperature"],
            min_temp=cfg["min_temperature"], max_temp=cfg["max_temperature"]))
    if seed is not None:
        opt._prev_shipped_plan = np.asarray(seed, dtype=float)
    t0 = datetime(2026, 1, 15, 0, 0)
    out, wind, rain, sun = weather("winter_cold", t0)
    st = ThermalState(
        room_temperature=20.0, upper_floor_temperature=20.0,
        lower_floor_temperature=20.0, slab_temperature=21.0,
        buffer_tank_temperature=25.0, outdoor_temperature=float(out[0]))
    inputs = solve_inputs(
        initial_state=st, prices=prices("winter_typical", t0),
        outdoor_temps=out, wind_speeds=wind, precipitation=rain,
        solar_radiation=sun, start_time=t0)
    saved = optm._COMFORT_FLOOR_L1
    if l1 is not None:
        optm._COMFORT_FLOOR_L1 = l1
    started = time.perf_counter()
    try:
        if continuation:
            res = opt.optimize(inputs=inputs)
        else:
            with mock.patch.object(optm, "_multi_start_minimize", nocont_ms):
                res = opt.optimize(inputs=inputs)
    finally:
        optm._COMFORT_FLOOR_L1 = saved
    return (np.asarray(res.power_schedule), float(res.objective_value),
            time.perf_counter() - started)


env_line()
wall, solves = 0.0, 0
figures = {}
for tz in (True, False):
    label = "two_zone" if tz else "single_zone"
    half_pw, _, s = storage_solve(tz, l1=0.5 * optm._COMFORT_FLOOR_L1)
    wall += s; solves += 1
    plain_pw, j_plain, s = storage_solve(tz)
    wall += s; solves += 1
    off_pw, j_off, s = storage_solve(tz, continuation=False)
    wall += s; solves += 1
    _, j_seeded, s = storage_solve(tz, seed=half_pw)
    wall += s; solves += 1
    gain = j_off - j_plain
    print(f"RESULT f21_p3_{label}_j_plain={j_plain:.6f}", flush=True)
    print(f"RESULT f21_p3_{label}_j_continuation_off={j_off:.6f}", flush=True)
    print(f"RESULT f21_p3_{label}_continuation_gain={gain:+.6f}", flush=True)
    print(f"RESULT f21_p3_{label}_j_seeded_half_price={j_seeded:.6f}", flush=True)
    print(f"RESULT f21_p3_{label}_seeded_race_margin={j_seeded + 0.1 - j_plain:+.6f} "
          f"(the arm the check no longer reads)", flush=True)
    print(f"RESULT f21_p3_{label}_bit_identical={int(bool(j_plain == j_off and np.array_equal(plain_pw, off_pw)))} "
          f"(exact null arm: 1 required for single_zone)", flush=True)
    figures[label] = (j_plain, j_off, j_seeded)

# The perturbation ladder: is the gain a slope or a cliff?
for scale in (0.25, 0.5, 0.75, 1.0):
    _, j, s = storage_solve(True, cls=scaled_opt(scale))
    wall += s; solves += 1
    print(f"RESULT f21_p3_ladder_scale_{scale:.2f}_gain={figures['two_zone'][1] - j:+.6f} "
          f"(gain against the continuation-off arm; scale 1.0 is no continuation)",
          flush=True)

# The thread null control: the same two-zone figures under pinned BLAS threads.
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "1"
_, j_plain_p, s = storage_solve(True)
wall += s; solves += 1
_, j_off_p, s = storage_solve(True, continuation=False)
wall += s; solves += 1
print(f"RESULT f21_p3_threads_pinned_j_plain={j_plain_p:.6f}", flush=True)
print(f"RESULT f21_p3_threads_pinned_continuation_gain={j_off_p - j_plain_p:+.6f}", flush=True)
print(f"RESULT f21_p3_threads_identical="
      f"{int(bool(j_plain_p == figures['two_zone'][0] and j_off_p == figures['two_zone'][1]))}",
      flush=True)
print(f"RESULT f21_p3_solves={solves} wall_s={wall:.1f}", flush=True)

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
