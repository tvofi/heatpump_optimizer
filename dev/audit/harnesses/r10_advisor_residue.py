#!/usr/bin/env python3
"""R10-ADVISOR-RESIDUE (#2257): the three seams R10-ADVISOR (#2572) left open, sized.

WHY IT EXISTS. #2572 recorded three monthly figures it did not fix, each with
a cause it named but never moved: (a) the what-if's ``monthly_cost_delta``,
(b) the Advisor inbox's sensor-gap and hot-water rows, (c) the held figure's
asymmetry between a degree cooler and a degree warmer. The brief sizes each
under its own perturbation before any change, beside the null of
``r10_sav_null_terms.py`` (a flat price and a constant outdoor temperature,
where nothing a month should average can move). A seam whose figure reads
flat under its own perturbation is recorded, not fixed.

Arms (each prints RESULT lines, then the arm's VERDICT):

  whatif  (a) Perturbation: where the live house starts (``r10_advisor_degree.STARTS``:
          at the target, coasted, pre-heated), at three instants. Per start,
          the scratch solve ``async_simulate`` builds (``_shadow``) against
          the live one, for the two degree tiles (``price_tiles.specs``), the
          cap tile (75 %) and a fuse-sized cap (50 %): the plan's figure
          (``monthly_cost_delta``, what the what-if summary and the fuse
          advisor's ``cost_delta_sek_month`` read before #2257's residue), the
          held one, and the settled one (each plan's spend plus its
          ``deferred_energy_cost``: what the fuse advisor and the cap tile
          read after it). A month figure that moves with the house's start
          prices a one-off; a cap can cost, never save. Null control: the
          held figure, which starts held at its own target.
  inbox   (b) Perturbation: the instant the row is read, every hour of the
          suite's seven price days (``r10_advisor_degree.PRICE_DAYS``). The
          sensor-gap row is ``topology.rank_sensor_gaps`` fed by the sensor's
          own ``_gap_probe_terms`` at ``_gap_energy_rate``'s rate for an
          install with no outdoor and no tank sensor, the pump series held
          fixed. The hot-water row is the card's
          (cost_per_day(from) - cost_per_day(to)) x 30 on the coordinator's
          own ``_dhw_setpoint_sweep``, run on that day's price window and the
          hour's outdoor temperature, from 60 degC (a swept candidate, so the
          card's interpolation is the identity), for a household drawing 80 L a
          day (so the sweep recommends below 60). Both are handed what
          production hands them: a ``MonthlyLedger`` settling every interval
          (seeded with the month before) and its ``recent_kwh_price``, which a
          tree without it (the merge base) neither publishes nor reads. Null
          control: the flat price and a constant outdoor temperature.
  asym    (c) Perturbation: the solve's start hour, every two hours of a day,
          on the null series and on the varying one. The held pair's gap
          (warmer + cooler) against its mean magnitude. Whether anything
          reads the two tiles together is a grep, not this arm.
  mixing  The 30-day mean folds days priced at different schedules (after a
          target change, or under an away setback). Perturbation: the whole
          schedule moved -2..+2 K; per shift, the held degree (half of warmer
          minus cooler) at three instants, on the null and the varying series.
          A figure that does not move with where the schedule sits is not
          biased by a mean that mixes schedules.

    PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_advisor_residue.py [whatif] [inbox] [asym] [mixing]

With no arm named, all four run. ``whatif``, ``asym`` and ``mixing`` solve:
about 90, 72 and 90 solves.
"""
from __future__ import annotations

import inspect
import sys
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

import numpy as np

sys.path.insert(0, "dev/audit/harnesses")
import r10_advisor_degree as deg  # noqa: E402
from profiles import DT, prices, solve_inputs, weather  # noqa: E402
from heatpump_optimizer import price_tiles, sensor, topology  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402
from heatpump_optimizer.ledger import SPOT_PRICE_META, MonthlyLedger  # noqa: E402

N = deg.N
#: Instants a what-if is asked at: midnight, the morning ramp, the afternoon.
HOURS = (0, 7, 15)


def _series(flat: bool) -> tuple[np.ndarray, list[np.ndarray]]:
    return deg._series(2, flat)


