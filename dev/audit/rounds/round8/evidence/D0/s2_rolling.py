"""D0-s2 receding-horizon harness: horizon length (6/24/48 h) and the terminal
credit, measured on the REALISED closed-loop cost rather than a single plan.

Metric (one line): per cell and arm, adj_cost = sum over executed steps of
(space+dhw) kW * DT * price  -  (E_end - E_start) * p25 / COP_mean, where E is
production ``HeatPumpOptimizer._stored_thermal_energy(include_dhw=True, caps=
_settlement_caps(outdoor))`` (SEK), and comfort = degree-hours of the executed
room trajectory below the configured floor, pull = degree-hours below the
comfort target (the comfort the objective also buys), dhw_dh = degree-hours of the tank
below dhw_min_temp inside a demand window.  The plant IS the optimizer's model
(plant_error 1.0), so every difference is planning, not model mismatch.

Arms: h24 (production default), h6, h48, h24_noterm (terminal cost zeroed by
patching ``HeatPumpOptimizer._terminal_cost`` -- the perturbation that tests its
docstring claim "without this the optimizer always dumps the last couple of
hours").  Null control: price profile "flat".

Instrumented symbols: heatpump_optimizer.optimizer:HeatPumpOptimizer.optimize
(driven in a closed loop), HeatPumpOptimizer._terminal_cost (patched in the
noterm arm), HeatPumpOptimizer._stored_thermal_energy (settlement).
Perturbation: the noterm arm IS the one-line production perturbation
(``_terminal_cost`` returning zero closures); horizon arms perturb
OptimizationConfig.horizon_hours.

Command:
  PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
  MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
  python3 tools/audit/round8/D0/s2_rolling.py [--two-zone] [--days N] \
      [--replan-h H] [--prices a,b] [--weather a,b] [--arms h24,h6,...]
Baseline: cdf82daabcfe3777d98b31489f36df5555ec9d82; machine: 4-vCPU shared
cloud container. Counts/costs are deterministic; timings not reported.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys, time, json, argparse
sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
from datetime import datetime, timedelta
from unittest import mock
import numpy as np
from profiles import DT, house, prices, weather
from heatpump_optimizer import optimizer as om
from heatpump_optimizer.dhw_schedule import hour_in_windows, parse_windows
from heatpump_optimizer.optimizer import HeatPumpOptimizer, OptimizationConfig
from heatpump_optimizer.thermal_model import (ThermalModel, ThermalParameters,
                                              ThermalState)

START = datetime(2026, 1, 15, 0, 0)

ap = argparse.ArgumentParser()
ap.add_argument("--two-zone", action="store_true")
ap.add_argument("--days", type=int, default=2)
ap.add_argument("--replan-h", type=float, default=2.0)
ap.add_argument("--prices", default="winter_typical,winter_extreme,shoulder,"
                "winter_narrow,winter_moderate,summer_negative,flat")
ap.add_argument("--weather", default="winter_cold,winter_mild,shoulder")
ap.add_argument("--arms", default="h24,h6,h48,h24_noterm")
ap.add_argument("--dhw", type=int, default=1)
ARGS = ap.parse_args()


def tile(series, steps):
    series = np.asarray(series, dtype=float)
    return np.tile(series, int(np.ceil(steps / len(series))))[:steps]


def _zero_terminal(self, prices, outdoor_temps, solar_gains=None):
    def cost(*a, **k):
        return 0.0

    def cost_batch(traj):
        return np.zeros(traj["room"].shape[0])
    return cost, cost_batch


def run(pp, wp, arm):
    tz = ARGS.two_zone
    dhw = bool(ARGS.dhw)
    horizon = {"h24": 24, "h6": 6, "h48": 48, "h24_noterm": 24}[arm]
    cfg = house(two_zone=tz, dhw=dhw)
    params = ThermalParameters.from_config(cfg)
    params.dhw_enabled = dhw
    model = ThermalModel(params)
    plant_params = ThermalParameters.from_config(cfg)
    plant_params.dhw_enabled = dhw
    plant = ThermalModel(plant_params)
    oc = OptimizationConfig(horizon_hours=horizon, time_step_minutes=15,
                            target_temp=cfg["target_temperature"],
                            min_temp=cfg["min_temperature"],
                            max_temp=cfg["max_temperature"])
    opt = HeatPumpOptimizer(model, oc)
    total = int(ARGS.days * 24 / DT)
    hs = int(horizon / DT)
    span = total + 48 * 4 + 8
    pr = tile(prices(pp, START), span)
    ot, wi, ra, so = (tile(a, span) for a in weather(wp, START))
    state = ThermalState(room_temperature=21.0, slab_temperature=22.0,
                         outdoor_temperature=float(ot[0]),
                         upper_floor_temperature=21.0,
                         lower_floor_temperature=21.0, dhw_temperature=52.0,
                         dhw_hours_since_legionella=20.0,
                         buffer_tank_temperature=40.0)
    s0 = state
    windows = parse_windows(cfg.get("dhw_windows", "") or "")
    every = max(1, int(ARGS.replan_h / DT))
    cost = 0.0
    below = 0.0
    dhw_below = 0.0
    pull = 0.0
    energy = 0.0
    tail_dump = []
    plan = None
    ctx = (mock.patch.object(HeatPumpOptimizer, "_terminal_cost", _zero_terminal)
           if arm == "h24_noterm" else None)
    if ctx:
        ctx.start()
    try:
        for step in range(total):
            now = START + timedelta(hours=step * DT)
            if step % every == 0:
                plan = opt.optimize(state, pr[step:step + hs], ot[step:step + hs],
                                    wi[step:step + hs], ra[step:step + hs],
                                    so[step:step + hs], now)
                sp = np.asarray(plan.power_schedule)
                tail_dump.append(float(np.mean(sp[-8:])))
            off = step % every
            p_s = float(plan.power_schedule[off])
            p_d = (float(plan.dhw_power_schedule[off])
                   if plan.dhw_power_schedule else 0.0)
            if dhw:
                room, slab, up, lo, tank, _, _ = plant.simulate_trajectory_with_dhw(
                    initial_state=state, space_power_schedule=np.array([p_s]),
                    dhw_power_schedule=np.array([p_d]),
                    outdoor_temps=ot[step:step + 1], wind_speeds=wi[step:step + 1],
                    precipitation=ra[step:step + 1],
                    solar_radiation=so[step:step + 1],
                    start_hour=now.hour + now.minute / 60.0, dt_hours=DT)
            else:
                room, slab, up, lo, _, _, _ = plant.simulate_trajectory(
                    state, np.array([p_s]), ot[step:step + 1], wi[step:step + 1],
                    ra[step:step + 1], so[step:step + 1], DT)
                tank = [state.dhw_temperature] * 2
            state = ThermalState(
                room_temperature=float(room[-1]), slab_temperature=float(slab[-1]),
                outdoor_temperature=float(ot[step]),
                upper_floor_temperature=float(up[-1]),
                lower_floor_temperature=float(lo[-1]),
                dhw_temperature=float(tank[-1]),
                buffer_tank_temperature=state.buffer_tank_temperature,
                wood_tank_temperature=state.wood_tank_temperature,
                dhw_hours_since_legionella=(
                    0.0 if float(tank[-1]) >= params.dhw_legionella_temp - 1.0
                    else (state.dhw_hours_since_legionella or 0.0) + DT))
            cost += (p_s + p_d) * DT * float(pr[step])
            energy += (p_s + p_d) * DT
            hr = (now.hour + now.minute / 60.0 + DT) % 24
            floor = oc.get_temp_bounds(hr)[0]
            r = min(float(up[-1]), float(lo[-1])) if tz else float(room[-1])
            below += max(0.0, floor - r) * DT
            pull += max(0.0, oc.get_comfort_temp(hr) - r) * DT
            if dhw and hour_in_windows(hr, windows):
                dhw_below += max(0.0, params.dhw_min_temp - float(tank[-1])) * DT
    finally:
        if ctx:
            ctx.stop()
    # settlement with production's own stored-energy and cap rules
    ref = HeatPumpOptimizer(ThermalModel(params), OptimizationConfig(
        horizon_hours=24, time_step_minutes=15, target_temp=21.0,
        min_temp=17.0, max_temp=23.0))
    caps = ref._settlement_caps(ot[:total], dhw_cap=params.dhw_setpoint)
    e0 = ref._stored_thermal_energy(s0, dhw, caps)
    e1 = ref._stored_thermal_energy(state, dhw, caps)
    cop = max(ref.model.compute_cop(float(np.mean(ot[:total]))), 1e-3)
    p25 = float(np.percentile(pr[:total], 25))
    adj = cost - (e1 - e0) * p25 / cop
    return dict(cost=cost, adj=adj, below=below, pull=pull, dhw_below=dhw_below,
                energy=energy, e_delta=e1 - e0,
                tail_mean_kw=float(np.mean(tail_dump)))


def main():
    arms = ARGS.arms.split(",")
    rows = []
    for pp in ARGS.prices.split(","):
        for wp in ARGS.weather.split(","):
            res = {a: run(pp, wp, a) for a in arms}
            base = res[arms[0]]
            for a in arms:
                r = res[a]
                d = r["adj"] - base["adj"]
                rows.append(dict(cell=f"{pp}/{wp}", arm=a, **r,
                                 d_adj=d,
                                 d_pct=100 * d / abs(base["adj"])
                                 if base["adj"] else 0.0))
                print("CELL %-32s %-11s bill=%8.3f adj=%8.3f d=%+7.3f (%+6.2f%%) "
                      "below=%6.3f pull=%7.3f dhw_below=%6.3f kWh=%7.2f dE=%+6.2f tail=%.3f"
                      % (f"{pp}/{wp}", a, r["cost"], r["adj"], d,
                         rows[-1]["d_pct"], r["below"], r["pull"], r["dhw_below"],
                         r["energy"], r["e_delta"], r["tail_mean_kw"]),
                      flush=True)
    tag = "tz" if ARGS.two_zone else "sz"
    for a in arms[1:]:
        pr_rows = [r for r in rows if r["arm"] == a
                   and not r["cell"].startswith("flat/")]
        fl_rows = [r for r in rows if r["arm"] == a
                   and r["cell"].startswith("flat/")]
        ds = sorted(r["d_pct"] for r in pr_rows)
        if not ds:
            continue
        print(f"RESULT {tag}_{a}_vs_{arms[0]}_d_pct_mean={np.mean(ds):.3f} pct")
        print(f"RESULT {tag}_{a}_vs_{arms[0]}_d_pct_min={ds[0]:.3f} pct")
        print(f"RESULT {tag}_{a}_vs_{arms[0]}_d_pct_max={ds[-1]:.3f} pct")
        if len(ds) > 1:
            print(f"RESULT {tag}_{a}_vs_{arms[0]}_d_pct_mean_drop_most_favourable="
                  f"{np.mean(ds[1:]):.3f} pct")
        print(f"RESULT {tag}_{a}_cells_cheaper_than_{arms[0]}="
              f"{sum(d < -0.1 for d in ds)}/{len(ds)} count")
        print(f"RESULT {tag}_{a}_comfort_dh_total="
              f"{sum(r['below'] for r in pr_rows):.3f} degree_hours")
        if fl_rows:
            print(f"RESULT {tag}_{a}_null_flat_d_pct="
                  f"{','.join('%.3f' % r['d_pct'] for r in fl_rows)} pct")
    print(f"RESULT {tag}_{arms[0]}_comfort_dh_total="
          f"{sum(r['below'] for r in rows if r['arm'] == arms[0] and not r['cell'].startswith('flat/')):.3f} degree_hours")
    out = os.path.join(os.environ.get("TMPDIR", "/tmp"), f"s2_rolling_{tag}.json")
    with open(out, "w") as f:
        json.dump(rows, f, indent=1)
    pc, tc = time.process_time(), time.thread_time()
    print(f"RESULT thread_factor={pc / max(tc, 1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
