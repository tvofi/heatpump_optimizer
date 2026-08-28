import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "custom_components"))
import numpy as np
from datetime import datetime, timedelta
from profiles import prices, weather, house, DT, N
from heatpump_optimizer.thermal_model import (
    ThermalModel, ThermalParameters, ThermalState)
from heatpump_optimizer.optimizer import (
    HeatPumpOptimizer, OptimizationConfig, count_compressor_starts)
from heatpump_optimizer.dhw_schedule import parse_windows, hour_in_windows

START = datetime(2026,1,15,0,0)
ISSUES=[]
def issue(scen,msg):
    ISSUES.append(f"[{scen}] {msg}")

def run(scen, price_p, weather_p, two_zone=False, dhw=True, start=START, **over):
    cfg = house(two_zone=two_zone, dhw=dhw, **over)
    p = ThermalParameters.from_config(cfg); p.dhw_enabled = dhw
    m = ThermalModel(p)
    oc = OptimizationConfig(
        horizon_hours=24, time_step_minutes=15,
        target_temp=cfg["target_temperature"], min_temp=cfg["min_temperature"],
        max_temp=cfg["max_temperature"])
    opt = HeatPumpOptimizer(m, oc)
    pr = prices(price_p, start)
    ot, wind, rain, sol = weather(weather_p, start)
    st = ThermalState(room_temperature=21.0, slab_temperature=22.0,
        outdoor_temperature=float(ot[0]), dhw_temperature=50.0,
        dhw_hours_since_legionella=20.0,
        upper_floor_temperature=21.0, lower_floor_temperature=21.0,
        buffer_tank_temperature=40.0)
    r = opt.optimize(st, pr, ot, wind, rain, sol, start)

    pw = np.asarray(r.power_schedule)
    room = np.asarray(r.room_temp_trajectory[1:])
    kwh = pw.sum()*DT

    # ---- invariants ----
    if r.status not in ("optimal","success"): issue(scen,f"solver status {r.status!r}")
    if pw.min() < -1e-6: issue(scen,f"negative power {pw.min():.3f} kW")
    if pw.max() > p.max_electrical_power+1e-6:
        issue(scen,f"power {pw.max():.2f} kW exceeds pump max {p.max_electrical_power}")
    if not np.all(np.isfinite(pw)): issue(scen,"non-finite power")
    # Per-step bounds: the optimizer allows a 0.5C setback outside day hours,
    # so a blanket floor is both too lenient by day and wrong by night.
    _worst = 0.0; _at = None
    for _i in range(len(pw)):
        _t = start + timedelta(hours=_i*DT); _h = _t.hour + _t.minute/60
        _lo = oc.get_temp_bounds(_h)[0]
        _d = _lo - room[_i]
        if _d > _worst: _worst, _at = _d, (_h, room[_i], _lo)
    if _worst > 0.05:
        issue(scen,f"room {_at[1]:.2f}C below bound {_at[2]:.1f} at h={_at[0]:.2f}")
    if room.max() > cfg["max_temperature"]+0.5 and kwh > 0.5:
        issue(scen,f"room {room.max():.1f}C above max {cfg['max_temperature']}")
    if not (-100 <= r.savings_percentage <= 100):
        issue(scen,f"savings {r.savings_percentage}% out of range")
    if r.predicted_cost < -1e-6 and pr.min() >= 0:
        issue(scen,f"negative predicted cost {r.predicted_cost} with non-negative prices")
    if r.baseline_cost < 0: issue(scen,f"negative baseline {r.baseline_cost}")

    # ---- DHW availability during demand windows ----
    dhw_ok = "-"
    dhw_peak = float("nan")
    if dhw and r.dhw_temp_trajectory:
        dt_traj = np.asarray(r.dhw_temp_trajectory[1:])
        dhw_pw = np.asarray(r.dhw_power_schedule)
        wins = parse_windows(cfg["dhw_windows"])
        hrs = [(start.hour + i*DT) % 24 for i in range(N)]
        inw = np.array([hour_in_windows(h, wins) for h in hrs])
        if inw.any():
            worst = dt_traj[inw].min()
            dhw_ok = f"{worst:.1f}"
            # 0.5 C, not the 2.0 C this allowed until v5.1.8. The wider bar
            # was wide enough to sit through a real regression: the floor
            # repair stopped topping the tank up at all and left a demand
            # window 1.11 C under the promised minimum, and every scenario
            # here still passed. The planner's own repair stage converges to
            # hundredths of a degree when it is working, so anything past
            # half a degree is a defect, not slack.
            if worst < cfg["dhw_min_temperature"] - 0.5:
                issue(scen,f"DHW only {worst:.1f}C during demand window "
                           f"(need {cfg['dhw_min_temperature']})")
        if dt_traj.max() > 70.5:
            issue(scen,f"DHW overshoot {dt_traj.max():.1f}C")

        # Hot water is a deferrable load -- but only up to what the tank can
        # hold. The DISCRETIONARY part is the energy bought OUTSIDE a demand
        # window: the planner picked those hours freely, so putting them in
        # the priciest slots means it failed to shift. Energy bought INSIDE a
        # window is the tank being refilled as it is drained, and a household
        # that draws more in a day than its tank holds has to buy the
        # difference at whatever the price is then.
        #
        # Judging the whole schedule against a flat "share of slots" bar
        # measured the tank rather than the planner, and v5.1.8 made that
        # visible: the planning ceiling used to be the disinfection
        # temperature (60 C) rather than the owner's own charge limit (55 C
        # by default), so the store looked 5 C deeper than they had asked
        # for. With the honest, smaller store the same optimal plan carries
        # 37% of its energy in the top price quartile where it used to carry
        # 17% -- not because it stopped shifting, but because there is less
        # to shift with. The "does it pre-charge at all" half of that bar
        # survives as the outside-the-window check just below.
        dhw_kwh = dhw_pw.sum()*DT
        if dhw_kwh > 0.2 and pr.max()/max(pr.min(), 0.01) > 2.0:
            exp_slots = pr >= np.percentile(pr, 75)
            dhw_peak = dhw_pw[exp_slots].sum()*DT/dhw_kwh
            free_kwh = dhw_pw[~inw].sum()*DT if inw.any() else dhw_kwh
            free_mask = (~inw) if inw.any() else np.ones(N, dtype=bool)
            if free_kwh > 0.2:
                free_peak = dhw_pw[exp_slots & free_mask].sum()*DT/free_kwh
                if free_peak > exp_slots.mean():
                    issue(scen,f"DHW pre-charges {free_peak:.0%} of its "
                               f"discretionary energy in the most expensive "
                               f"{exp_slots.mean():.0%} of slots")
            elif inw.any():
                # No discretionary energy at all: everything was bought
                # inside a demand window, so the bar above has nothing to
                # measure -- and skipping outright let a plan that buys ALL
                # its hot water in the priciest slots go unjudged. What is
                # left to judge is the buying it did do. Inside the windows
                # the planner still chooses WHICH slots, so its energy must
                # not be more concentrated in the expensive ones than an even
                # spread across those windows would be.
                inside_kwh = dhw_pw[inw].sum()*DT
                bar = float((exp_slots & inw).sum()) / float(inw.sum())
                got = (dhw_pw[exp_slots & inw].sum()*DT
                       / max(inside_kwh, 1e-9))
                if inside_kwh > 0.2 and got > bar + 1e-9:
                    issue(scen,f"DHW buys {got:.0%} of its energy in the "
                               f"most expensive slots of its demand windows "
                               f"({bar:.0%} of them)")
            # It should also be willing to charge ahead of the window rather
            # than only inside it.
            if inw.any() and not inw.all():
                outside = dhw_pw[~inw].sum()*DT/dhw_kwh
                cheapest_outside = pr[~inw].min() < pr[inw].min() - 1e-9
                if cheapest_outside and outside < 0.2:
                    issue(scen,f"DHW heats only {outside:.0%} outside the demand "
                               f"windows although cheaper hours exist there")

    # ---- did it actually avoid the expensive hours? ----
    if pr.max()/max(pr.min(),0.01) > 2.0 and kwh > 0.5:
        exp = pr >= np.percentile(pr, 75)
        share_peak = pw[exp].sum()*DT/kwh
        share_slots = exp.mean()
        if share_peak > share_slots:
            issue(scen,f"uses {share_peak:.0%} of energy in the most expensive "
                       f"{share_slots:.0%} of slots (price-blind)")
    else:
        share_peak = float("nan")

    # ---- compressor cycling ----
    #
    # Reported rather than asserted on, because the point of measuring it is to
    # decide whether a cycling penalty is worth paying for at all. A plan that
    # does not chatter does not need one, and the penalty is not free: it buys
    # smoothness with savings.
    starts = r.compressor_starts
    total_starts = starts + count_compressor_starts(
        np.asarray(r.dhw_power_schedule or [])
    )
    if total_starts > N * DT:  # more than one start per hour of horizon
        issue(scen, f"plan chatters: {total_starts} compressor starts in "
                    f"{N*DT:.0f} h")

    # ---- plan reason codes ----
    #
    # Every heating step must carry an explanation. Without one an unexpected
    # slot is indistinguishable from a bug, which is what makes bug reports
    # against this optimizer so weak.
    if r.space_reasons:
        unexplained = sum(
            1 for i, p in enumerate(r.power_schedule)
            if p > 0.05 and (i >= len(r.space_reasons)
                             or r.space_reasons[i] == "idle")
        )
        if unexplained:
            issue(scen, f"{unexplained} heating steps carry no reason code")
    elif kwh > 0.5:
        issue(scen, "plan publishes no reason codes at all")

    # ---- price provenance ----
    if len(r.price_known) != len(r.prices):
        issue(scen, "price provenance mask does not cover the horizon")

    print(f"{scen:<34} {r.status[:7]:<7} {kwh:6.2f}kWh base={r.baseline_cost:7.2f} "
          f"cost={r.predicted_cost:7.2f} sav={r.savings_percentage:5.1f}% "
          f"room {room.min():4.1f}-{room.max():4.1f} dhw>={dhw_ok:>5} "
          f"peak%={share_peak:.2f} dhwpeak%={dhw_peak:.2f} "
          f"starts={total_starts:2d} kW={r.projected_peak_kw:4.1f} "
          f"{r.solve_time_ms:5.0f}ms")
    return r

