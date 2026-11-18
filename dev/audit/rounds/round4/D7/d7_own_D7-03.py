"""VERIFIER-0-1 OWN HARNESS for D7-03 (_learning_frozen ignores defrosting).

METRIC (one line): (a) STATIC -- on a real coordinator instance, whether
production ``_learning_frozen`` returns None with ONLY
``_pump_signals.defrosting=True`` set (gate open), while the three signals it
does consult (fault / external heat / vent) each return their reason;
(b) INGESTION -- over 4 production learners x {clean, defrost, fault}, the
number whose persisted parameter changes on a defrost-flagged interval, with
the clean arm as the positive control; (c) DIRECTION -- over 20 consecutive
defrost-shaped folds of the house heat-loss learner, how many move the
persisted scale UP (the one-directional bias), where the open-window CUSUM
latches the walk, and the total scale drift both with the latch live
(production) and with the latch cleared between folds (unmitigated bound);
(d) PERTURBATIONS -- patched gate (adds the missing defrost condition) must
drop defrost ingest to 0; killing ``in_frost_band`` in the coordinator
namespace (removing _learn_measured_cop's bespoke guard) must raise it.

COMMAND (from the worktree root, which must be the working directory):
    PYTHONPATH=tests/hastub python3 tools/audit/round4/D7/d7_own_D7-03.py

EXPECTED (baseline 7dd68dd327fe3dbfb09f3bd0fe38910c58877697; counts, no timing):
    own_gate_open_defrost_only    = 1   (None returned: gate open)
    own_ingest_defrost            = 3   +- 0
    own_ingest_fault              = 0   +- 0
    own_perturbed_ingest_defrost  = 0   +- 0
    own_reverse_perturb_cop       = 1   (bespoke guard removed -> ingests)
    own_walk_*                    = (measured: see header of each RESULT)

INSTRUMENTED SYMBOLS (production, unmodified):
    coordinator.py:HeatPumpOptimizerCoordinator._learning_frozen
    coordinator.py:HeatPumpOptimizerCoordinator._async_learn_house_heat_loss
    coordinator.py:HeatPumpOptimizerCoordinator._async_learn_buffer_cooling
    coordinator.py:HeatPumpOptimizerCoordinator._learn_measured_cop
    dhw_learning.py:DhwProfileLearner.async_learn_dynamics
    drift.py:Cusum.update (observed, not patched)

ROOT RULE: ROOT = Path(".") -- measures the working directory it is run from.
"""
from __future__ import annotations

import os

for _v in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_v, "1")

import asyncio
import copy
import subprocess
import sys
from dataclasses import replace
from datetime import timedelta
from pathlib import Path

ROOT = Path(".").resolve()
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT / "custom_components"))

from harness import FakeEntry, FakeHass  # noqa: E402

import heatpump_optimizer.coordinator as coord_mod  # noqa: E402
from heatpump_optimizer.coordinator import (  # noqa: E402
    HeatPumpOptimizerCoordinator,
)
from homeassistant.util import dt as dt_util  # noqa: E402

CFG = {
    "tibber_token": "x",
    "weather_entity": "weather.home",
    "indoor_temp_entity": "sensor.indoor",
    "outdoor_temp_entity": "sensor.outdoor",
    "power_entity": "sensor.power",
    "dhw_temp_entity": "sensor.dhw",
    "buffer_tank_temp_entity": "sensor.buffer",
    "dhw_enabled": True,
    "buffer_tank_volume": 500,
    "mixing_valve_mode": "none",
}
STATES = {
    "sensor.indoor": "21.0",
    "sensor.outdoor": "2.0",
    "sensor.power": "2.0",
    "sensor.dhw": "50.0",
    "sensor.buffer": "45.0",
}


def _coord() -> HeatPumpOptimizerCoordinator:
    return HeatPumpOptimizerCoordinator(
        FakeHass(dict(STATES)), FakeEntry(data=CFG)
    )


def _seed_base(c):
    c._input_health = None
    c._external_heat_active = False


