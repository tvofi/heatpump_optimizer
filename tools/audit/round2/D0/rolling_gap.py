"""D0 closed loop: is the single-solve gap realised under re-planning (MPC masking)?

Metric: realised electricity cost plus the realised capacity charge
(tariff.peak_cost on the realised draw; zero without a tariff), SEK, settled
for the end-state difference
with production's own _deferred_energy_cost (two dhw-cap conventions), over
``--days`` simulated days of
closed-loop operation (the tests/rolling.py:run_rolling shape: re-plan every
``--replan-hours``, apply the plan's first steps to a plant, advance, repeat),
production's solver vs the same solver with the race's cheap fixes patched in
through heatpump_optimizer.optimizer:_multi_start_minimize (d0lib.ImprovedSolver:
third candidate refined, bang-bang seeds at 0.6/0.8 of the answer's energy,
one restart). Comfort parity: degree-hours below the per-step floor and min
room temperature; DHW parity: window steps with the tank under dhw_min_temp.
The plant is the optimizer's own model at ``--plant-error 1.0`` (the solver
gap alone) or a leakier house.

Command (headline cell, two-zone DHW, winter_typical/winter_cold, 2 days):
    PYTHONPATH=tests/hastub python tools/audit/round2/D0/rolling_gap.py
Null control:
    PYTHONPATH=tests/hastub python tools/audit/round2/D0/rolling_gap.py --price flat
More cells:
    ... rolling_gap.py --price winter_extreme|winter_moderate|shoulder --weather ...
Capacity tariff (single-zone, the golden capacity_tariff_15min settings):
    ... rolling_gap.py --tz 0 --opt '{"peak_price_per_kw":20.0,"peak_threshold_kw":6.0,"peak_window_minutes":15,"baseline_load_kw":1.0}'
    ... the same with --price flat (null control)
Perturbation: --improved-off makes both arms production (gap -> 0 exactly);
D0_SOLVES=3 sets optimizer._MULTI_START_SOLVES for the production arm
(expected: gap DOWN).

Expected on baseline c398fc8 (Apple M1): realised_gap_pct on the headline
cell positive, of the order of the single-solve gap (0.5-2 % of the bill);
at flat prices near zero. Counts (solves, improved_calls) exact; CPU provisional.
Writes nothing outside stdout.
"""
from __future__ import annotations

import os

for _threads in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
                 "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_threads, "1")

import argparse
import sys
import time
from contextlib import nullcontext
from datetime import timedelta
from unittest import mock

sys.path.insert(0, "tools/audit/round2/D0")

import numpy as np  # noqa: E402

import d0lib as L  # noqa: E402
from heatpump_optimizer.dhw_schedule import hour_in_windows, parse_windows  # noqa: E402
from heatpump_optimizer.tariff import peak_cost  # noqa: E402
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState  # noqa: E402
from profiles import DT, house, prices, weather  # noqa: E402


def tile(series, steps):
    series = np.asarray(series, dtype=float)
    if len(series) >= steps:
        return series[:steps]
    return np.tile(series, int(np.ceil(steps / len(series))))[:steps]


