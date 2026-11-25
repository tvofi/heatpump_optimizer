#!/usr/bin/env python3
"""D3-s1 (box D3-g35): shared loader and synthetic step-test plant for the probe_<key>.py harnesses.

Not a harness on its own: each probe_<key>.py carries the header (metric, command, expected,
baseline, machine, instrumented symbol, perturbation) and imports this module from its own dir.
The module under test is the BASELINE's sysid.py read with `git show <baseline>:<path>` (so a
gate's committed mutant in any worktree never leaks in), optionally with one exact-text line
replaced in memory, compiled into a private module name inside the integration's package.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import importlib.util
import math
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np

BASELINE = "92d38ecb640bd462f2e19c0814d0f0b7df1ee692"
REL = "custom_components/heatpump_optimizer/sysid.py"


def repo_root(start):
    here = Path(start).resolve()
    if here.is_file():
        here = here.parent
    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
    for cand in (here, *here.parents):
        if (cand / marker).is_file():
            return cand
    raise RuntimeError(f"no repository root above {start}")


ROOT = repo_root(__file__)
sys.path.insert(0, str(ROOT))
_COUNTER = [0]


def load_tap(old, expr):
    """The baseline module with `_TAP.append(<expr>)` inserted before the exact line `old`:
    an instrumentation arm (not the mutant) that exposes the value the mutated comparison reads."""
    indent = old[: len(old) - len(old.lstrip())]
    mod = load(old, f"{indent}_TAP.append({expr})\n{old}", pre={"_TAP": []})
    return mod


def load(old=None, new=None, pre=None):
    """The baseline sysid module; with old/new, that exact line replaced once (the mutant)."""
    import custom_components.heatpump_optimizer  # noqa: F401  (package context)
    text = subprocess.run(["git", "show", f"{BASELINE}:{REL}"], cwd=ROOT, check=True,
                          capture_output=True, text=True).stdout
    if old is not None:
        lines = text.split("\n")
        hits = [i for i, ln in enumerate(lines) if ln == old]
        assert len(hits) == 1, f"mutant line found {len(hits)} times: {old!r}"
        lines[hits[0]] = new
        text = "\n".join(lines)
    _COUNTER[0] += 1
    name = f"custom_components.heatpump_optimizer.sysid_probe_g35_{_COUNTER[0]}"
    spec = importlib.util.spec_from_loader(name, loader=None)
    mod = importlib.util.module_from_spec(spec)
    mod.__package__ = "custom_components.heatpump_optimizer"
    sys.modules[name] = mod
    if pre:
        mod.__dict__.update(pre)
    exec(compile(text, str(ROOT / REL), "exec"), mod.__dict__)
    return mod


def plant_samples(mod, ua=0.2, cap=3.0, gains=0.3, q=4.0, t_out=0.0, t0=20.0,
                  settle_h=1.0, step_h=2.0, relax_h=2.0, cadence_min=10.0,
                  drift=0.0, noise=0.0, seed=0, start_steady=True,
                  last_settle_room=None):
    """Exact first-order plant C dT/dt = Q + G - UA (T - T_out), sampled at a cadence.

    The sensor reads T + drift * t (+ noise). Settling and relax carry power 0, the step q.
    start_steady puts T at the steady state of the settle input (so settle is flat)."""
    rng = np.random.default_rng(seed)
    k = ua / cap
    T = (t_out + gains / ua) if start_steady else t0
    when0 = datetime(2026, 1, 15, 23, 0, tzinfo=timezone.utc)
    dt = cadence_min / 60.0
    out = []
    t = 0.0
    phases = [(mod.PHASE_SETTLING, settle_h, 0.0), (mod.PHASE_STEP, step_h, q),
              (mod.PHASE_RELAX, relax_h, 0.0)]
    for phase, dur, power in phases:
        n = int(round(dur / dt))
        for _ in range(n):
            reading = T + drift * t + (noise * rng.standard_normal() if noise else 0.0)
            out.append(mod.SysIdSample(when=when0 + timedelta(hours=t), room_temp=float(reading),
                                       outdoor_temp=float(t_out), power_kw=float(power),
                                       phase=phase))
            # advance exactly for one interval under this phase's input
            t_ss = t_out + (power + gains) / ua
            T = t_ss + (T - t_ss) * math.exp(-k * dt)
            t += dt
    if last_settle_room is not None:
        idx = max(i for i, s in enumerate(out) if s.phase == mod.PHASE_SETTLING)
        out[idx].room_temp = last_settle_room
    return out


def run(mod, samples, config=None):
    sid = mod.SystemIdentification(config or mod.SysIdConfig(enabled=True))
    sid.samples = list(samples)
    return sid.identify()


def fmt(res):
    g = res.internal_gains_kw
    return (f"completed={int(res.completed)} reason={res.reason!r} "
            f"ua={res.heat_loss_kw_per_c} gains={g} drift={res.sensor_drift_c_per_h} "
            f"conf={res.confidence}")


def tapped(tap_mod, samples, config=None, which=-1):
    """Run identify() on the tap arm; the value the mutated comparison read (None: not reached)."""
    tap_mod._TAP.clear()
    res = run(tap_mod, samples, config)
    return (tap_mod._TAP[which] if tap_mod._TAP else None), res


def hunt(value_of, lo, hi, target, scan=4000):
    """Search a scalar input x in [lo, hi] for value_of(x) == target EXACTLY (float equality).

    Bisection on the sign of value_of(x) - target down to adjacent floats, then a scan of
    `scan` consecutive floats either side of the crossing. Returns (x_hit or None, tried, closest)
    where closest = (|value - target|, x, value) over every evaluated x."""
    tried = 0
    best = (math.inf, None, None)

    def ev(x):
        nonlocal tried, best
        tried += 1
        v = value_of(x)
        if v is not None and math.isfinite(v):
            d = abs(v - target)
            if d < best[0]:
                best = (d, x, v)
        return v

    vlo, vhi = ev(lo), ev(hi)
    if vlo is None or vhi is None:
        return None, tried, best
    if vlo == target:
        return lo, tried, best
    if vhi == target:
        return hi, tried, best
    slo = vlo > target
    if slo == (vhi > target):
        return None, tried, best
    a, b = lo, hi
    for _ in range(200):
        mid = 0.5 * (a + b)
        if mid in (a, b):
            break
        v = ev(mid)
        if v is None:
            return None, tried, best
        if v == target:
            return mid, tried, best
        if (v > target) == slo:
            a = mid
        else:
            b = mid
    xa, xb = a, b
    for _ in range(scan):
        xa = math.nextafter(xa, -math.inf)
        xb = math.nextafter(xb, math.inf)
        for x in (xa, xb):
            v = ev(x)
            if v == target:
                return x, tried, best
    return None, tried, best


def multi_hunt(tap_line, expr, make, lo, hi, target, seconds, scan=150):
    """hunt() repeated over a secondary input `s` (restarts), stopping at the first exact hit.

    make(x, s) -> samples. Returns (x, s, tried) or (None, None, tried)."""
    tap = load_tap(tap_line, expr)
    tot = 0
    for s in seconds:
        f = lambda x: tapped(tap, make(x, s))[0]
        hit, tried, _best = hunt(f, lo, hi, target, scan=scan)
        tot += tried
        if hit is not None:
            return hit, s, tot
    return None, None, tot


def drive(old, new, measure, cases):
    """Run measure(mod, samples, config) over every case on both arms and print RESULT lines.

    cases: list of (label, samples, config|None). Prints one RESULT per case and arm, plus
    differing_cases = how many cases' measured value differs between the arms."""
    base, mut = load(), load(old, new)
    differing = 0
    for label, samples, cfg_kw in cases:
        vb = measure(base, samples, base.SysIdConfig(enabled=True, **(cfg_kw or {})))
        vm = measure(mut, samples, mut.SysIdConfig(enabled=True, **(cfg_kw or {})))
        same = (vb == vm) or (isinstance(vb, float) and isinstance(vm, float)
                              and math.isnan(vb) and math.isnan(vm))
        differing += 0 if same else 1
        print(f"RESULT case[{label}].baseline={vb!r}")
        print(f"RESULT case[{label}].mutant={vm!r}")
    print(f"RESULT cases={len(cases)}")
    print(f"RESULT differing_cases={differing}")
    return differing


