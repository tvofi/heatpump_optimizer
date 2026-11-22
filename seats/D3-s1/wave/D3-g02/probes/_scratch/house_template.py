#!/usr/bin/env python3
# Metric: METRIC
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g02/probes/probe_KEY.py
# Expected: EXPECTED
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g02 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB);
#   counts and float values only, no timing (contention-immune).
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._async_learn_house_heat_loss,
#   line LINE `OLDTXT`.
# Perturbation: key KEY (KIND), `OLDTXT` -> `NEWTXT`, applied in memory: the method is recompiled from its own
#   source with that one line replaced and patched onto the class for the mutant arm only (never on disk).
#   DIRECTION
# Null control: NULLTXT
# Key of the count: the coordinator's own learner state after one real _async_learn_house_heat_loss call on the
#   interval _close_fabric_interval closes (features.py's _fabric_lower_samples fixture shape): house heat-loss scale,
#   its sample count, the open-window CUSUM statistic and trip flag, thermal-learning saves, and the return value.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import asyncio, inspect, sys, textwrap, time
from dataclasses import replace
from datetime import timedelta
from pathlib import Path
from unittest import mock


def repo_root(start):
    here = Path(start).resolve()
    if here.is_file():
        here = here.parent
    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
    for cand in (here, *here.parents):
        if (cand / marker).is_file():
            return cand
    raise RuntimeError(f"no repository root above {start}")


ROOT = repo_root(__file__)
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT / "custom_components"))
_cpu0, _th0 = time.process_time(), time.thread_time()
from harness import FakeEntry, FakeHass  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
from heatpump_optimizer import coordinator as co  # noqa: E402
from heatpump_optimizer.thermal_model import ThermalState  # noqa: E402

CLS = co.HeatPumpOptimizerCoordinator
FN = "_async_learn_house_heat_loss"
OLD = OLDREPR
NEW = NEWREPR


def mutant_fn():
    src = textwrap.dedent(inspect.getsource(getattr(CLS, FN)))
    lines = src.splitlines(keepends=True)
    hits = [i for i, ln in enumerate(lines) if ln.strip() == OLD]
    assert len(hits) == 1, f"anchor {OLD!r} found {len(hits)} times"
    ln = lines[hits[0]]
    lines[hits[0]] = ln[: len(ln) - len(ln.lstrip())] + NEW + "\n"
    ns = dict(co.__dict__)
    exec(compile("".join(lines), co.__file__, "exec"), ns)
    return ns[FN]


MUT = mutant_fn()


def run(arm, room0, outdoor, room1, hours=0.5, power=2.0, two_zone=False, upper0=None, upper1=None):
    """One dark learning interval room0 -> room1 at `outdoor`; returns the learner's observable state."""
    cfg = {"tibber_token": "x", "weather_entity": "weather.home",
           "indoor_temp_entity": "sensor.indoor", "outdoor_temp_entity": "sensor.outdoor"}
    if two_zone:
        cfg.update({"upper_floor_thermal_mass": 3.0, "lower_floor_thermal_mass": 8.0})
    c = CLS(FakeHass({}), FakeEntry(data=cfg))
    saves = []

    async def counted():
        saves.append(c._house_heat_loss_scale)

    c._async_save_thermal_learning = counted
    base = ThermalState(
        room_temperature=room0, upper_floor_temperature=room0 if upper0 is None else upper0,
        lower_floor_temperature=room0, slab_temperature=27.0,
        outdoor_temperature=outdoor, solar_radiation=0.0,
    )
    c._last_house_sample = base
    c._last_house_sample_time = dt_util.now() - timedelta(hours=hours)
    c._current_state = replace(base, room_temperature=room1,
                               upper_floor_temperature=room1 if upper1 is None else upper1)
    c._current_action = {"power": power}
    interval = c._close_fabric_interval()
    if arm == "mutant":
        with mock.patch.object(CLS, FN, MUT):
            ret = asyncio.run(c._async_learn_house_heat_loss(interval))
    else:
        ret = asyncio.run(c._async_learn_house_heat_loss(interval))
    return (c._house_heat_loss_scale, c._house_heat_loss_samples, c._vent_cusum.stat,
            bool(c._vent_cusum.tripped), len(saves), ret, interval is not None)


PRE

INPUTS = INPUTSLIST

moved = 0
for label, kw in INPUTS:
    b = run("baseline", **kw)
    m = run("mutant", **kw)
    d = int(b != m)
    moved += d
    for arm, r in (("baseline", b), ("mutant", m)):
        print(f"RESULT {label}_{arm}_scale={r[0]!r} samples={r[1]} cusum_stat={r[2]!r} tripped={int(r[3])} "
              f"saves={r[4]} returned={r[5]} interval={int(r[6])}")
    print(f"RESULT {label}_moved={d} count")
print(f"RESULT inputs_moved={moved} count of {len(INPUTS)}")
_cpu, _th = time.process_time() - _cpu0, time.thread_time() - _th0
print(f"RESULT thread_factor={_cpu / max(_th, 1e-9):.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    _sw = sum(int(l.split()[1]) for l in open("/proc/vmstat") if l.startswith("pswpin"))
except OSError:
    _sw = -1
print(f"RESULT swapins={_sw}")
