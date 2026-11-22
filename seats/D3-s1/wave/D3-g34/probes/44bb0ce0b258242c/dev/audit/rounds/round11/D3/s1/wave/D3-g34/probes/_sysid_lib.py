#!/usr/bin/env python3
# Shared helper of box D3-g34's probes (not a harness on its own; each probe_<key>.py carries the header).
# Metric helper: whether SystemIdentification.identify's whole SysIdResult (its repr, every float exact)
#   differs between the baseline method and the one-line mutant recompiled in memory from the method's
#   own source, on one sample series.
# Command: imported by dev/audit/rounds/round11/D3/s1/wave/D3-g34/probes/probe_<key>.py
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g34 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB).
# Instrumented symbol: custom_components.heatpump_optimizer.sysid:SystemIdentification.identify.
# Perturbation: the probe's one-line mutant, applied in memory (never on disk).
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import inspect, math, resource, sys, textwrap, time
from datetime import datetime, timedelta, timezone
from pathlib import Path


def repo_root(start):
    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
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
import numpy as np  # noqa: E402
from custom_components.heatpump_optimizer import sysid  # noqa: E402

SI = sysid.SystemIdentification
T0 = datetime(2026, 1, 15, 23, 0, tzinfo=timezone.utc)
_C0 = (time.process_time(), time.thread_time())


def mutant_identify(line_no, old, new):
    """identify() with source line `line_no` (file numbering) replaced by `new`, compiled in sysid's namespace."""
    lines, start = inspect.getsourcelines(SI.identify)
    idx = line_no - start
    if lines[idx].rstrip("\n") != old:
        raise SystemExit(f"REFUSE sysid.py:{line_no} is {lines[idx]!r}, not {old!r}")
    lines = list(lines)
    lines[idx] = new + "\n"
    src = "\n" * (start - 1) + textwrap.dedent("".join(lines))  # keep file line numbers in tracebacks
    ns = dict(sysid.__dict__)
    exec(compile(src, sysid.__file__, "exec"), ns)
    return ns["identify"]


def samples(temps, outs, powers, phases, hours):
    """SysIdSample list; hours[i] is sample i's offset from T0 in hours."""
    return [sysid.SysIdSample(when=T0 + timedelta(hours=h), room_temp=float(t), outdoor_temp=float(o),
                              power_kw=float(p), phase=ph)
            for t, o, p, ph, h in zip(temps, outs, powers, phases, hours)]


def plant(ua=0.2, cap=5.0, gains=0.3, q=(3.7, 6.0, 0.0), hours=(1.0, 2.0, 2.0), dt_h=0.25, t_room=None,
          t_out=0.0, noise=0.0, drift=0.0, seed=0):
    """An exact first-order house (C dT/dt = -UA (T - Tout) + Q + G) sampled every dt_h through settle,
    step and relax; optional white sensor noise (degC) and a linear sensor drift (degC/h)."""
    rng = np.random.default_rng(seed)
    phases = []
    for ph, n in zip((sysid.PHASE_SETTLING, sysid.PHASE_STEP, sysid.PHASE_RELAX), hours):
        phases += [ph] * int(round(n / dt_h))
    phases.append(sysid.PHASE_RELAX)
    qs = {sysid.PHASE_SETTLING: q[0], sysid.PHASE_STEP: q[1], sysid.PHASE_RELAX: q[2]}
    temps, t = [], (t_out + (q[0] + gains) / ua if t_room is None else t_room)  # settle starts at equilibrium
    for i, ph in enumerate(phases):
        temps.append(t)
        t_inf = t_out + (qs[ph] + gains) / ua
        t = t_inf + (t - t_inf) * math.exp(-ua / cap * dt_h)
    hrs = [i * dt_h for i in range(len(phases))]
    meas = [tt + noise * rng.standard_normal() + drift * h for tt, h in zip(temps, hrs)]
    return samples(meas, [t_out] * len(phases), [qs[p] for p in phases], phases, hrs)


def call(fn, smp, config=None):
    sid = SI(config)
    sid.samples = list(smp)
    try:
        return fn(sid)
    except Exception as exc:  # noqa: BLE001 - a raise is an outcome the arms compare
        return f"raise {type(exc).__name__}: {exc}"


def short(r):
    if isinstance(r, str):
        return r
    if not r.completed:
        return f"refused:{r.reason}"
    return f"completed ua={r.heat_loss_kw_per_c!r} C={r.thermal_mass_kwh_per_c!r} conf={r.confidence!r}"


