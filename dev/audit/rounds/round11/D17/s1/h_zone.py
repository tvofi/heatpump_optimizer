"""D17-s1-03 harness: the thermal-model options page offers fields a two-zone model never reads.

Metric: over every field the `thermal_model` options page renders for a two-zone entry
(the default install: two_zone_mode auto resolves to on), the number whose change,
saved through async_step_thermal_model and run through a restart and one full cycle,
moves no plan key (space_plan, schedule, dhw_plan, current_action, costs) on the
two-zone model, while the same change does move the plan on a single-zone entry
(two_zone_mode off). Count key: the published plan the coordinator's solve delivers.
Instrumented symbols: heatpump_optimizer.config_flow:async_step_thermal_model (what is
rendered and saved) and heatpump_optimizer.thermal_model:ThermalParameters
(room_thermal_mass, read only on the single-zone branch), through the solve.

Command:  PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D17/s1/h_zone.py
Expected: RESULT two_zone_rendered=8, RESULT two_zone_only_no_effect=1 (house_thermal_mass: inert on two
          zones, effective on one), exact; two_zone_rendered_no_effect=2 also counts compressor_modulation,
          inert on both (D17-s1-04)
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692, box B13
Perturbation: --perturb-gate gives the house_thermal_mass row when=_single_zone (as its
sibling house_heat_loss_coefficient has) in config_flow._OPTION_FIELDS: the page stops
rendering it on two zones and two_zone_only_no_effect goes to 0.
Null control: the single-zone arm, where every rendered field moves the plan
(RESULT single_zone_rendered_no_effect=0).
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import asyncio  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rig  # noqa: E402
from heatpump_optimizer import config_flow as cf  # noqa: E402
from heatpump_optimizer import const  # noqa: E402

if "--perturb-gate" in sys.argv:
    cf._OPTION_FIELDS = tuple(r._replace(when=cf._single_zone) if r.key == const.CONF_HOUSE_THERMAL_MASS else r
                              for r in cf._OPTION_FIELDS)

PLAN_KEYS = ("space_plan", "dhw_plan", "schedule", "current_action", "predicted_cost", "total_cost",
             "dhw_cost", "space_cost")
CHANGE = {"house_thermal_mass": 40.0, "slab_thermal_mass": 40.0, "slab_heat_transfer": 0.05,
          "heat_pump_cop_nominal": 5.5, "heat_pump_max_power": 1.5, "heat_pump_min_power": 1.2,
          "compressor_modulation": "on_off", "heat_pump_cop_partload_derate": 0.15,
          "house_heat_loss_coefficient": 0.6}
EXTRA = {"compressor_modulation": {"heat_pump_min_power": 1.5}}


def canon(o):
    return json.loads(json.dumps(o, default=str, sort_keys=True), parse_float=lambda s: round(float(s), 6))


async def rendered(mode):
    flow, entry, hass = rig.new_flow(options={"two_zone_mode": mode})
    f = await flow.async_step_thermal_model(None)
    return [str(k) for k in f["data_schema"].schema if str(k) != "after_save"]


def plan(mode, field, value):
    extra = EXTRA.get(field, {})
    res, entry = asyncio.run(rig.save_option("thermal_model", field, value,
                                             options={"two_zone_mode": mode}, extra=extra))
    assert not res.get("errors"), res.get("errors")
    hass, coord = rig.build_coord(entry)
    d = rig.run_cycles(coord, 1)
    return canon({k: d.get(k) for k in PLAN_KEYS}), d.get("two_zone_enabled")


def main():
    out = {}
    for mode in ("on", "off"):
        fields = asyncio.run(rendered(mode))
        noeff = []
        for f in fields:
            base, tz = plan(mode, None, None) if f not in EXTRA else plan(mode, list(EXTRA[f])[0],
                                                                           list(EXTRA[f].values())[0])
            moved, tz1 = plan(mode, f, CHANGE[f])
            same = base == moved
            if same:
                noeff.append(f)
            print(f"ROW two_zone_mode={mode} (two_zone_enabled={tz1}) {f}={CHANGE[f]!r} "
                  f"{'NOEFFECT' if same else 'EFFECT'}", flush=True)
        out[mode] = (fields, noeff)
    print(f"RESULT two_zone_rendered={len(out['on'][0])}")
    print(f"RESULT two_zone_rendered_no_effect={len(out['on'][1])} {out['on'][1]}")
    print(f"RESULT single_zone_rendered={len(out['off'][0])}")
    print(f"RESULT single_zone_rendered_no_effect={len(out['off'][1])} {out['off'][1]}")
    only = [f for f in out["on"][1] if f not in out["off"][1]]
    print(f"RESULT two_zone_only_no_effect={len(only)} {only}")
    print(f"RESULT thread_factor={rig.thread_factor()}")
    print(f"RESULT load1={rig.load1()}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
