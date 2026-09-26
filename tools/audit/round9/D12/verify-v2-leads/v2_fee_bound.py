#!/usr/bin/env python3
"""Verifier V2 (independent), D12-s3-81: grid-fee bounds are SEK constants
applied without a currency conversion.

METRIC (independent of the finder's harness -- different fee, different FX
table, and reads the schema/const source directly rather than only exercising
spec_problem/coordinator): for each of 8 currencies at an independently-picked
ordinary distribution fee (0.04 EUR/kWh, a different assumption from the
finder's 0.05) converted at a second FX table (rates independently rounded
from a different date/source than the finder's), blocked = 1 if
grid_fee.spec_problem flags the rules text as implausible OR the converted fee
exceeds the CONF_GRID_FEE_FIXED selector's hardcoded max (read from
config_flow._page_schema's grid_fees page, never hand-copied). Leave-one-out:
report the count with each currency dropped in turn (a grid of 8), and the
range across drops.
RUN (export root):
  PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D12/verify-v2-leads/v2_fee_bound.py
EXPECTED at 1936d5ca72a06556eeed4e8e5bf3dea520e517e1: HUF and KRW block (both
seams; JPY blocks only the selector-max seam because 0.04 EUR/kWh in JPY sits
just under the SEK-sized rules bound but over the fixed selector max); SEK/EUR/
NOK/DKK (null set) block 0 of 4. Leave-one-out range: dropping HUF or KRW still
leaves >=1 blocked currency (JPY); the aggregate is not a single-cell artefact.
Baseline SHA 1936d5ca72a06556eeed4e8e5bf3dea520e517e1.
Instrumented: heatpump_optimizer.grid_fee:spec_problem, IMPLAUSIBLE_FEE_SEK_PER_KWH;
  heatpump_optimizer.config_flow:_page_schema (grid_fee_fixed selector max, via
  CONF_GRID_FEE_FIXED / _number(0, 5, ...) at config_flow.py:1720).
"""
from __future__ import annotations

import os
import sys
import time

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

from harness import FakeHass  # noqa: E402
from heatpump_optimizer import config_flow as cf  # noqa: E402
from heatpump_optimizer import grid_fee  # noqa: E402

t0, th0 = time.process_time(), time.thread_time()

# A second FX table, independently rounded, at a different fee assumption
# (0.04 EUR/kWh, not the finder's 0.05), over a smaller currency set that
# overlaps only partially with the finder's (drops GBP/CHF/PLN/CZK, keeps the
# null arm and the 4 flagged currencies).
FX2 = {"EUR": 1.0, "SEK": 11.0, "NOK": 11.5, "DKK": 7.5,
       "HUF": 390.0, "ISK": 140.0, "JPY": 158.0, "KRW": 1400.0}
NULL = ("SEK", "EUR", "NOK", "DKK")
FEE_EUR = 0.04


def selector_max():
    h = FakeHass({})
    for key, sel in cf._page_schema("grid_fees", {}, h).schema.items():
        if str(key) == "grid_fee_fixed":
            return float(sel.config["max"])
    raise RuntimeError("grid_fee_fixed not found on grid_fees page")


MAX = selector_max()
print(f"RESULT grid_fee_fixed_selector_max={MAX:g} (currency-agnostic, read from schema)")
print(f"RESULT implausible_fee_sek_per_kwh={grid_fee.IMPLAUSIBLE_FEE_SEK_PER_KWH:g} SEK/kWh")

rows = {}
for cur, fx in FX2.items():
    fee = round(FEE_EUR * fx, 2)
    rules_blocked = grid_fee.spec_problem(f"= {fee}") == grid_fee.ERROR_IMPLAUSIBLE
    selector_blocked = fee > MAX
    rows[cur] = (fee, rules_blocked, selector_blocked)
    print(f"CUR {cur} fee={fee:g} rules_blocked={int(rules_blocked)} "
          f"selector_blocked={int(selector_blocked)}")

blocked_currencies = [c for c, (_, r, s) in rows.items() if r or s]
null_blocked = [c for c in NULL if rows[c][1] or rows[c][2]]
print(f"RESULT blocked_currencies={len(blocked_currencies)} of {len(FX2)} "
      f"({','.join(blocked_currencies)})")
print(f"RESULT null_blocked={len(null_blocked)} of {len(NULL)}")

# leave-one-out over the 8-currency grid
loo_counts = []
for drop in FX2:
    kept = [c for c in blocked_currencies if c != drop]
    loo_counts.append(len(kept))
    print(f"# LOO drop={drop}: blocked_remaining={len(kept)}")
print(f"RESULT loo_min={min(loo_counts)} loo_max={max(loo_counts)} count")

print(f"RESULT thread_factor={(time.process_time()-t0)/max(time.thread_time()-th0,1e-9):.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    sw = [ln for ln in open("/proc/vmstat") if ln.startswith("pswpin")][0].split()[1]
except Exception:
    sw = "n/a"
print(f"RESULT swapins={sw}")
