#!/usr/bin/env python3
# Metric: the lower-floor learner's state after one HeatPumpOptimizerCoordinator._async_learn_lower_floor_loss cycle
#   whose residual is non-finite: (_lower_floor_loss_ratio, _lower_floor_loss_samples, ratio applies, saves, return
#   value), plus DEBUG "Ignoring lower floor loss sample" log records, for residual NaN, +inf and -inf (observed or
#   predicted lower-floor temperature non-finite).
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g03/probes/probe_3351754d.py
# EXPECTED RESULT state_<case>_baseline == state_<case>_mutant = (1.0, 0, 0, 0, True) for all three cases:
#   _loss_residual_rejected (`abs(residual) <= HOUSE_LOSS_MAX_RESIDUAL` is False for NaN and inf) refuses the sample.
# EXPECTED RESULT states_moved=0 count ; debug_log_baseline=0 ; debug_log_mutant=3 (the only observable difference)
# EXPECTED RESULT positive_control_moved=1 count (a finite in-band residual folds: ratio and samples move in both arms,
#   so the harness can see a fold)
# Harness: _replay_gate -> (2 kW, clean, not frozen, fold) and _replay_fabric -> the scripted predicted state are
#   stubbed at module level for both arms; the Newton step and the ratio apply are production's.
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g03 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB).
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._async_learn_lower_floor_loss,
#   line 5940 `if not np.isfinite(residual):`.
# Perturbation: key 3351754da55a2896 GUARD_OFF -> `if False:`, in memory. Direction: none on state (equivalent);
#   +1 DEBUG record per non-finite sample.
# Null control: the finite residual (positive control above) moves identically in both arms.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import asyncio, inspect, sys, textwrap, time, types
from types import SimpleNamespace
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
from custom_components.heatpump_optimizer import coordinator as co  # noqa: E402

CLS = co.HeatPumpOptimizerCoordinator
_T0 = (time.process_time(), time.thread_time())


def mutant(fn, line, old, new):
    """`fn` recompiled from its own source with production line `line` replaced (in memory only)."""
    lines, start = inspect.getsourcelines(fn)
    i = line - start
    assert lines[i].rstrip("\n") == old, f"anchor moved: {lines[i]!r}"
    lines[i] = new + "\n"
    ns = dict(co.__dict__)
    exec(compile(textwrap.dedent("".join(lines)), co.__file__, "exec"), ns)
    f = ns[fn.__name__]
    # rebound onto the module's own globals, so a patch of a module name reaches both arms alike
    return types.FunctionType(f.__code__, co.__dict__, f.__name__, f.__defaults__, f.__closure__)


def run(coro):
    return asyncio.run(coro)


def tail():
    p, t = time.process_time() - _T0[0], time.thread_time() - _T0[1]
    print(f"RESULT thread_factor={p / t if t > 0 else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        sw = sum(int(l.split()[1]) for l in open("/proc/vmstat") if l.startswith("pswpin"))
    except OSError:
        sw = -1
    print(f"RESULT swapins={sw} count")

import logging  # noqa: E402
from datetime import datetime, timedelta, timezone  # noqa: E402

FN = CLS._async_learn_lower_floor_loss
MUT = mutant(FN, 5940, "        if not np.isfinite(residual):", "        if False:")
T0 = datetime(2026, 1, 10, 3, 0, tzinfo=timezone.utc)


class _Count(logging.Handler):
    def __init__(self):
        super().__init__(logging.DEBUG)
        self.n = 0

    def emit(self, record):
        self.n += "Ignoring lower floor loss sample" in record.getMessage()


def cycle(fn, observed, predicted):
    applied, saves = [], []

    async def save():
        saves.append(1)

    prev = SimpleNamespace(lower_floor_temperature=20.0, outdoor_temperature=-5.0, solar_radiation=0.0)
    interval = co.FabricInterval(prev, T0, T0 + timedelta(minutes=30), 0.5, 1.2)
    me = SimpleNamespace(
        _thermal_params=SimpleNamespace(two_zone_enabled=True, lower_floor_heat_loss=0.08, lower_floor_thermal_mass=4.0),
        _config=SimpleNamespace(lower_floor_temp_entity="sensor.lower"),
        _current_state=SimpleNamespace(lower_floor_temperature=observed), _learning_frozen=lambda *a: None,
        _house_heat_loss_scale=1.0, _lower_floor_loss_ratio=1.0, _lower_floor_loss_samples=0,
        _async_save_thermal_learning=save, _learner_freezes=SimpleNamespace(note_freeze=lambda *a: None),
    )
    me._apply_lower_floor_loss_ratio = lambda r: (applied.append(r), setattr(me, "_lower_floor_loss_ratio", r))

    async def replay(coord, iv, heat, label):
        return SimpleNamespace(lower_floor_temperature=predicted)

    h = _Count()
    co._LOGGER.addHandler(h)
    old = co._LOGGER.level
    co._LOGGER.setLevel(logging.DEBUG)
    try:
        with mock.patch.object(co, "_replay_gate", lambda *a: (2.0, True, None, True)), \
             mock.patch.object(co, "_replay_fabric", replay):
            ret = run(fn(me, interval))
    finally:
        co._LOGGER.removeHandler(h)
        co._LOGGER.setLevel(old)
    return (me._lower_floor_loss_ratio, me._lower_floor_loss_samples, len(applied), len(saves), ret), h.n


nan, inf = float("nan"), float("inf")
cases = {"nan_observed": (nan, 20.0), "pos_inf_residual": (19.8, -inf), "neg_inf_residual": (19.8, inf)}
moved, logs = 0, {"baseline": 0, "mutant": 0}
for name, (obs, pred) in cases.items():
    sb, lb = cycle(FN, obs, pred)
    sm, lm = cycle(MUT, obs, pred)
    print(f"RESULT state_{name}_baseline={sb}")
    print(f"RESULT state_{name}_mutant={sm}")
    moved += sb != sm
    logs["baseline"] += lb
    logs["mutant"] += lm
print(f"RESULT states_moved={moved} count")
print(f"RESULT debug_log_baseline={logs['baseline']} count")
print(f"RESULT debug_log_mutant={logs['mutant']} count")
pb, pm = cycle(FN, 19.8, 20.0)[0], cycle(MUT, 19.8, 20.0)[0]
print(f"RESULT positive_control_state_baseline={pb}")
print(f"RESULT positive_control_moved={int(pb != (1.0, 0, 0, 0, True) and pb == pm)} count")
tail()
