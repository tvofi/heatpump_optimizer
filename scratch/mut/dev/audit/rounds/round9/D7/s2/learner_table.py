"""D7.M3 -- the learner x contamination ingest table.

Metric: per (learner, contamination) cell, 1 if the production learner
ingests ONE interval carrying that contamination (its own counter/state
moves, or for the rows marked 'gate' the production gate it consults lets
the sample through), 0 if it refuses. Key: the learner's delivered state
(coordinator._house_heat_loss_samples, _internal_gains_profile,
_cop_samples, _defrost.counts, _curve_day_worst, _sysid.active) or, for
'gate' rows, the return of the gate function itself
(coordinator:_freq_fold_blocked, coordinator:_learning_frozen with the
DHW key the DHW learner passes).
Headline RESULTs: away_ingesting_learners (count of thermal learners that
ingest an away interval) and distorted_ingest_derate (the derate row's
ingest on immersion; see learner_gates.py for that finding's own harness).

Command (repo root):
  PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D7/s2/learner_table.py
Perturbation (in memory): --away-freezes makes coordinator
HeatPumpOptimizerCoordinator._learning_frozen return "away" while
_away_state.active; away_ingesting_learners must go to 0 (to_zero), and
every other column is unchanged.
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1, machine: cloud container B7.
Root rule: sys.path from the working directory.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys, time, asyncio
sys.path.insert(0, ".")
sys.path.insert(0, "tests")
from dataclasses import replace
from datetime import timedelta
import numpy as np

from harness import FakeHass, FakeEntry, FakeState  # noqa: E402
from custom_components.heatpump_optimizer import coordinator as C  # noqa: E402
from custom_components.heatpump_optimizer import const  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402

COMMANDED = 3.0

if "--away-freezes" in sys.argv:
    _orig_frozen = C.HeatPumpOptimizerCoordinator._learning_frozen

    def _frozen(self, *keys):
        if self._away_state.active:
            return "away"
        return _orig_frozen(self, *keys)
    C.HeatPumpOptimizerCoordinator._learning_frozen = _frozen

ARMS = ("clean", "external_heat", "defrost", "pump_offline", "pump_fault",
        "pump_cooling", "ventilation", "away", "immersion")


def make(outdoor):
    hass = FakeHass()
    hass.states.set("sensor.indoor", FakeState("21.0"))
    hass.states.set("sensor.outdoor", FakeState(str(outdoor)))
    hass.states.set("sensor.hp_power", FakeState(str(COMMANDED * 1000), unit="W"))
    hass.states.set("sensor.dhw", FakeState("50.0"))
    cfg = {
        "indoor_temp_entity": "sensor.indoor",
        "outdoor_temp_entity": "sensor.outdoor",
        "heat_pump_power_entity": "sensor.hp_power",
        "dhw_temp_entity": "sensor.dhw",
        "dhw_tank_volume": 200.0,
        "heat_pump_max_power": 6.0,
        const.CONF_INTERNAL_GAINS_LEARNING_ENABLED: True,
        const.CONF_CURVE_LEARNING_ENABLED: True,
        const.CONF_SYSID_ENABLED: True,
    }
    coord = C.HeatPumpOptimizerCoordinator(hass, FakeEntry(data=cfg))
    asyncio.run(coord._update_current_state())
    ctx = getattr(coord, "_ctx", coord)
    ctx._current_state.outdoor_temperature = outdoor
    ctx._current_state.room_temperature = 21.0
    coord._current_action = {"power": COMMANDED, "space_power": COMMANDED,
                             "dhw_power": 0.0, "heat_pump_on": True}
    coord._measured_power = COMMANDED
    return coord


def contaminate(coord, arm):
    s = coord._pump_signals
    if arm == "external_heat":
        coord._external_heat_active = True
    elif arm == "defrost":
        coord._pump_signals = replace(s, defrosting=True)
    elif arm == "pump_offline":
        coord._pump_signals = replace(s, online=False, freeze_reason="pump_offline")
    elif arm == "pump_fault":
        coord._pump_signals = replace(s, fault=True, freeze_reason="pump_fault")
    elif arm == "pump_cooling":
        coord._pump_signals = replace(s, freeze_reason="pump_cooling")
    elif arm == "ventilation":
        coord._vent_cusum.tripped = True
    elif arm == "away":
        coord._away_state.active = True
    elif arm == "immersion":
        coord._immersion_active = True
        coord._measured_power = COMMANDED + 3.0


def house(arm):
    coord = make(2.0)
    ctx = getattr(coord, "_ctx", coord)
    coord._last_house_sample = replace(ctx._current_state, room_temperature=21.0)
    coord._last_house_sample_time = dt_util.now() - timedelta(minutes=30)
    contaminate(coord, arm)
    n0 = coord._house_heat_loss_samples
    g0 = None if coord._internal_gains_profile is None else list(coord._internal_gains_profile)
    asyncio.run(coord._async_learn_house_heat_loss())
    g1 = coord._internal_gains_profile
    return (int(coord._house_heat_loss_samples > n0),
            int(g1 is not None and g1 != g0))


def cop(arm):
    coord = make(7.0)
    contaminate(coord, arm)
    coord._cop_ratio_ewma = coord._measured_power / COMMANDED
    n0 = coord._cop_samples
    coord._learn_measured_cop()
    return int(coord._cop_samples > n0)


def derate(arm):
    coord = make(2.0)
    contaminate(coord, arm)
    n0 = sum(sum(r) for r in coord._defrost.counts)
    coord._pending_prediction = {
        "when": dt_util.now() - timedelta(minutes=30), "power": COMMANDED,
        "space_power": COMMANDED, "dhw_power": 0.0, "predicted_temp": 21.0,
        "price": 1.0, "outdoor": 2.0, "humidity": 85.0}
    coord._record_accuracy()
    return int(sum(sum(r) for r in coord._defrost.counts) > n0)


def curve(arm):
    coord = make(2.0)
    contaminate(coord, arm)
    coord._curve_day_worst = None
    coord._track_curve_comfort(dt_util.now())
    return int(coord._curve_day_worst is not None)


def sysid(arm):
    coord = make(2.0)
    ctx = getattr(coord, "_ctx", coord)
    coord._sysid.config.enabled = True
    assert coord._sysid.arm(dt_util.now(), plant=ctx._thermal_params), coord._sysid.result.reason
    contaminate(coord, arm)
    coord._run_system_identification(np.ones(48))
    return int(coord._sysid.active)


def freq_gate(arm):
    coord = make(2.0)
    contaminate(coord, arm)
    blocked = (coord._measured_power is None or coord._immersion_active
               or C._freq_fold_blocked(coord))
    return int(not blocked)


def dhw_gate(arm):
    coord = make(2.0)
    contaminate(coord, arm)
    return int(coord._learning_frozen(const.CONF_DHW_TEMP_ENTITY) is None)


ROWS = (
    ("house_heat_loss", lambda a: house(a)[0], "learner"),
    ("internal_gains_53", lambda a: house(a)[1], "learner"),
    ("measured_cop", cop, "learner"),
    ("defrost_derate_fallback", derate, "learner"),
    ("curve_comfort_2", curve, "learner"),
    ("sysid_experiment", sysid, "learner"),
    ("freq_map_61", freq_gate, "gate"),
    ("dhw_dynamics", dhw_gate, "gate"),
)
THERMAL = {"house_heat_loss", "internal_gains_53", "sysid_experiment"}


def main():
    t0p, t0t = time.process_time(), time.thread_time()
    table = {}
    print("learner".ljust(26) + " ".join(a[:8].rjust(8) for a in ARMS))
    for name, fn, kind in ROWS:
        row = [fn(a) for a in ARMS]
        table[name] = dict(zip(ARMS, row))
        print(f"{name:<26}" + " ".join(str(v).rjust(8) for v in row) + f"   ({kind})")
    for name in table:
        for arm in ARMS:
            print(f"RESULT ingest_{name}_{arm}={table[name][arm]} count")
    away = sum(table[n]["away"] for n in THERMAL)
    print(f"RESULT away_ingesting_learners={away} count  # of {len(THERMAL)} heat-balance learners")
    print(f"RESULT distorted_ingest_derate={table['defrost_derate_fallback']['immersion']} count")
    p, t = time.process_time() - t0p, time.thread_time() - t0t
    print(f"RESULT thread_factor={p / max(t, 1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        sw = [l for l in open('/proc/vmstat') if l.startswith('pswpin')][0].split()[1]
    except Exception:
        sw = "na"
    print(f"RESULT swapins={sw}")


if __name__ == "__main__":
    main()
