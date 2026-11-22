"""The pump's hot-water start condition: where a planned charge is one the pump makes.

A heat pump starts a hot-water charge only on a tank below its set-point less
its start hysteresis (``thermal_model.dhw_start_below_c``). Here that rule
becomes the per-step start temperature (:func:`dhw_start_temps`) and the
steps a charge may be bought on (:func:`startable_steps`). It also becomes the
floor repair that drops a charge the pump would never start and re-buys the
floor elsewhere (:func:`drop_unstartable`, :func:`place_startable`).
``dhw_planner.DhwPlanner`` calls them; they hold no state and read only their
arguments.
"""
from __future__ import annotations

from typing import Callable

import numpy as np

from .thermal_model import ThermalParameters, ThermalState, dhw_start_below_c, dhw_step_target_c


#: How many times :func:`place_startable` re-buys what the start condition
#: barred before it settles for dropping. A round re-buys under the charges
#: the round before kept, and the measured placements settle in two or three
#: (``dev/audit/harnesses/r10_dhw_start_hysteresis.py``, repair_rounds_max),
#: so eight is that with room to spare and still a bound.
STARTABLE_ROUNDS = 8


def dhw_start_temps(
    params: ThermalParameters, state: ThermalState, n_steps: int, cycle_step: int | None
) -> np.ndarray | None:
    """Per step, the tank temperature below which the pump starts a charge, °C.

    The target the arbiter writes on that step (``dhw_step_target_c`` on the
    set-point entity's grid, ``state.dhw_setpoint_grid``: the cycle's on
    ``cycle_step``, the everyday one elsewhere) less the pump's start
    hysteresis (``state.dhw_start_hysteresis_k``), so a disinfection charge
    is judged against its own target and a stepped entity's against the step
    it lands on. ``None`` where no start condition is known
    (``dhw_start_below_c``).
    """
    hysteresis_k, grid = state.dhw_start_hysteresis_k, state.dhw_setpoint_grid
    everyday = dhw_start_below_c(dhw_step_target_c(params, False, grid), hysteresis_k)
    if everyday is None:
        return None
    start = np.full(n_steps, everyday)
    if cycle_step is not None and 0 <= cycle_step < n_steps:
        start[cycle_step] = dhw_start_below_c(dhw_step_target_c(params, True, grid), hysteresis_k)
    return start


def startable_steps(
    plan: np.ndarray, temps: np.ndarray, start_below: np.ndarray | None, charge_running: bool = True
) -> np.ndarray:
    """The steps where charging is something the pump does.

    A step that opens on a tank below its start temperature (``temps[i]``,
    the simulated level at its start), and the step after one of a charge
    under way, which runs on to its target. A charge is under way from the
    step it opens below its start temperature, or from the first step when
    ``charge_running`` (``ThermalState.dhw_charge_under_way``) says one runs
    now. A charge the pump would not start carries nothing on, so the repair
    buys neither inside it nor behind it. Every step where no start condition
    is known (``start_below`` ``None``).
    """
    on = np.asarray(plan, dtype=float) > 0.0
    if start_below is None:
        return np.ones(on.size, dtype=bool)
    ok: np.ndarray = np.asarray(temps, dtype=float)[: on.size] < start_below[: on.size]
    under_way = bool(on[:1].any()) and (charge_running or bool(ok[:1].any()))
    for i in range(1, on.size):
        ok[i] |= under_way
        under_way = bool(on[i] and ok[i])
    return ok


def drop_unstartable(
    plan: np.ndarray,
    start_below: np.ndarray,
    temps_of: Callable[[np.ndarray], np.ndarray],
    charge_running: bool = True,
) -> np.ndarray:
    """``plan`` without the charges the pump would never start.

    Each run is judged in time order on the trajectory ``temps_of`` simulates
    for the runs kept before it: one that begins on a tank at or above its
    step's start temperature is removed whole. A run at the first step is
    kept while ``charge_running``, a charge under way (Bankaifan, #3440); with
    none running, it is judged like any other.
    """
    plan = np.array(plan, dtype=float)
    on = plan > 0.0
    for i in np.flatnonzero(on & ~np.append(charge_running, on[:-1])[: on.size]):
        end = i + int(np.argmin(np.append(on[i:], False)))
        if temps_of(plan)[i] >= start_below[i]:
            plan[i:end] = 0.0
    return plan


def place_startable(
    plan: np.ndarray,
    start_below: np.ndarray | None,
    temps_of: Callable[[np.ndarray], np.ndarray],
    repair: Callable[..., np.ndarray],
    charge_running: bool = True,
) -> np.ndarray:
    """The floor repair of ``plan`` under the pump's start condition.

    With no condition, ``repair(plan=plan)``, the call as it always was. With
    one, the charges the pump would not start are dropped and ``repair``,
    handed the condition so it places only on :func:`startable_steps`,
    re-buys what the floor still needs; a top-up warms the tank under every
    later charge, so the two repeat until the plan stands, at most
    :data:`STARTABLE_ROUNDS` times. The plan that leaves holds no charge the
    pump would not start, and is short of the floor only where no startable
    step can hold it. ``charge_running`` is :func:`drop_unstartable`'s;
    ``repair`` is handed it already bound.
    """
    if start_below is None:
        return repair(plan=plan)
    for _ in range(STARTABLE_ROUNDS):
        fixed = repair(plan=drop_unstartable(plan, start_below, temps_of, charge_running), start_below=start_below)
        if np.array_equal(fixed, plan):
            break
        plan = fixed
    return drop_unstartable(plan, start_below, temps_of, charge_running)
