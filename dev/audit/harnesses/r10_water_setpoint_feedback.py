"""R10-WATER-SETPOINT-FEEDBACK harness: does a water set-point settle at the
planned level on a controller that integrates on set-point minus return?

No finder harness exists: the report is outside PR #3380 (one Luxtronik 2.1
install, runs A-C). This is the simulated integrating controller of
``tests/features.py``'s R10-WATER-SETPOINT-FEEDBACK block, driven through the
production ``pump_arbiter._arbitrate`` (``hold``, ``desired``, ``_write``),
made to run on a tree without the loop too (no ``ArbiterInputs.defrosting``,
no ``ArbiterState.feedback``), so the same command reads both ends.

One line per arm: the plan, the option, the mean measured draw over the last
30 minutes of a three-hour block, whether every one of those minutes is
within 20 % of plan, the compressor starts, and the speed at minutes 30 and
180; then, for part 3, the lowest and highest value written against a
controller limit with and without its sensor configured, and the lowest
write beside the gate for a high-limit sensor reading around it. Synthetic
inputs only. Run from a worktree root:
  PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/r10_water_setpoint_feedback.py
"""
from __future__ import annotations

import asyncio
import dataclasses
import itertools
import random
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace as NS

from harness import FakeHass, FakeState
from heatpump_optimizer import pump_arbiter as pa
from heatpump_optimizer.const import MODE_AUTO
from heatpump_optimizer.entry_config import EntryConfig

UTC = timezone.utc
_DEFROST_FIELD = "defrosting" in {f.name for f in dataclasses.fields(pa.ArbiterInputs)}

T0 = datetime(2026, 1, 12, 8, 0, tzinfo=UTC)
SET = "number.fb_return_set"
RETURN = "sensor.fb_return"
IDS = itertools.count()
LIMIT_KEYS = ("space_setpoint_low_limit_entity", "space_setpoint_high_limit_entity")
LIMITS = ("sensor.fb_low_limit", "sensor.fb_high_limit")


class _Entry:
    """Config-entry stand-in; a plain class, because ``off_restore._RECORDS``
    is a WeakKeyDictionary and a ``SimpleNamespace`` cannot be weak-referenced."""

    def __init__(self, entry_id):
        self.entry_id = entry_id


class Coord:
    """The published surface the arbiter reads, with the meter and defrost
    flag the simulation sets each pass."""

    def __init__(self, *, unit="return", power_entity=True, feedback=None, lift=0.5,
                 ceiling=32.0, plan_kw=0.53, step=0.1, mode=None, limits=(None, None)):
        self.hass = FakeHass({
            SET: FakeState("26.0", attributes={"min": 15, "max": 45, "step": step}),
            RETURN: FakeState("25.9", unit="°C"),
        })
        config = {
            "pump_duty_mode": "control", "space_setpoint_entity": SET,
            "space_setpoint_unit": unit, "heat_pump_return_temp_entity": RETURN,
            "flow_min_lift_k": lift, "flow_heat_c": ceiling,
        }
        # The controller's limits on the set-point as sensors (part 3): a state
        # string or number per side, None for an unset slot.
        for key, entity, limit in zip(LIMIT_KEYS, LIMITS, limits):
            if limit is not None:
                config[key] = entity
                self.hass.states.set(entity, FakeState(str(limit), unit="°C"))
        if power_entity:
            config["heat_pump_power_entity"] = "sensor.fb_power"
        if feedback is not None:
            config["space_setpoint_power_feedback"] = feedback
        self._config = EntryConfig.from_mapping(config)
        self._mode = mode or MODE_AUTO
        self._current_action = {"mode": "eco"}
        stamps = [T0 + timedelta(minutes=15 * i) for i in range(24)]
        plan = list(plan_kw) if isinstance(plan_kw, (list, tuple)) else [plan_kw] * 24
        self._optimization_result = NS(
            timestamps=stamps, power_schedule=plan,
            dhw_power_schedule=[0.0] * 24, optimal_setpoints=[21.0] * 24)
        self._thermal_model = NS(
            params=NS(min_electrical_power=0.53), curve_flow_temp=lambda _o: 34.0)
        self._thermal_params = NS(
            dhw_setpoint=48.0, min_electrical_power=0.53, max_electrical_power=2.2)
        self._current_state = NS(outdoor_temperature=4.0, room_temperature=21.0)
        self.entry = _Entry(f"fb{next(IDS)}")
        self.power = None
        self.defrosting = False

    def arbiter_inputs(self):
        return pa.ArbiterInputs(
            hass=self.hass, config=self._config, mode=self._mode,
            plan=self._optimization_result, plan_stale=False, entry_released=False,
            state=self._current_state, thermal=self._thermal_model,
            params=self._thermal_params, action=self._current_action,
            measured_power_kw=self.power, disinfecting=False,
            **({"defrosting": self.defrosting} if _DEFROST_FIELD else {}))


