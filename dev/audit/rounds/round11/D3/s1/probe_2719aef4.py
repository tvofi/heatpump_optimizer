#!/usr/bin/env python3
# Metric: PriceShapeModel.expected_daily_min(day_types=[0], level=0.0) on a fully trusted model (shapes min 1.0):
#   baseline None ("no opinion"), and how many production call sites can pass level<=0.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/probe_2719aef4.py
# EXPECTED RESULT min_baseline=None
# EXPECTED RESULT min_mutant=0.0  (level 0 scaled by min shape 1.0: a zero price ceiling instead of "no opinion")
# EXPECTED RESULT mutant_is_not_none=1 count
# EXPECTED RESULT null_delta=0.0  (level=0.3 and level=-0.2/negative boundary: -0.2 -> None both arms; 0.3 -> 0.3 both arms)
# EXPECTED RESULT reach_callers_total=1 count  (coordinator.py is the only caller of expected_daily_min)
# EXPECTED RESULT reach_caller_guard_level_gt_1e6=1 count  (that caller only calls when `level > 1e-6`, so level==0.0 never arrives)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-rem (4 vCPU Xeon @ 2.10GHz).
# Instrumented symbol: custom_components.heatpump_optimizer.price_model:PriceShapeModel.expected_daily_min
#   (line 337 `        if not day_types or not np.isfinite(level) or level <= 0.0:`), caller coordinator.py:4361-4377.
# Perturbation: `level <= 0.0` -> `level < 0.0` applied in memory (method recompiled from its own source,
#   attached with mock.patch.object for the mutant arm). Direction: result None -> 0.0 at level == 0.0 only.
#   In production the sole caller is guarded by `if level > 1e-6` (coordinator.py:4370), so the boundary is
#   unreachable there: equivalent at the integration level, separable only by a direct unit call.
# Null control: level 0.3 (above the boundary) and level -0.2 (below it): same result both arms.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import inspect, re, sys, textwrap
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
from custom_components.heatpump_optimizer import price_model as pm  # noqa: E402

OLD = "        if not day_types or not np.isfinite(level) or level <= 0.0:"
NEW = "        if not day_types or not np.isfinite(level) or level < 0.0:"
M = pm.PriceShapeModel


def mutant_fn():
    src = textwrap.dedent(inspect.getsource(M.expected_daily_min))
    old = textwrap.dedent(OLD + "\n    pass").splitlines()[0]
    assert src.count(old) == 1, "anchor line moved"
    src = src.replace(old, textwrap.dedent(NEW + "\n    pass").splitlines()[0], 1)
    ns = dict(pm.__dict__)
    exec(compile(src, pm.__file__, "exec"), ns)
    return ns["expected_daily_min"]


model = M(days=[pm.SHAPE_CONFIDENCE_DAYS, pm.SHAPE_CONFIDENCE_DAYS])
levels = (0.0, 0.3, -0.2)
base = {lv: model.expected_daily_min([0], lv) for lv in levels}
with mock.patch.object(M, "expected_daily_min", mutant_fn()):
    mut = {lv: model.expected_daily_min([0], lv) for lv in levels}
null_delta = max(abs(mut[lv] - base[lv]) if base[lv] is not None and mut[lv] is not None
                 else float(base[lv] is not mut[lv]) for lv in (0.3, -0.2))

pkg = ROOT / "custom_components" / "heatpump_optimizer"
callers = [p.name for p in pkg.glob("*.py") if p.name != "price_model.py"
           and re.search(r"\.expected_daily_min\(", p.read_text())]
coord = (pkg / "coordinator.py").read_text()
i = coord.index("self._price_model.expected_daily_min(")
guard = "if level > 1e-6:" in coord[max(0, i - 400):i]
print(f"RESULT min_baseline={base[0.0]}")
print(f"RESULT min_mutant={mut[0.0]}")
print(f"RESULT mutant_is_not_none={int(mut[0.0] is not None)} count")
print(f"RESULT null_delta={null_delta}")
print(f"RESULT reach_callers_total={len(callers)} count")
print(f"RESULT reach_caller_guard_level_gt_1e6={int(guard)} count")
