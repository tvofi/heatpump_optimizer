#!/usr/bin/env python3
"""D3-s1 (box D3-g33): step-4 probe for full-gate key 95090bc58c6535b2, sysid.py:1913 CMP_BOUND.

Metric (one line): reached_fit = 1 when SystemIdentification.identify on exactly six usable samples (15-min cadence, tests/features.py:_sid_samples' plant) gets past both sample-count gates (its reason is neither 'not enough samples' nor 'not enough usable intervals').
Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g33/probes/probe_95090bc58c6535b2.py [--mutant]
Expected at the baseline: reached_fit_6=1, reached_fit_7=1, reached_fit_5=0. With --mutant: reached_fit_6=0, reached_fit_7=1, reached_fit_5=0. Counts exact (tolerance 0).
Inputs: 5, 6 (the tie), 7, 21 samples at 0.25 h on the features.py plant
Instrumented symbol: custom_components.heatpump_optimizer.sysid:SystemIdentification.identify.
Perturbation: --mutant applies the one-line mutant CMP_BOUND at sysid.py:1913
  `if len(usable) < 6:` -> `if len(usable) <= 6:`
  in memory to the baseline's own source (git show), never to the gate's tree; direction: reached_fit_6 1 -> 0 (down); 7 and 5 samples (null arms) do not move.
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
OLD = '        if len(usable) < 6:'
NEW = '        if len(usable) <= 6:'
LINE = 1913


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

def series(s, gaps_h, ua=0.12, c=6.0, g=0.5):
    """tests/features.py:_sid_samples' plant (UA 0.12, C 6.0, G 0.5, step 3 kW then relax, outdoor 0,
    room 20.7, Euler at <= 10-min substeps), sampled at the given interval lengths (hours); the
    first 12 samples (or the first ~40 %) are step, the rest relax."""
    n = len(gaps_h) + 1
    n_step = 12 if n >= 30 else max(2, (2 * n) // 5)
    when, temp, tout, out = datetime(2026, 2, 10, 0, 0, tzinfo=timezone.utc), 20.7, 0.0, []
    for i in range(n):
        step = i < n_step
        phase, power = (s.PHASE_STEP, 3.0) if step else (s.PHASE_RELAX, 0.0)
        out.append(s.SysIdSample(when, temp, tout, power, phase))
        if i < n - 1:
            dt = gaps_h[i]
            k = max(1, int(np.ceil(dt * 6 - 1e-9)))
            for _ in range(k):
                temp += (dt / k) * (power + g - ua * (temp - tout)) / c
            when = when + timedelta(seconds=round(dt * 3600.0, 6))
    return out


def fit(s, samples):
    sid = s.SystemIdentification(s.SysIdConfig(enabled=True))
    sid.samples = samples
    return sid.identify()


SHORT = ("not enough samples", "not enough usable intervals")


def reached(res):
    return int(res.reason not in SHORT)

def measure(s):
    for n in (5, 6, 7, 21):
        r = fit(s, series(s, [0.25] * (n - 1)))
        yield f"reached_fit_{n}", reached(r)
    yield "reason_6", repr(fit(s, series(s, [0.25] * 5)).reason)


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