def run(arm: str, *, days, dhw, two_zone, plant_error, price_profile,
        weather_profile, horizon_hours, replan_hours, fracs, opt_over=None):
    cfg = house(two_zone=two_zone, dhw=dhw)
    params = ThermalParameters.from_config(cfg)
    params.dhw_enabled = dhw
    model = ThermalModel(params)
    plant_params = ThermalParameters.from_config(cfg)
    plant_params.dhw_enabled = dhw
    plant_params.heat_loss_coefficient *= plant_error
    plant_params.upper_floor_heat_loss *= plant_error
    plant_params.lower_floor_heat_loss *= plant_error
    plant = ThermalModel(plant_params)
    opt_cfg = L.OptimizationConfig(
        horizon_hours=horizon_hours, time_step_minutes=15,
        target_temp=cfg["target_temperature"], min_temp=cfg["min_temperature"],
        max_temp=cfg["max_temperature"],
    )
    for key, value in (opt_over or {}).items():
        setattr(opt_cfg, key, value)
    optimizer = L.HeatPumpOptimizer(model, opt_cfg)

    total_steps = int(days * 24 / DT)
    horizon_steps = int(horizon_hours / DT)
    span = total_steps + horizon_steps + 4
    price_series = tile(prices(price_profile, L.START), span)
    outdoor, wind, rain, solar = (tile(a, span) for a in weather(weather_profile, L.START))
    state = ThermalState(
        room_temperature=cfg["target_temperature"],
        slab_temperature=cfg["target_temperature"] + 1.0,
        outdoor_temperature=float(outdoor[0]),
        upper_floor_temperature=cfg["target_temperature"],
        lower_floor_temperature=cfg["target_temperature"],
        dhw_temperature=52.0, dhw_hours_since_legionella=20.0,
        buffer_tank_temperature=40.0,
    )
    replan_every = max(1, int(replan_hours / DT))
    windows = parse_windows(cfg.get("dhw_windows", "") or "")
    hist = {k: [] for k in ("room", "dhw", "space", "dhwp", "price", "cost", "hour")}
    plan = None
    prev_plan = None
    churn = []          # mean |new plan - previous plan| over the steps both cover
    objectives = []     # per-solve objective_value
    solver = L.ImprovedSolver(fracs=fracs) if arm == "improved" else nullcontext()
    n_solves = 0
    cpu0 = time.process_time()
    with solver:
        for step in range(total_steps):
            now = L.START + timedelta(hours=step * DT)
            if step % replan_every == 0:
                plan = optimizer.optimize(
                    state, price_series[step:step + horizon_steps],
                    outdoor[step:step + horizon_steps], wind[step:step + horizon_steps],
                    rain[step:step + horizon_steps], solar[step:step + horizon_steps], now,
                )
                n_solves += 1
                objectives.append(float(plan.objective_value))
                if prev_plan is not None:
                    new = np.asarray(plan.power_schedule[:replan_every])
                    old = np.asarray(prev_plan.power_schedule[replan_every:2 * replan_every])
                    m = min(len(new), len(old))
                    if m:
                        churn.append(float(np.mean(np.abs(new[:m] - old[:m]))))
                prev_plan = plan
            off = step % replan_every
            sp = float(plan.power_schedule[off])
            dp = float(plan.dhw_power_schedule[off]) if plan.dhw_power_schedule else 0.0
            hr = now.hour + now.minute / 60.0
            if dhw:
                room, slab, upper, lower, tank = plant.simulate_trajectory_with_dhw(
                    initial_state=state, space_power_schedule=np.array([sp]),
                    dhw_power_schedule=np.array([dp]), outdoor_temps=outdoor[step:step + 1],
                    wind_speeds=wind[step:step + 1], precipitation=rain[step:step + 1],
                    solar_radiation=solar[step:step + 1], start_hour=hr, dt_hours=DT,
                )
            else:
                room, slab, upper, lower = plant.simulate_trajectory(
                    initial_state=state, power_schedule=np.array([sp]),
                    outdoor_temps=outdoor[step:step + 1], wind_speeds=wind[step:step + 1],
                    precipitation=rain[step:step + 1], solar_radiation=solar[step:step + 1],
                    dt_hours=DT,
                )
                tank = [state.dhw_temperature, state.dhw_temperature]
            state = ThermalState(
                room_temperature=float(room[-1]), slab_temperature=float(slab[-1]),
                outdoor_temperature=float(outdoor[step]),
                upper_floor_temperature=float(upper[-1]),
                lower_floor_temperature=float(lower[-1]),
                dhw_temperature=float(tank[-1]),
                buffer_tank_temperature=state.buffer_tank_temperature,
                wood_tank_temperature=state.wood_tank_temperature,
                dhw_hours_since_legionella=(
                    0.0 if float(tank[-1]) >= params.dhw_legionella_temp - 1.0
                    else (state.dhw_hours_since_legionella or 0.0) + DT
                ),
            )
            hist["room"].append(min(float(upper[-1]), float(lower[-1])) if two_zone else float(room[-1]))
            hist["dhw"].append(float(tank[-1]))
            hist["space"].append(sp)
            hist["dhwp"].append(dp)
            hist["price"].append(float(price_series[step]))
            hist["cost"].append((sp + dp) * DT * float(price_series[step]))
            hist["hour"].append(hr)
    cpu = time.process_time() - cpu0
    h = {k: np.asarray(v) for k, v in hist.items()}
    # Settlement inputs: the day after the run, as production prices its own
    # end state (25th-percentile price, mean-outdoor COP).
    settle_prices = price_series[total_steps:total_steps + horizon_steps]
    settle_outdoor = outdoor[total_steps:total_steps + horizon_steps]
    floor = np.array([opt_cfg.get_temp_bounds(hr)[0] for hr in h["hour"]])
    in_win = np.array([hour_in_windows(float(hr), windows) for hr in h["hour"]]) if dhw else np.zeros(total_steps, bool)
    # Realised capacity charge over the run: production's own peak_cost on the
    # realised total draw (top-k metering windows above the threshold).
    total = h["space"] + h["dhwp"]
    peak_charge = float(peak_cost(
        total, opt_cfg.baseline_load_array(total_steps), opt_cfg.peak_threshold_kw,
        opt_cfg.peak_price_per_kw, opt_cfg.peak_window_minutes, DT, opt_cfg.peak_count,
    ))
    return {
        "cost": float(np.sum(h["cost"])) + peak_charge,
        "energy_cost": float(np.sum(h["cost"])),
        "peak_charge": peak_charge,
        "energy": float(np.sum(h["space"] + h["dhwp"]) * DT),
        "comfort_dh": float(np.sum(np.maximum(0.0, floor - h["room"])) * DT),
        "min_room": float(np.min(h["room"])),
        "mean_room": float(np.mean(h["room"])),
        "dhw_short_steps": int(np.sum(in_win & (h["dhw"] < params.dhw_min_temp - 0.05))),
        "min_dhw_in_window": float(np.min(h["dhw"][in_win])) if in_win.any() else float("nan"),
        "end_room": float(h["room"][-1]),
        "end_dhw": float(h["dhw"][-1]),
        "n_solves": n_solves,
        "improved_calls": getattr(solver, "improved_calls", 0),
        "improved_gain": getattr(solver, "total_gain", 0.0),
        "cpu": cpu,
        "end_state": state,
        "optimizer": optimizer,
        "settle_prices": settle_prices,
        "settle_outdoor": settle_outdoor,
        "params": params,
        "churn": float(np.mean(churn)) if churn else 0.0,
        "objective_sum": float(np.sum(objectives)),
    }


