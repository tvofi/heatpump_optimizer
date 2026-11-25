"""Shared loader for box D3-g36's probes (not a harness itself).

load(key) returns custom_components.heatpump_optimizer.sysid compiled from the BASELINE source
(`git show 92d38ecb:...sysid.py`, so a gate's committed mutant in this worktree never leaks in),
with the key's one-line mutant (old -> new at its line, from state/results/complete/<key>.json)
applied in memory when key is given. slab_sid(mod, ...) builds an armed SystemIdentification on a
declared slab plant (the shipped ThermalParameters defaults) with samples rolled through the
module's own two-state rollout (_simulate_slab_path), so identify_slab completes on the baseline.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import importlib.util
import json
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np

BASE = "92d38ecb640bd462f2e19c0814d0f0b7df1ee692"
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
S1 = ROOT / "dev/audit/rounds/round11/D3/s1"
_n = 0


def mutant(key):
    return json.loads((S1 / "state/results/complete" / f"{key}.json").read_text())["mutant"]


def load(key=None):
    global _n
    import custom_components.heatpump_optimizer  # noqa: F401  (package context)
    text = subprocess.run(["git", "show", f"{BASE}:{REL}"], cwd=ROOT, check=True,
                          capture_output=True, text=True).stdout
    if key:
        m = mutant(key)
        lines = text.split("\n")
        i = m["line"] - 1
        assert lines[i] == m["old"], f"line {m['line']} is {lines[i]!r}, not {m['old']!r}"
        lines[i] = m["new"]
        text = "\n".join(lines)
    _n += 1
    name = f"custom_components.heatpump_optimizer.sysid_g36_{_n}"
    spec = importlib.util.spec_from_loader(name, loader=None)
    mod = importlib.util.module_from_spec(spec)
    mod.__package__ = "custom_components.heatpump_optimizer"
    sys.modules[name] = mod
    exec(compile(text, str(ROOT / REL), "exec"), mod.__dict__)
    return mod


NOW = datetime(2026, 1, 15, 23, 30, tzinfo=timezone.utc)


def plant():
    from custom_components.heatpump_optimizer.thermal_model import ThermalParameters
    p = ThermalParameters()
    p.two_zone_enabled = False
    return p


def slab_sid(mod, ua=None, cr=None, g=0.3, n_settle=2, n_step=8, n_relax=12, dt=0.5,
             step_kw=4.0, noise=0.0, seed=1, prior=None, dts=None, settle_kw=0.5):
    """An armed SystemIdentification whose samples are the module's own two-state rollout."""
    p = plant()
    ms, ks = float(p.slab_thermal_mass), float(p.slab_heat_transfer)
    ua0, cr0 = float(p.heat_loss_coefficient), float(p.room_thermal_mass)
    ua = ua0 if ua is None else ua
    cr = cr0 if cr is None else cr
    sid = mod.SystemIdentification(mod.SysIdConfig(enabled=True))
    sid.arm(NOW)
    sid._slab_pair = (ms, ks)
    sid._slab_prior = prior if prior is not None else (ua0, cr0)
    sid._two_zone_plant = None
    n = n_settle + n_step + n_relax
    powers = np.array([settle_kw] * n_settle + [step_kw] * n_step + [0.0] * n_relax, float)
    dt_arr = np.full(n - 1, dt) if dts is None else np.asarray(dts, float)
    outd = np.full(n, 0.0)
    rooms = mod._simulate_slab_path(ua, cr, g, ms, ks, 20.0, outd[:-1], powers[:-1], dt_arr, None)
    rooms = np.asarray(rooms, float)
    if noise:
        rooms = rooms + np.random.default_rng(seed).normal(0.0, noise, rooms.size)
    phases = ([mod.PHASE_SETTLING] * n_settle + [mod.PHASE_STEP] * n_step
              + [mod.PHASE_RELAX] * n_relax)
    when, out = NOW, []
    for i in range(n):
        out.append(mod.SysIdSample(when, float(rooms[i]), 0.0, float(powers[i]), phases[i]))
        if i < n - 1:
            when += timedelta(hours=float(dt_arr[i]))
    sid.samples = out
    return sid


def fit(res):
    if not res.completed:
        return f"refused:{res.reason}"
    return (f"ua={res.heat_loss_kw_per_c:.9f} cap={res.thermal_mass_kwh_per_c:.9f} "
            f"tau={res.time_constant_hours:.9f} conf={res.confidence:.9f} hw={res.ua_profile_halfwidth:.9g}")


def footer(t0):
    cpu = time.process_time() - t0[0]
    thr = time.thread_time() - t0[1]
    print(f"RESULT thread_factor={cpu / thr if thr > 0 else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        sw = [l for l in open('/proc/vmstat') if l.startswith('pswpin')][0].split()[1]
    except Exception:
        sw = "0"
    print(f"RESULT swapins={sw}")


def start():
    return (time.process_time(), time.thread_time())


class RolloutCap(Exception):
    pass


def counted(mod, cap=20000):
    """Wrap mod._simulate_slab_path with a call counter that raises RolloutCap past `cap` calls.

    The count is contention-immune (it is the number of two-state rollouts the fit asks for)."""
    orig = mod._simulate_slab_path
    box = {"n": 0}

    def wrapped(*a, **k):
        box["n"] += 1
        if box["n"] > cap:
            raise RolloutCap()
        return orig(*a, **k)

    mod.__dict__["_simulate_slab_path"] = wrapped
    return box


def counted_outcome(mod, cap=20000, **kw):
    s = slab_sid(mod, **kw)  # sample generation runs before the counter is installed
    box = counted(mod, cap)
    try:
        r = fit(s.identify_slab())
    except RolloutCap:
        r = f"capped:>{cap} rollouts"
    except Exception as e:
        r = f"raises:{type(e).__name__}"
    return r, box["n"]
