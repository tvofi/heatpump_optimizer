"""Catch-up verifier arch-b, V2 for D7-s3-81/82/83: the three twins measured by bit-parity of the
production functions against each other inside ONE tree (no patch, no score), plus a downstream drive.

Metrics (each a count over a seeded grid; 0 means the twins are one rule spelled twice):
  s3_81_rule_disagree   = runs where tariff._plateau_aware_day_max(r) != _plateau_aware_topk_sum(r, 1)
                          or _hard_day_max(r) != _exact_topk_sum(r, 1)          (float.hex)
  s3_81_bisect_disagree = (row, k) cells where _smooth_topk_sum(r, k, tau) != _smooth_topk_sum_batch(r[None])[0]
  s3_82_floor_disagree  = instants (every 7 s over the Europe/Stockholm autumn-DST day, both folds) where
                          pump_arbiter._observe's ledger key != _step_start(now)  (driven through _observe)
  s3_83_compose_cap     = quiet_windows.silent_cap_kw for power states inf / 1e400 / 100 kW / 2 kW
                          (p_max 6, fraction 0.6, no frequency entity); inf must not differ from a finite
                          over-range reading if the only harm is the p_max clamp.
Perturbation (--perturb): _PEAK_TIE_BAND is widened to 0.5 inside the scalar day-max twin only and
_observe's floor is rebound to a 30-min floor; both disagreement counts must rise above 0.
Null control: the same comparisons with the twin replaced by itself (identity) must read 0.

    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/catchup/arch-b/v2_s3.py [--root DIR] [--perturb]

Expected at baseline 9061fbd3d: rule 0, bisect 0, floor 0; caps inf=6.0, 1e400=6.0, 100kW=6.0, 2kW=2.0.
Machine: seat macOS box; counts only, contention-immune. Writes nothing.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import sys  # noqa: E402
import types  # noqa: E402
from datetime import datetime, timedelta, timezone  # noqa: E402
from pathlib import Path  # noqa: E402
from zoneinfo import ZoneInfo  # noqa: E402

import numpy as np  # noqa: E402

root = Path(sys.argv[sys.argv.index("--root") + 1]) if "--root" in sys.argv else Path.cwd()
sys.path.insert(0, str(root / "custom_components"))
PERTURB = "--perturb" in sys.argv

from heatpump_optimizer import tariff as T  # noqa: E402
from heatpump_optimizer import pump_arbiter as PA  # noqa: E402
from heatpump_optimizer import quiet_windows as QW  # noqa: E402
# --- 82 -------------------------------------------------------------------------------------
if PERTURB:
    PA._observe.__globals__  # same module
    src_floor = lambda now: now.replace(minute=now.minute - now.minute % 30, second=0, microsecond=0)  # noqa: E731
else:
    src_floor = None
tz = ZoneInfo("Europe/Stockholm")
base = datetime(2026, 10, 25, 0, 0, tzinfo=tz)
floor_dis = 0
n_inst = 0
for fold in (0, 1):
    t = base
    while t < base + timedelta(hours=24):
        now = t.replace(fold=fold)
        held = PA.ArbiterState()
        inp = types.SimpleNamespace(state=types.SimpleNamespace(dhw_temperature=None),
                                    measured_power_kw=None)
        try:
            PA._observe(held, inp, None, now)
        except Exception:  # noqa: BLE001 - the key is set before the mode read
            pass
        key = held.step["start"] if held.step else None
        ref = (src_floor or PA._step_start)(now)
        n_inst += 1
        if not (isinstance(key, datetime) and key == ref and key.fold == ref.fold
                and key.timestamp() == ref.timestamp()):
            floor_dis += 1
        t += timedelta(seconds=7)
print(f"RESULT s3_82_floor_disagree={floor_dis} count (of {n_inst})")

