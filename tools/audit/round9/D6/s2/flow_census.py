"""D6-s2 harness: the initial-setup claims of docs/configuration.md and docs/setup.md, driven.

Metrics (one line each):
  weather_submit_creates_entry  1 if submitting the 5 · Weather sensitivity page with its
                                defaults returns a create_entry result (the doc's claim
                                "Saving this page creates the entry"), else 0; the step it
                                actually returns is printed.
  wizard_steps                  forms/menus met on the documented "Continue setup ->
                                Describe my building" path from the first screen to the
                                entry, counted from the flow results the real
                                heatpump_optimizer.config_flow.HeatPumpOptimizerConfigFlow returns.
  entities_total / entities_enabled_default
                                entities the six platforms' real async_setup_entry add for
                                the entry that path creates (a real HeatPumpOptimizerCoordinator
                                after one input-read cycle), all / enabled by registry default.
  doc_entity_ids_missing        entity ids written in the seat's docs that no created
                                entity carries (key: the entity_id the production entity
                                object delivers).

Command (from the export root):
    PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D6/s2/flow_census.py
Perturbation: --perturb patches HeatPumpOptimizerConfigFlow.async_step_weather_sensitivity's
  submit arm to call _create_setup_entry() directly (the behaviour the doc describes);
  weather_submit_creates_entry must go 0 -> 1 and wizard_steps down by 1.
  --perturb-count skips the datetime platform's async_setup_entry (one entity fewer):
  entities_total must go down by 1 and the configuration.md:196 count flips to OK while the
  architecture.md counts flip to WRONG.
Expected: see REPORT.md (exact counts).
Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1. Machine: cloud container, 4 CPU, Linux.
Root rule: ROOT = Path.cwd().
"""

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import asyncio
import re
import sys
import time
from pathlib import Path
from unittest import mock

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT / "tests" / "hastub"))
_t0p, _t0t = time.process_time(), time.thread_time()

import golden  # noqa: E402
from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from heatpump_optimizer import const  # noqa: E402
import heatpump_optimizer.config_flow as cf  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402

SEAT_DOCS = ["docs/architecture.md", "docs/automations.md", "docs/configuration.md",
             "docs/dashboard-card.md", "docs/ecl110.md", "docs/how-it-works.md",
             "docs/setup.md"]


def defaults(schema, extra=None):
    payload = golden.empty_section_payload(schema)
    payload.update(extra or {})
    return schema(payload)


def drive(path_choice=("temperature", "building_describe")):
    """Drive the initial flow with default answers; return (steps, final_result, data)."""
    flow = cf.HeatPumpOptimizerConfigFlow()
    hass = FakeHass()
    hass.states.set("weather.home", FakeState("sunny"))
    flow.hass = hass
    flow.context = {}
    steps = []
    run = asyncio.run
    res = run(flow.async_step_user())
    steps.append(res.get("step_id"))
    # entity price source avoids the Tibber network check; the sequencing is identical
    res = run(flow.async_step_user(defaults(res["data_schema"], {
        const.CONF_PRICE_SOURCE: "entity", "price_entity": "sensor.prices",
        const.CONF_WEATHER_ENTITY: "weather.home"})))
    menu_iter = iter(path_choice)
    while True:
        steps.append(f"{res.get('type')}:{res.get('step_id')}")
        t = res.get("type")
        t = getattr(t, "value", t)
        if t == "create_entry":
            return steps, res, res.get("data")
        if len(steps) > 30:
            return steps, res, None
        if t == "menu":
            nxt = next(menu_iter)
            res = run(getattr(flow, f"async_step_{nxt}")())
            continue
        step = res["step_id"]
        res = run(getattr(flow, f"async_step_{step}")(defaults(res["data_schema"])))


def census(data, drop_platform=None):
    hass = FakeHass()
    hass.states.set("weather.home", FakeState("sunny"))
    entry = FakeEntry(data=dict(data))
    coord = HeatPumpOptimizerCoordinator(hass, entry)
    try:
        asyncio.run(coord._update_current_state())
    except Exception as exc:  # pragma: no cover - reported, not hidden
        print(f"# input cycle raised {exc!r}")
    entry.runtime_data = coord
    added = []
    import importlib
    for plat in const.PLATFORMS:
        name = getattr(plat, "value", str(plat)).split(".")[-1].lower()
        if name == drop_platform:
            continue
        mod = importlib.import_module(f"heatpump_optimizer.{name}")
        asyncio.run(mod.async_setup_entry(hass, entry, lambda ents, *_a, **_k: added.extend(ents)))
    return added


def enabled_default(e):
    return bool(getattr(e, "entity_registry_enabled_default",
                        getattr(e, "_attr_entity_registry_enabled_default", True)))


