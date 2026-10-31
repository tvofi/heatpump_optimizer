"""#1736's acceptance instrument: what a solve writes into the coordinator's
hubs, and whether the what-if prices what the live solve planned.

Metrics, one line each, all from one real HeatPumpOptimizerCoordinator on the
tests/harness.py FakeHass with injected hourly prices and weather, the clock
frozen, every solve run in-process through a transport that accepts either
hand-off shape (the positional one before #1736, the record after):

  hub_fields_moved_in_solve   compared fields of _opt_config, _thermal_params
                              and _current_state that differ, WHILE the solve
                              is parked, from their values before it -- probe
                              arm: away + economy + learned solar/gains + a
                              live burn + DHW with day-type evidence; the
                              _null arm: none of them live.
  hub_fields_moved_after_solve  the same, after the solve returns.
  views_setback_published     of the five comfort/DHW-floor fields the thermal
                              and DHW views publish, how many differ from the
                              configured value while an away solve is parked
                              (#1736 H1).
  quiet_band_economy, quiet_band_away  the comfort band the quiet-period
                              learner is handed after an economy / away solve,
                              against quiet_band_configured (#1736 H2).
  draw_pattern_hub_is_blend   1 when the parameters hold the day-type blend
                              after a solve rather than the learner's own
                              pattern (#1736 H3).
  learner_freeze_reads_copy   1 when the DHW learner's burn freeze follows a
                              state copy over the live detector (#1736 H4).
  whatif_live_power_maxdiff_setback_off / _on  max |power| difference, kW,
                              between the live plan and the card's what-if
                              with no overrides, on identical inputs: setback
                              inactive (the null arm, which must be 0) and
                              active (#1736's parity lead).
  whatif_comfort_day_setback_on, live_comfort_day_setback_on  the comfort
                              target each of those two solves planned with.
  published_min_temp_setback_on, solved_min_temp_setback_on  the floor the
                              thermal view publishes during an away cycle,
                              against the floor the plan was solved with.

Usage, from the root of the tree under test (copy the file into a base tree
to measure it -- the root is the cwd):

    PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/solve_inputs_parity.py

Measured at the merge base 9fed34071 (M1, python 3.14.7):
  hub_fields_moved_in_solve=12, _null=4; hub_fields_moved_after_solve=7, _null=4
  (the solve refreshes the tariff, the baseline load, the inlet and the draw
  pattern even with nothing live); views_setback_published=4 of 5;
  quiet_band_economy=3.5, quiet_band_away=0.5 against quiet_band_configured=2.0;
  draw_pattern_hub_is_blend=1; learner_freeze_reads_copy=1.
Measured at #1736's head: every hub row 0 in both arms, views 0 of 5, both
bands 2.0, both flags 0. Unchanged at both ends, because #1736 is a refactor
and not a product decision: whatif_live_power_maxdiff_setback_off=0.000000,
_setback_on=5.000000; live/what-if comfort day 16.0/21.0 C; published/solved
minimum 19.0/16.0 C.
Null controls: the setback-off parity arm compares two solves on identical
inputs and must read 0, and the probe's own rows are differences against the
same coordinator's state before the solve, so a tree that writes nothing
reads 0 in both arms.
"""
from __future__ import annotations

import asyncio
import copy
import logging
import os
import sys
from dataclasses import fields
from datetime import timedelta

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
sys.argv = [sys.argv[0]]
logging.disable(logging.CRITICAL)
for _p in ("tests", os.path.join("tests", "hastub"), "custom_components"):
    sys.path.insert(0, os.path.join(os.getcwd(), _p))

import numpy as np  # noqa: E402
from harness import FakeEntry, FakeHass, FakeState  # noqa: E402

try:  # a tree with the frozen EntryConfig (#1745) rebuilds it; a base tree writes the dict
    from harness import with_config  # noqa: E402
except ImportError:
    def with_config(holder, changes):
        holder._config.update(changes)
