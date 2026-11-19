"""D2.M3 savings-identity over layout x mixing_valve_mode x month.

Each cell: solve the golden house with the cell's topology_layout and
mixing_valve_mode (two-zone where a valve needs it), then book every plan step's
settlement snapshot (optimizer.get_current_action's readings,
OptimizationResult.settlement_schedule) into a production
ledger.MonthlyLedger through observe_spot_and_settle_savings with a perfect
meter (actual kWh = the plan's shipped space+DHW draw x dt) at the raw input
price, and read the published row from MonthlyLedger.savings_months.

Metric definitions (one line each):
  I_row   = |row.savings_sek - (row.baseline_sek - row.actual_sek)|              (tol 0.005)
  I_tie   = |(ledger baseline - stored - actual)_unrounded - (plan baseline_cost - plan spend)|
            plan spend = sum(raw price * shipped draw * dt)                       (tol 1e-6)
  I_tel   = |sum(stored_kw_th*dt) - (E(end) - E(start))|, E = optimizer._stored_thermal_energy
            uncapped over the plan's own published trajectory                    (tol 1e-6 kWh_th)
  month=upgraded_mid_month_from_previous_release: half the steps booked, the ledger
            round-tripped through as_dict/JSON/from_dict (the restart an upgrade
            is), then the rest; the row must equal the whole-month row (tol 0.005).
  month=buffer_above_curve: as whole, with the plan starting its buffer at 60 C.
Count key: the published row (savings_months) and the settlement snapshot the
plan delivers; never a re-labelled input.

Run:  PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D2/s3/m3_savings.py
Expected at baseline: identity_failures=0 over 60 cells (see REPORT for the
measured value). Perturbation for the judge: --perturb-drop-stored books every
snapshot without stored_kw_th, I_tie must go up on every cell with a store change.
Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692, machine B6 (shared).
"""
import _common  # noqa: F401
from _common import footer, solve_golden, np

import argparse
import json
from datetime import datetime, timedelta

LAYOUTS = ["no_valve", "single_tank_valve", "slab_shunt", "two_tank_4way", "valve_upper_direct_slab"]
MODES = ["manual", "none", "smart_read", "smart_write"]
MONTHS = ["whole", "upgraded_mid_month_from_previous_release", "buffer_above_curve"]


def spec_for(layout, mode, month):
    cfg = {"topology_layout": layout, "mixing_valve_mode": mode,
           "buffer_tank_volume": 750.0, "buffer_max_temperature": 70.0}
    if layout == "two_tank_4way":
        cfg.update({"wood_tank_top_entity": "sensor.wood_top", "wood_tank_volume": 500.0})
    st = {"buffer_tank_temperature": 60.0 if month == "buffer_above_curve" else 32.0}
    two_zone = layout != "no_valve" or mode != "none"
    return dict(two_zone=two_zone, dhw=True, config_overrides=cfg, state_overrides=st)


