#!/usr/bin/env python3
"""R10-CONFIGFLOW-PAGES (#2238; D7-s2-56 and Arm A3'): the options page template, driven.

Ported from the design's probes ``rejected_rerender.py`` and ``clear_required.py``
(``dev/programme/designs/R10-CONFIGFLOW-PAGES-probes/`` on ``design/R10-CONFIGFLOW-PAGES``
32892dc67). Every arm drives the production step handlers of
``HeatPumpOptimizerOptionsFlow`` over ``tests/harness``'s ``FakeEntry``/``FakeHass``.

Arms (one per invocation):

  (default)   For each of the nine validating options pages, store an entity in each of
              the page's ``_STORED`` rows (``when`` gates opened), submit with every one
              cleared plus one field that makes the page reject, and count the cleared rows
              that re-render with the STORED entity as ``suggested_value``.
                stale_slots   cleared rows re-rendered as stored (the defect)
                rejected      pages whose submit was refused
  --null      The same rejection with nothing cleared: ``shown_stored`` counts rows
              re-rendered as stored (a page that accepts this submit shows no form and
              contributes 0; its ``rejected`` reads 0).
  --clear-required        Stored ``price_source: entity`` and ``price_entity: sensor.price``;
              submit the entities page with the source and no price entity (cleared).
  --clear-required --null The same submit with ``price_entity: sensor.other``.
  --accepted  A3: one accepted submit per page, plus the A3' case. Prints each case's
              saved options as canonical JSON with its sha1, so the output at the base and
              at the head are diffed. The case ``price_entity_cleared_under_entity_source``
              is the one deliberate behaviour change (A3-exception): it is printed on its
              own line, excluded from ``digest``, and ``exceptions`` must read 1.

Re-run when ``_page``, ``_clear_absent``, any options ``async_step_*`` of the nine pages or
their predicates change.

    PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_configflow_pages.py [arm]

Expected, measured at origin/main 6d86acc90 (base) and at the arm-A head:
    default                 base: stale_slots=27 stored_rows=30   head: stale_slots=0 stored_rows=30
    --null                  base and head: shown_stored=19 rejected=7
    --clear-required        base: type=menu stored_price_entity=None
                            head: type=form errors=price_entity_required stored_price_entity='sensor.price'
    --clear-required --null base and head: type=menu stored_price_entity='sensor.other'
    --accepted              base and head: the same digest, exceptions=1
"""
import asyncio
import hashlib
import json
import sys
from pathlib import Path


def repo_root(start):
    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
    from pathlib import Path
    here = Path(start).resolve()
    if here.is_file():
        here = here.parent
    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
    for cand in (here, *here.parents):
        if (cand / marker).is_file():
            return cand
    raise RuntimeError(f"no repository root above {start}")


ROOT = repo_root(Path(__file__))
sys.path[:0] = [str(ROOT / "tests"), str(ROOT / "custom_components")]

from harness import FakeEntry, FakeHass  # noqa: E402
from heatpump_optimizer import config_flow as cf  # noqa: E402
from heatpump_optimizer import const as c  # noqa: E402
from heatpump_optimizer.freq_control import FREQ_MODE_CONTROL  # noqa: E402


async def _refuse_token(_hass, _token):
    return "invalid_auth"


async def _accept_token(_hass, _token):
    return "ok"


#: page -> (base config opening its gates, the field set that makes it reject)
REJECT = {
    "entities": ({c.CONF_PRICE_SOURCE: c.PRICE_SOURCE_TIBBER, c.CONF_TIBBER_TOKEN: "old"},
                 {c.CONF_PRICE_SOURCE: c.PRICE_SOURCE_TIBBER, c.CONF_TIBBER_TOKEN: "new-bad"}),
    "entities_metering": ({}, {c.CONF_FREQ_CONTROL_MODE: FREQ_MODE_CONTROL}),
    "comfort": ({}, {c.CONF_MIN_TEMP: 25.0, c.CONF_MAX_TEMP: 18.0}),
    "hot_water": ({c.CONF_DHW_ENABLED: True}, {c.CONF_DHW_WINDOWS: "nonsense"}),
    "hot_water_tank": ({}, {c.CONF_DHW_DISINFECTION_MODE: FREQ_MODE_CONTROL}),
    "building": ({c.CONF_WOOD_FURNACE_ENABLED: True},
                 {c.CONF_WOOD_FURNACE_ENABLED: True, c.CONF_MIXING_VALVE_WRITE_TARGET_KIND: "flow"}),
    "grid": ({}, {c.CONF_PEAK_TARIFF_MONTHS: "13-14"}),
    "grid_connection": ({}, {c.CONF_SILENT_MODE_WINDOWS: "nonsense"}),
    "grid_fees": ({}, {c.CONF_GRID_FEE_RULES: "nonsense"}),
}