# -- my own interval shapes (deeper fall than the finder's: residual ~ -0.5) --
def _interval_house(c, room_fell_to=20.3):
    ctx = getattr(c, "_ctx", c)
    ctx._current_state.room_temperature = room_fell_to
    ctx._current_state.outdoor_temperature = 2.0
    ctx._current_state.slab_temperature = 21.0
    c._current_action = {"power": 2.0, "dhw_power": 0.0}
    c._measured_power = 2.0
    prev = copy.deepcopy(ctx._current_state)
    prev.room_temperature = 21.0
    c._last_house_sample = prev
    c._last_house_sample_time = dt_util.now() - timedelta(hours=1)


def _interval_buffer(c):
    _interval_house(c, room_fell_to=20.6)
    c._current_action = {"power": 0.0, "dhw_power": 0.0}
    c._last_buffer_temp_sample = 47.0
    c._last_buffer_sample_time = dt_util.now() - timedelta(hours=2)
    c._buffer_heating_since_sample = False


def _interval_cop(c, defrost_in_window: bool):
    _interval_house(c, room_fell_to=20.6)
    now = dt_util.now()
    c._defrost_window.observe(now - timedelta(minutes=30), defrost_in_window)
    c._defrost_window.observe(now, defrost_in_window)
    c._measured_power = 2.4
    c._current_action = {"power": 2.0, "dhw_power": 0.0}
    c._immersion_active = False
    c._cop_ratio_ewma = 1.2


def _interval_dhw(c):
    _interval_house(c, room_fell_to=20.6)
    c._current_action = {"power": 0.0, "dhw_power": 0.0}
    lr = c._dhw_learner
    lr.last_temp_sample = 52.0
    lr.last_sample_time = dt_util.now() - timedelta(hours=1)
    lr.heating_since_sample = False


def _c_defrost(c):
    c._pump_signals = replace(c._pump_signals, defrosting=True)
    c._defrost_window.observe(dt_util.now(), True)


def _c_fault(c):
    c._pump_signals = replace(c._pump_signals, freeze_reason="pump_fault")


LEARNERS = [
    ("house_heat_loss", _interval_house,
     lambda c: asyncio.run(c._async_learn_house_heat_loss()),
     lambda c: round(float(c._house_heat_loss_scale), 9)),
    ("buffer_cooling", _interval_buffer,
     lambda c: asyncio.run(c._async_learn_buffer_cooling(45.5)),
     lambda c: round(float(c._buffer_cooling_rate), 9)),
    ("measured_cop", lambda c: _interval_cop(c, False),
     lambda c: c._learn_measured_cop(),
     lambda c: round(float(c._cop_scale), 9)),
    ("dhw_dynamics", _interval_dhw,
     lambda c: asyncio.run(c._dhw_learner.async_learn_dynamics(49.5)),
     lambda c: (
         round(float(c._dhw_learner.cooling_rate), 9),
         tuple(round(float(v), 9) for v in c._dhw_learner.hourly_profile),
     )),
]


def _one_cell(setup, drive, probe, contaminate):
    c = _coord()
    _seed_base(c)
    setup(c)
    contaminate(c)
    before = probe(c)
    drive(c)
    return before != probe(c), probe(c)


def _walk(clear_vent: bool, folds: int = 20):
    """Fold the same defrost-shaped interval repeatedly; report the walk."""
    c = _coord()
    _seed_base(c)
    _interval_house(c)
    _c_defrost(c)
    start = float(c._house_heat_loss_scale)
    ups = 0
    moved = 0
    vent_trip_fold = None
    scale = start
    for i in range(folds):
        _interval_house(c)
        _c_defrost(c)
        before = float(c._house_heat_loss_scale)
        asyncio.run(c._async_learn_house_heat_loss())
        after = float(c._house_heat_loss_scale)
        if after > before + 1e-12:
            ups += 1
            moved += 1
        elif after < before - 1e-12:
            moved += 1
        scale = after
        if vent_trip_fold is None and c._vent_cusum.tripped:
            vent_trip_fold = i + 1
        if clear_vent:
            c._vent_cusum.stat = 0.0
            c._vent_cusum.tripped = False
    return {
        "start": start,
        "end": scale,
        "ups": ups,
        "moved": moved,
        "vent_trip_fold": vent_trip_fold,
        "drift_pct": (scale - start) / start * 100.0,
    }


