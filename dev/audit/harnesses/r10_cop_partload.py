"""R10-COP-PARTLOAD: does COP depend on compressor power enough to plan on?

    PYTHONPATH=tests/hastub:custom_components:tests \\
        python3 dev/audit/harnesses/r10_cop_partload.py [--no-solves]

Synthetic throughout; no private data, no heat meter. The tree's own COP law
(``ThermalModel.compute_cop``) has no power argument, so a synthetic install
built from it measures a part-load effect of exactly zero by construction.
The plant here is therefore independent of that law: one vapour-compression
cycle at a fixed fraction of Carnot, whose condensing temperature sits above
the supply water by ``Q / UA_COND`` and whose evaporating temperature sits
below the air by ``Q_evap / UA_EVAP``, plus a constant auxiliary draw (fan,
controls). The cycle fraction is calibrated so the plant equals the model's
COP at the band's midpoint; only ratios are printed. Four parts:

1. ``partload``: COP against electrical power across the configured band at a
   fixed lift (outdoor 5 degC, supply water 35 degC), as a ratio to the
   band's best, on every plant of the sensitivity grid (UA_COND, UA_EVAP,
   aux). ``null``: an infinite-UA, zero-aux plant must read 1.000 at every
   power, or the instrument invents the effect.
2. ``burst``: the supply-temperature rise of a burst at ``p_max`` over a step
   at ``p_min`` at a fixed return (30 degC) and water flow, and the COP that
   rise costs through the tree's own ``flow_lift_factor``. ``null``: equal
   powers rise 0 K.
3. ``solves`` (skipped with ``--no-solves``): R10-SETPOINT-BOOST's 16
   synthetic installs at its spread and flat price days, solved by the tree
   with no term (``d=0``; its plan sha1 is the byte-identity null across
   trees) and, where the tree has the term, at the central plant's own derate.
   Each published space plan is re-priced on the central plant: the share of
   planned heat the plant would not deliver, the cost per delivered kWh, and
   its gain over a counterfactual delivering the same plant heat at one
   constant power. ``gain`` > 0 means the shaped plan beats the flat one with
   the part-load physics charged against it; the flat-price day is the null,
   where shaping buys no price and the term's cost is all that is left.
   ``term vs none`` is the term's effect on cost per delivered kWh.
"""
from __future__ import annotations

import sys

import numpy as np

from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters

K0 = 273.15
P_MIN, P_MAX = 1.5, 5.0
OUTDOOR_C, SUPPLY_C, RETURN_C = 5.0, 35.0, 30.0
#: Water capacity rate, kW/K: 0.4 kg/s x 4.19 kJ/(kg K), a 5 K spread at ~8 kW.
MCP_KW_K = 1.68
#: Central plant: plate condenser and finned air coil sized for a ~15 kW heat
#: output at ~3 K and ~6 K approach; 60 W of fan and controls.
CENTRAL = (5.0, 2.0, 0.06)
GRID = [(uc, ue, aux) for uc in (2.5, 5.0, 10.0) for ue in (1.0, 2.0, 4.0)
        for aux in (0.03, 0.06, 0.15)]
NULL_PLANT = (1e9, 1e9, 0.0)


def plant_cop(p_el: float, ua_c: float, ua_e: float, aux: float, eta: float,
              supply_c: float | None = SUPPLY_C, return_c: float = RETURN_C) -> tuple[float, float]:
    """Delivered COP and supply temperature at electrical draw ``p_el``.

    ``supply_c`` fixes the water lift; ``None`` fixes the return instead and
    lets the supply rise with the heat rate (the burst case)."""
    p_comp = p_el - aux
    cop_cycle, sup = 3.0, supply_c if supply_c is not None else return_c
    for _ in range(200):
        q = p_comp * cop_cycle
        sup = supply_c if supply_c is not None else return_c + q / MCP_KW_K
        t_c = sup + K0 + q / ua_c
        t_e = OUTDOOR_C + K0 - (q - p_comp) / ua_e
        new = eta * t_c / max(t_c - t_e, 1.0)
        if abs(new - cop_cycle) < 1e-12:
            break
        cop_cycle = 0.5 * (cop_cycle + new)
    return p_comp * cop_cycle / p_el, sup


