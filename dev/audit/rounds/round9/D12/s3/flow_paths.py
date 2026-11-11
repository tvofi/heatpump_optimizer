"""D12-s3 (round 9): plant the shipping initial config flow writes that the user never affirmed.

Metric: over every completion path of the real initial config flow (every menu
branch, every form submitted as an untouched browser submits it, except the
quick-setup plant questions which the --answers arm sets), count the paths whose
created entry, once driven through one real coordinator cycle, publishes a
plant no answer on that path affirmed: ``dhw_enabled`` true with a modelled
tank trajectory in ``dhw_plan``, or ``two_zone_enabled`` true.
Count key: the coordinator's delivered ``_async_update_data`` dict
(``dhw_enabled``, ``dhw_energy_kwh``, ``two_zone_enabled``), never the flow's
stored keys themselves.

Run from the export root:
    PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D12/s3/flow_paths.py [--answers no|shipped] [--perturb explicit_presence]

Production symbols: config_flow:HeatPumpOptimizerConfigFlow (async_step_* via
its own menus), thermal_model:_dhw_enabled_from_config and the two-zone
presence rule in ThermalParameters.from_config, coordinator:
HeatPumpOptimizerCoordinator._async_update_data.

Perturbation --perturb explicit_presence: the presence rules count only an
explicit answer (``dhw_enabled`` / ``two_zone_mode``), the one-line fix shape
for both; the invented-plant count on the wizard paths must go to zero.

Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1, box B7 (linux container).
Expected (--answers no): paths=5, invented_paths=3 (exact); see REPORT.md.
"""
from __future__ import annotations

import os

for _v in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_v, "1")

import argparse
import asyncio
import sys
import time

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import usable as U  # noqa: E402  (same directory: cell seeding and run helpers)
from harness import FakeEntry, FakeHass, ha_setup_entry  # noqa: E402

from heatpump_optimizer import config_flow, const, quick_setup, thermal_model  # noqa: E402

REQUIRED = {
    "name": "Heat Pump Optimizer",
    const.CONF_TIBBER_TOKEN: "tok",
    const.CONF_WEATHER_ENTITY: "weather.home",
}


class _OK:
    class _Resp:
        status = 200

        async def json(self):
            return {"data": {"viewer": {"name": "Home"}}}

        async def __aenter__(self):
            return self

        async def __aexit__(self, *exc):
            return False

    def post(self, *a, **k):
        return self._Resp()


def _untouched(schema, overrides):
    answers = {}
    for key in schema.schema if schema else ():
        name = str(key)
        if name in overrides:
            answers[name] = overrides[name]
            continue
        desc = getattr(key, "description", None) or {}
        if isinstance(desc, dict) and "suggested_value" in desc:
            answers[name] = desc["suggested_value"]
            continue
        try:
            default = key.default()
        except Exception:  # noqa: BLE001
            default = None
        if default is not None and type(default).__name__ != "Undefined":
            answers[name] = default
    return answers


async def _walk(choices, plant_answers):
    """Drive the flow; at the i-th menu take choices[i]. Returns (config, menus, trail)."""
    flow = config_flow.HeatPumpOptimizerConfigFlow()
    flow.hass = FakeHass()
    result = await flow.async_step_user(None)
    menus = []
    trail = []
    mi = 0
    for _ in range(40):
        kind = result.get("type")
        if kind == "create_entry":
            return dict(result["data"]), menus, trail
        if kind == "menu":
            options = list(result["menu_options"])
            menus.append((result["step_id"], options))
            if mi < len(choices):
                step = choices[mi]
            else:
                step = options[0]
            # quick_setup declines the pre-fill back to finish_setup; a second
            # visit to that menu finishes.
            if result["step_id"] == "finish_setup" and "quick_setup" in trail and step == "quick_setup":
                step = "finish_now"
            mi += 1
            trail.append(step)
            result = await getattr(flow, f"async_step_{step}")(None)
            continue
        step = result["step_id"]
        trail.append(step)
        overrides = dict(REQUIRED) if step == "user" else {}
        if step == "quick_setup":
            overrides.update(plant_answers)
        result = await getattr(flow, f"async_step_{step}")(_untouched(result.get("data_schema"), overrides))
    raise RuntimeError(f"flow did not finish: {trail}")