def _solve(opt, j: int, room: float, slab: float, pr, wx, caps=None):
    t = deg.START + timedelta(hours=j * DT)
    sl = slice(j, j + N)
    return opt.optimize(inputs=solve_inputs(
        initial_state=deg._state(room, slab, float(wx[0][j])), prices=pr[sl], outdoor_temps=wx[0][sl],
        wind_speeds=wx[1][sl], precipitation=wx[2][sl], solar_radiation=wx[3][sl], start_time=t,
        power_caps_extra=None if caps is None else np.full(N, caps)))


def arm_whatif() -> bool:
    opt, model = deg._optimizer()
    hours = opt.config.horizon_hours
    pmax = float(model.params.max_electrical_power)
    asks = [*price_tiles.specs(opt.config, pmax)[:2], ("power_cap_75", {}), ("fuse_cap_50", {})]
    caps = {"power_cap_75": round(0.75 * pmax, 2), "fuse_cap_50": round(0.5 * pmax, 2)}
    moved_plan = moved_held = 0
    rows = 0
    caps_seen: dict[str, list[float]] = {"plan": [], "settled": [], "plan_saves": [], "settled_saves": []}
    for label, flat in (("null", True), ("varying", False)):
        pr, wx = _series(flat)
        for hour in HOURS:
            j = int(hour / DT)
            figs: dict[str, list[tuple[float, float, float]]] = {name: [] for name, _ in asks}
            for room, slab in deg.STARTS:
                live = _solve(opt, j, room, slab, pr, wx)
                for name, overrides in asks:
                    shadow = deg._shadow(opt, model, overrides) if overrides else opt
                    sim = _solve(shadow, j, room, slab, pr, wx, caps.get(name))
                    figs[name].append((
                        price_tiles.per_month(sim.predicted_cost - live.predicted_cost, hours),
                        price_tiles.per_month(sim.baseline_cost - live.baseline_cost, hours),
                        price_tiles.per_month(sim.predicted_cost + sim.deferred_energy_cost
                                              - live.predicted_cost - live.deferred_energy_cost, hours)))
            for name, pairs in figs.items():
                plan = [p for p, _, _ in pairs]
                held = [h for _, h, _ in pairs]
                settled = [x for _, _, x in pairs]
                sp, sh, ss = max(plan) - min(plan), max(held) - min(held), max(settled) - min(settled)
                rows += 1
                if name in caps:
                    caps_seen["plan"].append(sp)
                    caps_seen["settled"].append(ss)
                    caps_seen["plan_saves"] += [p for p in plan if p < -1.0]
                    caps_seen["settled_saves"] += [x for x in settled if x < -1.0]
                moved_plan += sp > 1.0
                moved_held += sh > 1e-9
                print(f"RESULT whatif {label} {hour:02d}:00 {name:15s} plan by start "
                      f"{' '.join(f'{p:+7.1f}' for p in plan)} spread {sp:6.1f} | held "
                      f"{' '.join(f'{h:+6.1f}' for h in held)} spread {sh:.2f} | settled "
                      f"{' '.join(f'{x:+7.1f}' for x in settled)} spread {ss:6.1f}")
    print(f"RESULT whatif rows {rows} plan_moves_by_start {moved_plan} held_moves_by_start {moved_held}")
    n = len(caps_seen["plan"])
    print(f"RESULT whatif caps rows {n} spread_by_start mean plan {np.mean(caps_seen['plan']):.1f} "
          f"settled {np.mean(caps_seen['settled']):.1f}; figures reading a saving (< -1) plan "
          f"{len(caps_seen['plan_saves'])}/{3 * n} settled {len(caps_seen['settled_saves'])}/{3 * n}")
    ok = moved_held == 0
    print(f"VERDICT whatif {'the plan figure moves with the start; the held figure does not' if ok else 'INVALID: the held control moved'}")
    return ok


class _Draws:
    def quantile(self, _label, _q):
        return None


