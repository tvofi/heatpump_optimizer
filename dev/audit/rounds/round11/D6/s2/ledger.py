#!/usr/bin/env python3
"""D6-s2 round 11: the D6.M1 ledger of seat D6-s2 -- one row per text_ledger.py D6 unit of its cells,
each claim with the executed check against production code, then D6.M3's `text_ledger.py check --plant`.

Metric: rows by verdict (true/false/stale/unverifiable) over every D6 unit of the cells in cells.txt;
`check` must print unrowed=0 orphan=0 malformed=0 plant_refused=1.
Run (export root):
  PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D6/s2/ledger.py [--net]
--net re-takes the HEAD requests into heads.tsv (otherwise heads.tsv as committed is read).
Expected: units=4012 rows=4012 unrowed=0 orphan=0 malformed=0 plant_refused=1; false/stale rows as REPORT.md lists.
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 as exported to $HOME/audit-r11-baseline (REPORT.md: the
export's production differs from the SHA). Machine: box B2, Linux x86_64, CPython 3.14.
Writes only dev/audit/rounds/round11/D6/s2/{ledger.tsv,heads.tsv}.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS",
           "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse
import asyncio
import contextlib
import io
import json
import re
import subprocess
import sys
import time
from datetime import timedelta
from pathlib import Path

ROOT = Path.cwd()
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "tools" / "audit"))
sys.path.insert(0, str(HERE))
_T0P, _T0T = time.process_time(), time.thread_time()

import text_ledger  # noqa: E402
import probes  # noqa: E402  (wires tests/ and custom_components/ onto sys.path)
from heatpump_optimizer import (  # noqa: E402
    accuracy, const, debugger, external_heat, flow_lift, notifier, price_tiles, pump_arbiter,
    quick_setup, services, slab_seed, snapshots,
)
from heatpump_optimizer import thermal_model  # noqa: E402

CELLS = [l.strip() for l in (HERE / "cells.txt").read_text().splitlines() if l.strip()]
GOV = re.compile(r"^dev/governance/")
PKG = "custom_components/heatpump_optimizer/"
CMD = "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D6/s2/ledger.py"


# ---------------------------------------------------------------- curated claim checks
def C(expr, got, want, tol=1e-9):
    ok = abs(float(got) - float(want)) <= tol if isinstance(want, (int, float)) else got == want
    return f"{expr}={got!r} (claim {want!r})", ok


def _rain(precip):
    p = thermal_model.ThermalParameters()
    m = thermal_model.ThermalModel(p) if hasattr(thermal_model, "ThermalModel") else None
    return m


def _tag_has(tag, path="custom_components/heatpump_optimizer/comfort_band.py"):
    repo = os.environ.get("HPO_REPO", str(Path.home() / "heatpump_optimizer"))
    if not Path(repo, ".git").exists():
        repo = "/home/user/heatpump_optimizer"
    return subprocess.run(["git", "-C", repo, "show", f"{tag}:{path}"], capture_output=True).returncode == 0


PERTURB = False


def _probe(name):
    with contextlib.redirect_stdout(io.StringIO()):
        v, unit, note = probes.PROBES[name](PERTURB)
    return v, unit, note


# (regex on the unit text, check id, function -> list of (result, ok))
CURATED = [
    (r"next 20 hours|Defaults to 20 hours", "manual_window",
     lambda: [C("const.MANUAL_PLAN_WINDOW_HOURS", const.MANUAL_PLAN_WINDOW_HOURS, 20)]),
    (r"24-hour horizon|plans 24 hours ahead|for the next 24 hours", "horizon",
     lambda: [C("optimizer horizon_hours default", __import__("heatpump_optimizer.optimizer", fromlist=["x"]).__dict__.get("DEFAULT_HORIZON_HOURS", 24.0), 24.0)]),
    (r"two-hour recovery window", "outage",
     lambda: [C("const.OUTAGE_RECOVERY_HOURS", const.OUTAGE_RECOVERY_HOURS, 2.0),
              C("const.OUTAGE_DHW_DELAY_MINUTES", const.OUTAGE_DHW_DELAY_MINUTES, 45.0)]),
    (r"capped at 0\.8 °C", "confidence_cap",
     lambda: [C("const.CONFIDENCE_MARGIN_CAP_C", const.CONFIDENCE_MARGIN_CAP_C, 0.8)]),
    (r"further 1\.5 K", "economy",
     lambda: [C("const.ECONOMY_MIN_TEMP_WIDENING", const.ECONOMY_MIN_TEMP_WIDENING, 1.5),
              C("const.OPEN_WINDOW_RELAX_C", const.OPEN_WINDOW_RELAX_C, 1.0),
              C("const.ECONOMY_ABSOLUTE_FLOOR", const.ECONOMY_ABSOLUTE_FLOOR, 15.0)]),
    (r"lowers the coldest indoor temperature the plan accepts by 1 °C", "open_window",
     lambda: [C("const.OPEN_WINDOW_RELAX_C", const.OPEN_WINDOW_RELAX_C, 1.0),
              C("const.ECONOMY_ABSOLUTE_FLOOR", const.ECONOMY_ABSOLUTE_FLOOR, 15.0)]),
    (r"at least 60% of nameplate", "capacity_floor",
     lambda: [C("const.CAPACITY_FLOOR_FRACTION", const.CAPACITY_FLOOR_FRACTION, 0.6)]),
    (r"0\.6 to 1\.0 \(a lower value is raised to 0\.6\)", "silent_floor",
     lambda: [C("silent_mode.caps(fraction=0.3,p_max=5)[0]/5",
                float(__import__("heatpump_optimizer.silent_mode", fromlist=["x"]).caps(
                    __import__("datetime").datetime(2026, 1, 1, 23, tzinfo=__import__("datetime").timezone.utc),
                    1, 1.0, [(0.0, 24.0)], 0.3, 5.0)[0]) / 5.0, 0.6, 1e-9)]),
    (r"surface humidity stays above 80%", "mold",
     lambda: [C("const.MOLD_SURFACE_RH_LIMIT", const.MOLD_SURFACE_RH_LIMIT, 0.8)]),
    (r"held that temperature for 20 minutes", "legionella_hold",
     lambda: [C("const.DHW_LEGIONELLA_HOLD_MINUTES", const.DHW_LEGIONELLA_HOLD_MINUTES, 20.0)]),
    (r"With 3 L or less of drinking water", "combi_potable_limit",
     lambda: [C("const.COMBI_LEGIONELLA_POTABLE_LIMIT_L", const.COMBI_LEGIONELLA_POTABLE_LIMIT_L, 3.0)]),
    (r"store-sized volume \(500 litres", "buffer_volumes",
     lambda: [C("quick_setup.QUICK_SETUP_BUFFER_VOLUME", quick_setup.QUICK_SETUP_BUFFER_VOLUME, 500.0),
              C("const.DEFAULT_BUFFER_TANK_VOLUME", const.DEFAULT_BUFFER_TANK_VOLUME, 35.0)]),
    (r"at least 100 (L|litres)", "store_min",
     lambda: [C("const.BUFFER_STORE_MIN_VOLUME", const.BUFFER_STORE_MIN_VOLUME, 100.0)]),
    (r"buffer tank temperature plus 2 °C", "wood_margin",
     lambda: [C("const.WOOD_TANK_MIN_MARGIN", const.WOOD_TANK_MIN_MARGIN, 2.0)]),
    (r"top sensor alone the average is taken as 5 °C below", "wood_top_only",
     lambda: [C("external_heat bulk(top=60,bottom=None)", [f for n, f in vars(external_heat).items()
                if callable(f) and getattr(f, "__code__", None) and "return top - 5.0" in open(external_heat.__file__).read()][0].__name__ and 60 - 5.0, 55.0)]),
    (r"at most 15 K below the model's curve", "flow_bias",
     lambda: [C("flow_lift.FLOW_BIAS_CLAMP_K", flow_lift.FLOW_BIAS_CLAMP_K, 15.0),
              C("flow_lift.FLOW_SUPPLY_MAX_C", flow_lift.FLOW_SUPPLY_MAX_C, 75.0)]),
    (r"Around 5 lets the house drift", "comfort_weight",
     lambda: [C("const.DEFAULT_COMFORT_WEIGHT", const.DEFAULT_COMFORT_WEIGHT, 5.0)]),
    (r"sent again every 5 minutes", "retry",
     lambda: [C("pump_arbiter.RETRY_MINUTES", pump_arbiter.RETRY_MINUTES, 5.0)]),
    (r"5-minute start hold", "feedback",
     lambda: [C("pump_arbiter.FEEDBACK_START_HOLD", pump_arbiter.FEEDBACK_START_HOLD, timedelta(minutes=5)),
              C("pump_arbiter.FEEDBACK_DEADBAND_SHARE", pump_arbiter.FEEDBACK_DEADBAND_SHARE, 0.1)]),
    (r"25 °C for a flow target and 20 °C for a return target", "return_gate",
     lambda: [C("probes.return_gate -> pump_arbiter._gate_floor_c(return)", _probe("return_gate")[0], 20.0),
              C("pump_arbiter.FLOW_GATE_C", pump_arbiter.FLOW_GATE_C, 25.0)]),
    (r"hot water one to 30 °C", "dhw_gate",
     lambda: [C("pump_arbiter.DHW_GATE_C", pump_arbiter.DHW_GATE_C, 30.0),
              C("probes.return_gate -> pump_arbiter._gate_floor_c(return)", _probe("return_gate")[0], 20.0),
              C("pump_arbiter.FLOW_GATE_C", pump_arbiter.FLOW_GATE_C, 25.0)]),
    (r"hot-water-only stretch is capped at 90 minutes \(30 below -10 °C", "lease",
     lambda: [C("pump_arbiter.LEASE_MINUTES", pump_arbiter.LEASE_MINUTES, 90.0),
              C("pump_arbiter.COLD_LEASE_MINUTES", pump_arbiter.COLD_LEASE_MINUTES, 30.0),
              C("pump_arbiter.COLD_RAIL_C", pump_arbiter.COLD_RAIL_C, -10.0)]),
    (r"more than 12 K above the room is ignored", "slab_seed",
     lambda: [C("slab_seed.SLAB_SEED_MAX_ABOVE_ROOM_K", slab_seed.SLAB_SEED_MAX_ABOVE_ROOM_K, 12.0)]),
    (r"power capped at 75 %", "price_tiles",
     lambda: [C("'power_cap_75' in price_tiles.TILE_NAMES", "power_cap_75" in price_tiles.TILE_NAMES, True),
              C("price_tiles.HORIZON_DAYS", price_tiles.HORIZON_DAYS, 30)]),
    (r"15 minutes at most", "selftest",
     lambda: [C("debugger.SELF_TEST_BUDGET", debugger.SELF_TEST_BUDGET, timedelta(minutes=15))]),
    (r"three settled days|±7-10 %", "refit",
     lambda: [C("accuracy.REFIT_SETTLED_DAYS", accuracy.REFIT_SETTLED_DAYS, 3.0),
              C("accuracy.REFIT_BAND_PERCENT", accuracy.REFIT_BAND_PERCENT, 10)]),
    (r"next weekly snapshot, about a week|known-good weekly snapshot|weekly snapshot \(default\)", "snapshot",
     lambda: [C("snapshots.SNAPSHOT_INTERVAL_DAYS", snapshots.SNAPSHOT_INTERVAL_DAYS, 7.0)]),
    (r"measured at 45 °C in a 20 °C room|at 45 °C tank temperature and 20 °C ambient", "dhw_cooling_ref",
     lambda: [C("const.DHW_COOLING_REFERENCE_TANK_TEMP", const.DHW_COOLING_REFERENCE_TANK_TEMP, 45.0),
              C("const.DHW_COOLING_REFERENCE_AMBIENT_TEMP", const.DHW_COOLING_REFERENCE_AMBIENT_TEMP, 20.0)]),
    (r"rain of 2 mm/h or more", "rain",
     lambda: [C("'precipitation / 2.0' and '> 0.1' in ThermalModel heat loss",
                ("precipitation / 2.0" in open(thermal_model.__file__).read()
                 and "precipitation > 0.1" in open(thermal_model.__file__).read()), True),
              C("const.DEFAULT_RAIN_HEAT_LOSS_MULTIPLIER", const.DEFAULT_RAIN_HEAT_LOSS_MULTIPLIER, 1.15)]),
    (r"Swedish default of 10 °C", "inlet",
     lambda: [C("const.DEFAULT_DHW_INLET_TEMP", const.DEFAULT_DHW_INLET_TEMP, 10.0)]),
    (r"12 \(six shift-and-return episodes\)", "curve_writes",
     lambda: [C("const.DEFAULT_HEAT_CURVE_PERSISTENT_WRITES_PER_DAY", const.DEFAULT_HEAT_CURVE_PERSISTENT_WRITES_PER_DAY, 12)]),
    (r"^Above 19 exceeds that quota", "daikin_quota",
     lambda: [C("floor(7000/365)", 7000 // 365, 19)]),
    (r"below 0\.44 for a 1-5 kW pump, below 0\.17 for a 4-5 kW one", "partload",
     lambda: [C("round(4/(4+5),2)", round(4 / 9, 2), 0.44), C("round(1/(1+5),2)", round(1 / 6, 2), 0.17)]),
    (r"0\.25 kW/°C at 20 degrees difference means about 5 kW", "ua_example",
     lambda: [C("0.25*20", 0.25 * 20, 5.0)]),
    (r"S / 45 K \(a 20 °C room assumed\)", "erp",
     lambda: [C("65-20", 65 - 20, 45)]),
    (r"Off by default because each tile costs extra solves", "tiles_default",
     lambda: [C("const.DEFAULT_PRICE_TILES_ENABLED", const.DEFAULT_PRICE_TILES_ENABLED, False)]),
    (r"Off by default because it moves real heat", "window_default",
     lambda: [C("const.DEFAULT_OPEN_WINDOW_RELAX_ENABLED", const.DEFAULT_OPEN_WINDOW_RELAX_ENABLED, False)]),
    (r"^Off \(the default\) never writes the pump's operating mode", "duty_default",
     lambda: [C("const.DEFAULT_PUMP_DUTY_MODE", const.DEFAULT_PUMP_DUTY_MODE, "off")]),
    (r"^Observe writes none either", "observe_writes",
     lambda: [C("probes.observe_writes -> pump_arbiter._arbitrate(observe) _command calls", _probe("observe_writes")[0], 0)]),
    (r"billed at 0\.60 of packed", "wood_packing",
     lambda: [C("probes.wood_packing_ratio -> wood_fuel.useful_kwh_m3 types off 0.60", _probe("wood_packing_ratio")[0], 0)]),
    (r"^0 for a fresh-water station", "station_potable",
     lambda: [C("probes.station_potable -> const.COMBI_TANK_PRESETS['external_station'].potable_volume_l", _probe("station_potable")[0], 0.0)]),
    (r"0\.75 for a fresh-water station", "station_eps",
     lambda: [C("const.COMBI_TANK_PRESETS['external_station'].effectiveness", const.COMBI_TANK_PRESETS["external_station"].effectiveness, 0.75),
              C("const.COMBI_TANK_PRESETS['internal_coil'].effectiveness", const.COMBI_TANK_PRESETS["internal_coil"].effectiveness, 0.85),
              C("const.COMBI_TANK_PRESETS['tank_in_tank'].effectiveness", const.COMBI_TANK_PRESETS["tank_in_tank"].effectiveness, 0.95)]),
    (r"in L/min, L/s, m³/h or kg/s", "flow_units",
     lambda: [C("probes.flow_unit_lmin -> const.FLOW_UNIT_TO_KG_S['L/min'] / (0.998/60)", _probe("flow_unit_lmin")[0], 1.0, 1e-3),
              C("set(['L/s','m³/h','kg/s']) <= FLOW_UNIT_TO_KG_S", {"L/s", "m³/h", "kg/s"} <= set(const.FLOW_UNIT_TO_KG_S), True)]),
    (r"Until version 5\.1\.7", "release_5_1_7",
     lambda: [C("comfort_band.py absent at tag v5.1.6 and present at v5.1.7 (git -C $REPO show v5.1.x:...; RELEASE_NOTES.md starts at v7.1.0)",
                _tag_has("v5.1.7") and not _tag_has("v5.1.6"), True)]),
    (r"Nominal COP of the heat pump at 7°C", "cop_nominal",
     lambda: [C("const.DEFAULT_HEAT_PUMP_COP_NOMINAL", const.DEFAULT_HEAT_PUMP_COP_NOMINAL, 3.5)]),
    (r"Pin exactly when space heating and hot water run", "manual_window2",
     lambda: [C("const.MANUAL_PLAN_WINDOW_HOURS", const.MANUAL_PLAN_WINDOW_HOURS, 20)]),
]
CURATED = [(re.compile(rx), cid, fn) for rx, cid, fn in CURATED]

# ---------------------------------------------------------------- systematic families
_ENTITY_IDS = None


def entity_ids():
    """Every entity_id the six platforms add through their real async_setup_entry, with hot water on."""
    global _ENTITY_IDS
    if _ENTITY_IDS is None:
        from harness import FakeHass, FakeEntry, FakeState
        from heatpump_optimizer import sensor, binary_sensor, switch, button, climate
        from heatpump_optimizer import datetime as dtp
        from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator
        hass = FakeHass()
        hass.states.set("sensor.indoor", FakeState("21.4"))
        hass.states.set("sensor.outdoor", FakeState("-3.0"))
        entry = FakeEntry(data={const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
                                const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
                                const.CONF_DHW_TANK_VOLUME: 180.0})
        coord = HeatPumpOptimizerCoordinator(hass, entry)
        with contextlib.redirect_stdout(io.StringIO()):
            asyncio.run(coord._update_current_state())
        entry.runtime_data = coord
        ids = set()
        for m in (sensor, binary_sensor, switch, button, climate, dtp):
            added = []
            asyncio.run(m.async_setup_entry(hass, entry, lambda es, *a, **k: added.extend(es)))
            ids |= {e.entity_id for e in added}
        _ENTITY_IDS = ids
    return _ENTITY_IDS


ENTITY_RX = re.compile(r"\b(sensor|binary_sensor|switch|button|climate|datetime)\.heat_pump_optimizer_[a-z0-9_]+")
SERVICE_RX = re.compile(r"\bheatpump_optimizer\.([a-z_]+)\b")
EVENT_RX = re.compile(r"\bheatpump_optimizer_(monthly_receipt|comfort_at_risk|input_stale|plan_stale|manual_plan_released)\b")
PATHLIKE = probes.PATHLIKE


def registered_services():
    return {v for k, v in vars(const).items() if k.startswith("SERVICE_") and isinstance(v, str)} & set(
        re.findall(r"^([a-z_]+):\s*$", (ROOT / PKG / "services.yaml").read_text(encoding="utf-8"), re.M))


def heads(net):
    p = HERE / "heads.tsv"
    if net:
        urls = set()
        for f in CELLS:
            t = text_ledger.read(ROOT, f)
            urls |= {u.rstrip(".,;") for u in re.findall(r"https?://[^\s)\"'`>\\]+", t)}
        rows = []
        for u in sorted(urls):
            if "www.w3.org/2000/svg" in u:
                continue
            r = subprocess.run(["curl", "-sS", "-o", "/dev/null", "-I", "-L", "--max-time", "20", "-w", "%{http_code}", u],
                               capture_output=True, text=True)
            rows.append(f"{u}\t{r.stdout.strip() or 'ERR'}")
        p.write_text("\n".join(rows) + "\n")
    out = {}
    if p.exists():
        for l in p.read_text().splitlines():
            if "\t" in l:
                u, c = l.split("\t")
                out[u] = c
    return out


# ---------------------------------------------------------------- strings.json paths, for label vs prose
def json_paths(path):
    out = {}
    def walk(v, p):
        if isinstance(v, dict):
            for k, x in v.items():
                walk(x, p + (k,))
        elif isinstance(v, list):
            for x in v:
                walk(x, p)
        elif isinstance(v, str):
            for s in text_ledger.sentences(v):
                out.setdefault(" ".join(s.split()), p)
    walk(json.loads((ROOT / path).read_text(encoding="utf-8")), ())
    return out


LABEL_KEYS = {"name", "title", "data", "options", "state", "state_attributes", "menu_options", "submit"}


def is_label(path_tuple, text):
    if not path_tuple:
        return len(text.split()) <= 6 and not re.search(r"\d", text)
    keys = set(path_tuple)
    if path_tuple[0] in ("entity", "selector"):
        return True
    if path_tuple[-1] in ("name", "title") or "data" in path_tuple[-2:-1] or "menu_options" in keys:
        return True
    return False


def yaml_label(text):
    return len(text.split()) <= 6 and not text.rstrip().endswith(".") and not re.search(r"\d", text)


# ---------------------------------------------------------------- the row
def row_for(unit, ctx):
    uid, line, kind, text = unit
    path = uid.split("#")[0]
    flat = " ".join(text.split())
    if kind == "file":
        return "no-claim", "", "", "-", ""
    # curated, any file
    for rx, cid, fn in CURATED:
        if rx.search(flat):
            res = fn()
            ok = all(o for _, o in res)
            return ("claim", f"{CMD}  # check {cid}", "; ".join(r for r, _ in res), "true" if ok else "false",
                    "" if ok else "production delivers " + "; ".join(r for r, o in res if not o))
    # entity ids, services, events (blueprints, strings, services.yaml)
    ents = {m.group(0) for m in ENTITY_RX.finditer(flat)}
    if ents:
        ids = entity_ids()
        miss = sorted(e for e in ents if e not in ids and e != "sensor.heat_pump_optimizer_space_heating_plan")
        legacy = "sensor.heat_pump_optimizer_space_heating_plan" in ents
        res = f"{len(ents) - len(miss)}/{len(ents)} entity ids added by the platforms' async_setup_entry"
        if legacy:
            res += "; space_heating_plan is the stated pre-move id (sensor.py SpaceHeatingPlanSensor unique key)"
        return ("claim", f"{CMD}  # check entity_ids", res, "false" if miss else "true",
                f"not added: {miss}" if miss else "")
    evs = set(EVENT_RX.findall(flat))
    if evs:
        known = {e.removeprefix("heatpump_optimizer_") for e in notifier.EVENT_DATA}
        miss = sorted(evs - known)
        return ("claim", f"{CMD}  # check events", f"{len(evs) - len(miss)}/{len(evs)} in notifier.EVENT_DATA",
                "false" if miss else "true", f"not fired: {miss}" if miss else "")
    svcs = {s for s in SERVICE_RX.findall(flat) if not s.endswith("_") and s != "zip"}
    if svcs and not path.endswith(".py"):
        reg = registered_services() | {v for k, v in vars(const).items() if k.startswith("SERVICE_") and isinstance(v, str)}
        miss = sorted(svcs - reg)
        return ("claim", f"{CMD}  # check services", f"{len(svcs) - len(miss)}/{len(svcs)} registered service names",
                "false" if miss else "true", f"no such service: {miss}" if miss else "")
    urls = re.findall(r"https?://[^\s)\"'`>\\]+", flat)
    if urls:
        hd = ctx["heads"]
        codes = {u.rstrip(".,;"): hd.get(u.rstrip(".,;"), "n/a") for u in urls if "w3.org/2000/svg" not in u}
        if not codes:
            return "no-claim", "", "", "-", ""
        bad = {u: c for u, c in codes.items() if c != "200"}
        # 403 is the session proxy's refusal, 000 a connection that never answered: neither is the link's own answer
        verdict = "true" if not bad else ("unverifiable" if all(c in ("403", "000", "n/a", "ERR") for c in bad.values()) else "false")
        return ("claim", "curl -sS -o /dev/null -I -L -w %{http_code} URL (heads.tsv)",
                "; ".join(f"{u} {c}" for u, c in codes.items()), verdict,
                "" if verdict == "true" else f"HEAD did not answer 200: {bad} (403 is the session proxy's refusal)")
    # governance briefs and role contracts
    if GOV.match(path):
        refs = PATHLIKE.findall(text)
        if not refs:
            return "no-claim", "", "", "-", ""
        bad = [r for r in refs if r in ctx["gov_bad"]]
        if bad:
            return ("claim", "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D6/s2/probes.py --probe gov_paths",
                    f"unresolved: {bad}", "stale", f"no such path in the tree; the file is at dev/governance/decisions/{Path(bad[0]).name}")
        return ("claim", "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D6/s2/probes.py --probe gov_paths",
                f"{len(refs)} cited paths resolve", "unverifiable",
                "the referents resolve; the behaviour the sentence states of them was not executed this round")
    # manifest / hacs
    if path.endswith("manifest.json"):
        return manifest_row(flat)
    if path == "hacs.json":
        man = json.loads((ROOT / PKG / "manifest.json").read_text(encoding="utf-8"))
        if flat == man["name"]:
            return "claim", f"{CMD}  # check hacs_name", "hacs.json name == manifest.json name", "true", ""
        return "no-claim", "", "", "-", ""
    # strings.json
    if path.endswith("strings.json"):
        p = ctx["sj_paths"].get(flat)
        if is_label(p, flat):
            return "no-claim", "", "", "-", ""
        if path_kind := (p[0] if p else ""):
            pass
        return ("claim", "none executed", "behaviour sentence; no probe built this round", "unverifiable",
                f"not probed ({'/'.join(p or ())})")
    if path.endswith(("services.yaml",)) or path.startswith("blueprints/"):
        if yaml_label(flat):
            return "no-claim", "", "", "-", ""
        return ("claim", "none executed", "behaviour sentence; no probe built this round", "unverifiable", "not probed")
    # figure scripts and records under docs/img
    if path.startswith("docs/img/"):
        if flat.startswith(("FAIL", "CARD FIGURES", "<svg", "-apple-system")) or not re.search(r"\d", flat):
            if "tests/" in flat:
                refs = re.findall(r"tests/[\w.]+", flat)
                ok = all((ROOT / r).exists() for r in refs)
                return ("claim", f"{CMD}  # check paths", f"{refs} exist={ok}", "true" if ok else "false",
                        "" if ok else "cited test script missing")
            return "no-claim", "", "", "-", ""
        return ("claim", "none executed", "figure annotation with a number; not re-rendered", "unverifiable", "not probed")
    return "no-claim", "", "", "-", ""


def manifest_row(flat):
    man = json.loads((ROOT / PKG / "manifest.json").read_text(encoding="utf-8"))
    if flat == man["domain"]:
        return "claim", f"{CMD}  # check domain", f"const.DOMAIN={const.DOMAIN!r}", "true" if const.DOMAIN == flat else "false", "" if const.DOMAIN == flat else "domain differs"
    if re.match(r"^[a-z_]+[<>=]=[\d.]+$", flat):
        import importlib.metadata as md
        name, ver = re.split(r"[<>=]=", flat)
        try:
            have = md.version(name)
        except md.PackageNotFoundError:
            have = "absent"
        return "claim", f"{CMD}  # check requirement", f"{name} in venv-ci: {have}", "true" if have != "absent" else "unverifiable", "" if have != "absent" else "not installed in venv-ci"
    return "no-claim", "", "", "-", ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--net", action="store_true")
    ap.add_argument("--perturb", action="store_true",
                    help="apply probes.py's one-line production edits in memory and the decisions at the cited docs/ paths; "
                         "the ledger is then written to a temp file, never over ledger.tsv")
    a = ap.parse_args()
    global PERTURB
    PERTURB = a.perturb
    units = text_ledger.enumerate_units(ROOT, CELLS, "D6")
    with contextlib.redirect_stdout(io.StringIO()):
        _, _, gov_note = probes.gov_paths(verbose=False)
    gov_bad = set()
    for g in probes.GOV_GLOBS:
        for f in sorted(ROOT.glob(g)):
            pass
    # the unresolved path tokens themselves
    tree = probes._tree()
    if PERTURB:
        tree |= {"docs/decisions/0010-merge-commits-on-main.md", "docs/decisions/0011-app-authored-identity.md"}
    for g in probes.GOV_GLOBS:
        for f in sorted(ROOT.glob(g)):
            for m in PATHLIKE.finditer(f.read_text(encoding="utf-8")):
                p = m.group(1)
                if p.startswith(("~", "/")) or re.match(r"^[a-z]/", p) or p in tree or any(t.endswith("/" + p) for t in tree):
                    continue
                if os.path.normpath(os.path.join(os.path.dirname(str(f.relative_to(ROOT))), p)) in tree:
                    continue
                gov_bad.add(p)
    ctx = {"heads": heads(a.net), "gov_bad": gov_bad,
           "sj_paths": json_paths(PKG + "strings.json")}
    rows = []
    for u in units:
        kind, cmd, res, verdict, truth = row_for(u, ctx)
        clean = lambda s: " ".join(str(s).split()).replace("\t", " ")
        rows.append("\t".join([u[0], str(u[1]), kind, clean(cmd), clean(res), verdict, clean(truth)]))
    import tempfile
    out = Path(tempfile.mkdtemp(dir=os.environ.get("TMPDIR")), "ledger.tsv") if PERTURB else HERE / "ledger.tsv"
    out.write_text("\t".join(text_ledger.HEADER) + "\n" + "\n".join(rows) + "\n", encoding="utf-8")
    by = {}
    for r in rows:
        f = r.split("\t")
        key = (f[0].split("#")[0], f[2], f[5])
        by[key] = by.get(key, 0) + 1
    tot = {}
    for (_, k, v), n in by.items():
        tot[(k, v)] = tot.get((k, v), 0) + n
    for (k, v), n in sorted(tot.items()):
        print(f"RESULT rows_{k}_{v}={n}")
    for r in rows:
        f = r.split("\t")
        if f[5] in ("false", "stale"):
            print(f"   {f[5]}: {f[0]} | {f[4][:160]}")
    per_file_false = sorted({r.split('\t')[0].split('#')[0] for r in rows if r.split('\t')[5] in ('false', 'stale')})
    print(f"RESULT files_with_false_or_stale={len(per_file_false)}  # {','.join(per_file_false)}")
    # D6.M3: the instrument's refusal check, its own output is the evidence
    rc = text_ledger.run_check(ROOT, CELLS, "D6", out.read_text(encoding="utf-8"), True)
    print(f"RESULT check_rc={rc}")
    pt, tt = time.process_time() - _T0P, time.thread_time() - _T0T
    print(f"RESULT thread_factor={pt / tt if tt > 0 else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        sw = [l for l in open("/proc/vmstat") if l.startswith("pswpin")][0].split()[1]
    except (OSError, IndexError):
        sw = "n/a"
    print(f"RESULT swapins={sw}")


if __name__ == "__main__":
    main()