from homeassistant.util import dt as dt_util  # noqa: E402

from heatpump_optimizer import const  # noqa: E402
from heatpump_optimizer import coordinator as cmod  # noqa: E402
from heatpump_optimizer.optimizer import optimize_in_process  # noqa: E402

NOW = dt_util.now().replace(minute=7, second=0, microsecond=0)
SEEN: list[dict] = []
INSIDE = {"fn": None, "out": None}


async def _transport(hass, optimizer, first, *rest, **kw):
    """In-process, either hand-off shape; records what each solve was given."""
    SEEN.append({"config": copy.deepcopy(optimizer.config)})
    if INSIDE["fn"] is not None:
        INSIDE["out"] = INSIDE["fn"]()
    if rest or kw:
        result = optimize_in_process(optimizer, first, rest, kw)
    else:
        result = optimize_in_process(optimizer, first)
    SEEN[-1]["power"] = np.asarray(result.power_schedule, dtype=float)
    return result


cmod._await_optimize = _transport


class _Hass(FakeHass):
    spawn_real = False

    def async_create_task(self, coro, name=None, eager_start=None):
        coro.close()


def make(name, *, away=False, economy=False, learned=False, dhw=False):
    t0 = NOW.replace(minute=0) - timedelta(hours=1)
    hass = _Hass({
        "sensor.indoor": FakeState("21.0", unit="°C"),
        "sensor.outdoor": FakeState("-5.0", unit="°C"),
    })
    coord = cmod.HeatPumpOptimizerCoordinator(hass, FakeEntry(data={
        "tibber_token": "x", "weather_entity": "weather.home",
        "heat_pump_switch_entity": "switch.heat_pump",
        "indoor_temp_entity": "sensor.indoor",
        "outdoor_temp_entity": "sensor.outdoor",
    }, entry_id=f"eg_b1_{name}"))
    coord._skip_solve_once = False
    coord._prices = [{"total": round(0.6 + 0.5 * (h % 12) / 12.0, 4),
                      "starts_at": (t0 + timedelta(hours=h)).isoformat(),
                      "level": "NORMAL"} for h in range(48)]
    coord._weather_forecast = [{"datetime": (t0 + timedelta(hours=h)).isoformat(),
                                "temperature": -5.0, "wind_speed": 3.0,
                                "precipitation": 0.0, "humidity": 85.0}
                               for h in range(48)]
    coord._solar_radiation_forecast = [0.0] * 48
    if dhw:
        coord._thermal_params.dhw_enabled = True
        learner = coord._dhw_learner
        spike = [0.3] * 24
        spike[6], spike[20] = 5.0, 4.0
        learner.profile_weekday = learner.normalize_profile(spike)
        learner.profile_weekend = learner.normalize_profile(spike[::-1])
        learner.daytype_samples = [30, 30]
    if learned:
        with_config(coord, {
            const.CONF_SOLAR_APERTURE_LEARNING_ENABLED: True,
            const.CONF_INTERNAL_GAINS_LEARNING_ENABLED: True,
        })
        coord._solar_aperture.update(scale=1.3, n=1.0e6)
        coord._internal_gains_profile = [0.35] * 24
        coord._external_heat_active = True
    if economy:
        coord._mode = const.MODE_ECONOMY
    coord._away_state.override_active = bool(away)
    return coord


def hubs(coord):
    return {f"{n}.{f.name}": repr(getattr(h, f.name))
            for n, h in (("opt", coord._opt_config), ("par", coord._thermal_params),
                         ("st", coord._current_state))
            for f in fields(h) if f.compare}


def moved(a, b):
    return sum(1 for k in a if a[k] != b.get(k))


def views(coord):
    t, d = coord._thermal_view(), coord._dhw_view()
    return {"day": t["comfort_temp_day"], "night": t["comfort_temp_night"],
            "min": t["min_temperature"], "dhw_min": d["dhw_min_temperature"],
            "dhw_idle": d["dhw_idle_min_temperature"]}


