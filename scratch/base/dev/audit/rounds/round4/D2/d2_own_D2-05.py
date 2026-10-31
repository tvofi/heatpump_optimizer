"""VERIFIER-OWN harness for round-4 D2-05 (seat D2-1, refute-first).

Independent of the finder's grid_fee_decimal_comma.py: (a) MY OWN spec
corpus (different strings, including a whole-spec comma list and Swedish
month/weekday spellings); (b) the unreachability is MEASURED, not read --
_parse_rule is monkeypatched to record every token it is handed, and the
harness counts how many contain a comma (must be 0, proving the
replace(",", ".") inside it is dead code); (c) the rejected spec's
degradation is measured at two timestamps inside and outside the declared
window.

METRIC (one line):
  own_specs_rejected = #{my corpus of decimal-comma specs that
  grid_fee.is_valid_spec rejects}, with the dotted equivalents accepted
  (null control); own_tokens_containing_comma = #{rate tokens _parse_rule
  ever received that contain ","} while parsing that corpus (contract: any,
  if the conversion is reachable; measured: 0).

EXACT COMMAND (from a tree root):
  PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
    MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
    /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 \
    tools/audit/round4/D2/d2_own_D2-05.py

EXPECTED (baseline 7dd68dd; exact counts, tolerance 0):
  own_specs_tested            = 7
  own_specs_rejected          = 7
  own_dotted_ok               = 7      (null control)
  own_tokens_containing_comma = 0      (the conversion is unreachable)
  own_unit_comma_rate         = 0.45   (_parse_rule itself accepts "= 0,45")
  own_fragment1_rate          = 0.0    (the silent zero the split produces)
  own_schedule_fee_after_reject_jan = 0.0
  own_schedule_fee_after_reject_jul = 0.0
  own_perturbed_specs_rejected = 0     (split on ";" / newline only)
  own_perturbed_fee_jan       = 0.4    (the rule's own rate)

INSTRUMENTED SYMBOLS: grid_fee.py:parse_rules (monkeypatched wrapper counts
tokens), grid_fee.py:_parse_rule (wrapped, then driven alone),
grid_fee.py:is_valid_spec, grid_fee.py:GridFeeSchedule.from_config /
current_fee.
PERTURBATION (executed in-section 4): parse on ";" and newline only.
NULL CONTROL: dotted equivalents all parse.

ROOT RULE: os.getcwd(). BASELINE SHA: 7dd68dd; measured on branch head
0855277 (custom_components/ diff vs baseline: version strings only).
MACHINE: 8-core Apple M1, macOS 25.6.0, python 3.11.5.
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

from datetime import datetime, timezone  # noqa: E402

from _d2common import Cpu, footer, result  # noqa: E402
from heatpump_optimizer import const, grid_fee  # noqa: E402

CPU = Cpu()

SPECS = [
    "nov-mar = 0,40",                       # Swedish lowercase months
    "man-fre 06:00-22:00 = 0,55",           # Swedish weekdays
    "lor 22:00-06:00 = 0,12",               # wrap-around night window
    "Nov-Mar 07:00-19:00 = 1,25; = 0,40",   # two comma rates, one line each
    "apr-okt = 0,05\nnov-mar = 0,35",       # newline-separated, both comma
    "Jan-Dec 06:00-22:00 = 0,60",
    "= 0,33",
]

# --- 1. the corpus: rejected with comma, accepted with a dot -----------------
with CPU:
    rejected = sum(1 for s in SPECS if not grid_fee.is_valid_spec(s))
    dotted = sum(
        1 for s in SPECS
        if grid_fee.is_valid_spec(s.replace(",", ".")))
result("own_specs_tested", len(SPECS), "count")
result("own_specs_rejected", rejected, "count")
result("own_dotted_ok", dotted, "count")

# --- 2. unreachability MEASURED: count commas in tokens _parse_rule sees ------
seen_tokens: list[str] = []
_orig_parse_rule = grid_fee._parse_rule


def spying_parse_rule(line):
    body, sep, rate_token = line.rpartition("=")
    seen_tokens.append(rate_token)
    return _orig_parse_rule(line)


grid_fee._parse_rule = spying_parse_rule
try:
    with CPU:
        for s in SPECS:
            try:
                grid_fee.parse_rules(s)
            except grid_fee.GridFeeError:
                pass
finally:
    grid_fee._parse_rule = _orig_parse_rule
result("own_tokens_seen", len(seen_tokens), "count")
result("own_tokens_containing_comma",
       sum(1 for t in seen_tokens if "," in t), "count")

# the unit on its own does convert (the dead code, proven alive-but-dead)
with CPU:
    r = grid_fee._parse_rule("= 0,45")
result("own_unit_comma_rate", float(r.rate), "SEK/kWh")
# and the first fragment of a split rate is a SILENT zero
with CPU:
    frag = grid_fee._parse_rule("nov-mar = 0")
result("own_fragment1_rate", float(frag.rate), "SEK/kWh")

# --- 3. what a rejected spec prices at, inside and outside its window ---------
cfg = {
    const.CONF_GRID_FEE_MODE: grid_fee.MODE_RULES,
    const.CONF_GRID_FEE_RULES: "nov-mar 07:00-19:00 = 0,40",
    const.CONF_GRID_FEE_FIXED: 0.0,
}
with CPU:
    sched = grid_fee.GridFeeSchedule.from_config(cfg)
    fee_jan = sched.current_fee(datetime(2026, 1, 15, 12, 0,
                                         tzinfo=timezone.utc))
    fee_jul = sched.current_fee(datetime(2026, 7, 15, 12, 0,
                                         tzinfo=timezone.utc))
result("own_schedule_rules_after_reject", len(sched.rules), "count")
result("own_schedule_fee_after_reject_jan", float(fee_jan), "SEK/kWh")
result("own_schedule_fee_after_reject_jul", float(fee_jul), "SEK/kWh")

# --- 4. perturbation: split on ";" and newline only ---------------------------
_orig_parse_rules = grid_fee.parse_rules


def parse_rules_semicolon(spec):
    if not spec:
        return []
    raw = str(spec).replace("\n", ";")
    out = []
    for line in raw.split(";"):
        line = line.strip()
        if line:
            out.append(grid_fee._parse_rule(line))
    return out


grid_fee.parse_rules = parse_rules_semicolon
try:
    with CPU:
        pert_rejected = sum(1 for s in SPECS
                            if not grid_fee.is_valid_spec(s))
        sched2 = grid_fee.GridFeeSchedule.from_config(cfg)
        fee2 = sched2.current_fee(datetime(2026, 1, 15, 12, 0,
                                           tzinfo=timezone.utc))
finally:
    grid_fee.parse_rules = _orig_parse_rules
result("own_perturbed_specs_rejected", pert_rejected, "count")
result("own_perturbed_fee_jan", float(fee2), "SEK/kWh")

footer(CPU, "[d]2_own_D2-05")
