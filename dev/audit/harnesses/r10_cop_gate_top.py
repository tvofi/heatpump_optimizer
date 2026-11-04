"""R10-COP-GATE part D harness: does the ceiling store's learned top reach the
range a solve books, and the band the arbiter maps the plan's steps on?

Ported from the finder's ``evidence/r3_probe_reader.py`` at
``design-verdict/R10-CEILING-PROBE`` 3a261d864 (the measurement carry 12
cites: the store's median published, no solve reading it) and extended, as
the design note asks, to print the solve's ruling and its top.

  reader    store-only reads at 11 and 12 samples of a 3.0 kW pump behind a
            configured (1.0, 5.0): ``learned_max_kw``, the window's
            ``planned_range`` and the top the solve books
  rule      every row of the design's rule table, plus the 15 % edge
  map       the flow set-point one arbiter pass writes for a 3.0 kW plan step,
            the plan stamped with the learned band against unstamped

Synthetic inputs only. Run from a worktree root (any tree; an arm whose
symbols the tree lacks prints ``absent``, and at a base with no ruling the
solve books the hub's configured top):
  PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/r10_cop_gate_top.py
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from types import SimpleNamespace as NS

from harness import FakeHass, FakeState
from heatpump_optimizer import draw_range as dr
from heatpump_optimizer import pump_arbiter as pa
from heatpump_optimizer.entry_config import EntryConfig

NOW = datetime(2026, 10, 27, 1, 0, tzinfo=timezone.utc)
NOW_S = NOW.timestamp()
CFG = (1.0, 5.0)
PARAMS = NS(min_electrical_power=CFG[0], max_electrical_power=CFG[1])
CAP = NS(plan_writes_power=lambda: False, can_duty_cycle=lambda: True)
ECHO = NS(plan_writes_power=lambda: True, can_duty_cycle=lambda: True)


def store(values, newest_s=NOW_S):
    d = dr.DrawRange()
    for k, v in enumerate(values):
        d.observe_ceiling(v, newest_s - (len(values) - 1 - k) * 1800.0)
    return d


def ruling(d, cap=CAP, now_s=NOW_S, params=PARAMS):
    fn = getattr(dr, "solve_band", None)
    if fn is None:
        return None
    return fn(d, params, cap, now_s)


def solve_top(d, cap=CAP, now_s=NOW_S):
    """The top the solve copy books: the ruling's, or the hub's with none."""
    b = ruling(d, cap, now_s)
    return CFG[1] if b is None else b.max_kw


def reader_arm() -> None:
    for n in (11, 12):
        d = store([3.0] * n)
        b = ruling(d)
        print(f"reader: {n} samples -> learned_max_kw {d.learned_max_kw(NOW_S)!r} "
              f"planned_range {dr.planned_range(d, PARAMS, CAP)!r} solve top {solve_top(d)!r} "
              f"solve_band {'absent' if b is None else (b.source, b.reason)}")


def rule_arm() -> None:
    rows = (
        ("eleven samples", store([3.0] * 11), CAP, NOW_S),
        ("twelve at 3.0", store([3.0] * 12), CAP, NOW_S),
        ("lapsed (+46 d)", store([3.0] * 12), CAP, NOW_S + 46 * 86400.0),
        ("within 15 % (4.5)", store([4.5] * 12), CAP, NOW_S),
        ("edge (4.25)", store([4.25] * 12), CAP, NOW_S),
        ("above (6.0)", store([6.0] * 12), CAP, NOW_S),
        ("plan writes power", store([3.0] * 12), ECHO, NOW_S),
    )
    for label, d, cap, now_s in rows:
        b = ruling(d, cap, now_s)
        print(f"rule: {label:18s} -> " + ("absent" if b is None else
              f"{b.source} {b.reason} max {b.max_kw} min {b.min_kw}"))


def _flow(band) -> float | None:
    hass = FakeHass({"number.water_set": FakeState("40", attributes={"min": 25, "max": 63})})
    config = EntryConfig.from_mapping({"pump_duty_mode": "control", "space_setpoint_entity": "number.water_set",
                                       "space_setpoint_unit": "flow"})
    plan = NS(timestamps=[NOW], power_schedule=[3.0], dhw_power_schedule=[0.0], optimal_setpoints=[21.0])
    if band is not None:
        plan.solve_band = band
    params = NS(dhw_setpoint=48.0, min_electrical_power=CFG[0], max_electrical_power=CFG[1])
    inp = pa.ArbiterInputs(hass=hass, config=config, mode="auto", plan=plan, plan_stale=False,
                           entry_released=False, state=NS(outdoor_temperature=2.0, room_temperature=21.0),
                           thermal=NS(params=params, curve_flow_temp=lambda _o: 34.2), params=params,
                           action={"mode": "eco", "power": 3.0}, measured_power_kw=None, disinfecting=False)
    target = pa._flow_target(inp, "space", NOW + timedelta(minutes=1))
    return None if target is None else getattr(target, "value", target)


def map_arm() -> None:
    b = ruling(store([3.0] * 12))
    print(f"map: 3.0 kW plan step, unstamped -> {_flow(None)!r}")
    print(f"map: 3.0 kW plan step, stamped {'absent' if b is None else 'learned (1.0, 3.0)'} -> "
          f"{_flow(None if b is None else b.as_dict())!r}")


if __name__ == "__main__":
    reader_arm()
    rule_arm()
    map_arm()
