"""D0 round 9, seat D0-s3, step D0.M6: MPC masking over a receding horizon.

Closed loop, plant == the optimizer's own model (so every difference is the
planner's, not model error), re-planning every --replan steps (default 2 = the
30-minute DEFAULT_OPTIMIZATION_INTERVAL) over --days days on tiled profiles.
Each cycle hands the optimizer the previous cycle's shipped plan exactly as
coordinator._warm_seeded does (optimizer._prev_shipped_plan = the previous
result's power_schedule, unshifted).

Arms (--arms, comma list):
  prod   production: warm start as _warm_seeded hands it (unshifted).
  cold   no warm start at all (_prev_shipped_plan never set).
  shift  the previous plan shifted by the elapsed steps (prev[k:], tail held),
         i.e. aligned to the new horizon's clock.
  open   re-plan once per day (every 96 steps) and execute that plan open-loop:
         on day 1 exactly the first cycle's plan, i.e. what the loop would
         realize if it trusted its own plan. RESULT
         lastday_excess_prod_over_daily = the production loop's money on the
         last simulated day over this arm's, same plant and inputs.
  noterm the production loop with HeatPumpOptimizer._terminal_cost returning
         zero (the ruler keeps production's terminal cost).
  chal   production's warm start, plus race.py's Challenger replacing
         optimizer._multi_start_minimize (a stronger search on the exact
         captured objective).

Metrics:
  realized_J  the production objective of the FIRST cycle (captured from the
              first optimizer._multi_start_minimize call: its objective and
              args) evaluated on the realized first-horizon space schedule
              (and the realized DHW schedule as its args) -- one ruler for
              every arm, since all arms start from the same state.
  realized energy SEK over the day, degree-steps below the comfort floor.
  seam: per cycle on the prod arm's own trajectory, the same solve with the
        shifted warm start; RESULT seam_cycles_better = cycles where it
        scores strictly lower (J rel. 1e-6), seam_gap_mean_pct, and
        warm_candidate_misaligned = cycles where the handed plan's step-0 is
        the previous plan's step-0 while the clock moved >= 1 step.
Count key: objective values as production's objective returns them for the
delivered schedules.

Command (from the export root):
  PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
    /home/claude/venv314/bin/python tools/audit/round9/D0/s3/mpc.py \
    --topo one --dhw 0 --prices winter_typical --weather winter_cold \
    [--arms prod,open,cold,shift,noterm,chal] [--seam 1] [--days 1] [--replan 2] [--horizon 24]
Perturbation: --warm-shift-prod makes the prod arm hand the shifted plan (the
one-line change to coordinator._warm_seeded / optimizer._warm_start_starts);
seam_cycles_better and the prod-vs-shift realized gap must go to_zero.
Expected values: see REPORT.md (baseline 1936d5ca, B3 container).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys, time, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from datetime import timedelta
from race import Challenger, PRICES, START
from profiles import prices as P_prices, weather as P_weather, house, DT
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState
from heatpump_optimizer.optimizer import HeatPumpOptimizer, OptimizationConfig
from heatpump_optimizer import optimizer as om

ORIG_MSM = om._multi_start_minimize
ORIG_TC = HeatPumpOptimizer._terminal_cost


def _zero_tc(self, prices, outdoor_temps, solar_gains=None, humidity=None):
    return (lambda *a, **k: 0.0), (lambda traj: np.zeros(traj["room"].shape[0]))


def tile(a, n):
    a = np.asarray(a, float)
    return np.tile(a, int(np.ceil(n / len(a))))[:n]


def shifted(prev, k):
    prev = np.asarray(prev, float)
    if k <= 0:
        return prev.copy()
    return np.concatenate([prev[k:], np.full(k, prev[-1])])


class Loop:
    def __init__(self, tz, dhw, pp, wp, days, replan, horizon_h=24):
        self.cfg = house(two_zone=tz)
        self.tz, self.dhw = tz, bool(dhw)
        self.days, self.replan = days, replan
        self.H = int(horizon_h / DT)
        self.T = int(days * 24 / DT)
        span = self.T + self.H + 8
        self.pr = tile(P_prices(pp, START), span)
        w = P_weather(wp, START)
        self.ot, self.wi, self.ra, self.so = (tile(a, span) for a in w)
        self.noterm = False
        self.oc = OptimizationConfig(horizon_hours=horizon_h, time_step_minutes=15,
                                     target_temp=21.0, min_temp=17.0, max_temp=23.0)

    def model(self):
        p = ThermalParameters.from_config(self.cfg)
        p.dhw_enabled = self.dhw
        return ThermalModel(p)

    def state0(self):
        return ThermalState(room_temperature=21.0, slab_temperature=22.0,
                            outdoor_temperature=float(self.ot[0]),
                            upper_floor_temperature=21.0, lower_floor_temperature=21.0,
                            buffer_tank_temperature=40.0, dhw_temperature=48.0,
                            dhw_hours_since_legionella=20.0)

    def solve(self, state, step, prev, mode, capture=None, chal=False):
        o = HeatPumpOptimizer(self.model(), self.oc)
        if prev is not None and mode != "cold":
            o._prev_shipped_plan = (shifted(prev, self.replan) if mode == "shift"
                                    else np.asarray(prev, float).copy())
        sl = slice(step, step + self.H)
        ch = Challenger(self.pr[sl], DT) if chal else None

        def seam(objective, candidates, bounds, args=(), **kw):
            if capture is not None and not capture:
                capture.append((objective, args))
            if ch is not None:
                return ch(objective, candidates, bounds, args=args, **kw)
            return ORIG_MSM(objective, candidates, bounds, args=args, **kw)

        om._multi_start_minimize = seam
        if self.noterm:
            HeatPumpOptimizer._terminal_cost = _zero_tc
        try:
            return o.optimize(state, self.pr[sl], self.ot[sl], self.wi[sl],
                              self.ra[sl], self.so[sl],
                              START + timedelta(hours=step * DT))
        finally:
            om._multi_start_minimize = ORIG_MSM
            HeatPumpOptimizer._terminal_cost = ORIG_TC

    def advance(self, m, state, step, sp, dp):
        now = START + timedelta(hours=step * DT)
        sl = slice(step, step + 1)
        if self.dhw:
            room, slab, up, lo, tank, buf, wood = m.simulate_trajectory_with_dhw(
                initial_state=state, space_power_schedule=np.array([sp]),
                dhw_power_schedule=np.array([dp]), outdoor_temps=self.ot[sl],
                wind_speeds=self.wi[sl], precipitation=self.ra[sl],
                solar_radiation=self.so[sl], start_hour=now.hour + now.minute / 60.0,
                dt_hours=DT)
        else:
            room, slab, up, lo, buf, _, _ = m.simulate_trajectory(
                initial_state=state, power_schedule=np.array([sp]),
                outdoor_temps=self.ot[sl], wind_speeds=self.wi[sl],
                precipitation=self.ra[sl], solar_radiation=self.so[sl], dt_hours=DT,
                start_hour=now.hour + now.minute / 60.0)
            tank = [state.dhw_temperature] * 2
        return ThermalState(
            room_temperature=float(room[-1]), slab_temperature=float(slab[-1]),
            outdoor_temperature=float(self.ot[step]),
            upper_floor_temperature=float(up[-1]), lower_floor_temperature=float(lo[-1]),
            dhw_temperature=float(tank[-1]),
            buffer_tank_temperature=float(buf[-1]) if buf is not None and len(buf) else state.buffer_tank_temperature,
            wood_tank_temperature=state.wood_tank_temperature,
            dhw_hours_since_legionella=(0.0 if float(tank[-1]) >= m.params.dhw_legionella_temp - 1.0
                                        else (state.dhw_hours_since_legionella or 0.0) + DT))

    def run(self, mode, seam=False):
        self.noterm = mode == "noterm"
        m = self.model()
        state = self.state0()
        prev = None
        plan = None
        cap = []
        sp_hist, dp_hist, cost, room_min = [], [], 0.0, []
        traj = {"room": [state.room_temperature], "upper": [state.upper_floor_temperature],
                "lower": [state.lower_floor_temperature]}
        seam_rows = []
        misaligned = 0
        replan = int(24 / DT) if mode == "open" else self.replan
        for step in range(self.T):
            if step % replan == 0:
                if seam and prev is not None:
                    a = self.solve(state, step, prev, "prod")
                    b = self.solve(state, step, prev, "shift")
                    ja, jb = float(a.objective_value), float(b.objective_value)
                    seam_rows.append((ja, jb, abs(a.power_schedule[0] - b.power_schedule[0])))
                    if abs(prev[0] - prev[min(self.replan, len(prev) - 1)]) > 1e-9:
                        misaligned += 1
                    plan = a
                else:
                    plan = self.solve(state, step, prev,
                                      "prod" if mode in ("chal", "open", "noterm") else mode,
                                      capture=cap if step == 0 else None,
                                      chal=(mode == "chal"))
                prev = np.asarray(plan.power_schedule, float)
            off = step % replan
            sp = float(plan.power_schedule[off])
            dp = float(plan.dhw_power_schedule[off]) if plan.dhw_power_schedule else 0.0
            sp_hist.append(sp); dp_hist.append(dp)
            cost += (sp + dp) * DT * float(self.pr[step])
            state = self.advance(m, state, step, sp, dp)
            traj["room"].append(state.room_temperature)
            traj["upper"].append(state.upper_floor_temperature)
            traj["lower"].append(state.lower_floor_temperature)
            room_min.append(min(state.upper_floor_temperature, state.lower_floor_temperature)
                            if self.tz else state.room_temperature)
        hrs = [((step + 1) * DT) % 24 for step in range(self.T)]
        floor = np.array([self.oc.get_temp_bounds(h)[0] for h in hrs])
        viol = float(np.maximum(0.0, floor - np.array(room_min)).sum())
        # Settle the end state with production's own valuation of stored heat:
        # HeatPumpOptimizer._terminal_cost over the horizon that follows the
        # last simulated step (the ORIGINAL closure, whatever the arm ran).
        sl = slice(self.T, self.T + self.H)
        tc, _ = ORIG_TC(HeatPumpOptimizer(self.model(), self.oc), self.pr[sl], self.ot[sl])
        one = lambda v: np.array([float(v)])
        settle = float(tc(one(state.room_temperature), one(state.slab_temperature),
                          one(state.upper_floor_temperature), one(state.lower_floor_temperature),
                          one(state.buffer_tank_temperature)))
        # Realized comfort terms, by production's own HeatPumpOptimizer._comfort_terms
        # over the whole simulated run (targets and bounds per hour of day).
        tgt = np.array([self.oc.get_comfort_temp(h) for h in hrs])
        mx = np.array([self.oc.get_temp_bounds(h)[1] for h in hrs])
        band = np.maximum(tgt - floor, 1.0)
        pen, pull = HeatPumpOptimizer._comfort_terms(
            HeatPumpOptimizer(self.model(), self.oc), np.array(traj["room"]),
            np.array(traj["upper"]), np.array(traj["lower"]), tgt, floor, mx, band)
        return dict(sp=np.array(sp_hist), dp=np.array(dp_hist), cost=cost, viol=viol,
                    settle=settle, comfort=float(pen) + float(pull), room_mean=float(np.mean(room_min)),
                    cap=cap, seam=seam_rows, misaligned=misaligned, state=state)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--topo", default="one")
    ap.add_argument("--dhw", type=int, default=0)
    ap.add_argument("--prices", default="winter_typical")
    ap.add_argument("--weather", default="winter_cold")
    ap.add_argument("--arms", default="prod,cold,shift")
    ap.add_argument("--seam", type=int, default=1)
    ap.add_argument("--days", type=float, default=1)
    ap.add_argument("--replan", type=int, default=2)
    ap.add_argument("--horizon", type=int, default=24)
    ap.add_argument("--warm-shift-prod", action="store_true")
    a = ap.parse_args()
    for pp in a.prices.split(","):
        L = Loop(a.topo == "two", a.dhw, pp, a.weather, a.days, a.replan, a.horizon)
        tag = f"{a.topo}|{a.dhw}|{pp}|{a.weather}"
        out = {}
        # ruler: first-cycle objective, captured from a plain production solve
        ruler = []
        L.solve(L.state0(), 0, None, "cold", capture=ruler)
        obj, args = ruler[0]
        H = L.H
        for arm in a.arms.split(","):
            mode = arm
            if arm == "prod" and a.warm_shift_prod:
                mode = "shift"
            t0 = time.process_time()
            r = L.run(mode)
            sp = r["sp"][:H]
            dargs = (r["dp"][:H],) if args else ()
            if len(sp) < H:
                J = float("nan")
            else:
                J = float(obj(sp, *dargs))
            out[arm] = (J, r)
            print(f"{tag} arm {arm:<5} realized_J {J:10.4f}  energy {r['cost']:8.3f} SEK  "
                  f"viol {r['viol']:.3f}  starts {int(np.sum(np.diff((r['sp']>0.1).astype(int))>0))}  "
                  f"cpu {time.process_time()-t0:.1f}s", flush=True)
            D = int(24 / DT)
            days = []
            for d in range(int(len(r["sp"]) // D)):
                sl = slice(d * D, (d + 1) * D)
                e = r["sp"][sl] + r["dp"][sl]
                days.append((float(np.sum(e * DT * L.pr[sl])), float(np.sum(e) * DT)))
            r["days"] = days
            print("    per day SEK/kWh: " + "  ".join(f"d{i+1} {c:.2f}/{k:.1f}" for i, (c, k) in enumerate(days))
                  + f"  end room {r['state'].room_temperature:.2f} slab {r['state'].slab_temperature:.2f}"
                  + f" upper {r['state'].upper_floor_temperature:.2f} lower {r['state'].lower_floor_temperature:.2f}"
                  + f" dhw {r['state'].dhw_temperature:.1f}", flush=True)
        if "open" in out and "prod" in out:
            g = 100.0 * (out["prod"][0] - out["open"][0]) / max(abs(out["open"][0]), 1e-12)
            print(f"RESULT realized_excess_prod_over_open_{pp}={g:.4f} %  "
                  f"(J {out['prod'][0]-out['open'][0]:.4f}; energy {out['prod'][1]['cost']-out['open'][1]['cost']:.3f} SEK)")
        if "open" in out and "prod" in out and out["prod"][1]["days"]:
            cp, kp = out["prod"][1]["days"][-1]
            co, ko = out["open"][1]["days"][-1]
            sp_, so_ = out["prod"][1]["settle"], out["open"][1]["settle"]
            tp = out["prod"][1]["cost"] + sp_
            to = out["open"][1]["cost"] + so_
            cp_, co_ = out["prod"][1]["comfort"], out["open"][1]["comfort"]
            print(f"RESULT settled_objective_excess_prod_over_daily_{pp}="
                  f"{100.0*((tp+cp_)-(to+co_))/max(abs(to+co_),1e-12):.4f} %  "
                  f"({(tp+cp_)-(to+co_):+.3f} units: money+settle {tp:.2f} vs {to:.2f}, "
                  f"comfort penalty+pull {cp_:.2f} vs {co_:.2f})")
            print(f"RESULT settled_excess_prod_over_daily_{pp}={100.0*(tp-to)/max(abs(to),1e-12):.4f} %  "
                  f"({tp-to:+.3f} SEK over {len(out['prod'][1]['days'])} d: money {out['prod'][1]['cost']:.2f} vs {out['open'][1]['cost']:.2f}, "
                  f"settle {sp_:.2f} vs {so_:.2f}, room mean {out['prod'][1]['room_mean']:.2f} vs {out['open'][1]['room_mean']:.2f}, "
                  f"viol {out['prod'][1]['viol']:.3f} vs {out['open'][1]['viol']:.3f})")
            print(f"RESULT lastday_excess_prod_over_daily_{pp}={100.0*(cp-co)/max(abs(co),1e-12):.4f} %  "
                  f"({cp-co:+.3f} SEK on {co:.2f}; kWh {kp:.1f} vs {ko:.1f})")
        base = out.get("prod")
        for arm, (J, r) in out.items():
            if arm == "prod" or base is None:
                continue
            g = 100.0 * (base[0] - J) / max(abs(base[0]), 1e-12)
            print(f"RESULT realized_gap_prod_minus_{arm}_{pp}={g:.4f} %  (energy {base[1]['cost']-r['cost']:.3f} SEK)")
        if a.seam:
            r = L.run("prod", seam=True) if not a.warm_shift_prod else None
            if r is not None:
                rows = np.array(r["seam"])
                gaps = 100.0 * (rows[:, 0] - rows[:, 1]) / np.maximum(np.abs(rows[:, 0]), 1e-12)
                better = int(np.sum(gaps > 1e-4))
                worse = int(np.sum(gaps < -1e-4))
                print(f"RESULT seam_cycles_{pp}={len(rows)}")
                print(f"RESULT seam_cycles_better_{pp}={better}")
                print(f"RESULT seam_cycles_worse_{pp}={worse}")
                print(f"RESULT seam_gap_mean_{pp}={gaps.mean():.4f} %  (max {gaps.max():.4f}, min {gaps.min():.4f})")
                print(f"RESULT seam_step0_differs_{pp}={int(np.sum(rows[:,2]>0.05))}")
                print(f"RESULT warm_candidate_misaligned_{pp}={r['misaligned']}")
            else:
                print(f"RESULT seam_cycles_better_{pp}=0  (perturbed: prod hands the shifted plan)")
    print(f"RESULT thread_factor={time.process_time()/max(time.thread_time(),1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")


if __name__ == "__main__":
    main()
