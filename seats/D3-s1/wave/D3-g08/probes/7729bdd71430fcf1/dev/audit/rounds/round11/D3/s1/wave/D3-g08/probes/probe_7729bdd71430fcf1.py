#!/usr/bin/env python3
# Metric: the fuse-advisor verdict HeatPumpOptimizerCoordinator._maybe_run_fuse_advisor leaves in _fuse_advisor
#   (published on the Monthly Peak sensor) and _fuse_advisor_at, or the exception it raises, after one run against a
#   stubbed what-if answer; key = the delivered dict.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g08/probes/probe_7729bdd71430fcf1.py
# Expected: the two differ only at breach == 0.0, where the clamp max(0.0, min(0.0, base - sim)) returns 0.0 for every finite, infinite or NaN difference, so the verdict is identical: moved 0 in every case (base above, equal and below sim; +-inf; NaN; a missing breach field read as 0.0). Exact (deterministic).
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g08 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB).
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._maybe_run_fuse_advisor
#   (coordinator.py:9022), scheduled after a solve at coordinator.py:6474.
# Perturbation: mutant 7729bdd71430fcf1 (CMP_BOUND) `if breach > 0.0 and base_cold is not None and sim_cold is not None:` -> `if breach >= 0.0 and base_cold is not None and sim_cold is not None:`, compiled in memory from the coroutine's source.
# Inputs: a SimpleNamespace coordinator (no _ctx) with a real EntryConfig (main_fuse_amperes per case, 3 phases) as
#   _config/effective_config and the real _fuse_kw bound to it; channels unblocked; baseline house load 0.5 kW;
#   _stored_fuse_advisor patched to return nothing stored; dt_util.now fixed at 2026-07-15 12:00 UTC; async_simulate
#   stubbed to echo the cap and return the case's what-if fields. Cases in CASES / NULLS.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import asyncio, inspect, sys, textwrap
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest import mock
sys.path.insert(0, str(Path.cwd()))
import numpy as np  # noqa: E402
from custom_components.heatpump_optimizer import coordinator as co  # noqa: E402
from custom_components.heatpump_optimizer.const import CONF_MAIN_FUSE_A, CONF_MAIN_FUSE_PHASES  # noqa: E402
from custom_components.heatpump_optimizer.entry_config import EntryConfig  # noqa: E402

CLS = co.HeatPumpOptimizerCoordinator
OLD, NEW = "if breach > 0.0 and base_cold is not None and sim_cold is not None:", "if breach >= 0.0 and base_cold is not None and sim_cold is not None:"


def mutant(fn):
    src = textwrap.dedent(inspect.getsource(fn))
    assert src.count(OLD) == 1, "anchor line moved"
    ns = dict(co.__dict__)
    exec(compile(src.replace(OLD, NEW, 1), co.__file__, "exec"), ns)
    return ns[fn.__name__]


MUT = mutant(CLS._maybe_run_fuse_advisor)
NOW = datetime(2026, 7, 15, 12, 0, tzinfo=timezone.utc)


async def _nothing_stored(_store):
    return None


def run(fn, amps, answer, prior=None, echo=True):
    cfg = EntryConfig.from_mapping({CONF_MAIN_FUSE_A: amps, CONF_MAIN_FUSE_PHASES: 3})
    calls = []

    async def simulate(overrides, limited=True, base=None, steady=False):
        calls.append(dict(overrides))
        out = dict(answer)
        if echo:
            out["overrides"] = {"power_cap_kw": overrides["power_cap_kw"]}
        return out

    me = SimpleNamespace(_config=cfg, effective_config=cfg, _ledger_store=None, _fuse_advisor_at=None,
                         _fuse_advisor=dict(prior or {}),
                         _pump_signals=SimpleNamespace(space_blocked=False, dhw_blocked=False, mode=None),
                         _baseline_house_load=lambda n: np.full(n, 0.5), async_simulate=simulate)
    me._fuse_kw = lambda: CLS._fuse_kw(me)
    try:
        with mock.patch.object(co.dt_util, "now", lambda: NOW), \
                mock.patch.object(co, "_stored_fuse_advisor", _nothing_stored):
            asyncio.run(fn(me, SimpleNamespace()))
    except Exception as exc:
        return f"raises {type(exc).__name__}: {exc}"
    return (tuple(sorted(me._fuse_advisor.items())),
            None if me._fuse_advisor_at is None else me._fuse_advisor_at.isoformat(), len(calls))


def ans(breach, base, sim):
    return {'power_cap_breach_c': breach, 'baseline_min_room_temperature': base, 'min_room_temperature': sim,
            'projected_peak_kw': 9.0, 'cost_delta_sek_steady': 1.0}
CASES = {
    'b0_base_above': dict(amps=25, answer=ans(0.0, 20.5, 20.0)),
    'b0_equal': dict(amps=25, answer=ans(0.0, 20.0, 20.0)),
    'b0_base_below': dict(amps=25, answer=ans(0.0, 19.0, 20.0)),
    'b0_inf': dict(amps=25, answer=ans(0.0, float('inf'), 20.0)),
    'b0_neg_inf': dict(amps=25, answer=ans(0.0, float('-inf'), 20.0)),
    'b0_nan': dict(amps=25, answer=ans(0.0, float('nan'), 20.0)),
    'b_neg_zero': dict(amps=25, answer=ans(-0.0, 19.0, 20.0)),
    'b_missing': dict(amps=25, answer={'baseline_min_room_temperature': 20.0, 'min_room_temperature': 21.0, 'projected_peak_kw': 9.0}),
}
NULLS = {'b_positive': dict(amps=25, answer=ans(0.3, 20.5, 20.4))}

moved = nmoved = 0
for name, kw in CASES.items():
    b, m = run(CLS._maybe_run_fuse_advisor, **kw), run(MUT, **kw)
    moved += int(b != m)
    print(f"RESULT {name}_baseline={b}")
    print(f"RESULT {name}_mutant={m}")
for name, kw in NULLS.items():
    b, m = run(CLS._maybe_run_fuse_advisor, **kw), run(MUT, **kw)
    nmoved += int(b != m)
    print(f"RESULT null_{name}_baseline={b} mutant={m}")
print(f"RESULT cases_moved={moved} count of {len(CASES)}")
print(f"RESULT null_moved={nmoved} count of {len(NULLS)}")