def outcome(mod, samples, config):
    """The whole published result of identify(), as one comparable tuple."""
    r = run(mod, samples, config)
    return (int(r.completed), r.reason, r.heat_loss_kw_per_c, r.thermal_mass_kwh_per_c,
            r.internal_gains_kw, r.sensor_drift_c_per_h, r.confidence)


def std_cases(m):
    """The honest-search grid every equivalence probe runs: clean, drifting, noisy (5 seeds),
    zero/negative/high gains, slow cadence, unsettled start, tiny and zero steps, the plausible
    bounds' neighbourhoods, a near-zero settle ΔT, and a flat (unexcited) window."""
    P = lambda **kw: plant_samples(m, **kw)
    cases = [("clean", P(), None), ("drift+0.01", P(drift=0.01), None),
             ("drift-0.01", P(drift=-0.01), None), ("drift+0.05", P(drift=0.05), None)]
    cases += [(f"noise0.02_s{s}", P(noise=0.02, seed=s), None) for s in range(5)]
    cases += [(f"noise0.005_s{s}", P(noise=0.005, seed=s), None) for s in range(3)]
    cases += [("gains0", P(gains=0.0), None), ("gains-0.3", P(gains=-0.3), None),
              ("gains1.9", P(gains=1.9), None), ("gains3", P(gains=3.0), None),
              ("cadence30", P(cadence_min=30.0), None), ("cadence60", P(cadence_min=60.0), None),
              ("unsettled1.3", P(start_steady=False, t0=1.3), None),
              ("q0.1", P(q=0.1), None), ("q1e-5", P(q=1e-5), None), ("q0", P(q=0.0), None),
              ("tau~200", P(ua=0.015, cap=3.0, gains=0.0), None),
              ("ua~5", P(ua=4.9, cap=10.0, gains=0.0, q=40.0), None),
              ("ua~0.01", P(ua=0.0101, cap=1.0, gains=0.0), None),
              ("tau~0.1", P(ua=3.2, cap=0.3, gains=0.0, cadence_min=1.0), None),
              ("settle_dT_1e-6", P(last_settle_room=1e-6), None),
              ("prior0.05", P(drift=0.01), {"sensor_drift_prior_c_per_h": 0.05}),
              ("short", P(settle_h=0.5, step_h=0.5, relax_h=0.5), None)]
    return cases


def footer():
    cpu = time.process_time()
    thr = time.thread_time() or cpu
    print(f"RESULT thread_factor={cpu / thr if thr else 1.0:.2f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
