"""D1 staleness watchdog under a backward host-clock step.

METRIC (one line): the number of guarded input readings that
`InputReader._age_gate` flags `problem == "stale"` in ONE real
`_update_current_state()` cycle, for the SAME set of dead sensors, with and
without a backward step of the host clock between the sensors' last report and
the read.

MECHANISM: `custom_components/heatpump_optimizer/inputs.py:InputReader._age_minutes`
ends with `return max(0.0, (now - stamp).total_seconds() / 60.0)`. A state
stamped ahead of `now` therefore reports age 0.0 — "reported this instant" —
rather than "unknowable". Every gate downstream (`_age_gate`, `InputHealth`,
`_learning_frozen`, the published `input_health` string) reads that 0.0 as
maximum freshness, so the whole watchdog is off for the width of the step while
the module docstring promises the opposite ("a dead sensor stops reporting too,
so the fail-closed intent is preserved").

ARMS (12 configured entities, all last reported 3 h before the step):
  honest   — clock never steps; the 3 h old readings are read at their true age
  stepped  — the host clock steps BACK 4 h (NTP correction, manual set, a VM
             resumed with a fast clock); every stamp is now 1 h in the future
  forward  — the host clock steps FORWARD 4 h (the null/control direction: the
             clamp cannot fire, so this arm must be identical to `honest`)

COMMAND (from the repository root):
  PYTHONPATH=tests/hastub python3 tools/audit/round3/D1/stale_clock.py

EXPECTED (baseline ae36eff, 8-core M1, python 3.11.5):
  RESULT guarded_readings=11               tolerance: exact
  RESULT stale_honest=9                    tolerance: exact
  RESULT stale_stepped_back=0              tolerance: exact
  RESULT stale_stepped_forward=11          tolerance: exact
  RESULT age_reported_stepped_back_max=0.0 (every reading claims age 0.0)
  RESULT learners_frozen_honest=4 of 4
  RESULT learners_frozen_stepped_back=0 of 4
  RESULT learners_frozen_stepped_forward=4 of 4
  Counts only; no wall/CPU number is claimed.

PERTURBATION (built in, no tree edit needed):
  PYTHONPATH=tests/hastub python3 tools/audit/round3/D1/stale_clock.py --perturb
monkeypatches `inputs.InputReader._age_minutes` so a stamp AHEAD of `now`
returns `inf` instead of `max(0.0, ...)` — the one-line production fix. Then:
  stale_stepped_back      0 -> 11   (UP; this is the finding)
  stale_stepped_forward  11 -> 11   (unchanged; the null control arm)
  stale_honest            9 ->  9   (unchanged; the null control arm)
Dropping the clamp WITHOUT the `inf` does NOT move the number — a bare
negative age fails `age > limit` just as 0.0 does — which is why the fix has to
name the future stamp rather than merely stop clamping it.

BASELINE SHA: ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1
MACHINE: 8-core Apple M1, 8 GB, macOS 25.6, python 3.11.5
"""
from __future__ import annotations

import asyncio
import os
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, "tools/audit/round3/D1")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import d1lib  # noqa: E402

from harness import FakeEntry, FakeState  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
from heatpump_optimizer import const  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402

UTC = timezone.utc
T0 = datetime(2025, 1, 15, 12, 0, tzinfo=UTC)
SENSOR_AGE = timedelta(hours=3)  # every sensor died three hours ago
STEP = timedelta(hours=4)  # how far the host clock moves

# Every entity in `const.INPUT_MAX_AGE_MINUTES` that a plain numeric sensor can
# stand in for: those are exactly the reads the watchdog is supposed to gate.
ENTITY_KEYS = [
    const.CONF_INDOOR_TEMP_ENTITY,
    const.CONF_OUTDOOR_TEMP_ENTITY,
    const.CONF_DHW_TEMP_ENTITY,
    const.CONF_FLOOR_RETURN_TEMP_ENTITY,
    const.CONF_SOLAR_RADIATION_ENTITY,
    const.CONF_POWER_ENTITY,
    const.CONF_ENERGY_ENTITY,
    const.CONF_HOUSE_POWER_ENTITY,
    const.CONF_BUFFER_TANK_TEMP_ENTITY,
    const.CONF_PV_PRODUCTION_ENTITY,
    const.CONF_LOWER_FLOOR_TEMP_ENTITY,
    const.CONF_MIXING_VALVE_TARGET_ENTITY,
]

UNITS = {
    const.CONF_POWER_ENTITY: "kW",
    const.CONF_HOUSE_POWER_ENTITY: "kW",
    const.CONF_PV_PRODUCTION_ENTITY: "kW",
    const.CONF_ENERGY_ENTITY: "kWh",
}

VALUES = {
    const.CONF_INDOOR_TEMP_ENTITY: "21.4",
    const.CONF_OUTDOOR_TEMP_ENTITY: "-3.0",
    const.CONF_DHW_TEMP_ENTITY: "48.0",
    const.CONF_FLOOR_RETURN_TEMP_ENTITY: "28.0",
    const.CONF_SOLAR_RADIATION_ENTITY: "120.0",
    const.CONF_POWER_ENTITY: "1.4",
    const.CONF_ENERGY_ENTITY: "1234.5",
    const.CONF_HOUSE_POWER_ENTITY: "2.1",
    const.CONF_BUFFER_TANK_TEMP_ENTITY: "34.0",
    const.CONF_PV_PRODUCTION_ENTITY: "0.4",
    const.CONF_LOWER_FLOOR_TEMP_ENTITY: "20.2",
    const.CONF_MIXING_VALVE_TARGET_ENTITY: "33.0",
}