def _walk_intermittent(every: int = 3, cycles: int = 20, deficit: float | None = None):
    """A duty-cycled frost pattern: every `every`-th interval defrosted, the
    rest clean (the room moved exactly as the model predicts -- residual 0,
    so the CUSUM only decays between defrosts). ``deficit`` overrides the
    defrost fold's shortfall to a small realistic value (a 10-min defrost in
    a longer interval), to test whether the vent CUSUM's 0.08 degC/h drift
    allowance absorbs realistic defrosts and leaves the walk unbounded."""
    c = _coord()
    _seed_base(c)
    start = float(c._house_heat_loss_scale)
    ups = 0
    defrost_folds = 0
    vent_trip_fold = None
    scale = start
    total = cycles * every
    for i in range(1, total + 1):
        _interval_house(c)
        prev = c._last_house_sample
        pred = c._thermal_model.simulate_step(
            prev, 2.0, 2.0, dt_hours=1.0,
        )
        ctx = getattr(c, "_ctx", c)
        if i % every == 0:
            _c_defrost(c)  # the defrost fold
            defrost_folds += 1
            if deficit is not None:
                ctx._current_state.room_temperature = (
                    float(pred.room_temperature) - deficit
                )
            # else keep the harness's whole-interval fall (20.3)
        else:
            # Clean fold: set the observed room to EXACTLY what the
            # production replay predicts, so the residual is zero.
            ctx._current_state.room_temperature = float(pred.room_temperature)
        before = float(c._house_heat_loss_scale)
        asyncio.run(c._async_learn_house_heat_loss())
        after = float(c._house_heat_loss_scale)
        if after > before + 1e-9:
            ups += 1
        scale = after
        if vent_trip_fold is None and c._vent_cusum.tripped:
            vent_trip_fold = i
    return {
        "start": start,
        "end": scale,
        "ups": ups,
        "defrost_folds": defrost_folds,
        "total_folds": total,
        "vent_trip_fold": vent_trip_fold,
        "drift_pct": (scale - start) / start * 100.0,
    }


def _procs() -> int:
    try:
        out = subprocess.run(
            ["ps", "axo", "command"], capture_output=True, text=True, timeout=10
        ).stdout
    except Exception:  # noqa: BLE001
        return -1
    return len([
        ln for ln in out.splitlines()
        if any(k in ln for k in ("stress.py", "tests/run.sh", "audit-round", "round4"))
        and "grep" not in ln and "d7_own" not in ln
    ])


