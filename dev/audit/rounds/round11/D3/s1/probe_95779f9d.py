#!/usr/bin/env python3
# Metric: the SOURCE label max_abs_component returns for a schedule whose fixed component and one rules rate tie exactly
#   (fixed=0.25, rule "= 0.25"), plus the tie of two equal-|rate| rules (value unchanged). Baseline label 'fixed'.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/probe_95779f9d.py
# EXPECTED RESULT label_baseline=fixed  (strict compare keeps the first holder, the fixed component)
# EXPECTED RESULT label_mutant=rules  (tie now hands the label to the rule)
# EXPECTED RESULT label_changed=1 count
# EXPECTED RESULT value_delta=0.0  (the returned magnitude is identical; only the source string moves)
# EXPECTED RESULT rules_tie_label_delta=0 count  (two rules of equal rate, no fixed tie: label 'rules' either arm; the rule choice is unobservable)
# EXPECTED RESULT null_label_delta=0 count  (rule strictly beyond fixed: both arms say 'rules')
# EXPECTED RESULT reach_from_config_tie=1 count  (GridFeeSchedule.from_config on a fixed=rate config produces the tied schedule)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-rem (4 vCPU Xeon @ 2.10GHz).
# Instrumented symbol: custom_components.heatpump_optimizer.grid_fee:max_abs_component (line 355 `            if abs(rule.rate) > worst:`), consumed at
#   coordinator.py:7623 (it is imported by name there, so this probe calls the module function directly; the
#   coordinator only forwards the label into a repair-issue placeholder).
# Perturbation: `            if abs(rule.rate) > worst:` -> `            if abs(rule.rate) >= worst:`, applied in memory (function recompiled from its own source, patched
#   onto the module for the mutant arm only). Direction: label 'fixed' -> 'rules' on a fixed/rule tie; the value is unchanged.
#   Between two RULES of equal rate the chosen rule differs but worst/source are the same, so that tie is equivalent.
# Null control: a rule strictly beyond the fixed component, where the comparison is decided without the tie.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import inspect, sys, textwrap
from pathlib import Path
from unittest import mock

def repo_root(start):
    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
    from pathlib import Path
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
from custom_components.heatpump_optimizer import grid_fee as gf  # noqa: E402

OLD = "            if abs(rule.rate) > worst:"
NEW = "            if abs(rule.rate) >= worst:"
FN = "max_abs_component"


def mutant_fn():
    src = textwrap.dedent(inspect.getsource(getattr(gf, FN)))
    old = textwrap.dedent(OLD + "\n    pass").splitlines()[0]
    assert src.count(old) == 1, "anchor line moved"
    src = src.replace(old, textwrap.dedent(NEW + "\n    pass").splitlines()[0], 1)
    ns = dict(gf.__dict__)
    exec(compile(src, gf.__file__, "exec"), ns)
    return ns[FN]


def sched(fixed, spec):
    return gf.GridFeeSchedule(mode=gf.MODE_RULES, fixed=fixed, rules=gf.parse_rules(spec))


tie = sched(0.25, "= 0.25")
rules_tie = sched(0.0, "Mon = 0.25, Tue = 0.25")
null = sched(0.25, "= 0.5")
fn = getattr(gf, FN)
b_tie, b_rt, b_null = fn(tie), fn(rules_tie), fn(null)
with mock.patch.object(gf, FN, mutant_fn()):
    mfn = getattr(gf, FN)
    m_tie, m_rt, m_null = mfn(tie), mfn(rules_tie), mfn(null)

cfg = gf.GridFeeSchedule.from_config({"grid_fee_mode": gf.MODE_RULES, "grid_fee_fixed": 0.25, "grid_fee_rules": "= 0.25"})
reach = int(cfg.fixed == cfg.rules[0].rate == 0.25)
print(f"RESULT label_baseline={b_tie[1]}")
print(f"RESULT label_mutant={m_tie[1]}")
print(f"RESULT label_changed={int(b_tie[1] != m_tie[1])} count")
print(f"RESULT value_delta={abs(m_tie[0] - b_tie[0])}")
print(f"RESULT rules_tie_label_delta={int(b_rt != m_rt)} count")
print(f"RESULT null_label_delta={int(b_null != m_null)} count")
print(f"RESULT reach_from_config_tie={reach} count")