def calibrate(plant: tuple[float, float, float], target: float) -> float:
    mid = 0.5 * (P_MIN + P_MAX)
    lo, hi = 0.05, 1.0
    for _ in range(100):
        eta = 0.5 * (lo + hi)
        if plant_cop(mid, *plant, eta)[0] < target:
            lo = eta
        else:
            hi = eta
    return 0.5 * (lo + hi)


def ratio_curve(plant, target, powers, **kw) -> np.ndarray:
    eta = calibrate(plant, target)
    cops = np.array([plant_cop(p, *plant, eta, **kw)[0] for p in powers])
    return cops / cops.max()


def partload(model: ThermalModel) -> np.ndarray:
    target = model.compute_cop(OUTDOOR_C, flow_temp=SUPPLY_C)
    powers = np.linspace(P_MIN, P_MAX, 8)
    print(f"partload: outdoor {OUTDOOR_C} supply {SUPPLY_C} model COP {target:.3f} "
          f"powers {np.round(powers, 2).tolist()}")
    null = ratio_curve(NULL_PLANT, target, powers)
    print(f"  null (UA inf, aux 0): min ratio {null.min():.4f}")
    worst_max, worst_min = 1.0, 1.0
    for plant in GRID:
        r = ratio_curve(plant, target, powers)
        worst_max, worst_min = min(worst_max, r[-1]), min(worst_min, r[0])
        tag = " central" if plant == CENTRAL else ""
        print(f"  UAc {plant[0]:>4} UAe {plant[1]:>3} aux {plant[2]:.2f}: "
              f"ratio {np.round(r, 3).tolist()} best at {powers[r.argmax()]:.2f} kW{tag}")
    print(f"partload: grid {len(GRID)} plants; ratio at p_max >= {worst_max:.3f}, "
          f"at p_min >= {worst_min:.3f}")
    return ratio_curve(CENTRAL, target, powers)


def burst(model: ThermalModel) -> None:
    target = model.compute_cop(OUTDOOR_C, flow_temp=SUPPLY_C)
    eta = calibrate(CENTRAL, target)
    _, s_min = plant_cop(P_MIN, *CENTRAL, eta, supply_c=None)
    _, s_max = plant_cop(P_MAX, *CENTRAL, eta, supply_c=None)
    _, s_same = plant_cop(P_MIN, *CENTRAL, eta, supply_c=None)
    rise = s_max - s_min
    lift_min = model.flow_lift_factor(OUTDOOR_C, s_min)
    lift_max = model.flow_lift_factor(OUTDOOR_C, s_max)
    # the tree's factor is one-sided above its reference: report the Carnot
    # ratio relative to the floor step's own supply as well
    t_out = OUTDOOR_C + K0
    carnot = ((s_max + K0) / (s_max + K0 - t_out)) / ((s_min + K0) / (s_min + K0 - t_out))
    print(f"burst: return {RETURN_C} supply at p_min {s_min:.2f} at p_max {s_max:.2f} "
          f"rise {rise:.2f} K (null rise {s_same - s_min:.2f} K); tree flow_lift_factor "
          f"{lift_min:.4f} -> {lift_max:.4f} (ratio {lift_max / lift_min:.4f}); "
          f"Carnot ratio across the rise {carnot:.4f}")


def solve(sb, cell, prices, derate: float):
    """``r10_setpoint_boost.solve``'s install with the part-load derate set
    (absent on a tree without the term, where only ``derate == 0`` runs)."""
    loss, buffer_l, dhw, rounded = cell
    p = ThermalParameters()
    if buffer_l:
        p.mixing_valve_mode, p.buffer_tank_volume = "manual", buffer_l
    p.min_electrical_power, p.max_electrical_power = sb.CFG_MIN, sb.CFG_MAX
    p.dhw_enabled, p.house_heat_loss_scale = dhw, loss
    if derate:
        p.cop_partload_derate = derate
    opt = sb.HeatPumpOptimizer(ThermalModel(p), sb.OptimizationConfig(clamp_planned_levels=rounded))
    return opt.optimize(inputs=sb.solve_inputs(
        initial_state=sb.ThermalState(
            room_temperature=20.0, upper_floor_temperature=20.0,
            lower_floor_temperature=20.0, slab_temperature=20.5,
            outdoor_temperature=5.0, buffer_tank_temperature=24.0,
            dhw_temperature=48.0,
        ),
        prices=prices, outdoor_temps=np.full(96, 5.0), start_time=sb.T0,
    ))


