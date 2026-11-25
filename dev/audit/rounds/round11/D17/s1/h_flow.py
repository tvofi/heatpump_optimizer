"""D17-s1 options-flow harness: every options-step, every after_save, the
modbus_prefill page's fields and the factory reset, against strings.json.

Metric: per item, PASS/FAIL of its documented effect made a check:
  options-step <menu>    the rendered menu offers exactly strings.json's menu_options
                         and each offered page opens
  options-step <page>    the page opens; a submit with one field changed and
                         after_save=menu writes the entry through immediately
                         (async_update_entry recorded, value in entry.options) and
                         returns to the section menu that lists it ("Saving writes
                         through immediately")
  option <page>.after_save  "menu" -> the section menu; "close" -> the dialog closes
                         (create_entry) with the value kept
  option modbus_prefill.<f>  a GCHV package whose registers hold known values; the
                         preview suggests the value the field's own description
                         derives (x0.1, 7//days, h*256+m, capacity/COP), the save keeps
                         it, and a restarted coordinator reads it
  option factory_reset.*  unticked: the menu comes back, nothing changed; ticked: the
                         chosen scope is reset (settings / learned / both)
Count key: an item FAILs on the flow's own result, the entry's stored options, or
the restarted coordinator's EntryConfig value; never on an input attribute.

Command:  PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D17/s1/h_flow.py
Expected: RESULT steps_examined=26, RESULT after_save_examined=22,
          RESULT modbus_examined=18, RESULT factory_examined=2, RESULT flow_fail=0 (exact);
          under --perturb-close after_save_fail=22, flow_fail=61
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692, box B13
Perturbation: --perturb-close swaps const.AFTER_SAVE_CLOSE's routing by patching
config_flow.AFTER_SAVE_CLOSE to "menu" in memory: after_save_fail goes up.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import asyncio  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
from unittest import mock  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rig  # noqa: E402
from harness import FakeState  # noqa: E402
from heatpump_optimizer import config_flow, const  # noqa: E402

MENUS = {m: list(rig.OPT_STEPS[m]["menu_options"]) for m in ("init", "advanced")}
PARENT = {p: m for m in MENUS for p in MENUS[m]}

# One documented field per page to change; values inside the page's own selector range.
CHANGE = {
    "entities": ("price_vat", 1.25), "comfort": ("comfort_temp_day", 22.0),
    "hot_water": ("dhw_setpoint", 58.0), "building": ("buffer_max_temperature", 80.0),
    "tuning": ("price_weight", 2.0), "heat_curve": ("heat_curve_offset_band_k", 1.0),
    "building_preset": ("window_area", 20.0), "thermal_model": ("heat_pump_cop_nominal", 4.5),
    "grid": ("peak_tariff_price_per_kw", 80.0), "solar_pv": ("pv_system_efficiency", 0.7),
    "away": ("away_temperature", 14.0), "quick_setup": ("heated_area_m2", 300.0),
    "learning": ("staleness_max_age_scale", 2.0),
    "entities_metering": ("heat_meter_sees_dhw", True),
    "entities_pump": ("pump_duty_mode", "observe"), "hot_water_tank": ("shower_flow_lpm", 12.0),
    "hot_water_pumps": ("vvc_lead_minutes", 30), "grid_connection": ("main_fuse_phases", 1),
    "grid_fees": ("contract_fixed_price", 0.9), "learning_features": ("precip_type_enabled", True),
    "thermal_model_zones": ("solar_orientation_factor", 0.5),
}
# What a page needs beside its changed field to validate (the base entry has no price source).
EXTRA = {"entities": {"price_source": "entity", "price_entity": "sensor.price"}}
FAILS = []
ROWS = []


def row(kind, item, ok, why):
    ROWS.append((kind, item, ok))
    if not ok:
        FAILS.append((kind, item, why))
    print(f"ROW {kind} {item} {'PASS' if ok else 'FAIL'} {why}", flush=True)


def universe(kind):
    out = subprocess.check_output([sys.executable, "tools/audit/enumerate.py", "d17-features", "--kind", kind],
                                  text=True)
    return [l.split()[1] for l in out.splitlines()]


async def menu_step(name):
    flow, entry, hass = rig.new_flow()
    res = await getattr(flow, f"async_step_{name}")(None)
    shown = list(res.get("menu_options") or [])
    opened = []
    for p in shown:
        f2, _, _ = rig.new_flow()
        try:
            r = await getattr(f2, f"async_step_{p}")(None)
            opened.append(r.get("type") in ("form", "menu"))
        except Exception as e:  # noqa: BLE001
            opened.append(False)
    ok = res.get("type") == "menu" and shown == MENUS[name] and all(opened)
    row("options-step", name, ok, f"shown={shown} documented={MENUS[name]} opened={sum(opened)}/{len(opened)}")


async def overview():
    """'An empty slot is shown as empty ... {setup_summary}': a filled slot changes the summary."""
    out = []
    for extra in ({}, {"dhw_temp_entity": "sensor.dhw"}):
        flow, entry, hass = rig.new_flow(data={**rig.BASE_DATA, **extra})
        res = await flow.async_step_setup_overview(None)
        out.append((res.get("type"), (res.get("description_placeholders") or {}).get("setup_summary", "")))
    ok = out[0][0] == "form" and out[0][1] and out[0][1] != out[1][1] and "sensor.dhw" in out[1][1]
    row("options-step", "setup_overview", ok, f"types={[o[0] for o in out]} summary_moves={out[0][1] != out[1][1]}")


async def page(name, after, value_check=True):
    field, value = CHANGE[name]
    flow, entry, hass = rig.new_flow()
    hass.states.set("sensor.price", FakeState("0.8"))
    form = await getattr(flow, f"async_step_{name}")(None)
    answers = rig.schema_defaults(form)
    sec = rig.field_section(form, field)
    (answers if sec is None else answers.setdefault(sec, {}))[field] = value
    for f2, v2 in EXTRA.get(name, {}).items():
        s2 = rig.field_section(form, f2)
        (answers if s2 in (None, False) else answers.setdefault(s2, {}))[f2] = v2
    answers["after_save"] = after
    res = await rig.submit(flow, name, answers)
    stored = {**entry.data, **entry.options}
    if res.get("type") == "create_entry" and res.get("data") is not None:
        stored = {**entry.data, **res["data"]}
    return res, stored, list(hass.config_entries.updated), entry


async def form_step(name):
    if name == "factory_reset":
        return  # factory_reset() rows it
    res, stored, updated, _ = await page(name, "menu")
    ok = (res.get("type") == "menu" and res.get("step_id") == PARENT.get(name)
          and stored.get(CHANGE[name][0]) == CHANGE[name][1] and bool(updated))
    row("options-step", name, ok, f"type={res.get('type')} step={res.get('step_id')} parent={PARENT.get(name)} "
        f"stored={stored.get(CHANGE[name][0])!r} written={bool(updated)} errors={res.get('errors')}")


async def after_save(name):
    r_menu, s_menu, _, _ = await page(name, "menu")
    r_close, s_close, _, _ = await page(name, "close")
    f, v = CHANGE[name]
    ok = (r_menu.get("type") == "menu" and r_menu.get("step_id") == PARENT.get(name)
          and r_close.get("type") == "create_entry" and s_close.get(f) == v)
    row("option", f"{name}.after_save", ok, f"menu->{r_menu.get('type')}/{r_menu.get('step_id')} "
        f"close->{r_close.get('type')} kept={s_close.get(f)!r}")


# ---- modbus_prefill -------------------------------------------------------
PKG = {404: "520", 405: "650", 406: "420", 518: str(22 * 256), 519: str(6 * 256), 711: str(0b11111110),
       712: str(5 * 256 + 30), 713: str(7 * 256), 714: str((1 << 7) | (1 << 1)), 4109: "0", 601: "7"}
HEX = {a: f"{a:04x}h" for a in PKG}
NAMED = {"sensor.hp_unit_capacity": "9.0", "sensor.hp_outdoor_air_temperature": "-3.5",
         "sensor.hp_dhw_tank_temperature": "48.0", "sensor.hp_leaving_water_temperature_t1": "35.0",
         "sensor.hp_entering_water_temperature_tw_in": "30.0", "sensor.hp_actual_compressor_frequency": "50",
         "binary_sensor.hp_night_mode_frequency_reduction_active": "off"}
# The value each field's description derives from the package (doc formula, not code).
DOC_EXPECT = {
    "dhw_setpoint": 52.0,                 # 0194H x0.1
    "dhw_legionella_temperature": 65.0,   # 0195H x0.1
    "dhw_min_temperature": 42.0,          # 0196H x0.1
    "dhw_windows": "05:30-07:00",         # 02C8H/02C9H h*256+m, schedule has a day set
    "dhw_legionella_interval_days": 3.0,  # 7 // days set in 02CAH (2 days)
    "silent_mode_windows": "22:00-06:00",  # 0206H/0207H
    "heat_pump_max_power": round(9.0 / const.DEFAULT_HEAT_PUMP_COP_NOMINAL, 1),  # capacity / COP nominal
    "space_setpoint_unit": "flow",        # 100DH == water temperature control
    "mixing_valve_write_target_kind": "flow",  # as above, two-zone configured
    "outdoor_temp_entity": "sensor.hp_outdoor_air_temperature",
    "dhw_temp_entity": "sensor.hp_dhw_tank_temperature",
    "heat_pump_supply_temp_entity": "sensor.hp_leaving_water_temperature_t1",
    "heat_pump_return_temp_entity": "sensor.hp_entering_water_temperature_tw_in",
    "compressor_freq_sensor": "sensor.hp_actual_compressor_frequency",
    "heat_pump_capacity_limited_entity": "binary_sensor.hp_night_mode_frequency_reduction_active",
}


def pkg_states(prefix="hp"):
    st = {f"sensor.{prefix}_gchv_r{a}_{HEX[a]}": FakeState(v) for a, v in PKG.items()}
    st.update({k.replace(".hp_", f".{prefix}_"): FakeState(v) for k, v in NAMED.items()})
    return st


async def modbus(items):
    data = {const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor", const.CONF_DHW_TANK_VOLUME: 180.0,
            "two_zone_mode": "on"}
    flow, entry, hass = rig.new_flow(data=data)
    for k, v in pkg_states().items():
        hass.states.set(k, v)
    await flow.async_step_modbus_prefill(None)
    preview = await rig.submit(flow, "modbus_prefill", {"modbus_prefill_prefix": "hp", "prefill_offer": True})
    sugg = {}
    sch = preview.get("data_schema")
    if sch is not None:
        for k in sch.schema:
            sv = (getattr(k, "description", None) or {}).get("suggested_value")
            sugg[str(k)] = sv
    saved = await rig.submit(flow, "modbus_prefill", {**{k: v for k, v in sugg.items() if v is not None},
                                                      "after_save": "menu"})
    stored = {**entry.data, **entry.options}
    hass2, coord = rig.build_coord(entry, states={**{k: v for k, v in pkg_states().items()}})
    cfg = rig.EntryConfig_of(coord)
    for item in items:
        f = item.split(".", 1)[1]
        if f == "prefill_offer":
            ok = stored.get("prefill_offer") is True
            row("option", item, ok, f"stored={stored.get('prefill_offer')!r} (survives restart: in entry)")
            continue
        if f == "modbus_prefill_prefix":
            # saved only when the package was found under it; a prefix finding nothing is not saved
            # ("hp" is the default and is not stored as a setting, #1107: use "wp")
            res_p = {}
            for typed, present in (("wp", "wp"), ("zz", "wp")):
                f3, e3, h3 = rig.new_flow(data=data)
                for k, v in pkg_states(present).items():
                    h3.states.set(k, v)
                await f3.async_step_modbus_prefill(None)
                pv = await rig.submit(f3, "modbus_prefill", {"modbus_prefill_prefix": typed})
                keep = {}
                if pv.get("data_schema") is not None:
                    keep = {str(k): (getattr(k, "description", None) or {}).get("suggested_value")
                            for k in pv["data_schema"].schema}
                    keep = {k: v for k, v in keep.items() if v is not None}
                await rig.submit(f3, "modbus_prefill", {**keep, "after_save": "menu"})
                res_p[typed] = e3.options.get("modbus_prefill_prefix")
            ok = res_p["wp"] == "wp" and res_p["zz"] is None
            row("option", item, ok, f"found-under-wp stored={res_p['wp']!r}; nothing-under-zz stored={res_p['zz']!r}")
            continue
        if f == "prefill_device":
            await device_route(item)
            continue
        exp = DOC_EXPECT.get(f)
        got_s, got_k = sugg.get(f), stored.get(f)
        got_c = cfg.raw.get(f) if hasattr(cfg, "raw") else None
        ok = got_s == exp and got_k == exp and got_c == exp
        row("option", item, ok, f"doc={exp!r} suggested={got_s!r} stored={got_k!r} coordinator={got_c!r} "
            f"saved={saved.get('type')}/{saved.get('step_id')}")


async def device_route(item):
    sys.path.insert(0, "tools/devices")
    import gen_device_fixtures as gen
    from homeassistant.helpers import device_registry as dr
    from homeassistant.helpers import entity_registry as er
    fx = gen.load("tuya_heat_pump_000004k4z6.json")
    flow, entry, hass = rig.new_flow(data={const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor"})
    dr.async_get(hass).add("dev1", name=fx["device_name"])
    reg = er.async_get(hass)
    for r in fx["records"]:
        reg.add(r["entity_id"], unique_id=r["unique_id"], device_id="dev1", platform="tuya_heat_pump",
                original_name=r["original_name"], original_device_class=r["device_class"],
                unit_of_measurement=r["unit"])
    slug = fx["device_name"].lower().replace(" ", "_")
    hass.states.set(f"sensor.{slug}_outdoor_ambient_temperature_t4", FakeState("-3.5"))
    hass.states.set(f"number.{slug}_dhw_setpoint", FakeState("50"))
    await flow.async_step_modbus_prefill(None)
    preview = await rig.submit(flow, "modbus_prefill", {"prefill_device": "dev1"})
    keys = [str(k) for k in (preview.get("data_schema").schema if preview.get("data_schema") else {})]
    ok = preview.get("type") == "form" and "outdoor_temp_entity" in keys
    row("option", item, ok, f"device preview offers {sorted(keys)[:8]}")


# ---- factory reset ---------------------------------------------------------
async def factory_reset(items):
    out = {}
    learned = {}
    for scope, confirm in (("both", False), ("settings", True), ("learners", True), ("both", True)):
        entry_opts = {"comfort_temp_day": 23.0}
        flow, entry, hass = rig.new_flow(options=entry_opts)
        hass2, coord = rig.build_coord(entry)
        await rig.run_cycles_async(coord, 1)
        entry.runtime_data = coord
        calls = []
        real_reset = coord.async_reset_heat_loss_learners

        async def spy(*a, _r=real_reset, **k):
            calls.append(1)
            return await _r(*a, **k)

        coord.async_reset_heat_loss_learners = spy  # the learned-values reset, observed
        flow.hass = hass2
        hass2.config_entries.entries.append(entry)
        await flow.async_step_factory_reset(None)
        res = await rig.submit(flow, "factory_reset", {"scope": scope, "confirm": confirm})
        out[(scope, confirm)] = (res.get("type"), res.get("step_id") or res.get("reason"),
                                 dict(entry.options).get("comfort_temp_day"))
        learned[(scope, confirm)] = len(calls)
    print("factory:", out, learned)
    for item in items:
        f = item.split(".", 1)[1]
        if f == "confirm":
            r = out[("both", False)]
            ok = r[0] == "menu" and r[1] == "advanced" and r[2] == 23.0
            row("option", item, ok, f"unticked -> {r}")
        else:
            s, l = out[("settings", True)], out[("learners", True)]
            ok = (s[2] is None and l[2] == 23.0 and out[("both", True)][2] is None
                  and learned[("settings", True)] == 0 and learned[("learners", True)] > 0
                  and learned[("both", True)] > 0)
            row("option", item, ok, f"settings->{s} learners->{l} both->{out[('both', True)]} learned_resets={learned}")


async def main(argv):
    if "--perturb-close" in argv:
        mock.patch.object(config_flow, "AFTER_SAVE_CLOSE", "menu").start()
    steps = universe("options-step")
    opts = universe("option")
    for s in steps:
        if s in MENUS:
            await menu_step(s)
        elif s == "setup_overview":
            await overview()
        elif s == "factory_reset":
            flow, entry, hass = rig.new_flow()
            r = await flow.async_step_factory_reset(None)
            row("options-step", s, r.get("type") == "form", f"opens={r.get('type')} (effect rowed under its fields)")
        elif s == "modbus_prefill":
            flow, entry, hass = rig.new_flow()
            r = await flow.async_step_modbus_prefill(None)
            r2 = await rig.submit(flow, s, {"modbus_prefill_prefix": "hp"})
            r3 = await rig.submit(flow, s, {"after_save": "menu"})
            row("options-step", s, r.get("type") == "form" and r3.get("step_id") == PARENT[s],
                f"opens={r.get('type')} save->{r3.get('type')}/{r3.get('step_id')}")
        else:
            await form_step(s)
    for o in opts:
        if o.endswith(".after_save") and o.split(".")[0] in CHANGE:
            await after_save(o.split(".")[0])
        elif o.endswith(".after_save") and o.startswith("modbus_prefill"):
            flow, entry, hass = rig.new_flow()
            await flow.async_step_modbus_prefill(None)
            await rig.submit(flow, "modbus_prefill", {"modbus_prefill_prefix": "hp"})
            r = await rig.submit(flow, "modbus_prefill", {"after_save": "close"})
            row("option", o, r.get("type") == "create_entry", f"close->{r.get('type')}")
    await modbus([o for o in opts if o.startswith("modbus_prefill.") and not o.endswith("after_save")])
    await factory_reset([o for o in opts if o.startswith("factory_reset.")])
    n = lambda kind, pred: sum(1 for k, i, ok in ROWS if k == kind and pred(i))  # noqa: E731
    print(f"RESULT steps_examined={n('options-step', lambda i: True)} of {len(steps)}")
    print(f"RESULT after_save_examined={n('option', lambda i: i.endswith('after_save'))}")
    print(f"RESULT modbus_examined={n('option', lambda i: i.startswith('modbus_prefill.') and not i.endswith('after_save'))}")
    print(f"RESULT factory_examined={n('option', lambda i: i.startswith('factory_reset.'))}")
    print(f"RESULT after_save_fail={sum(1 for k, i, w in FAILS if i.endswith('after_save'))}")
    print(f"RESULT flow_fail={len(FAILS)}")
    for f in FAILS:
        print("FAIL", *f)
    print(f"RESULT thread_factor={rig.thread_factor()}")
    print(f"RESULT load1={rig.load1()}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1:]))