async def arm(step: timedelta) -> dict:
    """One cycle. Sensors last reported at T0 - 3 h; the read happens at
    T0 + `step`. `step = -4 h` is the host clock stepping backwards."""
    dt_util.freeze(T0)
    reported_at = T0 - SENSOR_AGE

    config = {}
    hass = d1lib.make_hass()
    for key in ENTITY_KEYS:
        entity_id = f"sensor.{key}"
        config[key] = entity_id
        hass.states.set(
            entity_id,
            FakeState(
                VALUES[key],
                last_updated=reported_at,
                last_reported=reported_at,
                unit=UNITS.get(key),
            ),
        )
    config[const.CONF_DHW_TANK_VOLUME] = 180.0


    coord = HeatPumpOptimizerCoordinator(hass, FakeEntry(data=config))
    # The read is what moves: the sensors are unchanged, the clock is not.
    dt_util.freeze(T0 + step)
    await coord._update_current_state()

    health = coord._input_health
    guarded = {
        key: reading
        for key, reading in health.readings.items()
        if reading.max_age_minutes is not None and reading.entity_id
    }
    stale = [k for k, r in guarded.items() if r.problem == "stale"]
    ages = [r.age_minutes for r in guarded.values() if r.age_minutes is not None]
    frozen = coord._learning_frozen(
        const.CONF_POWER_ENTITY, const.CONF_OUTDOOR_TEMP_ENTITY
    )
    frozen_indoor = coord._learning_frozen(const.CONF_INDOOR_TEMP_ENTITY)
    frozen_dhw = coord._learning_frozen(const.CONF_DHW_TEMP_ENTITY)
    frozen_buffer = coord._learning_frozen(const.CONF_BUFFER_TANK_TEMP_ENTITY)
    view = coord._input_health_view()
    out = {
        "guarded": len(guarded),
        "stale": len(stale),
        "stale_keys": sorted(stale),
        "age_min": min(ages) if ages else None,
        "age_max": max(ages) if ages else None,
        "frozen": 1 if frozen else 0,
        "frozen_reason": frozen,
        "frozen_indoor": frozen_indoor,
        "frozen_dhw": frozen_dhw,
        "frozen_buffer": frozen_buffer,
        "frozen_count": sum(
            1 for r in (frozen, frozen_indoor, frozen_dhw, frozen_buffer) if r
        ),
        "health_text": view.get("input_health"),
    }
    try:
        await coord.async_shutdown()
    except Exception:  # noqa: BLE001
        pass
    hass.shutdown()
    dt_util.freeze(None)
    return out


def _perturb() -> None:
    """The one-line fix, applied by monkeypatch so the tree is never edited."""
    from heatpump_optimizer import inputs

    def _age_minutes(self, state):
        stamp = (
            getattr(state, "last_reported", None)
            or getattr(state, "last_updated", None)
            or getattr(state, "last_changed", None)
        )
        if not isinstance(stamp, datetime):
            return None
        now = self._utcnow()
        if stamp.tzinfo is None or now.tzinfo is None:
            return None
        if stamp > now:
            return float("inf")
        return (now - stamp).total_seconds() / 60.0

    inputs.InputReader._age_minutes = _age_minutes


async def main() -> None:
    if "--perturb" in sys.argv:
        _perturb()
        print("MODE perturbed (a future stamp reports age=inf)")
    else:
        print("MODE baseline")
    honest = await arm(timedelta(0))
    back = await arm(-STEP)
    fwd = await arm(STEP)

    print(f"RESULT guarded_readings={honest['guarded']}")
    print(f"RESULT stale_honest={honest['stale']}")
    print(f"RESULT stale_stepped_back={back['stale']}")
    print(f"RESULT stale_stepped_forward={fwd['stale']}")
    print(f"RESULT age_reported_stepped_back_min={back['age_min']}")
    print(f"RESULT age_reported_stepped_back_max={back['age_max']}")
    print(f"RESULT age_reported_honest_min={honest['age_min']}")
    print(f"RESULT learners_frozen_honest={honest['frozen_count']} of 4")
    print(f"RESULT learners_frozen_stepped_back={back['frozen_count']} of 4")
    print(f"RESULT learners_frozen_stepped_forward={fwd['frozen_count']} of 4")
    for name, res in (("honest", honest), ("back", back), ("fwd", fwd)):
        print(
            f"  freeze reasons {name:6s} = "
            f"{res['frozen_reason']!r} {res['frozen_indoor']!r} "
            f"{res['frozen_dhw']!r} {res['frozen_buffer']!r}"
        )
    print(f"  health honest        = {honest['health_text']!r}")
    print(f"  health stepped_back  = {back['health_text']!r}")
    print(f"  health stepped_fwd   = {fwd['health_text']!r}")
    print(f"  stale keys honest    = {honest['stale_keys']}")
    print(f"  stale keys back      = {back['stale_keys']}")
    d1lib.emit_conditions()


if __name__ == "__main__":
    asyncio.run(main())
