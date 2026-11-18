"""D7.M3 -- learner freeze versus COP flow: which learner ingests a contaminated interval.

Metric: per (learner, contamination) cell, 1 if the production learner's own
sample counter moves on ONE interval carrying that contamination, else 0.
Counted key: the learner's delivered state -- DefrostDerate.counts (fallback
estimator, frost band, no defrost flag), coordinator._cop_samples
(_learn_measured_cop), coordinator._house_heat_loss_samples
(_async_learn_house_heat_loss) -- never an input attribute.
Headline: derate_ingests_distorted = number of the three draw-distorting
contaminations (immersion latch, pump backup heater, night-mode capacity cap)
that coordinator:_record_accuracy -> _settle_defrost -> DefrostDerate.observe
folds although coordinator:_cop_fold_blocked -- the predicate that makes
_learn_measured_cop (the learner the derate "learns from the same signal" as)
refuse the interval -- is True for it.
Also: derate_factor_after_24 = the frost-band bucket's derate factor after
24 contaminated intervals (capacity_limited: seeded at a learned 0.80), and
the clean control.

Command (repo root):
  PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D7/s2/learner_gates.py
Perturbation (in memory): --gate-derate wraps coordinator
HeatPumpOptimizerCoordinator._settle_defrost so it returns when
coordinator._cop_fold_blocked(self) (the one predicate the COP learner uses).
Expected: derate_ingests_distorted 3 -> 0 (to_zero); clean control stays 1.
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
from unittest import mock

from harness import FakeHass, FakeEntry, FakeState  # noqa: E402
from custom_components.heatpump_optimizer import coordinator as C  # noqa: E402
from custom_components.heatpump_optimizer import pump_signals as PS  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402

OUTDOOR = 2.0          # inside defrost.in_frost_band [0, 5)
COMMANDED = 3.0        # kW electrical the plan commanded (>= 0.3 * 6 kW floor)
ELEMENT = 3.0          # kW resistive element on the same meter

if "--gate-derate" in sys.argv:
    _orig = C.HeatPumpOptimizerCoordinator._settle_defrost

    def _gated(self, sample, window):
        if C._cop_fold_blocked(self):
            return
        return _orig(self, sample, window)
    C.HeatPumpOptimizerCoordinator._settle_defrost = _gated


def make():
    hass = FakeHass()
    hass.states.set("sensor.indoor", FakeState("21.0"))
    hass.states.set("sensor.outdoor", FakeState(str(OUTDOOR)))
    hass.states.set("sensor.hp_power", FakeState(str(COMMANDED * 1000), unit="W"))
    cfg = {
        "indoor_temp_entity": "sensor.indoor",
        "outdoor_temp_entity": "sensor.outdoor",
        "heat_pump_power_entity": "sensor.hp_power",
        "heat_pump_max_power": 6.0,
    }
    coord = C.HeatPumpOptimizerCoordinator(hass, FakeEntry(data=cfg))
    asyncio.run(coord._update_current_state())
    ctx = getattr(coord, "_ctx", coord)
    ctx._current_state.outdoor_temperature = OUTDOOR
    coord._current_action = {"power": COMMANDED, "space_power": COMMANDED,
                             "dhw_power": 0.0, "heat_pump_on": True}
    return coord


def contaminate(coord, arm):
    measured = COMMANDED
    if arm == "immersion_latch":
        coord._immersion_active = True
        measured = COMMANDED + ELEMENT
    elif arm == "backup_heater":
        coord._pump_signals = replace(
            coord._pump_signals,
            electric_heat=replace(coord._pump_signals.electric_heat, backup_heater=True))
        measured = COMMANDED + ELEMENT
    elif arm == "capacity_limited":
        coord._pump_signals = replace(
            coord._pump_signals,
            electric_heat=replace(coord._pump_signals.electric_heat, capacity_limited=True))
        measured = COMMANDED * 0.6
    coord._measured_power = measured


def derate_bucket_count(coord):
    return sum(sum(row) for row in coord._defrost.counts)


def settle_once(coord):
    coord._pending_prediction = {
        "when": dt_util.now() - timedelta(minutes=30),
        "power": COMMANDED, "space_power": COMMANDED, "dhw_power": 0.0,
        "predicted_temp": 21.0, "price": 1.0, "outdoor": OUTDOOR, "humidity": 85.0,
    }
    coord._record_accuracy()


def main():
    t0p, t0t = time.process_time(), time.thread_time()
    arms = ("clean", "immersion_latch", "backup_heater", "capacity_limited")
    distorted_ingest = 0
    for arm in arms:
        coord = make()
        contaminate(coord, arm)
        blocked = C._cop_fold_blocked(coord)
        before_d = derate_bucket_count(coord)
        settle_once(coord)
        derate = derate_bucket_count(coord) - before_d
        # The COP learner stands the whole frost band down on a flag-less
        # install (by design), so its own gate is exercised just outside it.
        getattr(coord, "_ctx", coord)._current_state.outdoor_temperature = 7.0
        before_c = coord._cop_samples
        coord._cop_ratio_ewma = coord._measured_power / COMMANDED  # let a shift through the blip gate
        coord._learn_measured_cop()
        cop = coord._cop_samples - before_c
        print(f"RESULT derate_ingest_{arm}={derate} count  # cop_fold_blocked={blocked}")
        print(f"RESULT cop_learner_ingest_{arm}={cop} count")
        if arm != "clean" and derate > 0 and blocked:
            distorted_ingest += 1
    print(f"RESULT derate_ingests_distorted={distorted_ingest} count  # of 3")
    # Walk: 24 intervals (12 h at the 30-min cadence) latched vs clean.
    for arm in ("clean", "immersion_latch", "backup_heater", "capacity_limited"):
        coord = make()
        if arm == "capacity_limited":
            # a bucket that already learned a real derate, then a capped night
            t, h = coord._defrost._bucket(OUTDOOR, 85.0)
            coord._defrost.factors[t][h] = 0.80
            coord._defrost.counts[t][h] = 30
        contaminate(coord, arm)
        for _ in range(24):
            settle_once(coord)
        f = coord._defrost.factor(OUTDOOR, 85.0)
        t, h = coord._defrost._bucket(OUTDOOR, 85.0)
        raw = coord._defrost.factors[t][h]
        print(f"RESULT derate_factor_after_24_{arm}={f:.4f} ratio  # published factor(); bucket raw={raw:.4f}")
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
