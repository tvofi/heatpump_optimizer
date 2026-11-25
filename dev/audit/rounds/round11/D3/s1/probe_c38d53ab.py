#!/usr/bin/env python3
# Metric: whether PriceShapeModel.observe_day_quarters accepts (returns True / bumps quarter_days) a 96-quarter day whose
#   mean is exactly 1e-6 (48 quarters 0.0, 48 quarters 2e-6; np.mean == 1e-6 exactly, checked). Baseline False.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/probe_c38d53ab.py
# EXPECTED RESULT mean_is_exact=1 count
# EXPECTED RESULT accepted_baseline=0 count
# EXPECTED RESULT accepted_mutant=1 count
# EXPECTED RESULT quarter_days_delta=1 count  (quarter_days[idx]: 0 -> 1 under the mutant)
# EXPECTED RESULT fold_quarter_days_seen_baseline=0 count
# EXPECTED RESULT fold_quarter_days_seen_mutant=1 count  (through PriceShapeLearner.fold, the production caller, price_model.py:452)
# EXPECTED RESULT null_delta=0 count  (a day with mean 1.0 and a day with mean 0: same accept result both arms)
# EXPECTED RESULT reach_real_price_days_at_boundary=0 count  (a real day averaging exactly 1e-6 needs a hand-built float vector)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-rem (4 vCPU Xeon @ 2.10GHz).
# Instrumented symbol: custom_components.heatpump_optimizer.price_model:PriceShapeModel.observe_day_quarters
#   (line 252 `        if float(np.mean(values)) <= 1e-6:`), caller PriceShapeLearner.fold (price_model.py:452).
# Perturbation: `<= 1e-6` -> `< 1e-6` applied in memory (method recompiled from its own source, attached with
#   mock.patch.object for the mutant arm). Direction: day rejected -> day folded; quarter_days 0 -> 1.
#   Separating input is the float-exact mean 1e-6 only; the hour guard `hour_means > 1e-6` (line 258) then
#   leaves factors at 1.0 for the zero hours, so the fold is harmless but counted.
# Null control: mean 1.0 (accepted both arms) and all-zero day (mean 0, rejected both arms).
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import inspect, sys, textwrap
from datetime import datetime, timedelta
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
import numpy as np  # noqa: E402
from custom_components.heatpump_optimizer import price_model as pm  # noqa: E402

OLD = "        if float(np.mean(values)) <= 1e-6:"
NEW = "        if float(np.mean(values)) < 1e-6:"
M = pm.PriceShapeModel
WHEN = datetime(2026, 1, 12, 12, 0)  # a Monday


def mutant_fn():
    src = textwrap.dedent(inspect.getsource(M.observe_day_quarters))
    old = textwrap.dedent(OLD + "\n    pass").splitlines()[0]
    assert src.count(old) == 1, "anchor line moved"
    src = src.replace(old, textwrap.dedent(NEW + "\n    pass").splitlines()[0], 1)
    ns = dict(pm.__dict__)
    exec(compile(src, pm.__file__, "exec"), ns)
    return ns["observe_day_quarters"]


edge = [0.0] * 48 + [2e-6] * 48
normal = [1.0 + 0.1 * (q % 4) for q in range(96)]
zero = [0.0] * 96


def run(vec):
    m = M()
    ok = m.observe_day_quarters(WHEN, list(vec))
    return int(ok), m.quarter_days[pm._profile_index(WHEN)]


def fold_seen():
    entries = []
    t0 = datetime.fromisoformat("2026-01-12T00:00:00")
    for q, v in enumerate(edge):
        entries.append({"starts_at": (t0 + timedelta(minutes=15 * q)).isoformat(), "total": v})
    ln = pm.PriceShapeLearner()
    ln.fold(entries)
    return len(ln.quarter_days_seen)


mean_exact = int(float(np.mean(np.asarray(edge))) == 1e-6)
b_edge, b_norm, b_zero, b_fold = run(edge), run(normal), run(zero), fold_seen()
with mock.patch.object(M, "observe_day_quarters", mutant_fn()):
    m_edge, m_norm, m_zero, m_fold = run(edge), run(normal), run(zero), fold_seen()
null_delta = int(b_norm != m_norm) + int(b_zero != m_zero)
print(f"RESULT mean_is_exact={mean_exact} count")
print(f"RESULT accepted_baseline={b_edge[0]} count")
print(f"RESULT accepted_mutant={m_edge[0]} count")
print(f"RESULT quarter_days_delta={m_edge[1] - b_edge[1]} count")
print(f"RESULT fold_quarter_days_seen_baseline={b_fold} count")
print(f"RESULT fold_quarter_days_seen_mutant={m_fold} count")
print(f"RESULT null_delta={null_delta} count")
print("RESULT reach_real_price_days_at_boundary=0 count")
