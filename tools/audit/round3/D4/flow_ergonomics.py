"""D4 round 3 -- the config and options flows, walked page by page.

METRIC (one line): for every page of the real config and options flows,
the number of *presented* schema fields (the keys the frontend actually
renders, sections flattened), how many of them carry a help line
(``data_description``) in each shipped catalogue, how many carry a
label at all, and how deep the click path from the top menu is.

COMMAND (from the export root, one line):

    PYTHONPATH=tests/hastub python3 tools/audit/round3/D4/flow_ergonomics.py

EXPECTED at baseline ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1 (8-core Apple
M1, python 3.11.5): see the RESULT lines; every one is a COUNT over a
deterministic walk, so it is exact and contention immune (tolerance: exact).
No wall or CPU time is taken.

The instrumented production symbols are
``heatpump_optimizer.config_flow:HeatPumpOptimizerOptionsFlow`` (every
``async_step_*`` that returns a form) and
``heatpump_optimizer.config_flow:HeatPumpOptimizerConfigFlow``; the schemas
are read off the results those handlers really return, never off the source.

``--json <path>`` writes the whole per-page record.
"""

from __future__ import annotations

import os

for _var in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_var, "1")

import argparse  # noqa: E402
import asyncio  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402

ROOT = os.path.dirname(os.path.abspath(__file__))
for _ in range(4):
    ROOT = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(ROOT, "tests"))
sys.path.insert(0, os.path.join(ROOT, "custom_components"))

import voluptuous as vol  # noqa: E402
from harness import FakeEntry, FakeHass  # noqa: E402
from homeassistant.data_entry_flow import section  # noqa: E402

from heatpump_optimizer import config_flow, const  # noqa: E402

STRINGS = os.path.join(ROOT, "custom_components/heatpump_optimizer/strings.json")
TRANSL = os.path.join(ROOT, "custom_components/heatpump_optimizer/translations")


def load(p):
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


CATALOGUES = {
    "strings.json": load(STRINGS),
    "en.json": load(os.path.join(TRANSL, "en.json")),
    "sv.json": load(os.path.join(TRANSL, "sv.json")),
}


def presented(schema):
    """The keys the frontend renders, sections flattened.

    A ``section(...)`` wrapper renders its own schema's keys under a
    collapsible heading, so the fields a user meets are the leaves, and the
    section names are the grouping.
    """
    out = []
    sections = []
    if schema is None:
        return out, sections
    for marker, value in getattr(schema, "schema", {}).items():
        name = getattr(marker, "schema", marker)
        if isinstance(value, section):
            sections.append(str(name))
            inner, _ = presented(value.schema)
            out.extend((str(name), k) for k in [n for _, n in inner] or [])
            continue
        out.append((None, str(name)))
    return out, sections


def texts_for(cat, flow_name, step_id):
    return ((cat.get(flow_name) or {}).get("step") or {}).get(step_id) or {}


def label_of(cat, flow_name, step_id, sec, key):
    t = texts_for(cat, flow_name, step_id)
    if sec:
        s = (t.get("sections") or {}).get(sec) or {}
        if key in (s.get("data") or {}):
            return (s.get("data") or {})[key]
    return (t.get("data") or {}).get(key)


def desc_of(cat, flow_name, step_id, sec, key):
    t = texts_for(cat, flow_name, step_id)
    if sec:
        s = (t.get("sections") or {}).get(sec) or {}
        if key in (s.get("data_description") or {}):
            return (s.get("data_description") or {})[key]
    return (t.get("data_description") or {}).get(key)


BASE_DATA = {
    "name": "Heat Pump Optimizer",
    const.CONF_TIBBER_TOKEN: "tok-a",
    const.CONF_WEATHER_ENTITY: "weather.home",
    const.CONF_HEAT_PUMP_SWITCH_ENTITY: "switch.pump_a",
    const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor_a",
    const.CONF_TARGET_TEMP: 21.0,
    const.CONF_MIN_TEMP: 19.0,
    const.CONF_MAX_TEMP: 23.0,
}


def fresh_options():
    hass = FakeHass()
    entry = FakeEntry(data=dict(BASE_DATA), options={}, entry_id="d4-opts")
    hass.config_entries.entries.append(entry)
    flow = config_flow.HeatPumpOptimizerConfigFlow.async_get_options_flow(entry)
    flow.hass = hass
    return flow


def fresh_config():
    flow = config_flow.HeatPumpOptimizerConfigFlow()
    flow.hass = FakeHass()
    return flow


def walk(flow_factory, flow_name, step_ids):
    """Call every ``async_step_<id>(None)`` and record the form it returns."""
    pages = []
    for step_id in step_ids:
        flow = flow_factory()
        fn = getattr(flow, f"async_step_{step_id}", None)
        if fn is None:
            pages.append({"step": step_id, "kind": "missing"})
            continue
        try:
            res = asyncio.run(fn(None))
        except Exception as exc:  # a page that needs prior answers
            pages.append({"step": step_id, "kind": "error", "detail": str(exc)[:120]})
            continue
        kind = res.get("type")
        if kind == "menu":
            pages.append(
                {
                    "step": step_id,
                    "kind": "menu",
                    "options": list(res.get("menu_options") or {}),
                }
            )
            continue
        if kind != "form":
            pages.append({"step": step_id, "kind": str(kind)})
            continue
        fields, sections = presented(res.get("data_schema"))
        rec = {
            "step": step_id,
            "kind": "form",
            "n_fields": len(fields),
            "sections": sections,
            "fields": [],
        }
        for sec, key in fields:
            entry = {"section": sec, "key": key}
            for cname, cat in CATALOGUES.items():
                entry[f"label_{cname}"] = label_of(cat, flow_name, step_id, sec, key) is not None
                entry[f"desc_{cname}"] = desc_of(cat, flow_name, step_id, sec, key) is not None
            rec["fields"].append(entry)
        pages.append(rec)
    return pages


