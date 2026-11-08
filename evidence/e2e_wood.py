"""Reviewer's own instrument (not the finder's, not the fixer's): drive the
production entry wood_fuel_from_parts end to end on the 16 cells x 2 price
days x 2 derates (pp.solve), at 41 wood prices spanning each cell's band, and
compare the published cheaper_hour_count with an independent re-statement of
the derated price: on and sek < price / (cop(T) * (1 - d * clip((P_space+P_dhw
- Pmin)/(Pmax-Pmin), 0, 1))). Also reports the linear (no-draw) count, so the
defect size is visible, and a null: at d=0 published == linear."""
import inspect, sys
from datetime import timezone
from types import SimpleNamespace as NS
import numpy as np
sys.path.insert(0, "dev/audit/harnesses")
import r10_partload_pricing as pp, r10_setpoint_boost as sb
from heatpump_optimizer import wood_fuel as wf
from heatpump_optimizer.thermal_model import partload_factor
CFG = {"wood_tank_top_entity": "sensor.t", "external_heat_detection_enabled": True,
       "wood_type": "mixed", "wood_packing": "packed", "wood_furnace_efficiency": 75.0}
has_pl = "partload_at" in inspect.signature(wf.wood_fuel_from_parts).parameters
sek1 = wf.wood_sek_per_kwh(1.0, "mixed", "packed", 75.0)
D = 0.112
mism = {}; short = {}; nullbad = 0; cells = 0
for tag, prices in (("spread", sb.SPREAD), ("flat", sb.FLAT)):
    for d in (0.0, D):
        for cell in sb.CELLS:
            opt, res = pp.solve(cell, prices, d)
            p = opt.model.params; cells += 1
            pr = np.asarray(res.prices, float)
            sp = np.nan_to_num(np.asarray(res.power_schedule, float))
            dh = np.nan_to_num(np.asarray(res.dhw_power_schedule or [0.0]*len(pr), float))
            on = np.asarray(res.heat_pump_on_schedule, bool)
            cop = np.array([float(opt.model.compute_cop(float(t))) for t in res.outdoor_temps])
            x = np.clip((sp + dh - p.min_electrical_power) / (p.max_electrical_power - p.min_electrical_power), 0, 1)
            f = 1.0 - p.cop_partload_derate * x
            lin_price, true_price = pr / cop, pr / (cop * f)
            band = (lin_price[on].min(), true_price[on].max()) if on.any() else (1, 1)
            for w in np.linspace(*band, 41):
                cfg = dict(CFG, wood_price_sek_m3=float(w) / sek1)
                kw = dict(external_heat=NS(suppressing=False), opt_config=NS(dt_hours=0.25, min_temp=20.0),
                          thermal_params=p, thermal_model=opt.model, current_state=NS(wood_tank_temperature=None),
                          result=res, local_tz=timezone.utc)
                if has_pl: kw["partload_at"] = partload_factor
                v = wf.wood_fuel_from_parts(cfg, **kw)
                sek = v["sek_per_kwh"]
                pub = v.get("cheaper_hour_count") or 0
                exp = int((on & (sek < true_price)).sum())
                linc = int((on & (sek < lin_price)).sum())
                key = (tag, d)
                mism[key] = max(mism.get(key, 0), abs(pub - exp))
                short[key] = max(short.get(key, 0), exp - linc)
                if d == 0.0 and pub != linc: nullbad += 1
for k in mism: print(f"RESULT {k[0]} d={k[1]} published-vs-derated mismatch max {mism[k]}; derated-vs-linear shortfall max {short[k]}")
print(f"RESULT partload_at wired: {has_pl}; null (d=0 published != linear) {nullbad}; cells {cells}")
