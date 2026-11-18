"""R10-RCA-SETPOINT-LATCH-DEADLOCK detector: from every persisted arbiter state,
the demanded space write reaches the entity with no person acting.

    python3 -I dev/audit/harnesses/r10_rca_setpoint_latch.py --check <checkout> [--passes N]

The pump-duty arbiter (``pump_arbiter.apply``) runs on a flow set-point
install, with Control on and a plan that heats the house on every step. The
stub device takes every write. A reference install with no persisted state
gives the demanded target. Then each persisted starting state is driven for
N one-minute passes (default 10): the space record (none, the idle gate
``FLOW_GATE_C``, or the heating flow), the record a loop move dropped (none,
or the gate; only where the tree has ``ArbiterState.dropped``), the entity's
reading (the gate, 40, or the heating flow), and whether the off restore is
already armed on the entity (only where the tree has ``pump_arbiter.CONSUMER``).
Every state must end with the entity reading the demanded target.

Exit codes: 0 every state converges; 1 a state never gets the demanded
write (the defect); 2 the reference install was never written, so the
harness can see no write (the skip control); 3 the modules were loaded from
outside the named checkout (provenance refusal).
"""
from __future__ import annotations

import argparse
import asyncio
import itertools
import os
import sys
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace as NS

UTC = timezone.utc
T0 = datetime(2026, 1, 10, 6, 0, tzinfo=UTC)
TUYA = ("Heating", "DHW (Hot Water)", "Heating + DHW", "Cooling", "Cooling + DHW")
SPACE = "number.water_set"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", required=True, help="checkout root to measure")
    ap.add_argument("--passes", type=int, default=10)
    args = ap.parse_args()
    root = os.path.realpath(args.check)
    # Older trees read package data relative to the cwd: measure from the root.
    os.chdir(root)
    for sub in ("custom_components", "tests", "tests/hastub"):
        sys.path.insert(0, os.path.join(root, sub))

    import harness  # noqa: PLC0415
    from heatpump_optimizer import pump_arbiter as pa  # noqa: PLC0415
    from heatpump_optimizer.const import MODE_AUTO  # noqa: PLC0415
    from heatpump_optimizer.entry_config import EntryConfig  # noqa: PLC0415

    for mod in (harness, pa):
        if not os.path.realpath(mod.__file__).startswith(root + os.sep):
            print(f"REFUSED {mod.__name__} loaded from {mod.__file__}, not {root}")
            return 3

    def plan(n):
        return NS(
            timestamps=[T0 + timedelta(minutes=15 * i) for i in range(n)],
            power_schedule=[1.5] * n,
            dhw_power_schedule=[0.0] * n,
            optimal_setpoints=[21.0] * n,
        )

    class Coord:
        def __init__(self, reading: str, entry_id: str) -> None:
            self.hass = harness.FakeHass({
                "select.pump_mode": harness.FakeState("Heating", attributes={"options": list(TUYA)}),
                "number.dhw_set": harness.FakeState("48", attributes={"min": 40, "max": 63}),
                SPACE: harness.FakeState(reading, attributes={"min": 25, "max": 63}),
            })
            self._config = EntryConfig.from_mapping({
                "pump_duty_mode": "control",
                "heat_pump_mode_entity": "select.pump_mode",
                "dhw_setpoint_entity": "number.dhw_set",
                "space_setpoint_entity": SPACE,
                "space_setpoint_unit": "flow",
            })
            self._mode = MODE_AUTO
            self.stale = False
            self._current_action = {"mode": "eco"}
            self._optimization_result = plan(400)
            self._thermal_model = NS(params=NS(min_electrical_power=0.4), curve_flow_temp=lambda _o: 34.2)
            self._thermal_params = NS(dhw_setpoint=48.0, dhw_max_temp=48.0, dhw_cycle_temp=None)
            self._current_state = NS(outdoor_temperature=0.0)
            self.entry = harness.FakeEntry(entry_id=entry_id)

        def _plan_is_stale(self) -> bool:
            return self.stale

        @property
        def effective_config(self):
            return self._config

        @property
        def thermal_params(self):
            return self._thermal_params

        def arbiter_inputs(self):
            return pa.ArbiterInputs(
                hass=self.hass, config=self._config, mode=self._mode,
                plan=self._optimization_result, plan_stale=self.stale, entry_released=False,
                state=self._current_state, thermal=self._thermal_model, params=self._thermal_params,
                action=self._current_action, measured_power_kw=None, disinfecting=False,
            )

        async def async_set_mode(self, mode) -> None:
            self._mode = mode

    def converge(coord: Coord) -> float:
        for i in range(args.passes):
            asyncio.run(pa.apply(coord, T0 + timedelta(minutes=i)))
            for _d, _s, data in coord.hass.services.calls:  # the device takes each write
                value = data.get("option", data.get("value"))
                coord.hass.states.get(data["entity_id"]).state = str(value)
            coord.hass.services.calls.clear()
        return float(coord.hass.states.get(SPACE).state)

    ids = itertools.count()
    ref_reading = "40"
    target = converge(Coord(ref_reading, f"latch{next(ids)}"))
    if target == float(ref_reading):
        print(f"SKIP the reference install was never written (reads {target}): nothing to measure")
        return 2

    gate, heat = float(pa.FLOW_GATE_C), target
    has_dropped = "dropped" in getattr(pa.ArbiterState, "__dataclass_fields__", {})
    has_restore = hasattr(pa, "CONSUMER")
    if has_restore:
        from heatpump_optimizer import off_restore  # noqa: PLC0415
    states = list(itertools.product(
        (None, gate, heat),
        (None, gate) if has_dropped else (None,),
        (gate, 40.0, heat),
        (False, True) if has_restore else (False,),
    ))
    failed = 0
    for written, dropped, reading, armed in states:
        coord = Coord(f"{reading:g}", f"latch{next(ids)}")
        held = pa.state_for(coord)
        held.loaded = True
        if armed:
            coord.entry.runtime_data = coord
            asyncio.run(off_restore.async_arm(coord.hass, coord.entry, coord._config, pa.CONSUMER))
        if written is not None:
            held.written["space_setpoint"] = (written, T0 - timedelta(hours=1))
        if dropped is not None:
            held.dropped["space_setpoint"] = dropped
        final = converge(coord)
        if final != target:
            failed += 1
            print(f"FAIL written={written} dropped={dropped} reading={reading:g} armed={armed}: "
                  f"reads {final:g} after {args.passes} passes, demanded {target:g}")
    print(f"SUMMARY root={root} demanded={target:g} states={len(states)} failed={failed} "
          f"passes={args.passes} dropped_axis={has_dropped} armed_axis={has_restore}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