def draw_kw(hz):
    return 0.0 if hz <= 0 else 0.5 + (hz - 26.0) * 0.0269


def sim(*, minutes=180, hyst=0.5, stop_hyst=None, clamp=(10.0, 50.0), revert_at=None,
            defrost=(), seed=7, **coord_kw):
    """Run the controller and the arbiter for ``minutes``; a dict of traces.

    One pass at each minute, plus a listener pass at a random second in about
    a third of the minutes; the physics steps every 10 s. ``revert_at`` (min)
    drops the register to 35.0 degC with the compressor still running (the
    SHI's 600 s volatility); ``defrost`` is a set of minutes the flag reads on.
    """
    rng = random.Random(seed)
    coord = Coord(**coord_kw)
    held = pa.state_for(coord)
    held.loaded = True
    stop_hyst = hyst if stop_hyst is None else stop_hyst
    ret, reg, hz, prog = 25.9, 26.0, 0.0, 0.0
    starts, writes, trace, issues_seen = 0, [], [], []
    seen = 0
    for minute in range(minutes):
        passes = [0] + ([rng.randint(5, 55)] if rng.random() < 0.34 else [])
        for second in range(0, 60, 10):
            now = T0 + timedelta(minutes=minute, seconds=second)
            for at in passes:
                if second <= at < second + 10:
                    coord.power = round(draw_kw(hz), 3)
                    coord.defrosting = minute in defrost
                    coord.hass.states.get(RETURN).state = f"{ret:.2f}"
                    asyncio.run(pa._arbitrate(
                        coord, held, coord.arbiter_inputs(), "control",
                        now + timedelta(seconds=at - second)))
                    for _d, _s, data in coord.hass.services.calls[seen:]:
                        if (data or {}).get("entity_id") == SET:
                            sent = float(data["value"])
                            reg = min(max(sent, clamp[0]), clamp[1])
                            writes.append((minute, sent, round(ret, 2)))
                            coord.hass.states.get(SET).state = f"{reg:.1f}"
                    seen = len(coord.hass.services.calls)
                    if held.retry:
                        issues_seen.append(minute)
            if revert_at is not None and minute == revert_at and second == 0:
                reg = 35.0
                coord.hass.states.get(SET).state = "35.0"
            dt = 10.0 / 60.0
            if hz <= 0 and ret <= reg - hyst + 1e-9:
                hz, prog, starts = 52.0, 3.0, starts + 1
            elif hz > 0 and ret >= reg + stop_hyst - 1e-9:
                hz = 0.0
            elif hz > 0 and prog > 0:
                prog -= dt
            elif hz > 0:
                hz = min(max(hz + 0.9 * (reg - ret) * dt, 26.0), 90.0)
            ret += (25.0 + 3.0 * draw_kw(hz) - ret) * dt / 60.0
        run = getattr(held, "feedback", None)
        trace.append((minute, hz, draw_kw(hz), reg, ret,
                      None if run is None else run.start))
    return {"coord": coord, "held": held, "starts": starts, "writes": writes,
            "trace": trace, "issues": issues_seen}


