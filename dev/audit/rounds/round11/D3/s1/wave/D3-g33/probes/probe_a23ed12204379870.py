#!/usr/bin/env python3
"""D3-s1 (box D3-g33): step-4 probe for full-gate key a23ed12204379870, sysid.py:1715 CMP_BOUND.

Metric (one line): refuses = 1 when SystemIdentification._unadoptable returns a reason when the declared night's halfwidth equals UA_ADOPTION_HALFWIDTH_BAR exactly (log 1.10), settle interval 15 min.
Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g33/probes/probe_a23ed12204379870.py [--mutant]
Expected at the baseline: refuses_tie=0, refuses_above=1, refuses_below=0. With --mutant: refuses_tie=1, refuses_above=1, refuses_below=0. Counts exact (tolerance 0).
Inputs: halfwidth == bar (stubbed, the tie), nextafter above/below, the real halfwidth on the dst_checks plant
Instrumented symbol: custom_components.heatpump_optimizer.sysid:SystemIdentification._unadoptable.
Perturbation: --mutant applies the one-line mutant CMP_BOUND at sysid.py:1715
  `if hw <= UA_ADOPTION_HALFWIDTH_BAR:` -> `if hw < UA_ADOPTION_HALFWIDTH_BAR:`
  in memory to the baseline's own source (git show), never to the gate's tree; direction: refuses_tie 0 -> 1 (up); halfwidths off the tie do not move.
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
OLD = '        if hw <= UA_ADOPTION_HALFWIDTH_BAR:'
NEW = '        if hw < UA_ADOPTION_HALFWIDTH_BAR:'
LINE = 1715


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
    bar = s.UA_ADOPTION_HALFWIDTH_BAR
    yield "refuses_tie", int(unadopt(s, 0.25, hw=bar)[0] is not None)
    yield "refuses_above", int(unadopt(s, 0.25, hw=float(np.nextafter(bar, 9.0)))[0] is not None)
    yield "refuses_below", int(unadopt(s, 0.25, hw=float(np.nextafter(bar, -9.0)))[0] is not None)
    why, seen = unadopt(s, 0.25)
    yield "refuses_real", int(why is not None)
    yield "halfwidth_real_minus_bar", repr([v - bar for v in seen])


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
