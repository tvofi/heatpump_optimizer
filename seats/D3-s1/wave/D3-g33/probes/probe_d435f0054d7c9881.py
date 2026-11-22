#!/usr/bin/env python3
"""D3-s1 (box D3-g33): step-4 probe for full-gate key d435f0054d7c9881, sysid.py:1557 BOOLOP.

Metric (one line): raised = number of the input horizons (None, empty array) on which conditions_met (KIND_FIT, default window, hour 1) raises instead of returning; ok_ramp = 1 when a 24-step ramp horizon passes (null arm).
Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g33/probes/probe_d435f0054d7c9881.py [--mutant]
Expected at the baseline: raised=0, ok_ramp=1. With --mutant: raised=2, ok_ramp=1. Counts exact (tolerance 0).
Inputs: price_horizon None, np.array([]), ramp 0.5..2.0 (24 steps), flat ones(24); price 0.5
Instrumented symbol: custom_components.heatpump_optimizer.sysid:SystemIdentification.conditions_met.
Perturbation: --mutant applies the one-line mutant BOOLOP at sysid.py:1557
  `if price_horizon is not None and len(price_horizon):` -> `if price_horizon is not None or len(price_horizon):`
  in memory to the baseline's own source (git show), never to the gate's tree; direction: raised 0 -> 2 (up); production never passes either: coordinator.py:6379 returns 'no_prices' before sysid when the horizon has < 4 steps.
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: cloud box D3-g33, Linux x86_64, nproc 4,
Intel Xeon @ 2.10GHz, 16 GB, venv-ci CPython. Wall numbers none; counts exact.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import importlib.util
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np

BASE = "92d38ecb640bd462f2e19c0814d0f0b7df1ee692"
OLD = '        if price_horizon is not None and len(price_horizon):'
NEW = '        if price_horizon is not None or len(price_horizon):'
LINE = 1557


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


def load(mutant: bool):
    import custom_components.heatpump_optimizer  # noqa: F401  (package context)
    text = subprocess.run(["git", "show", f"{BASE}:custom_components/heatpump_optimizer/sysid.py"],
                          cwd=ROOT, check=True, capture_output=True, text=True).stdout
    if mutant:
        lines = text.splitlines(True)
        assert lines[LINE - 1].rstrip("\n") == OLD, "mutated line not at its baseline line number"
        lines[LINE - 1] = NEW + "\n"
        text = "".join(lines)
    name = "custom_components.heatpump_optimizer.sysid_probe_g33"
    spec = importlib.util.spec_from_loader(name, loader=None)
    mod = importlib.util.module_from_spec(spec)
    mod.__package__ = "custom_components.heatpump_optimizer"
    sys.modules[name] = mod
    exec(compile(text, str(ROOT / "custom_components/heatpump_optimizer/sysid.py"), "exec"), mod.__dict__)
    return mod


T0 = datetime(2026, 1, 15, 23, 0, tzinfo=timezone.utc)

def cond(s, cfg, hour, outdoor=0.0, price=0.5, horizon="ramp", kind=None):
    sid = s.SystemIdentification(cfg)
    if kind is not None:
        sid.kind = kind
    if isinstance(horizon, str):
        horizon = np.linspace(0.5, 2.0, 24)
    now = datetime(2026, 1, 15, hour, 30, tzinfo=timezone.utc)
    return sid.conditions_met(now, outdoor, price, horizon, 0)


def open_hours(s, cfg):
    return [h for h in range(24) if cond(s, cfg, h)[1] != "outside the night window"]

def measure(s):
    cfg = s.SysIdConfig(enabled=True)
    raised = 0
    for h in (None, np.array([], dtype=float)):
        try:
            cond(s, cfg, 1, horizon=h, kind=s.KIND_FIT)
        except Exception:
            raised += 1
    yield "raised", raised
    yield "ok_ramp", int(cond(s, cfg, 1, kind=s.KIND_FIT)[0])
    yield "ok_flat", int(cond(s, cfg, 1, horizon=np.ones(24), kind=s.KIND_FIT)[0])


def _swapins():
    try:
        for line in open("/proc/vmstat"):
            if line.startswith("pswpin "):
                return int(line.split()[1])
    except OSError:
        pass
    return 0


if __name__ == "__main__":
    p0, t0 = time.process_time(), time.thread_time()
    s = load("--mutant" in sys.argv)
    for name, value in measure(s):
        print(f"RESULT {name}={value}")
    p1, t1 = time.process_time(), time.thread_time()
    print(f"RESULT thread_factor={(p1 - p0) / max(t1 - t0, 1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print(f"RESULT swapins={_swapins()}")