def _dhw_row(price_window: np.ndarray, outdoor: float, recent: float | None) -> float:
    """The card's hot-water row on the coordinator's own sweep, from 60 degC,
    handed the published recent kWh price as ``_build_data_dict`` hands it
    (a tree before that route, the merge base, prices at the feed's window)."""
    cfg = deg.house(two_zone=False, dhw=True, dhw_daily_consumption=80.0)
    params = deg.ThermalParameters.from_config(cfg)
    params.dhw_enabled = True
    params.dhw_setpoint = 60.0
    stub = SimpleNamespace(
        _thermal_params=params, _prices=[{"total": float(p)} for p in price_window],
        _current_state=SimpleNamespace(outdoor_temperature=outdoor),
        _dhw_learner=SimpleNamespace(draw_stats=_Draws()), _thermal_model=deg.ThermalModel(params))
    sweep_fn = HeatPumpOptimizerCoordinator._dhw_setpoint_sweep
    routed = "kwh_price" in inspect.signature(sweep_fn).parameters
    sweep = sweep_fn(stub, recent) if routed else sweep_fn(stub)
    cost = {c["setpoint"]: c["cost_per_day"] for c in sweep["candidates"]}
    return (cost[60] - cost[sweep["recommended_setpoint"]]) * 30.0


def _gap_row(data: dict, hp: list[float]) -> float:
    """The sensor-gap row as ``SensorGapAdvisorSensor`` ranks it, from ``data``."""
    rate = sensor._gap_energy_rate(data, {})
    gaps = topology.rank_sensor_gaps({}, house_kw=[], hp_kw=hp, peak_price=45.0, peak_window=60,
                                     peak_count=3, **sensor._gap_probe_terms({}, hp, [], rate))
    top = [g for g in gaps if g.get("empty") and g.get("sek_per_month")]
    return float(top[0]["sek_per_month"]) if top else 0.0


def arm_inbox() -> bool:
    """Each row read every hour of a week, the ledger settling every interval
    as production's does: seeded with the month before (31 days of the same
    price rotation), so its level is a month's when the week starts."""
    hp = [2.0 if i % 3 else 0.0 for i in range(96)]
    moved = {}
    for label, flat in (("null", True), ("varying", False)):
        day_prices = [np.full(N, 1.20) if flat else prices(p, deg.START) for p in deg.PRICE_DAYS]
        out = weather("winter_mild", deg.START)[0]
        out = np.full(N, float(np.mean(out))) if flat else out
        ledger = MonthlyLedger()
        seed = deg.START.replace(day=1) - timedelta(days=31)
        for d in range(31):
            for i, p in enumerate(day_prices[d % len(day_prices)]):
                ledger.observe_meta_mean(seed + timedelta(days=d, hours=i * DT), SPOT_PRICE_META, float(p))
        gap_all, dhw_all, gap_day, dhw_day = [], [], [], []
        for k, pr in enumerate(day_prices):
            g, d = [], []
            for h in range(24):
                for i in range(4 * h, 4 * h + 4):
                    ledger.observe_meta_mean(deg.START + timedelta(days=k, hours=i * DT), SPOT_PRICE_META, float(pr[i]))
                now = (deg.START + timedelta(days=k, hours=h)).replace(tzinfo=UTC)
                # A tree before the recent price (its merge base) publishes none.
                recent = getattr(ledger, "recent_kwh_price", lambda _now: None)(now)
                data = {"current_price": float(pr[h * 4]), "recent_kwh_price": recent}
                g.append(_gap_row(data, hp))
                d.append(_dhw_row(pr, float(out[h * 4]), recent))
            gap_all += g
            dhw_all += d
            gap_day.append(float(np.mean(g)))
            dhw_day.append(float(np.mean(d)))
            print(f"RESULT inbox {label} day {k} {deg.PRICE_DAYS[k]:15s} gap {min(g):6.1f}..{max(g):6.1f} "
                  f"hot_water {min(d):6.1f}..{max(d):6.1f}")
        for row, xs, days in (("gap", gap_all, gap_day), ("hot_water", dhw_all, dhw_day)):
            a = np.asarray(xs)
            within = max(max(xs[i:i + 24]) - min(xs[i:i + 24]) for i in range(0, len(xs), 24))
            moved[(label, row)] = float(a.max() - a.min())
            print(f"RESULT inbox {label} {row:9s} mean {a.mean():6.1f} range {a.min():6.1f}..{a.max():6.1f} "
                  f"(max/min {a.max() / a.min() if a.min() > 0 else float('nan'):.2f}) widest_day {within:6.1f} "
                  f"day_means {min(days):6.1f}..{max(days):6.1f}")
    ok = moved[("null", "gap")] < 1e-9 and moved[("null", "hot_water")] < 1e-9
    print(f"VERDICT inbox {'the null reads flat; the varying rows move by the max/min above' if ok else 'INVALID: the null moved'}")
    return ok