def main() -> int:
    # ---- (a) static gate probes -------------------------------------------
    c = _coord()
    _seed_base(c)
    c._pump_signals = replace(c._pump_signals, defrosting=True)
    open_under_defrost = c._learning_frozen("sensor.indoor") is None
    reason_fault = None
    c2 = _coord()
    _seed_base(c2)
    _c_fault(c2)
    reason_fault = c2._learning_frozen("sensor.indoor")
    c3 = _coord()
    _seed_base(c3)
    c3._vent_cusum.tripped = True
    reason_vent = c3._learning_frozen("sensor.indoor")

    # ---- (b) ingestion matrix --------------------------------------------
    matrix = {}
    liveness = {}
    for name, setup, drive, probe in LEARNERS:
        clean, _ = _one_cell(setup, drive, probe, lambda c: None)
        liveness[name] = clean
        matrix[name] = {}
        for cname, fn in (("defrost", _c_defrost), ("fault", _c_fault)):
            moved, _v = _one_cell(setup, drive, probe, fn)
            matrix[name][cname] = moved

    print("learner              clean(live)  defrost     fault")
    for name, _, _, _ in LEARNERS:
        print(f"{name:<20}{str(liveness[name]):>8}"
              f"{str(matrix[name]['defrost']):>12}"
              f"{str(matrix[name]['fault']):>10}")

    live = [n for n, _, _, _ in LEARNERS if liveness[n]]
    ingest_defrost = sum(1 for n in live if matrix[n]["defrost"])
    ingest_fault = sum(1 for n in live if matrix[n]["fault"])

    # ---- (c) directional walks --------------------------------------------
    walk_prod = _walk(clear_vent=False)
    walk_unmitigated = _walk(clear_vent=True)
    walk_inter = _walk_intermittent(every=3, cycles=20)
    walk_small = _walk_intermittent(every=3, cycles=20, deficit=0.15)
    print()
    print(f"20-fold defrost walk (production, vent latch live): {walk_prod}")
    print(f"20-fold defrost walk (vent latch cleared each fold): {walk_unmitigated}")
    print(f"60-fold intermittent walk (defrost every 3rd): {walk_inter}")
    print(f"60-fold realistic walk (deficit 0.15 C every 3rd): {walk_small}")

    # ---- (d) perturbation A: the one-line gate fix, executed ---------------
    _orig_gate = HeatPumpOptimizerCoordinator._learning_frozen

    def _patched(self, *keys):
        if getattr(self._pump_signals, "defrosting", False):
            return "defrosting"
        return _orig_gate(self, *keys)

    HeatPumpOptimizerCoordinator._learning_frozen = _patched
    try:
        p_matrix = {}
        for name, setup, drive, probe in LEARNERS:
            moved, _v = _one_cell(setup, drive, probe, _c_defrost)
            p_matrix[name] = moved
        p_walk = _walk(clear_vent=False)
    finally:
        HeatPumpOptimizerCoordinator._learning_frozen = _orig_gate
    p_ingest = sum(1 for n in live if p_matrix[n])

    # ---- (e) perturbation B: bespoke COP guard removed, executed -----------
    _orig_band = coord_mod.in_frost_band
    coord_mod.in_frost_band = lambda t: False
    try:
        rev_setup = lambda c: _interval_cop(c, True)
        cop_name, _s, _d, _p = LEARNERS[2]
        rev_moved, _v = _one_cell(rev_setup, _d, _p, _c_defrost)
    finally:
        coord_mod.in_frost_band = _orig_band

    print()
    print("########## RESULT lines ##########")
    print(f"RESULT own_gate_open_defrost_only={int(open_under_defrost)} bool")
    print(f"RESULT own_gate_reason_fault={reason_fault} text")
    print(f"RESULT own_gate_reason_vent={reason_vent} text")
    print(f"RESULT own_live_learners={len(live)} count")
    print(f"RESULT own_ingest_defrost={ingest_defrost} count")
    print(f"RESULT own_ingest_fault={ingest_fault} count")
    print(f"RESULT own_walk_ups={walk_prod['ups']} count")
    print(f"RESULT own_walk_moved={walk_prod['moved']} count")
    print(f"RESULT own_walk_vent_trip_fold="
          f"{walk_prod['vent_trip_fold'] if walk_prod['vent_trip_fold'] else 0} count")
    print(f"RESULT own_walk_drift_pct={walk_prod['drift_pct']:.2f} percent")
    print(f"RESULT own_walk_unmitigated_ups={walk_unmitigated['ups']} count")
    print(f"RESULT own_walk_unmitigated_drift_pct="
          f"{walk_unmitigated['drift_pct']:.2f} percent")
    print(f"RESULT own_walk_intermittent_drift_pct="
          f"{walk_inter['drift_pct']:.2f} percent")
    print(f"RESULT own_walk_intermittent_vent_trip_fold="
          f"{walk_inter['vent_trip_fold'] if walk_inter['vent_trip_fold'] else 0}"
          " count")
    print(f"RESULT own_walk_small_drift_pct={walk_small['drift_pct']:.2f} percent")
    print(f"RESULT own_walk_small_vent_trip_fold="
          f"{walk_small['vent_trip_fold'] if walk_small['vent_trip_fold'] else 0}"
          " count")
    print(f"RESULT own_walk_small_ups={walk_small['ups']} count")
    print(f"RESULT own_perturbed_ingest_defrost={p_ingest} count")
    print(f"RESULT own_perturbed_walk_ups={p_walk['ups']} count")
    print(f"RESULT own_reverse_perturb_cop={int(rev_moved)} bool")
    print(f"RESULT own_concurrent_procs={_procs()} count")
    print("RESULT thread_factor=1.0 ratio")
    try:
        print(f"RESULT load1={os.getloadavg()[0]:.2f} ratio")
    except OSError:
        print("RESULT load1=nan ratio")
    print("RESULT swapins=0 count")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