#: A3: (case, page, stored config, submit) -- each accepted at the base.
EXCEPTION = "price_entity_cleared_under_entity_source"
_PRICE = {c.CONF_PRICE_SOURCE: c.PRICE_SOURCE_ENTITY, c.CONF_PRICE_ENTITY: "sensor.price"}
ACCEPTED = [
    ("entities_keep", "entities", _PRICE, {**_PRICE, c.CONF_WEATHER_ENTITY: "weather.home"}),
    ("entities_replace", "entities", _PRICE, {**_PRICE, c.CONF_PRICE_ENTITY: "sensor.other"}),
    ("entities_tibber", "entities", _PRICE,
     {c.CONF_PRICE_SOURCE: c.PRICE_SOURCE_TIBBER, c.CONF_TIBBER_TOKEN: "t"}),
    (EXCEPTION, "entities", _PRICE, {c.CONF_PRICE_SOURCE: c.PRICE_SOURCE_ENTITY}),
    ("entities_metering", "entities_metering", {}, {c.CONF_FREQ_CONTROL_MODE: "observe"}),
    ("comfort", "comfort", {}, {c.CONF_MIN_TEMP: 18.0, c.CONF_MAX_TEMP: 24.0}),
    ("hot_water", "hot_water", {c.CONF_DHW_ENABLED: True}, {c.CONF_DHW_WINDOWS: "06:00-07:00"}),
    ("hot_water_tank", "hot_water_tank", {}, {c.CONF_DHW_DISINFECTION_MODE: "observe"}),
    ("building", "building", {c.CONF_WOOD_FURNACE_ENABLED: True},
     {c.CONF_WOOD_FURNACE_ENABLED: False}),
    ("grid", "grid", {}, {c.CONF_PEAK_TARIFF_MONTHS: "nov-feb", c.CONF_PEAK_TARIFF_WINDOW: "3"}),
    ("grid_connection", "grid_connection", {c.CONF_SILENT_MODE_WINDOWS: "22:00-06:00"},
     {c.CONF_MAIN_FUSE_A: 25}),
    ("grid_fees", "grid_fees", {c.CONF_GRID_FEE_ENTITY: "sensor.fee"}, {}),
]


def suggested(result, key):
    def walk(schema):
        for m, v in schema.schema.items():
            inner = cf._section_inner(v)
            if inner is not None:
                yield from walk(inner)
            else:
                yield m
    for m in walk(result["data_schema"]):
        if str(getattr(m, "schema", m)) == key:
            d = getattr(m, "description", None) or {}
            return d.get("suggested_value", getattr(m, "default", None))
    return None


def _flow(entry):
    flow = cf.HeatPumpOptimizerOptionsFlow(entry)
    flow.hass = FakeHass()
    return flow


async def rerender(step, null):
    base, bad = REJECT[step]
    rows = [r for r in cf._page_rows(step, {**base, c.CONF_WOOD_FURNACE_ENABLED: True})
            if r.default is cf._STORED]
    stored = {r.key: f"sensor.stored_{i}" for i, r in enumerate(rows)}
    res = await getattr(_flow(FakeEntry(data={**base, **stored})), f"async_step_{step}")(
        dict(bad) if not null else {**stored, **bad})
    rejected = res.get("type") == "form" and bool(res.get("errors"))
    if "data_schema" not in res:
        return len(rows), False, 0, res.get("type"), res.get("step_id")
    hits = sum(1 for k, v in stored.items() if suggested(res, k) == v)
    return len(rows), rejected, hits, res.get("type"), res.get("errors")


async def clear_required(null):
    entry = FakeEntry(data=dict(_PRICE))
    submit = {c.CONF_PRICE_SOURCE: c.PRICE_SOURCE_ENTITY}
    if null:
        submit[c.CONF_PRICE_ENTITY] = "sensor.other"
    res = await _flow(entry).async_step_entities(submit)
    saved = {**entry.data, **(entry.options or {})}
    errs = ",".join(sorted((res.get("errors") or {}).values())) or None
    print(f"RESULT type={res.get('type')} errors={errs} "
          f"stored_price_entity={saved.get(c.CONF_PRICE_ENTITY)!r}")


async def accepted():
    cf.validate_tibber_token = _accept_token
    lines, exceptions = [], 0
    for case, step, stored, submit in ACCEPTED:
        entry = FakeEntry(data={}, options=dict(stored))
        flow = _flow(entry)
        await getattr(flow, f"async_step_{step}")(None)
        res = await getattr(flow, f"async_step_{step}")(dict(submit))
        body = json.dumps({"type": res.get("type"), "errors": res.get("errors"),
                           "options": entry.options}, sort_keys=True, default=repr)
        sha = hashlib.sha1(body.encode()).hexdigest()[:12]
        if case == EXCEPTION:
            exceptions += 1
            print(f"  A3-exception: {case} {sha} {body}")
            continue
        lines.append(f"{case} {sha}")
        print(f"  {case} {sha} {body}")
    digest = hashlib.sha1("\n".join(lines).encode()).hexdigest()[:12]
    print(f"RESULT cases={len(lines)} exceptions={exceptions} digest={digest}")


def main():
    args = set(sys.argv[1:])
    null = "--null" in args
    if "--clear-required" in args:
        asyncio.run(clear_required(null))
        return
    if "--accepted" in args:
        asyncio.run(accepted())
        return
    cf.validate_tibber_token = _refuse_token
    label = "shown_stored" if null else "stale_slots"
    tot_rows = tot_hits = tot_rej = 0
    for step in REJECT:
        n, rej, hits, typ, why = asyncio.run(rerender(step, null))
        tot_rows += n
        tot_hits += hits
        tot_rej += rej
        print(f"  {step}: stored_rows={n} rejected={int(rej)} {label}={hits} [{typ} {why}]")
    print(f"RESULT pages={len(REJECT)} rejected={tot_rej} stored_rows={tot_rows} {label}={tot_hits}")


if __name__ == "__main__":
    main()