def arm_asym() -> bool:
    opt, model = deg._optimizer()
    hours = opt.config.horizon_hours
    down, up = (deg._shadow(opt, model, o) for _, o in price_tiles.specs(opt.config, 6.0)[:2])
    spans = {}
    for label, flat in (("null", True), ("varying", False)):
        pr, wx = _series(flat)
        gaps, mags = [], []
        for hour in range(0, 24, 2):
            j = int(hour / DT)
            room, slab = deg.STARTS[0]
            live = _solve(opt, j, room, slab, pr, wx)
            c = price_tiles.per_month(_solve(down, j, room, slab, pr, wx).baseline_cost - live.baseline_cost, hours)
            w = price_tiles.per_month(_solve(up, j, room, slab, pr, wx).baseline_cost - live.baseline_cost, hours)
            gaps.append(w + c)
            mags.append(0.5 * (w - c))
            print(f"RESULT asym {label} {hour:02d}:00 cooler {c:+6.2f} warmer {w:+6.2f} gap {w + c:+6.2f}")
        spans[label] = max(gaps) - min(gaps)
        print(f"RESULT asym {label} gap {min(gaps):+.2f}..{max(gaps):+.2f} of mean magnitude {np.mean(mags):.2f} "
              f"(worst {max(abs(x) for x in gaps) / np.mean(mags) * 100:.1f} %)")
    if spans["null"] > 1e-6:
        print("VERDICT asym the gap moves with the start hour in the null too: the estimator's, not the prices'")
    else:
        print(f"VERDICT asym the gap is constant in the null; {'it moves' if spans['varying'] > 1e-6 else 'nor does it move'} with the start hour on varying prices")
    return True


def arm_mixing() -> bool:
    """The held degree priced from schedules moved -2, -1, 0, +1, +2 K: the
    days a 30-day mean folds after a target change or an away setback."""
    opt, model = deg._optimizer()
    hours = opt.config.horizon_hours
    # Every comfort level the schedule has set, a kelvin down (the cooler tile's).
    down = price_tiles.specs(opt.config, 6.0)[0][1]
    worst = 0.0
    for label, flat in (("null", True), ("varying", False)):
        pr, wx = _series(flat)
        for hour in HOURS:
            j = int(hour / DT)
            row = []
            for shift in (-2.0, -1.0, 0.0, 1.0, 2.0):
                base = deg._shadow(opt, model, {k: round(v + 1.0 + shift, 1) for k, v in down.items()})
                room, slab = deg.STARTS[0]
                live = _solve(base, j, room, slab, pr, wx)
                c, w = (price_tiles.per_month(_solve(deg._shadow(base, model, o), j, room, slab, pr, wx).baseline_cost
                                              - live.baseline_cost, hours)
                        for _, o in price_tiles.specs(base.config, 6.0)[:2])
                row.append((c, w))
            mags = [0.5 * (w - c) for c, w in row]
            spread = (max(mags) - min(mags)) / float(np.mean(mags))
            worst = max(worst, spread)
            print(f"RESULT mixing {label} {hour:02d}:00 per-degree by schedule shift -2..+2 "
                  f"{' '.join(f'{m:6.2f}' for m in mags)} spread {spread * 100:.1f} %")
    print(f"RESULT mixing worst spread {worst * 100:.1f} % of the per-degree figure")
    print(f"VERDICT mixing {'the held degree does not move with where the schedule sits' if worst < 0.01 else 'the held degree moves with where the schedule sits'}")
    return True


if __name__ == "__main__":
    arms = sys.argv[1:] or ["whatif", "inbox", "asym", "mixing"]
    results = [{"whatif": arm_whatif, "inbox": arm_inbox, "asym": arm_asym, "mixing": arm_mixing}[a]()
               for a in arms]
    sys.exit(0 if all(results) else 1)