def run(coord):
    return asyncio.run(coord.async_run_optimization())


def hub_arm(**kw):
    coord = make("hub", **kw)
    before = hubs(coord)
    INSIDE["fn"] = lambda: hubs(coord)
    run(coord)
    INSIDE["fn"] = None
    return moved(before, INSIDE["out"]), moved(before, hubs(coord))


def views_arm():
    coord = make("views", away=True)
    configured = views(coord)
    INSIDE["fn"] = lambda: views(coord)
    run(coord)
    INSIDE["fn"] = None
    return sum(1 for k in configured if configured[k] != INSIDE["out"][k])


def band_arm(**kw):
    coord = make("band", **kw)
    with_config(coord, {const.CONF_COMFORT_LEARNING_ENABLED: True})
    bands = []
    real = coord._comfort_learner.record_quiet_period

    def spy(when, span, band, *a, **k):
        bands.append(band)
        return real(when, span, band, *a, **k)

    coord._comfort_learner.record_quiet_period = spy
    run(coord)
    configured = max(0.5, coord._opt_config.comfort_temp_day - coord._opt_config.min_temp)
    return (bands[0] if bands else None), configured


def blend_arm():
    coord = make("blend", dhw=True)
    blend = coord._dhw_learner.pattern_for(NOW.weekday() >= 5)
    run(coord)
    return int(list(coord._thermal_params.dhw_hourly_draw_pattern) == list(blend))


def freeze_arm():
    coord = make("freeze")
    coord._external_heat_active = False
    coord._current_state.external_heat_active = True
    return int(bool(coord._dhw_learner._external_heat_active()))


def parity_arm(away):
    coord = make(f"parity_{away}", away=away)
    SEEN.clear()
    run(coord)
    published = coord._thermal_view()["min_temperature"]
    coord._last_simulation = None
    answer = asyncio.run(coord.async_simulate({}))
    live, card = SEEN[0], SEEN[-1]
    assert len(SEEN) == 2 and "error" not in answer, (len(SEEN), answer)
    return (float(np.max(np.abs(live["power"] - card["power"]))),
            live["config"].comfort_temp_day, card["config"].comfort_temp_day,
            published, live["config"].min_temp)


def main():
    dt_util.freeze(NOW)
    try:
        probe = hub_arm(away=True, economy=True, learned=True, dhw=True)
        null = hub_arm()
        print(f"RESULT hub_fields_moved_in_solve={probe[0]} fields")
        print(f"RESULT hub_fields_moved_in_solve_null={null[0]} fields")
        print(f"RESULT hub_fields_moved_after_solve={probe[1]} fields")
        print(f"RESULT hub_fields_moved_after_solve_null={null[1]} fields")
        print(f"RESULT views_setback_published={views_arm()} of 5")
        eco, configured = band_arm(economy=True)
        away, _ = band_arm(away=True)
        print(f"RESULT quiet_band_economy={eco} K")
        print(f"RESULT quiet_band_away={away} K")
        print(f"RESULT quiet_band_configured={configured} K")
        print(f"RESULT draw_pattern_hub_is_blend={blend_arm()} flag")
        print(f"RESULT learner_freeze_reads_copy={freeze_arm()} flag")
        off, on = parity_arm(False), parity_arm(True)
        print(f"RESULT whatif_live_power_maxdiff_setback_off={off[0]:.6f} kW")
        print(f"RESULT whatif_live_power_maxdiff_setback_on={on[0]:.6f} kW")
        print(f"RESULT live_comfort_day_setback_on={on[1]} C")
        print(f"RESULT whatif_comfort_day_setback_on={on[2]} C")
        print(f"RESULT published_min_temp_setback_on={on[3]} C")
        print(f"RESULT solved_min_temp_setback_on={on[4]} C")
    finally:
        dt_util.freeze(None)


if __name__ == "__main__":
    main()