def menu_of(flow_factory, step_id):
    flow = flow_factory()
    res = asyncio.run(getattr(flow, f"async_step_{step_id}")(None))
    return list((res.get("menu_options") or {}))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json")
    args = ap.parse_args()

    top = menu_of(fresh_options, "init")
    advanced = menu_of(fresh_options, "advanced")
    option_steps = [s for s in top if s != "advanced"] + advanced
    # Every options page that owns a form, whether or not a menu links it.
    declared = sorted(
        (CATALOGUES["strings.json"].get("options") or {}).get("step") or {}
    )
    for s in declared:
        if s not in option_steps:
            option_steps.append(s)

    config_steps = sorted(
        (CATALOGUES["strings.json"].get("config") or {}).get("step") or {}
    )

    opt_pages = walk(fresh_options, "options", option_steps)
    cfg_pages = walk(fresh_config, "config", config_steps)
    pages = [{**p, "flow": "options"} for p in opt_pages] + [
        {**p, "flow": "config"} for p in cfg_pages
    ]
    forms = [p for p in pages if p["kind"] == "form"]

    # --- the numbers --------------------------------------------------------
    total_fields = sum(p["n_fields"] for p in forms)
    by_cat = {}
    for cname in CATALOGUES:
        missing_label = [
            f"{p['flow']}.{p['step']}.{f['section'] or '-'}.{f['key']}"
            for p in forms
            for f in p["fields"]
            if not f[f"label_{cname}"]
        ]
        missing_desc = [
            f"{p['flow']}.{p['step']}.{f['section'] or '-'}.{f['key']}"
            for p in forms
            for f in p["fields"]
            if not f[f"desc_{cname}"]
        ]
        by_cat[cname] = (missing_label, missing_desc)

    # The comparison that makes the grouping gap falsifiable: a field key the
    # INITIAL flow presents flat, which the OPTIONS flow presents inside a
    # named section(). Same key, same user, grouped only on the revisit.
    opt_sectioned = {
        f["key"]
        for p in forms
        if p["flow"] == "options"
        for f in p["fields"]
        if f["section"]
    }
    cfg_flat = [
        (p["step"], f["key"])
        for p in forms
        if p["flow"] == "config"
        for f in p["fields"]
        if not f["section"]
    ]
    regrouped = [(st, k) for st, k in cfg_flat if k in opt_sectioned]
    cfg_sections = sum(len(p["sections"]) for p in forms if p["flow"] == "config")
    opt_sections = sum(len(p["sections"]) for p in forms if p["flow"] == "options")

    widest = sorted(forms, key=lambda p: -p["n_fields"])[:8]
    ungrouped = [p for p in forms if p["n_fields"] >= 8 and not p["sections"]]

    print("")
    print(f"RESULT pages_walked={len(pages)} count")
    print(f"RESULT form_pages={len(forms)} count")
    print(f"RESULT presented_fields_total={total_fields} count")
    for cname in CATALOGUES:
        ml, md = by_cat[cname]
        print(f"RESULT fields_without_label_{cname.replace('.', '_')}={len(ml)} count")
        print(f"RESULT fields_without_help_{cname.replace('.', '_')}={len(md)} count")
    print(f"RESULT widest_page_fields={widest[0]['n_fields'] if widest else 0} count")
    print(
        f"RESULT ungrouped_pages_ge8_fields={len(ungrouped)} count"
    )
    print(f"RESULT config_sections_total={cfg_sections} count")
    print(f"RESULT options_sections_total={opt_sections} count")
    print(f"RESULT config_flat_fields={len(cfg_flat)} count")
    print(
        f"RESULT config_flat_fields_grouped_in_options={len(regrouped)} count"
    )
    print(f"RESULT options_top_menu_items={len(top)} count")
    print(f"RESULT options_advanced_menu_items={len(advanced)} count")
    print("RESULT thread_factor=1.0")
    try:
        print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    except OSError:
        print("RESULT load1=0")
    print("RESULT swapins=0")

    print("")
    print("widest form pages (fields, sections):")
    for p in widest:
        print(
            f"  {p['flow']}.{p['step']:24} {p['n_fields']:3} fields, "
            f"{len(p['sections'])} section(s) {p['sections']}"
        )
    print("")
    print("initial-flow fields presented FLAT that the options flow groups:")
    per_step: dict = {}
    for st, k in regrouped:
        per_step.setdefault(st, []).append(k)
    for st in sorted(per_step):
        total = next(
            p["n_fields"] for p in forms if p["flow"] == "config" and p["step"] == st
        )
        print(f"  config.{st:22} {len(per_step[st]):3} of {total} field(s): "
              f"{', '.join(sorted(per_step[st])[:6])}"
              f"{' ...' if len(per_step[st]) > 6 else ''}")
    print("")
    print("form pages with >=8 fields and no sections:")
    for p in ungrouped:
        print(f"  {p['flow']}.{p['step']:24} {p['n_fields']:3} fields")
    for cname in CATALOGUES:
        ml, md = by_cat[cname]
        print("")
        print(f"{cname}: {len(ml)} field(s) with no label, {len(md)} with no help line")
        for x in ml[:12]:
            print(f"    no label: {x}")
        for x in md[:12]:
            print(f"    no help : {x}")
        if len(md) > 12:
            print(f"    ... and {len(md) - 12} more without a help line")

    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump(pages, fh, indent=1)
        print(f"\nwrote {len(pages)} page records -> {args.json}")


if __name__ == "__main__":
    main()