def main() -> None:
    for label, kw, plan in (
        ("return 0.53 kW", {}, 0.53),
        ("return 0.53 kW", {"feedback": False}, 0.53),
        ("flow 0.53 kW", {"unit": "flow"}, 0.53),
    ):
        run = sim(**kw)
        tail = run["trace"][-30:]
        mean = sum(row[2] for row in tail) / len(tail)
        every = all(abs(row[2] - plan) <= 0.2 * plan for row in tail)
        option = "off" if kw.get("feedback") is False else "default"
        print(f"{label:16s} option {option:7s} mean {mean:.3f} kW  every-minute-within-20% "
              f"{every}  starts {run['starts']}  speed {run['trace'][30][1]:.1f} -> "
              f"{run['trace'][-1][1]:.1f} Hz")
    # Part 3: the controller's limits read from their two optional sensors
    # (a Luxtronik's inputs 10104 and 10103). A tree that does not read them
    # prints the same row with the sensors as without.
    for label, kw, side in (
        ("return limit 27.6", {"plan_kw": [0.53] * 8 + [1.2] * 16, "clamp": (10.0, 27.6)}, 1),
        ("return minimum 28.0",
         {"plan_kw": [1.2] * 8 + [0.53] * 16, "ceiling": 40.0, "clamp": (28.0, 50.0)}, 0),
    ):
        for sensors in (False, True):
            limits = tuple(kw["clamp"][i] if sensors and i == side else None for i in (0, 1))
            sent = [w[1] for w in sim(limits=limits, **kw)["writes"]]
            print(f"{label:20s} sensor {'set' if sensors else 'unset':5s} writes {len(sent)}  "
                  f"lowest {min(sent):.1f}  highest {max(sent):.1f}")
    # The class the part-3 review left open: a high-limit sensor reading at
    # or around the gate, the value that means off. One row per unit and
    # reading: the lowest write beside the gate, and whether it clears it.
    step_up = {"plan_kw": [0.53] * 8 + [1.2] * 16, "clamp": (10.0, 27.6)}
    for unit in ("return", "flow"):
        for offset in (None, -5.0, 0.0, 0.05, 0.1):
            gate = pa._gate_c(Coord(unit=unit).arbiter_inputs())
            limit = None if offset is None else round(gate + offset, 3)
            sent = [w[1] for w in sim(unit=unit, limits=(None, limit), **step_up)["writes"]]
            name = "unset" if limit is None else f"{limit:.2f}"
            print(f"{unit:6s} gate {gate:.1f}  high limit {name:5s} writes {len(sent)}  "
                  f"lowest {min(sent):.1f}  above the gate {min(sent) > gate}")


def lift_row(lift, feedback, hyst):
    """One part-4 arm: energy drawn against the booked, the last 30 minutes,
    and the settle minute: the first minute from which the 5-minute mean draw
    stays within 20 % of plan to the end of the run (None: it never does)."""
    plan, minutes = 0.53, 180
    kw = {"lift": lift}
    if feedback is not None:
        kw["feedback"] = feedback
    run = sim(minutes=minutes, hyst=hyst, plan_kw=plan, **kw)
    draw = [row[2] for row in run["trace"]]
    tail = sum(draw[-30:]) / 30
    ok = [abs(sum(draw[max(0, m - 4):m + 1]) / len(draw[max(0, m - 4):m + 1]) - plan) <= 0.2 * plan
          for m in range(minutes)]
    settle = next((m for m in range(minutes) if all(ok[m:])), None)
    return {"kwh": sum(draw) / 60.0, "tail": tail, "settle": settle, "starts": run["starts"],
            "step": settle is not None and settle <= 15}


def part4() -> None:
    """Part 4 (R10-FEEDBACK-SETTLE-LARGE-LIFT): a floor lift of 0.5, 2, 4 and 6 K,
    the loop on and off, the controller's start hysteresis at 0.5 K and at the
    lift. Booked: plan 0.53 kW for 3 h. Each arm is run twice (null control)."""
    print(f"booked {0.53 * 3:.2f} kWh")
    for hyst_of in ("0.5K", "=lift"):
        for lift in (0.5, 2.0, 4.0, 6.0):
            for fb in (None, False):
                hyst = 0.5 if hyst_of == "0.5K" else lift
                first, again = lift_row(lift, fb, hyst), lift_row(lift, fb, hyst)
                print(f"hyst {hyst_of:5s} lift {lift:3.1f} K  loop {'off' if fb is False else 'on ':3s}  "
                      f"drew {first['kwh']:.2f} kWh  last30 {first['tail']:.3f} kW  "
                      f"settle min {first['settle']}  within one step {first['step']}  "
                      f"starts {first['starts']}  repeat identical {first == again}")


if __name__ == "__main__":
    import sys
    if "--lift" in sys.argv:
        part4()
        raise SystemExit
    main()