def doc_entity_ids():
    ids = {}
    pat = re.compile(r"\b((?:sensor|binary_sensor|switch|button|climate|number|select|datetime)"
                     r"\.heat_pump_optimizer(?:_[a-z0-9_]*[a-z0-9])?)\b")
    for d in SEAT_DOCS:
        for n, line in enumerate((ROOT / d).read_text().splitlines(), 1):
            for m in pat.finditer(line):
                ids.setdefault(m.group(1), []).append(f"{d}:{n}")
    return ids


def main():
    patches = []
    if "--perturb" in sys.argv:
        orig = cf.HeatPumpOptimizerConfigFlow.async_step_weather_sensitivity

        async def as_documented(self, user_input=None):
            if user_input is not None:
                self._data.update(user_input)
                return self._create_setup_entry()
            return await orig(self, user_input)
        patches.append(mock.patch.object(cf.HeatPumpOptimizerConfigFlow,
                                         "async_step_weather_sensitivity", as_documented))
    for p in patches:
        p.start()
    try:
        # What the weather page's submit returns, on its own
        flow = cf.HeatPumpOptimizerConfigFlow()
        flow.hass = FakeHass()
        flow.context = {}
        flow._data.update({const.CONF_WEATHER_ENTITY: "weather.home"})
        form = asyncio.run(flow.async_step_weather_sensitivity())
        after = asyncio.run(flow.async_step_weather_sensitivity(defaults(form["data_schema"])))
        t = getattr(after.get("type"), "value", after.get("type"))
        print(f"# weather_sensitivity submit -> type={t} step_id={after.get('step_id')}")
        print(f"RESULT weather_submit_creates_entry={int(t == 'create_entry')} count")
        steps, final, data = drive()
        print("# path:", " -> ".join(str(s) for s in steps))
        print(f"RESULT wizard_steps={len(steps)} count")
    finally:
        for p in patches:
            p.stop()
    if data is None:
        print("RESULT entities_total=na")
        return
    added = census(data, "datetime" if "--perturb-count" in sys.argv else None)
    print(f"# entry data keys: {len(data)}")
    print(f"RESULT entities_total={len(added)} count")
    print(f"RESULT entities_enabled_default={sum(enabled_default(e) for e in added)} count")
    by_dom = {}
    for e in added:
        eid = getattr(e, "entity_id", None) or "?"
        by_dom[eid.split(".")[0]] = by_dom.get(eid.split(".")[0], 0) + 1
    print("# by domain:", by_dom)
    have = {getattr(e, "entity_id", None) for e in added}
    ids = doc_entity_ids()
    # every "<N> entities" count and per-domain breakdown stated in the seat's docs
    census_by = {"sensors": by_dom.get("sensor", 0), "binary sensors": by_dom.get("binary_sensor", 0),
                 "buttons": by_dom.get("button", 0), "switches": by_dom.get("switch", 0),
                 "climate": by_dom.get("climate", 0), "datetime": by_dom.get("datetime", 0)}
    wrong = 0
    for d in SEAT_DOCS:
        for n, line in enumerate((ROOT / d).read_text().splitlines(), 1):
            for m in re.finditer(r"\b(\d+) entities\b", line):
                ok = int(m.group(1)) == len(added)
                wrong += not ok
                print(f"# count {'OK   ' if ok else 'WRONG'} {d}:{n} '{m.group(0)}' vs census {len(added)}")
            for m in re.finditer(r"\b(\d+) (sensors|binary sensors|buttons|switches|climate|datetime)\b", line):
                if m.group(2) == "sensors" and "binary sensors" in line[max(0, m.start() - 7):m.end()]:
                    continue
                if d.endswith("architecture.md") or "entities" in line:
                    ok = int(m.group(1)) == census_by[m.group(2)]
                    wrong += not ok
                    print(f"# count {'OK   ' if ok else 'WRONG'} {d}:{n} '{m.group(0)}' vs census {census_by[m.group(2)]}")
    print(f"RESULT doc_entity_counts_wrong={wrong} count")
    cm = re.search(r"All (\d+) entities appear", (ROOT / "docs/configuration.md").read_text())
    print(f"RESULT configuration_md_count_delta={len(added) - int(cm.group(1))} count")
    missing = {k: v for k, v in ids.items() if k not in have and not k.endswith("optimizer")}
    for k, v in sorted(ids.items()):
        print(f"# doc id {'OK     ' if k in have else 'MISSING'} {k}  ({', '.join(v)})")
    print(f"RESULT doc_entity_ids={len(ids)} count")
    print(f"RESULT doc_entity_ids_missing={len(missing)} count")
    tp, tt = time.process_time() - _t0p, time.thread_time() - _t0t
    print(f"RESULT thread_factor={tp / tt if tt else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        sw = [l for l in open("/proc/vmstat") if l.startswith("pswpin")][0].split()[1]
    except Exception:
        sw = "na"
    print(f"RESULT swapins={sw}")


if __name__ == "__main__":
    main()
