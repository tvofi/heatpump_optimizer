"""VERIFIER 3 own harness, D2-05 (independent drive of the same mechanism).

METRIC (one line): v3_comma_specs_valid = count of comma-rate specs for which
grid_fee.is_valid_spec is True (expect 0), vs v3_dotted_specs_valid for the
dot twins (expect all); plus v3_handedited_fee_sek = the SEK/kWh fee
GridFeeSchedule.from_config prices at Monday noon for a store carrying a
comma spec (expect 0.0), and the same under MY OWN one-line perturbation of
parse_rules (split on ";" and newlines only), where the fee must become the
intended 0.27.

EXACT COMMAND (from a tree root):
    PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
      MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
      /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 \
      tools/audit/round4/D2/verify03_d2_05.py

ROOT RULE: os.getcwd(). BASELINE SHA of the finding: 7dd68dd.
"""
from __future__ import annotations

import os
import sys

for _t in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_t, "1")

ROOT = os.getcwd()
sys.path.insert(0, os.path.join(ROOT, "tools", "audit", "round4", "D2"))
sys.path.insert(0, os.path.join(ROOT, "tests"))
sys.path.insert(0, os.path.join(ROOT, "tests", "hastub"))
sys.path.insert(0, os.path.join(ROOT, "custom_components"))

from datetime import datetime  # noqa: E402

from _d2common import Cpu, footer, result  # noqa: E402
from heatpump_optimizer import const, grid_fee  # noqa: E402

CPU = Cpu()

COMMA_SPECS = [
    "= 0,45",
    "Nov-Mar = 0,27",
    "Nov-Mar Mon-Fri 06:00-22:00 = 0,31",
    "Jan-Dec lör-sön = 0,12",
    "maj, jun = 0,05; jul = 0,03",
    "= 1,5; Nov-Mar = 0,75",
]
DOT_SPECS = [
    "= 0.45",
    "Nov-Mar = 0.27",
    "Nov-Mar Mon-Fri 06:00-22:00 = 0.31",
    "Jan-Dec lör-sön = 0.12",
    "maj, jun = 0.05; jul = 0.03",
    "= 1.5; Nov-Mar = 0.75",
]

with CPU:
    comma_ok = sum(1 for s in COMMA_SPECS if grid_fee.is_valid_spec(s))
    dot_ok = sum(1 for s in DOT_SPECS if grid_fee.is_valid_spec(s))
result("v3_specs", len(COMMA_SPECS), "count")
result("v3_comma_specs_valid", comma_ok, "count")
result("v3_dotted_specs_valid", dot_ok, "count")
result("v3_unit_rate_comma",
       grid_fee._parse_rule("= 0,45").rate, "SEK/kWh")

# a hand-edited store carrying a comma spec: what does the plan price at?
WHEN = datetime(2026, 1, 5, 12, 0)  # a Monday noon inside Nov-Mar
cfg = {const.CONF_GRID_FEE_MODE: grid_fee.MODE_RULES,
       const.CONF_GRID_FEE_RULES: "Nov-Mar Mon-Fri 06:00-22:00 = 0,27"}
with CPU:
    sched = grid_fee.GridFeeSchedule.from_config(cfg)
    fee_before = sched.current_fee(WHEN)
result("v3_handedited_rules", len(sched.rules), "count")
result("v3_handedited_fee_sek", fee_before, "SEK/kWh")

# my own perturbation: split on ';' and newlines only (one line changed)
_orig_parse_rules = grid_fee.parse_rules


def parse_rules_semicolon(spec):
    if not spec:
        return []
    raw = str(spec).replace("\n", ";")
    rules = []
    for line in raw.split(";"):
        line = line.strip()
        if line:
            rules.append(grid_fee._parse_rule(line))
    return rules


grid_fee.parse_rules = parse_rules_semicolon
try:
    result("v3_perturbed_comma_specs_valid",
           sum(1 for s in COMMA_SPECS if grid_fee.is_valid_spec(s)),
           "count")
    with CPU:
        sched2 = grid_fee.GridFeeSchedule.from_config(cfg)
        fee_after = sched2.current_fee(WHEN)
    result("v3_perturbed_handedited_rules", len(sched2.rules), "count")
    result("v3_perturbed_handedited_fee_sek", fee_after, "SEK/kWh")
finally:
    grid_fee.parse_rules = _orig_parse_rules

footer(CPU, "[v]erify03_d2_05")
