#!/usr/bin/env python3
"""D3-s1 (box D3-top6): the first hour of sysid's midnight-wrapping night window, which the full gate does not pin.

Metric (one line): open_hours = how many of the 24 hours of a day SystemIdentification.conditions_met
does NOT refuse with "outside the night window", at the default SysIdConfig (start_hour 23,
end_hour 5), outdoor 0 C, a cheap current price, a varying price horizon. first_hour_open = 1 when the
start hour (23) itself is open.
Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/m26_probe.py [--mutant]
Expected at the baseline: open_hours=6 (23,0,1,2,3,4), first_hour_open=1. With --mutant (R10 C2 M26,
sysid.py L1549 `hour >= cfg.start_hour` -> `hour > cfg.start_hour`, applied in memory to a copy of
the module source): open_hours=5, first_hour_open=0. The full gate on that mutant (fullgate.py, key
8e82d7a0b3617003) is the D3.M3 verdict this probe answers step 4 for.
Null arm: a non-wrapping window (start 1, end 5) is identical under both arms (open_hours_flat=4).
Instrumented symbol: custom_components.heatpump_optimizer.sysid:SystemIdentification.conditions_met.
Perturbation: --mutant moves open_hours 6 -> 5 (down) and first_hour_open 1 -> 0.
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: owner macOS arm64. Counts exact.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import importlib.util
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[6]
sys.path.insert(0, str(ROOT))
SRC = ROOT / "custom_components/heatpump_optimizer/sysid.py"
OLD = "            in_window = hour >= cfg.start_hour or hour < cfg.end_hour"
NEW = "            in_window = hour > cfg.start_hour or hour < cfg.end_hour"
REASON = "outside the night window"


def load(mutant: bool):
    import custom_components.heatpump_optimizer  # noqa: F401  (package context)
    # The baseline's own source (git show), so a gate's committed mutant in this worktree never leaks in.
    import subprocess
    text = subprocess.run(["git", "show", "92d38ecb640bd462f2e19c0814d0f0b7df1ee692:custom_components/heatpump_optimizer/sysid.py"],
                          cwd=ROOT, check=True, capture_output=True, text=True).stdout
    if mutant:
        assert text.count(OLD) == 1, "wrapping-window line not found exactly once"
        text = text.replace(OLD, NEW)
    name = "custom_components.heatpump_optimizer.sysid_probe"
    spec = importlib.util.spec_from_loader(name, loader=None)
    mod = importlib.util.module_from_spec(spec)
    mod.__package__ = "custom_components.heatpump_optimizer"
    sys.modules[name] = mod
    exec(compile(text, str(SRC), "exec"), mod.__dict__)
    return mod


def open_hours(s, cfg):
    sid = s.SystemIdentification(cfg)
    horizon = np.linspace(0.5, 2.0, 24)
    out = []
    for h in range(24):
        now = datetime(2026, 1, 15, h, 30, tzinfo=timezone.utc)
        ok, why = sid.conditions_met(now, 0.0, 0.5, horizon, 0)
        if why != REASON:
            out.append(h)
    return out


def main() -> int:
    s = load("--mutant" in sys.argv)
    wrap = open_hours(s, s.SysIdConfig(enabled=True))
    flat = open_hours(s, s.SysIdConfig(enabled=True, start_hour=1, end_hour=5))
    print(f"RESULT open_hours={len(wrap)}  # {wrap}")
    print(f"RESULT first_hour_open={int(23 in wrap)}")
    print(f"RESULT open_hours_flat={len(flat)}")
    print("RESULT thread_factor=1.00")
    return 0


if __name__ == "__main__":
    sys.exit(main())