def settle(prod, imp, convention: str) -> float:
    """Cost improved must pay to reach production's end state (negative = credit).

    Production's own ``_deferred_energy_cost`` (report-only in production).
    ``production``: dhw cap at the idle floor, as _optimize_with_dhw settles a
    midnight end; ``full_tank``: dhw cap at the setpoint, so the whole tank
    difference is priced -- the convention that is harder on the improved arm
    when it ends with a colder tank.
    """
    opt = prod["optimizer"]
    p = prod["params"]
    dhw_cap = p.dhw_setpoint if convention == "full_tank" else min(p.dhw_idle_min_temp, p.dhw_min_temp)
    caps = opt._settlement_caps(prod["settle_outdoor"], dhw_cap=float(dhw_cap))
    return float(opt._deferred_energy_cost(
        prod["end_state"], imp["end_state"], prod["settle_prices"], prod["settle_outdoor"],
        include_dhw=bool(p.dhw_enabled), caps=caps,
    ))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--price", default="winter_typical")
    ap.add_argument("--weather", default="winter_cold")
    ap.add_argument("--days", type=int, default=2)
    ap.add_argument("--replan-hours", type=float, default=2.0)
    ap.add_argument("--horizon", type=int, default=24)
    ap.add_argument("--plant-error", type=float, default=1.0)
    ap.add_argument("--tz", type=int, default=1)
    ap.add_argument("--dhw", type=int, default=1)
    ap.add_argument("--fracs", default="0.6,0.8")
    ap.add_argument("--improved-off", action="store_true")
    ap.add_argument("--opt", default=None, help="JSON OptimizationConfig overrides (e.g. a capacity tariff)")
    a = ap.parse_args()
    import json
    opt_over = json.loads(a.opt) if a.opt else None
    fracs = tuple(float(f) for f in a.fracs.split(",") if f)
    solves = os.environ.get("D0_SOLVES")
    patches = []
    if solves:
        patches.append(mock.patch.object(L.opt_mod, "_MULTI_START_SOLVES", int(solves)))
        patches[-1].start()
    kw = dict(days=a.days, dhw=bool(a.dhw), two_zone=bool(a.tz), plant_error=a.plant_error,
              price_profile=a.price, weather_profile=a.weather, horizon_hours=a.horizon,
              replan_hours=a.replan_hours, fracs=fracs, opt_over=opt_over)
    clock = L.CpuClock()
    with clock:
        prod = run("production", **kw)
        imp = run("production" if a.improved_off else "improved", **kw)
    for p in patches:
        p.stop()
    name = f"{a.price}/{a.weather}/{'tz' if a.tz else 'sz'}/{'dhw' if a.dhw else 'nodhw'}/{a.days}d/replan{a.replan_hours}h/plant{a.plant_error}"
    print(f"cell {name}")
    for label, r in (("production", prod), ("improved", imp)):
        print(f"  {label:<10} cost {r['cost']:8.3f} SEK (energy {r['energy_cost']:.3f} + peak {r['peak_charge']:.3f}) energy {r['energy']:7.2f} kWh comfort_dh {r['comfort_dh']:.4f} "
              f"min_room {r['min_room']:.3f} mean_room {r['mean_room']:.3f} dhw_short {r['dhw_short_steps']} "
              f"min_dhw_win {r['min_dhw_in_window']:.2f} end_room {r['end_room']:.3f} end_dhw {r['end_dhw']:.2f} "
              f"solves {r['n_solves']} improved_calls {r['improved_calls']} gain {r['improved_gain']:.3f} cpu {r['cpu']:.1f}s")
    gap = prod["cost"] - imp["cost"]
    s_prod = settle(prod, imp, "production")
    s_full = settle(prod, imp, "full_tank")
    print(f"RESULT realised_peak_charge_production={prod['peak_charge']:.4f} SEK")
    print(f"RESULT realised_peak_charge_improved={imp['peak_charge']:.4f} SEK")
    print(f"RESULT realised_cost_production={prod['cost']:.4f} SEK")
    print(f"RESULT realised_cost_improved={imp['cost']:.4f} SEK")
    print(f"RESULT realised_gap_unsettled={gap:.4f} SEK")
    print(f"RESULT settlement_production_convention={s_prod:+.4f} SEK")
    print(f"RESULT settlement_full_tank_convention={s_full:+.4f} SEK")
    print(f"RESULT realised_gap_settled_production={gap - s_prod:.4f} SEK")
    print(f"RESULT realised_gap_settled_full_tank={gap - s_full:.4f} SEK")
    print(f"RESULT realised_gap_pct_settled_full_tank={100.0 * (gap - s_full) / max(prod['cost'], 1e-9):.3f} pct_of_bill")
    print(f"RESULT realised_gap_per_day_settled_full_tank={(gap - s_full) / a.days:.4f} SEK_per_day")
    print(f"RESULT plan_churn_production={prod['churn']:.4f} kW")
    print(f"RESULT plan_churn_improved={imp['churn']:.4f} kW")
    print(f"RESULT objective_sum_production={prod['objective_sum']:.3f} SEK_objective")
    print(f"RESULT objective_sum_improved={imp['objective_sum']:.3f} SEK_objective")
    print(f"RESULT comfort_dh_production={prod['comfort_dh']:.4f} K_h")
    print(f"RESULT comfort_dh_improved={imp['comfort_dh']:.4f} K_h")
    print(f"RESULT min_room_production={prod['min_room']:.3f} C")
    print(f"RESULT min_room_improved={imp['min_room']:.3f} C")
    print(f"RESULT mean_room_delta={imp['mean_room'] - prod['mean_room']:+.4f} K")
    print(f"RESULT end_room_delta={imp['end_room'] - prod['end_room']:+.4f} K")
    print(f"RESULT dhw_short_production={prod['dhw_short_steps']} count")
    print(f"RESULT dhw_short_improved={imp['dhw_short_steps']} count")
    print(f"RESULT solves={prod['n_solves']} count")
    print(f"RESULT improved_calls={imp['improved_calls']} count")
    print(f"RESULT improved_single_solve_gain_total={imp['improved_gain']:.4f} SEK_objective")
    print("RESULT provisional=true flag")
    L.footer(clock)
    return 0


if __name__ == "__main__":
    sys.exit(main())
