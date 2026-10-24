"""Lead L4 (catch-up verifier, group `leads`): LegionellaGuard (and its
DisinfectionSwitch) hold the EntryConfig reference passed at construction.

Two in-process paths can change the coordinator's live config:
  1. an options save -> __init__.async_update_options -> async_reload (a new
     coordinator and a new guard), unless the saved config equals effective_config;
  2. coordinator.async_update_thermal_params (the set_thermal_parameters service)
     rebuilds the context in place: self._ctx = replace(ctx, _config=_with_quiet_keys(...))
     (coordinator.py ~5901) -- no reload, and the guard keeps the old object.

Metrics, after path 2 with params carrying both quiet window specs and a non-default
silent fraction, on a real LegionellaGuard built as coordinator._init_features builds it:
  M1 keys whose value differs between guard._config and the live ctx._config;
  M2 the same, restricted to the guard's and its switch's READ SET
     (dhw_free_disinfection_enabled, dhw_temp_entity, dhw_disinfection_switch_entity,
     dhw_disinfection_mode -- every EntryConfig field legionella.py / disinfection.py read).
Null: params with no quiet key -> M1 = M2 = 0.
Control / perturbation (shows M2 can see a stale read): the fold in memory also folds
dhw_free_disinfection_enabled -> M2 = 1.
Path 1: async_update_options on a stub entry whose saved config differs -> reload count.
Expected: M1 > 0, M2 = 0 at main (stale object, no field the guard reads), null 0,
control M2 = 1, path-1 reload count 1.
Command (tree root): PYTHONPATH=tests/hastub:custom_components python dev/audit/rounds/round10/catchup/leads/l4_legionella_config.py
Baseline: origin/main d749c986d. Machine: tvofi mac, 8 cores, not timing-sensitive.
"""
import asyncio
from dataclasses import replace
from types import SimpleNamespace

import heatpump_optimizer as pkg
from heatpump_optimizer import coordinator as cmod
from heatpump_optimizer import quiet_windows
from heatpump_optimizer.const import (
    CONF_QUIET_OFF_WINDOWS,
    CONF_QUIET_SILENT_WINDOWS,
    CONF_SILENT_MODE_FRACTION,
)
from heatpump_optimizer.entry_config import EntryConfig
from heatpump_optimizer.legionella import LegionellaGuard
from heatpump_optimizer.thermal_model import ThermalParameters

READ_SET = ("dhw_free_disinfection_enabled", "dhw_temp_entity",
            "dhw_disinfection_switch_entity", "dhw_disinfection_mode")

hass = SimpleNamespace(
    services=SimpleNamespace(async_call=None),
    states=SimpleNamespace(get=lambda e: None),
)
base = EntryConfig.from_mapping({"dhw_temp_entity": "sensor.tank"})


def build():
    ctx = cmod.CoordinatorContext(base, ThermalParameters(), hass, None, None)
    guard = LegionellaGuard(
        hass, "e1", ctx._thermal_params, ctx._config,
        action=lambda: {}, disinfect=cmod._disinfection_switch(hass, ctx._config),
        dhw_blocked=lambda: False,
    )
    return ctx, guard


def diff(a, b, keys=None):
    da, db = dict(a), dict(b)
    keys = keys or sorted(set(da) | set(db))
    return [k for k in keys if da.get(k) != db.get(k)]


def read_view(cfg):
    e = EntryConfig.from_mapping(cfg)
    return {k: getattr(e, k) for k in READ_SET}


def run(label, params):
    ctx, guard = build()
    live = replace(ctx, _config=cmod._with_quiet_keys(ctx._config, params))._config  # coordinator.py ~5901
    m1 = diff(guard._config, live)
    gv, lv = read_view(guard._config), read_view(live)
    m2 = [k for k in READ_SET if gv[k] != lv[k]]
    sw = cmod._disinfection_switch  # the switch shares the guard's object
    same_obj = guard.disinfect._config is guard._config
    print(f"RESULT {label} M1_keys_differ={len(m1)} {m1} M2_read_set_differ={len(m2)} {m2} switch_shares_guard_config={same_obj}")


QUIET = {CONF_QUIET_SILENT_WINDOWS: "22:00-06:00", CONF_QUIET_OFF_WINDOWS: "12:00-13:00",
         CONF_SILENT_MODE_FRACTION: 0.5}
run("main", QUIET)
run("null_no_quiet_keys", {})

orig = quiet_windows.apply_config_keys


def widened(config, params):
    orig(config, params)
    config["dhw_free_disinfection_enabled"] = not EntryConfig.from_mapping(config).dhw_free_disinfection_enabled


quiet_windows.apply_config_keys = widened
run("control_fold_touches_read_set", QUIET)
quiet_windows.apply_config_keys = orig


# Path 1: an options save that changes the config reloads the entry.
async def path1():
    reloads = []

    async def async_reload(entry_id):
        reloads.append(entry_id)

    entry = SimpleNamespace(entry_id="e1", data={}, options={"dhw_temp_entity": "sensor.other"},
                            runtime_data=SimpleNamespace(effective_config=base))
    h = SimpleNamespace(config_entries=SimpleNamespace(async_reload=async_reload))
    await pkg.async_update_options(h, entry)
    same = SimpleNamespace(entry_id="e1", data={}, options=dict(base),
                           runtime_data=SimpleNamespace(effective_config=base))
    await pkg.async_update_options(h, same)
    print(f"RESULT path1_options_changed reloads={len(reloads)} (changed save then identical save)")


asyncio.run(path1())