def solves(model: ThermalModel) -> int:
    import hashlib  # noqa: PLC0415

    sys.path.insert(0, "dev/audit/harnesses")
    import r10_setpoint_boost as sb  # noqa: PLC0415

    target = model.compute_cop(OUTDOOR_C)
    eta = calibrate(CENTRAL, target)
    best = max(plant_cop(p, *CENTRAL, eta)[0] for p in np.linspace(P_MIN, P_MAX, 50))
    # the term's value for this plant: its COP lost at max power vs the floor
    derate = round(1.0 - plant_cop(P_MAX, *CENTRAL, eta)[0] / plant_cop(P_MIN, *CENTRAL, eta)[0], 3)
    has_term = hasattr(ThermalParameters(), "cop_partload_derate")
    arms = (0.0, derate) if has_term else (0.0,)
    print(f"solves: central plant derate {derate} term in tree {has_term}")

    def r(p: float) -> float:
        return plant_cop(p, *CENTRAL, eta)[0] / best if p > 0 else 1.0

    def priced(plan: np.ndarray, prices: np.ndarray) -> tuple[float, float, float]:
        """(plant heat short of the model's, cost per plant kWh, gain over flat)."""
        level = np.where(plan >= P_MIN, plan, P_MIN)
        ratio = np.array([r(x) for x in level])
        heat_model = float((plan * target).sum())
        heat_plant = float((plan * target * ratio).sum())
        cost = float((plan * prices).sum() / 4.0)
        flat_level = max(heat_plant / (target * 96), P_MIN)
        flat_cost = float(prices.mean() * heat_plant / (target * r(flat_level)) / 4.0)
        return 1 - heat_plant / heat_model, cost / heat_plant, (flat_cost - cost) / flat_cost

    failures = 0
    for tag, prices in (("spread", sb.SPREAD), ("flat", sb.FLAT)):
        stats: dict[float, list[tuple[float, float, float]]] = {a: [] for a in arms}
        for cell in sb.CELLS:
            line = f"  {tag} {cell}"
            for arm in arms:
                try:
                    res = solve(sb, cell, prices, arm)
                except Exception as err:  # counted, never dropped
                    failures += 1
                    line += f" d={arm} failed: {err!r}"
                    continue
                plan = np.asarray(res.power_schedule, float)
                sha = hashlib.sha1(np.asarray(
                    res.power_schedule + list(res.dhw_power_schedule or []), float
                ).tobytes()).hexdigest()[:12]
                short, unit, gain = priced(plan, prices)
                stats[arm].append((short, unit, gain))
                line += (f" | d={arm} plan {sha} kWh {plan.sum() / 4:.1f} short {short:.4f}"
                         f" cost/plant-kWh {unit:.4f} gain-vs-flat {gain:+.4f}")
            print(line)
        for arm in arms:
            st = np.array(stats[arm])
            print(f"{tag} d={arm}: cells {len(st)} heat short max {st[:, 0].max():.4f} "
                  f"gain-vs-flat min {st[:, 2].min():+.4f} max {st[:, 2].max():+.4f} "
                  f"cells where flat wins {int((st[:, 2] < 0).sum())}")
        if len(arms) == 2 and stats[0.0] and stats[derate]:
            a, b = np.array(stats[0.0]), np.array(stats[derate])
            rel = b[:, 1] / a[:, 1] - 1
            print(f"{tag} term vs none: cost per plant kWh change min {rel.min():+.4f} "
                  f"max {rel.max():+.4f} cells cheaper {int((rel < -1e-9).sum())} "
                  f"dearer {int((rel > 1e-9).sum())}")
    return failures


def main(argv: list[str]) -> int:
    model = ThermalModel(ThermalParameters(
        min_electrical_power=P_MIN, max_electrical_power=P_MAX))
    partload(model)
    burst(model)
    failures = 0 if "--no-solves" in argv else solves(model)
    print(f"failures {failures}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
