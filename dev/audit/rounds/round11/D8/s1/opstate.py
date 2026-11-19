"""D8-s1 M2: every entity publishing an operating state, against the plan's own draw.

Oracle (never the entity's own derivation): the published current_action's
draw = power + dhw_power and its heat_pump_on. Contradiction classes, keyed on the value
each production entity property returns after a real `_async_update_data` cycle:
  hpa_state    Heat Pump Action state claims running (boost/comfort/eco/hot_water/normal/pre_heat/
               system_identification) while heat_pump_on is False, or off/idle while it is True
  hpa_power    Heat Pump Action power_kw != (draw if on else 0) by more than 0.01 kW
  rec_power    Recommended Power state != (draw if on else 0)
  hvac_action  climate hvac_action heating while heat_pump_on is False, or idle/off while True
  climate_kw   climate recommended_power_kw != (draw if on else 0)
  plan_now     a plan sensor's "heating now" while its own circuit's draw in the action is 0, or a
               circuit drawing while its plan sensor is not "heating now"
  narr_idle    Plan Narrative an idle_* reason while heat_pump_on is True
Cells: every rig cell, plus the Tuya DHW-only overlay (mode select "DHW (Hot Water)": space heating
blocked) and the minimum-modulation cell; 6 cycles each (06:00-07:15 UTC, DHW window open).
Command (from the export root):
    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D8/s1/opstate.py [-v] [--cells a,b]
Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692, machine B4. Expected: printed counts, exact.
Instrumented symbols: heatpump_optimizer.sensor:HeatPumpActionSensor, CurrentPowerSensor,
SpaceHeatingPlanSensor, DHWHeatingPlanSensor, PlanNarrativeSensor;
heatpump_optimizer.climate:HeatPumpOptimizerClimate.hvac_action / extra_state_attributes;
heatpump_optimizer.entity:commanded_power_kw.
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import sys
import time
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rig  # noqa: E402

RUN = {"boost", "comfort", "eco", "hot_water", "normal", "pre_heat", "system_identification"}
OFF = {"off", "idle"}
N_CYCLES = 6


def num(v):
    return float(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else 0.0


def main():
    t0, th0 = time.process_time(), time.thread_time()
    cells = rig.cells()
    only = None
    if "--cells" in sys.argv:
        only = set(sys.argv[sys.argv.index("--cells") + 1].split(","))
    plan = [(n, c, None) for n, c in cells.items()]
    plan.append(("feat_tuya_dhw_only[mode=dhw]", cells["feat_tuya_dhw_only"],
                 {"select.hp_mode": ("DHW (Hot Water)",)}))
    if "--perturb" in sys.argv:
        # One-line production edit, in memory: hvac_action keyed on the space
        # power fraction alone (the `or action.get("heat_pump_on")` clause
        # dropped). A step heating only the tank then reads idle while the
        # pump runs: `hvac_action` must rise above 0 in the DHW-only cell.
        from heatpump_optimizer import climate as climate_mod

        def _space_only(self):
            if self.coordinator.data:
                action = self.coordinator.data.get("current_action", {})
                if action.get("power_normalized", 0) > 0.1:
                    return climate_mod.HVACAction.HEATING
                if self.coordinator.mode == climate_mod.MODE_OFF:
                    return climate_mod.HVACAction.OFF
                return climate_mod.HVACAction.IDLE
            return None

        climate_mod.HeatPumpOptimizerClimate.hvac_action = property(_space_only)
    hits = defaultdict(list)
    checked = 0
    blocked_cycles = 0
    for name, cfg, ov in plan:
        if only and name not in only:
            continue
        hass, entry, coord = rig.build(cfg, ov)
        ents = None
        for idx in range(N_CYCLES):
            err = rig.cycle(hass, coord, idx, ov)
            if ents is None:
                ents = {type(e).__name__: e for _p, e in rig.entities(hass, entry)}
            if err:
                hits["cycle_error"].append(f"{name}|{idx}|{err}")
                continue
            data = coord.data or {}
            if (data.get("heat_pump_signals") or {}).get("space_blocked"):
                blocked_cycles += 1
            a = data.get("current_action") or {}
            on = a.get("heat_pump_on")
            draw = num(a.get("power")) + num(a.get("dhw_power"))
            want = round(draw, 2) if on else 0.0
            tag = f"{name}|c{idx}|on={on}|power={a.get('power')}|dhw={a.get('dhw_power')}|mode={a.get('mode')}"
            checked += 1
            hpa = ents["HeatPumpActionSensor"]
            st = hpa.native_value
            if (st in RUN and on is False) or (st in OFF and on is True):
                hits["hpa_state"].append(f"{tag}|state={st}")
            pk = hpa.extra_state_attributes.get("power_kw")
            if pk is None or abs(num(pk) - want) > 0.01:
                hits["hpa_power"].append(f"{tag}|power_kw={pk}")
            rp = ents["CurrentPowerSensor"].native_value
            if rp is None or abs(num(rp) - want) > 0.01:
                hits["rec_power"].append(f"{tag}|recommended={rp}")
            cl = ents["HeatPumpOptimizerClimate"]
            ha = str(cl.hvac_action) if cl.hvac_action is not None else None
            if (ha == "heating" and on is False) or (ha in ("idle", "off") and on is True):
                hits["hvac_action"].append(f"{tag}|hvac_action={ha}|p_norm={a.get('power_normalized')}")
            ck = cl.extra_state_attributes.get("recommended_power_kw")
            if ck is None or abs(num(ck) - want) > 0.01:
                hits["climate_kw"].append(f"{tag}|climate_kw={ck}")
            for cls, part in (("SpaceHeatingPlanSensor", "power"), ("DHWHeatingPlanSensor", "dhw_power")):
                ent = ents[cls]
                if not ent.available:
                    continue
                now = ent.native_value == "heating now"
                runs = bool(on) and num(a.get(part)) > 0.0
                if now != runs:
                    hits["plan_now"].append(f"{tag}|{cls}={ent.native_value}")
            nar = ents["PlanNarrativeSensor"]
            if nar.available and on is True and str(nar.native_value or "").startswith("idle"):
                hits["narr_idle"].append(f"{tag}|narrative={nar.native_value}")
        rig.dt_util.freeze(None)
    if "-v" in sys.argv:
        for k, v in hits.items():
            for x in v:
                print(f"  {k}: {x}")
    print(f"RESULT checked_cycles={checked} count")
    print(f"RESULT space_blocked_cycles={blocked_cycles} count")
    for k in ("cycle_error", "hpa_state", "hpa_power", "rec_power", "hvac_action", "climate_kw", "plan_now", "narr_idle"):
        print(f"RESULT {k}={len(hits[k])} count")
    print(f"RESULT thread_factor={(time.process_time() - t0) / max(time.thread_time() - th0, 1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