print("=== WINTER, single zone, space + DHW ===")
run("winter typical, cold",      "winter_typical","winter_cold")
run("winter extreme prices",     "winter_extreme","winter_cold")
run("winter mild, windy+rain",   "winter_typical","winter_mild")
run("winter flat price (control)","flat",         "winter_cold")

print("=== WINTER, TWO ZONE, space + DHW ===")
run("2zone winter typical",      "winter_typical","winter_cold", two_zone=True)
run("2zone winter extreme",      "winter_extreme","winter_cold", two_zone=True)
run("2zone winter mild",         "winter_typical","winter_mild", two_zone=True)
run("2zone flat price (control)","flat",          "winter_cold", two_zone=True)

print("=== SUMMER, DHW only (no space heating demand) ===")
run("summer warm, DHW only",     "summer_typical","summer_warm")
run("summer negative prices",    "summer_negative","summer_warm")
run("summer cool rainy",         "summer_typical","summer_cool")
run("summer flat price (control)","flat",         "summer_warm")
run("2zone summer warm",         "summer_typical","summer_warm", two_zone=True)

print("=== SHOULDER SEASON ===")
run("april shoulder",            "shoulder",      "shoulder")
run("2zone april shoulder",      "shoulder",      "shoulder", two_zone=True)

print("=== SPACE HEATING ONLY (DHW disabled) ===")
run("winter, no DHW",            "winter_typical","winter_cold", dhw=False)
run("summer, no DHW",            "summer_typical","summer_warm", dhw=False)
run("2zone winter, no DHW",      "winter_typical","winter_cold", two_zone=True, dhw=False)

print("\n" + ("NO ISSUES" if not ISSUES else f"{len(ISSUES)} ISSUES:\n  " + "\n  ".join(ISSUES)))
sys.exit(1 if ISSUES else 0)
