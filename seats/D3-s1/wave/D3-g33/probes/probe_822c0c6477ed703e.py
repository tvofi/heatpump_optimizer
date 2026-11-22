#!/usr/bin/env python3
"""D3-s1 (box D3-g33): step-4 probe for full-gate key 822c0c6477ed703e, sysid.py:1708 CMP_BOUND.

Metric (one line): consulted = 1 when SystemIdentification._unadoptable reads _declared_night_halfwidth (the gate's noise-free night) for two settle samples exactly 1e-3 h (3.6 s) apart; refuses = 1 when it returns a reason with the real halfwidth.
Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g33/probes/probe_822c0c6477ed703e.py [--mutant]
Expected at the baseline: consulted_tie=0, refuses_tie=0, consulted_null=1. With --mutant: consulted_tie=1, consulted_null=1 (refuses_tie as printed). Counts exact (tolerance 0).
Inputs: settle interval 0.001 h (the tie), 0.0009 h, 0.0011 h; null 0.25 h; real halfwidth and a stub returning 1.0 (> bar)
Instrumented symbol: custom_components.heatpump_optimizer.sysid:SystemIdentification._unadoptable.
Perturbation: --mutant applies the one-line mutant CMP_BOUND at sysid.py:1708
  `or self._baseline_temp is None or not 1e-3 < dt <= 2.0` -> `or self._baseline_temp is None or not 1e-3 <= dt <= 2.0`
  in memory to the baseline's own source (git show), never to the gate's tree; direction: consulted_tie 0 -> 1 (up); the 15-min null does not move.
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
OLD = '            or self._baseline_temp is None or not 1e-3 < dt <= 2.0'
NEW = '            or self._baseline_temp is None or not 1e-3 <= dt <= 2.0'
LINE = 1708


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

def unadopt(s, dt_h, hw=None):
    """_unadoptable on two settle samples dt_h apart, the dst_checks.py:2309 recipe."""
    sid = s.SystemIdentification(s.SysIdConfig(enabled=True))
    sid.samples = [s.SysIdSample(T0, 20.0, -2.0, 0.0, s.PHASE_SETTLING),
                   s.SysIdSample(T0 + timedelta(seconds=round(dt_h * 3600.0, 6)), 20.0, -2.0, 0.0,
                                 s.PHASE_SETTLING)]
    sid._slab_pair, sid._slab_prior, sid._baseline_temp = (8.0, 0.5), (0.2, 6.0), 20.0
    seen = []
    real = s._declared_night_halfwidth
    def hook(*a):
        v = real(*a) if hw is None else hw
        seen.append(v)
        return v
    s._declared_night_halfwidth = hook
    try:
        why = sid._unadoptable(1.0, -2.0)
    finally:
        s._declared_night_halfwidth = real
    return why, seen

def measure(s):
    why, seen = unadopt(s, 1e-3)
    yield "consulted_tie", len(seen)
    yield "refuses_tie", int(why is not None)
    yield "halfwidth_tie", repr(seen)
    yield "refuses_tie_stub", int(unadopt(s, 1e-3, hw=1.0)[0] is not None)
    yield "consulted_below", len(unadopt(s, 9e-4, hw=1.0)[1])
    yield "consulted_above", len(unadopt(s, 1.1e-3, hw=1.0)[1])
    yield "consulted_null", len(unadopt(s, 0.25, hw=1.0)[1])


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