def book(ledger_mod, steps, drop_stored, split=None):
    led = ledger_mod.MonthlyLedger()
    for k, (when, pend, actual, spot, dt) in enumerate(steps):
        if split is not None and k == split:
            led = ledger_mod.MonthlyLedger.from_dict(json.loads(json.dumps(led.as_dict())))
        p = dict(pend)
        if drop_stored:
            p.pop("stored_kw_th", None)
        led.observe_spot_and_settle_savings(when, spot, p, actual, dt)
    return led


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--perturb-drop-stored", action="store_true")
    ap.add_argument("--only-layout")
    a = ap.parse_args()
    import golden  # noqa: F401
    from heatpump_optimizer import ledger as L

    fails = 0
    cells = 0
    for layout in LAYOUTS:
        if a.only_layout and layout != a.only_layout:
            continue
        for mode in MODES:
            for month in MONTHS:
                cells += 1
                rec = solve_golden("winter_single_dhw", spec_for(layout, mode, month), keep=False)
                opt, res, inp = rec["opt"], rec["result"], rec["inputs"]
                p = opt.model.params
                n = len(res.power_schedule)
                dt = opt.config.dt_hours
                raw = np.asarray(inp.forecast.prices, dtype=float)[:n]
                draw = np.asarray(res.power_schedule, dtype=float)
                if res.dhw_power_schedule:
                    draw = draw + np.asarray(res.dhw_power_schedule, dtype=float)
                t0 = datetime(2026, 1, 1, 0, 0)  # month-aligned so one month holds the day
                steps = []
                for i in range(n):
                    pend = dict(res.settlement_schedule[i])
                    pend["power"] = float(draw[i])
                    steps.append((t0 + timedelta(hours=dt * i), pend, float(draw[i] * dt), float(raw[i]), dt))
                now = datetime(2026, 2, 3)
                led = book(L, steps, a.perturb_drop_stored,
                           split=n // 2 if month.startswith("upgraded") else None)
                row = led.savings_months(now)[0]
                i_row = abs((row["savings_sek"] or 0.0) - (row["baseline_sek"] - row["actual_sek"])) \
                    if row["savings_sek"] is not None else float("nan")
                mk = "2026-01"
                stored_sek = row["stored_heat_sek"]
                base_l = led.line(mk, "savings_baseline")["sek"] * (row["meter_calibration"] or 1.0)
                act_l = led.line(mk, "savings_actual")["sek"]
                plan_base = float(np.sum(raw * np.asarray(res.baseline_power_schedule, dtype=float)) * dt)
                plan_spend = float(np.sum(raw * draw) * dt)
                i_tie = abs((base_l - act_l) - (plan_base - plan_spend))
                # telescoping of the stored line
                import copy
                s0 = copy.copy(inp.state)
                s1 = copy.copy(inp.state)
                tz = p.two_zone_enabled
                s0.room_temperature = res.room_temp_trajectory[0]; s1.room_temperature = res.room_temp_trajectory[-1]
                s0.slab_temperature = res.slab_temp_trajectory[0]; s1.slab_temperature = res.slab_temp_trajectory[-1]
                if tz:
                    s0.upper_floor_temperature = res.upper_temp_trajectory[0]; s1.upper_floor_temperature = res.upper_temp_trajectory[-1]
                    s0.lower_floor_temperature = res.lower_temp_trajectory[0]; s1.lower_floor_temperature = res.lower_temp_trajectory[-1]
                bt = res.buffer_temp_trajectory
                if bt:
                    s0.buffer_tank_temperature = bt[0]; s1.buffer_tank_temperature = bt[-1]
                elif rec["settle"]:
                    # unthrottled tank: the result publishes no buffer trajectory, the
                    # settlement's own plan end state carries it
                    s1.buffer_tank_temperature = rec["settle"][-1][1].buffer_tank_temperature
                d_e = opt._stored_thermal_energy(s1) - opt._stored_thermal_energy(s0)
                tel = sum(float(s.get("stored_kw_th", 0.0)) for s in res.settlement_schedule) * dt
                i_tel = abs(tel - d_e)
                ok = (not (i_row > 0.005)) and i_tie < 1e-6 and i_tel < 1e-6
                if month.startswith("upgraded"):
                    whole = book(L, steps, a.perturb_drop_stored).savings_months(now)[0]
                    d_up = max(abs((row[k] or 0) - (whole[k] or 0)) for k in ("baseline_sek", "actual_sek", "savings_sek"))
                    ok = ok and d_up <= 0.005
                else:
                    d_up = 0.0
                fails += 0 if ok else 1
                print(f"CELL savings-identity layout={layout} mixing_valve_mode={mode} month={month} "
                      f"resolved_layout={p.topology_layout} resolved_mode={p.mixing_valve_mode} two_zone={tz} "
                      f"I_row={i_row:.3g} I_tie={i_tie:.3e} I_tel={i_tel:.3e} upgrade_delta={d_up:.3g} "
                      f"row_saving={row['savings_sek']} stored_sek={stored_sek} plan_predicted_savings={res.predicted_savings:.3f} "
                      f"plan_deferred={res.deferred_energy_cost:.3f} buffer_end={bt[-1] if bt else None} "
                      f"{'OK' if ok else 'FAIL'}", flush=True)
    print(f"RESULT identity_failures={fails} count")
    print(f"RESULT cells={cells} count")
    footer()


if __name__ == "__main__":
    main()
