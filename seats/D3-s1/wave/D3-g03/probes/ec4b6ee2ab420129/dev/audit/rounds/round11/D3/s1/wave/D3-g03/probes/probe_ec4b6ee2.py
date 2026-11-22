#!/usr/bin/env python3
# Metric: thermal-learning saves (_async_save_thermal_learning awaits) and open-window INFO log records that
#   HeatPumpOptimizerCoordinator._async_learn_house_heat_loss makes on the cycle where the open-window detector's
#   state changes (its _vent_cusum.update returns True: trips on a sustained cold residual).
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g03/probes/probe_ec4b6ee2.py
# EXPECTED RESULT trip_saves_baseline=1 count log=1 ; trip_saves_mutant=0 count log=0 (the latched trip is not persisted
#   on the cycle it happens, so a restart before the next save forgets the open window and unfreezes the learners)
# EXPECTED RESULT null_delta=0 count (detector unchanged this cycle: neither arm saves)
# Harness: the replay seams are stubbed at module level for both arms alike (_replay_gate -> heat 2 kW, clean, not
#   frozen, no fold; _replay_fabric -> a predicted room 1.5 K warmer than the 19.0 C observed; learner_room_unread ->
#   False; _learned_zone_temperature -> the state's room temperature); the detector is a stub whose update() returns
#   the scripted change and records the residual it was fed.
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g03 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB).
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._async_learn_house_heat_loss,
#   line 5810 `if vent_changed:`.
# Perturbation: key ec4b6ee2ab420129 GUARD_OFF -> `if False:`, in memory. Direction: 1 save -> 0.
# Null control: a cycle on which the detector's state does not change.
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

FN = CLS._async_learn_house_heat_loss
MUT = mutant(FN, 5810, "        if vent_changed:", "        if False:")
T0 = datetime(2026, 1, 10, 3, 0, tzinfo=timezone.utc)


class _Count(logging.Handler):
    def __init__(self):
        super().__init__(logging.INFO)
        self.n = 0

    def emit(self, record):
        self.n += "Open-window detector" in record.getMessage()


def cycle(fn, changed):
    saves, fed = [], []

    async def save():
        saves.append(1)

    prev = SimpleNamespace(outdoor_temperature=-5.0, room_temperature=20.5, solar_radiation=0.0)
    interval = co.FabricInterval(prev, T0, T0 + timedelta(minutes=30), 0.5, 1.2)
    me = SimpleNamespace(
        _current_state=SimpleNamespace(room_temperature=19.0), _config=SimpleNamespace(), _thermal_params=SimpleNamespace(),
        _learning_frozen=lambda *a: None, _async_save_thermal_learning=save,
        _vent_cusum=SimpleNamespace(update=lambda now, r, ex: (fed.append(r), changed)[1], tripped=True, stat=4.2),
        _learner_freezes=SimpleNamespace(note_freeze=lambda *a: None),
    )

    async def replay(coord, iv, heat, label):
        return SimpleNamespace(room_temperature=20.5)

    h = _Count()
    co._LOGGER.addHandler(h)
    old = co._LOGGER.level
    co._LOGGER.setLevel(logging.INFO)
    try:
        with mock.patch.object(co, "_replay_gate", lambda *a: (2.0, True, None, False)), \
             mock.patch.object(co, "_replay_fabric", replay), \
             mock.patch.object(co, "learner_room_unread", lambda cfg: False), \
             mock.patch.object(co, "_learned_zone_temperature", lambda s, p: s.room_temperature):
            run(fn(me, interval))
    finally:
        co._LOGGER.removeHandler(h)
        co._LOGGER.setLevel(old)
    assert fed, "the detector was not reached"
    return len(saves), h.n


for arm, fn in (("baseline", FN), ("mutant", MUT)):
    s, n = cycle(fn, True)
    print(f"RESULT trip_saves_{arm}={s} count log={n}")
print(f"RESULT null_delta={int(cycle(FN, False) != cycle(MUT, False))} count")
tail()
