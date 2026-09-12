"""D2 round 4, finding D2-05: the decimal-comma handling `_parse_rule`
implements for a grid-fee rate is unreachable, because `parse_rules` has
already split the specification on that same comma.

METRIC (one line): `specs_rejected` = how many of the N decimal-comma fee
specifications `grid_fee.is_valid_spec` rejects, where the identical
specification written with a decimal point is accepted, and
`unit_accepts_comma` = whether `grid_fee._parse_rule` -- the function whose
body contains `rate_token.strip().replace(",", ".")` -- accepts the same
rate token on its own. Contract: a module that spells Swedish month and
weekday names ("maj", "lor", "son") and writes a comma-to-point conversion
for its rate should accept a Swedish decimal comma; measured,
specs_rejected == N and unit_accepts_comma == 1, so the conversion is dead
code and the format it exists for is refused.

WHY (re-derivable): `parse_rules` does
    raw = str(spec).replace(";", ",").replace("\\n", ",")
    for line in raw.split(","): ...
so "Nov-Mar 06:00-22:00 = 0,27" reaches `_parse_rule` as the two fragments
"Nov-Mar 06:00-22:00 = 0" and "27"; the first parses to a rate of 0.0 and
the second has no "=" and raises. The `.replace(",", ".")` inside
`_parse_rule` can only ever see a token that no longer contains a comma.

EXACT COMMAND (from the export root):
    PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
      MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
      /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 \
      tools/audit/round4/D2/grid_fee_decimal_comma.py

EXPECTED (baseline 7dd68dd): exact counts, tolerance 0.
    specs_tested            = 6
    specs_rejected          = 6
    dotted_equivalents_ok   = 6      (null control: the same specs with a
                                      decimal point all parse)
    unit_accepts_comma      = 1      (_parse_rule alone takes "= 0,45" and
                                      returns rate 0.45)
    first_fragment_rate     = 0.0    (what "= 0,45" would have become had the
                                      second fragment parsed: a SILENT zero,
                                      which is why the split matters and not
                                      only the rejection)
    schedule_fee_after_reject = 0.0  (GridFeeSchedule.from_config degrades a
                                      broken spec to no fees at all -- so a
                                      hand-edited or migrated store carrying
                                      a comma prices with zero grid fee and
                                      only a log line)

INSTRUMENTED SYMBOLS: grid_fee.py:parse_rules, grid_fee.py:_parse_rule,
grid_fee.py:is_valid_spec, grid_fee.py:spec_problem,
grid_fee.py:GridFeeSchedule.from_config, grid_fee.py:GridFeeSchedule.fee_vector.

PERTURBATION (the judge runs it): split on a separator the rate cannot
contain -- change `parse_rules`'s `raw.split(",")` to split on ";" and
newlines only (one line). Under it `specs_rejected` must FALL to 0 and
`schedule_fee_after_reject` must RISE to the rule's own rate. Section 3
executes exactly that perturbation in-process and prints both.

NULL CONTROL: `dotted_equivalents_ok` -- the same six specs with a decimal
point must all parse, or the harness is measuring the grammar and not the
separator.

ROOT RULE: os.getcwd(); resolves nothing from __file__.
BASELINE SHA: 7dd68dd327fe3dbfb09f3bd0fe38910c58877697 (export, no .git).
MACHINE: 8-core Apple M1, 8 GB, macOS 25.6.0, python 3.11.5, numpy 2.4.6.
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
    "= 0,45",
    "Nov-Mar 06:00-22:00 = 0,27",
    "maj = 0,20",
    "Mon-Fri 07:00-19:00 = 1,05",
    "lor 00:00-24:00 = 0,09",
    "= 0,18; Nov-Mar Mon-Fri 06:00-22:00 = 0,27",
]

with CPU:
    rejected = sum(1 for s in SPECS if not grid_fee.is_valid_spec(s))
    dotted_ok = sum(
        1 for s in SPECS
        if grid_fee.is_valid_spec(s.replace(",", ".").replace(";", ","))
    )
result("specs_tested", len(SPECS), "count")
result("specs_rejected", rejected, "count")
result("dotted_equivalents_ok", dotted_ok, "count")
result("first_spec_problem", str(grid_fee.spec_problem(SPECS[0])))
result("error_key_is_invalid",
       int(grid_fee.spec_problem(SPECS[0]) == grid_fee.ERROR_INVALID), "bool")

with CPU:
    rule = grid_fee._parse_rule("= 0,45")
result("unit_accepts_comma", int(abs(rule.rate - 0.45) < 1e-12), "bool")
result("unit_rate", float(rule.rate), "SEK/kWh")

# What the first fragment of a comma rate becomes on its own: a silent 0.0.
with CPU:
    frag = grid_fee._parse_rule("Nov-Mar 06:00-22:00 = 0")
result("first_fragment_rate", float(frag.rate), "SEK/kWh")

# And what the plan is priced with once from_config degrades the spec.
cfg = {
    const.CONF_GRID_FEE_MODE: grid_fee.MODE_RULES,
    const.CONF_GRID_FEE_RULES: "Nov-Mar 06:00-22:00 = 0,27",
    const.CONF_GRID_FEE_FIXED: 0.0,
}
with CPU:
    sched = grid_fee.GridFeeSchedule.from_config(cfg)
    fee = sched.current_fee(datetime(2026, 1, 15, 12, 0, tzinfo=timezone.utc))
result("schedule_rules_after_reject", len(sched.rules), "count")
result("schedule_fee_after_reject", float(fee), "SEK/kWh")

# --- the perturbation, executed --------------------------------------------
_orig = grid_fee.parse_rules


def parse_rules_semicolon_only(spec):
    if not spec:
        return []
    raw = str(spec).replace("\n", ";")
    out = []
    for line in raw.split(";"):
        line = line.strip()
        if line:
            out.append(grid_fee._parse_rule(line))
    return out


grid_fee.parse_rules = parse_rules_semicolon_only
try:
    with CPU:
        pert_rejected = sum(
            1 for s in SPECS if not grid_fee.is_valid_spec(s))
        sched2 = grid_fee.GridFeeSchedule.from_config(cfg)
        fee2 = sched2.current_fee(
            datetime(2026, 1, 15, 12, 0, tzinfo=timezone.utc))
    result("perturbed.specs_rejected", pert_rejected, "count")
    result("perturbed.schedule_fee_after_reject", float(fee2), "SEK/kWh")
finally:
    grid_fee.parse_rules = _orig

footer(CPU, "[g]rid_fee_decimal_comma")
