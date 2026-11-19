#!/usr/bin/env python3
# Metric: how many FeeRule objects grid_fee.parse_rules returns for the rules text "0.5" (a rate with no '=' part),
#   and the config-flow verdict grid_fee.spec_problem gives it. Baseline raises GridFeeError (-1 rules, 'invalid_grid_fee_rules').
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/probe_121362d4.py
# EXPECTED RESULT rules_baseline=-1 count  (GridFeeError raised; -1 stands for the raise)
# EXPECTED RESULT rules_mutant=1 count  (the bare "0.5" parses as one rule: rate 0.5, applies always)
# EXPECTED RESULT rules_delta=2 count
# EXPECTED RESULT verdict_baseline=invalid_grid_fee_rules
# EXPECTED RESULT verdict_mutant=None  (config flow would accept the text)
# EXPECTED RESULT null_delta=0 count  (well-formed "Mon-Fri = 0.25": same rules either arm)
# EXPECTED RESULT reach_calls_without_eq=2 count  (production entry points that hand _parse_rule a line with no '=')
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-rem (4 vCPU Xeon @ 2.10GHz).
# Instrumented symbol: custom_components.heatpump_optimizer.grid_fee:_parse_rule (line 173 guard `    if not sep:`),
#   reached through parse_rules (grid_fee.py:226), spec_problem (:242, config_flow.py:3927) and GridFeeSchedule.from_config (:287).
# Perturbation: GUARD_OFF `    if not sep:` -> `    if False:` applied in memory (function recompiled from its own source,
#   patched onto the module for the mutant arm only). Direction: rules parsed 0 (raise) -> 1; spec_problem 'invalid' -> None.
# Null control: a line with '=' where the guard is false either way; baseline and mutant parse identically.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import inspect, sys, textwrap
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[6]
sys.path.insert(0, str(ROOT))
from custom_components.heatpump_optimizer import grid_fee as gf  # noqa: E402

OLD = "    if not sep:"
NEW = "    if False:"


def mutant_fn():
    src = textwrap.dedent(inspect.getsource(gf._parse_rule))
    old = textwrap.dedent(OLD + "\n    pass").splitlines()[0]
    assert src.count(old) == 1, "anchor line moved"
    src = src.replace(old, textwrap.dedent(NEW + "\n    pass").splitlines()[0], 1)
    ns = dict(gf.__dict__)
    exec(compile(src, gf.__file__, "exec"), ns)
    return ns["_parse_rule"]


def n_rules(spec):
    try:
        return len(gf.parse_rules(spec))
    except gf.GridFeeError:
        return -1


mut = mutant_fn()
bad, good = "0.5", "Mon-Fri = 0.25"
rb, vb, gb = n_rules(bad), gf.spec_problem(bad), n_rules(good)
with mock.patch.object(gf, "_parse_rule", mut):
    rm, vm, gm = n_rules(bad), gf.spec_problem(bad), n_rules(good)

# Reach: spy on _parse_rule; production entry points fed a text with no '='.
seen = []
real = gf._parse_rule


def spy(line):
    seen.append("=" not in line)
    return real(line)


with mock.patch.object(gf, "_parse_rule", spy):
    gf.spec_problem(bad)  # config_flow.py:3927 path
    gf.GridFeeSchedule.from_config({"grid_fee_mode": gf.MODE_RULES, "grid_fee_rules": bad})  # store path
print(f"RESULT rules_baseline={rb} count")
print(f"RESULT rules_mutant={rm} count")
print(f"RESULT rules_delta={rm - rb} count")
print(f"RESULT verdict_baseline={vb}")
print(f"RESULT verdict_mutant={vm}")
print(f"RESULT null_delta={abs(gm - gb)} count")
print(f"RESULT reach_calls_without_eq={sum(seen)} count")