def compare(mut, cases, config_of=None):
    """Run every (name, samples[, config]) case on both arms; print one line per case and return the count
    of cases whose SysIdResult repr differs."""
    moved = 0
    for case in cases:
        name, smp = case[0], case[1]
        cfg = case[2] if len(case) > 2 else None
        b = call(SI.identify, smp, cfg)
        m = call(mut, smp, cfg)
        diff = repr(b) != repr(m)
        moved += diff
        print(f"CASE {name}: differs={int(diff)} baseline=[{short(b)}] mutant=[{short(m)}]")
    return moved


def footer():
    p, t = time.process_time() - _C0[0], time.thread_time() - _C0[1]
    print(f"RESULT thread_factor={p / t if t > 0 else 1.0:.3f} ratio")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print(f"RESULT swapins={resource.getrusage(resource.RUSAGE_SELF).ru_majflt} count")


def run_probe(line_no, old, new, cases, nulls):
    """Print one CASE line per input, then RESULT lines: the first case's outcome on each arm, the count
    of separating cases whose SysIdResult differs, and the count of null-control cases that differ."""
    mut = mutant_identify(line_no, old, new)
    moved = compare(mut, cases)
    null_moved = compare(mut, nulls) if nulls else 0
    if cases:
        name, smp = cases[0][0], cases[0][1]
        cfg = cases[0][2] if len(cases[0]) > 2 else None
        print(f"RESULT first_case={name}")
        print(f"RESULT outcome_baseline=[{short(call(SI.identify, smp, cfg))}]")
        print(f"RESULT outcome_mutant=[{short(call(mut, smp, cfg))}]")
    print(f"RESULT cases_differing={moved} count (of {len(cases)})")
    print(f"RESULT null_differing={null_moved} count (of {len(nulls)})")
    footer()
    return moved, null_moved


# ---- input builders the probes share -------------------------------------------------------------
S, T, R = sysid.PHASE_SETTLING, sysid.PHASE_STEP, sysid.PHASE_RELAX
ALT = [S, T, R] * 8


def relabel(smp, phases):
    return [sysid.SysIdSample(s.when, s.room_temp, s.outdoor_temp, s.power_kw, p) for s, p in zip(smp, phases)]


def insert_after(smp, idx, dt, bump=0.05):
    """smp with a copy of sample idx inserted after it, `dt` later and `bump` degC warmer, same phase."""
    q = list(smp)
    s = q[idx]
    q.insert(idx + 1, sysid.SysIdSample(when=s.when + dt, room_temp=s.room_temp + bump,
                                        outdoor_temp=s.outdoor_temp, power_kw=s.power_kw, phase=s.phase))
    return q


def exact_series(k, p, qs, outs, t0=20.0):
    """T[i+1] = T[i] - k (T[i] - Tout[i]) + p q[i] at dt = 1 h, phases alternating S/T/R so no in-phase
    triple exists (sigma2 = 0): rate = -k*delta + p*q holds to rounding."""
    temps = [t0]
    for q, o in zip(qs, outs):
        temps.append(temps[-1] - k * (temps[-1] - o) + p * q)
    n = len(temps)
    return samples(temps, list(outs) + [0.0], list(qs) + [0.0], ALT[:n], list(range(n)))


def collinear_series(c=2.0, k=0.25, outs=(24.0, 28.0, 26.0, 32.0, 30.0, 27.0, 34.0, 29.0, 31.0), t0=20.0):
    """power = c * (Tout - T) on every row, so the delta and power columns are exactly collinear (rank 1)."""
    temps, qs = [t0], []
    for o in outs:
        x = o - temps[-1]
        qs.append(c * x)
        temps.append(temps[-1] + k * x)
    n = len(temps)
    return samples(temps, list(outs) + [0.0], qs + [0.0], ALT[:n], list(range(n)))


def sigma_tie_series(break_tie=False):
    """Three in-phase triples (T, T+d, T) with d = u, 2u, 2u (u = 0.125) so the curvature term is 0 and
    sigma2 = 36u^2/18 = 0.03125 exactly; the delta column's deviations are (1,-1,.25,-.25,.25,-.25,0,0,0)
    around 20, so var*9/8/9 = 0.03125 exactly: sigma2 == x1_spread2/9 in float64."""
    u = 0.125
    temps = [20.0, 20.0 + u, 20.0, 21.0, 21.0 + 2 * u, 21.0, 22.0, 22.0 + 2 * u, 22.0, 21.5]
    phases = [S, S, S, T, T, T, R, R, R, S]
    devs = [1, -1, 0.25, -0.25, 0.25, -0.25, 0, 0, 0]
    outs = [t + 20 + d for t, d in zip(temps[:9], devs)] + [0.0]
    if break_tie:
        outs[0] += 0.0625
    return samples(temps, outs, [2, 2, 2, 5, 5, 5, 0, 0, 0, 2], phases, list(range(10)))