def enumerate_paths(plant_answers):
    real = config_flow.async_get_clientsession
    config_flow.async_get_clientsession = lambda hass, verify_ssl=True: _OK()
    try:
        done = {}
        frontier = [()]
        while frontier:
            choices = frontier.pop()
            cfg, menus, trail = asyncio.run(_walk(list(choices), plant_answers))
            key = tuple(trail)
            if key in done:
                continue
            done[key] = cfg
            # branch at each menu beyond the prefix
            for depth in range(len(choices), len(menus)):
                taken = list(choices) + [m[1][0] for m in menus[len(choices):depth]]
                for opt in menus[depth][1][1:]:
                    frontier.append(tuple(taken + [opt]))
        return done
    finally:
        config_flow.async_get_clientsession = real


def cycle(cfg):
    cfg = dict(cfg)
    # Offline stand-ins for the network price source and the thermometers the
    # untouched flow leaves unmapped; plant keys are untouched.
    cfg.pop(const.CONF_TIBBER_TOKEN, None)
    cfg.update({k: v for k, v in U.BASE.items() if k in ("price_source", "price_entity", "indoor_temp_entity", "outdoor_temp_entity")})
    cfg["heat_pump_switch_entity"] = "switch.hp"
    hass = FakeHass()
    U._seed(hass, {"switch.hp": ("on", None)})
    entry = FakeEntry(data=cfg)
    asyncio.run(ha_setup_entry(U.integration, hass, entry))
    return asyncio.run(entry.runtime_data._async_update_data())


def _planned_kwh(data):
    return sum((r.get("power") or 0.0) * 0.25 for r in (data.get("schedule") or []))


def _perturb_explicit_presence():
    def dhw(config):
        return bool(config.get(const.CONF_DHW_ENABLED, False))

    thermal_model._dhw_enabled_from_config = dhw
    orig = thermal_model.ThermalParameters.from_config.__func__

    def from_config(cls, config, *a, **k):
        config = dict(config)
        config.setdefault(const.CONF_TWO_ZONE_MODE, const.TWO_ZONE_MODE_OFF)
        return orig(cls, config, *a, **k)

    thermal_model.ThermalParameters.from_config = classmethod(from_config)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--answers", choices=("no", "shipped"), default="no")
    ap.add_argument("--perturb", choices=("explicit_presence",), default=None)
    args = ap.parse_args()
    if args.perturb:
        _perturb_explicit_presence()
    plant = (
        {k: False for k in quick_setup.SHIPPED_ANSWERS}
        if args.answers == "no"
        else dict(quick_setup.SHIPPED_ANSWERS)
    )
    t0, tt0 = time.process_time(), time.thread_time()
    paths = enumerate_paths(plant)
    invented = 0
    dhw_paths = zone_paths = 0
    for trail, cfg in sorted(paths.items()):
        data = cycle(cfg)
        asked = "quick_setup" in trail
        dhw_yes = asked and plant[quick_setup.FIELD_DHW_TANK]
        zone_yes = asked and plant[quick_setup.FIELD_TWO_ZONE]
        inv = []
        dplan = [r.get("dhw_temp") for r in (data.get("dhw_plan") or {}).get("forecast", []) if r.get("dhw_temp") is not None]
        if data.get("dhw_enabled") and dplan and not dhw_yes:
            inv.append(f"dhw(tank modelled over {len(dplan)} steps, planned {data.get('dhw_energy_kwh') or 0:.2f} kWh)")
            dhw_paths += 1
        if data.get("two_zone_enabled") and not zone_yes:
            inv.append("two_zone")
            zone_paths += 1
        if inv:
            invented += 1
            honest = dict(cfg)
            if not dhw_yes:
                honest[const.CONF_DHW_ENABLED] = False
            if not zone_yes:
                honest[const.CONF_TWO_ZONE_MODE] = const.TWO_ZONE_MODE_OFF
            hd = cycle(honest)
            inv.append(
                "plan vs the stated plant: planned %.2f vs %.2f kWh, predicted_cost %.3f vs %.3f"
                % (_planned_kwh(data), _planned_kwh(hd),
                   data.get("predicted_cost") or 0, hd.get("predicted_cost") or 0)
            )
        print("PATH", " > ".join(trail), "| asked_plant=%s" % asked, "| invented:", inv or "-")
    cpu, tcpu = time.process_time() - t0, time.thread_time() - tt0
    print(f"RESULT paths={len(paths)} count")
    print(f"RESULT invented_paths={invented} count")
    print(f"RESULT invented_dhw_paths={dhw_paths} count")
    print(f"RESULT invented_two_zone_paths={zone_paths} count")
    print(f"RESULT thread_factor={cpu / tcpu if tcpu else float('nan'):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        with open("/proc/vmstat") as fh:
            sw = next((int(l.split()[1]) for l in fh if l.startswith("pswpin")), 0)
    except OSError:
        sw = 0
    print(f"RESULT swapins={sw}")


if __name__ == "__main__":
    main()
