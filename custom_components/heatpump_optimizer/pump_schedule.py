"""Circulation pump scheduling (item 6): stop pumping heat nobody asked for.

Two pumps, two very different risk profiles:

* **The VVC pump** (hot-water circulation loop) exists so the tap runs hot
  immediately. Outside the demand windows nobody is at the tap, and the
  loop is a radiator fed straight from the tank — often 1–2 kWh/day of
  standby loss. Running it only inside the windows, plus a lead so the
  loop is hot when the window opens, is a pure win. Worst case of a wrong
  OFF: someone waits twenty seconds for hot water.
* **The space circulation pump** moves heat from the buffer/pump to the
  emitters. A wrong OFF here can cool the house or, in winter, freeze a
  pipe. It is therefore guarded by hard rails — forced ON whenever the
  plan wants heat now or next step, whenever the heat curve is being
  driven, whenever any zone sits close to its comfort floor, and whenever
  it is freezing outside. It switches off only in slots that are provably
  idle AND warm; when in doubt, it runs. The pump is a loss-trimming
  follower of the plan, never something the optimizer reasons about.

Both decisions are pure functions; the coordinator actuates only on
transitions, and only for entities the user explicitly configured.
"""
from __future__ import annotations

import logging

from .const import SPACE_PUMP_FLOOR_MARGIN_C
from .dhw_schedule import hour_in_windows

_LOGGER = logging.getLogger(__name__)

#: Planned electrical power below this counts as "no heat commanded".
_PLAN_ACTIVE_KW = 0.05


def vvc_should_run(
    hour_of_day: float, windows, lead_minutes: float
) -> tuple[bool, str]:
    """Whether the hot-water circulation loop should run right now.

    Inside a demand window, or within the lead time before one opens, the
    loop must be hot; anywhere else it is pure standby loss. With no
    windows configured hot water is "always required" and the pump is
    simply left on — the schedule can only save where a schedule exists.
    """
    if not windows:
        return True, "no demand windows; hot water always required"
    hour = float(hour_of_day) % 24.0
    if hour_in_windows(hour, windows):
        return True, "inside a hot-water demand window"
    lead_h = max(0.0, float(lead_minutes)) / 60.0
    if lead_h > 0.0 and hour_in_windows((hour + lead_h) % 24.0, windows):
        return True, f"window opens within {int(lead_minutes)} min; pre-heating the loop"
    return False, "outside every demand window"


def space_pump_should_run(
    *,
    plan_heat_now: bool,
    plan_heat_next: bool,
    curve_driven: bool,
    zone_temps: list[float],
    floor_temp: float,
    outdoor_temp: float | None,
) -> tuple[bool, str]:
    """Whether the space circulation pump must run — rails first.

    Every rail is a reason to run; the OFF branch is reached only when
    none holds. The asymmetry is deliberate: the savings of an extra OFF
    hour are watts, the cost of a wrong OFF is a cold house or a burst
    pipe.
    """
    if plan_heat_now:
        return True, "the plan commands heat this step"
    if plan_heat_next:
        return True, "the plan commands heat next step"
    if curve_driven:
        return True, "the heat curve is being driven"
    if outdoor_temp is None:
        return True, "outdoor temperature unknown; not risking it"
    if float(outdoor_temp) < 0.0:
        return True, "freezing outside; circulation protects the pipes"
    margin = SPACE_PUMP_FLOOR_MARGIN_C
    for temp in zone_temps:
        if temp is not None and float(temp) < float(floor_temp) + margin:
            return True, (
                f"a zone is within {margin:.1f} °C of its comfort floor"
            )
    return False, "provably idle and warm; trimming pump losses"


def plan_commands_heat(power_schedule, step_index: int) -> tuple[bool, bool]:
    """(heat now, heat next step) read from the plan's power schedule."""
    if not power_schedule:
        return True, True  # no plan yet — the rails treat unknown as ON
    n = len(power_schedule)
    idx = max(0, min(int(step_index), n - 1))
    now_on = float(power_schedule[idx]) > _PLAN_ACTIVE_KW
    nxt = min(idx + 1, n - 1)
    next_on = float(power_schedule[nxt]) > _PLAN_ACTIVE_KW
    return now_on, next_on
