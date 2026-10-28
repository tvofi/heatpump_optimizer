"""Design spike for R10-CONFIGFLOW-PAGES (D7-s2-56), driven through the production steps.

For every options page that can reject a submit: store an entity in each of the page's
``_STORED`` entity rows (``when`` gates opened), submit with every one of them cleared plus
one field that makes the page reject, and read the cleared rows' ``suggested_value`` on the
re-rendered form.

  stale_slots   cleared rows that re-render as the STORED entity (the defect)
  rejected      pages whose submit was rejected (errors non-empty); a page that saved is a
                harness failure, not a pass
Null control (--null): the same rejection with nothing cleared; every stored row must re-render
as stored, so stale_slots counts 0 by construction and `shown_stored` equals the row count.

    PYTHONPATH=tests/hastub python3 rejected_rerender.py [--null]
"""
import asyncio
import sys
from pathlib import Path

here = Path(__file__).resolve()
root = next(c for c in here.parents if (c / "custom_components/heatpump_optimizer/manifest.json").is_file())
sys.path[:0] = [str(root / "tests"), str(root / "custom_components")]

from harness import FakeEntry, FakeHass  # noqa: E402
from heatpump_optimizer import config_flow as cf  # noqa: E402
from heatpump_optimizer import const as c  # noqa: E402
from heatpump_optimizer.freq_control import FREQ_MODE_CONTROL  # noqa: E402
from heatpump_optimizer import mixing_valve  # noqa: E402


async def _refuse_token(_hass, _token):
    return "invalid_auth"


cf.validate_tibber_token = _refuse_token

#: page -> (base config opening its gates, the field set that makes it reject)
REJECT = {
    "entities": ({c.CONF_PRICE_SOURCE: c.PRICE_SOURCE_TIBBER, c.CONF_TIBBER_TOKEN: "old"},
                 {c.CONF_PRICE_SOURCE: c.PRICE_SOURCE_TIBBER, c.CONF_TIBBER_TOKEN: "new-bad"}),
    "entities_metering": ({}, {c.CONF_FREQ_CONTROL_MODE: FREQ_MODE_CONTROL}),
    "comfort": ({}, {c.CONF_MIN_TEMP: 25.0, c.CONF_MAX_TEMP: 18.0}),
    "hot_water": ({c.CONF_DHW_ENABLED: True} if hasattr(c, "CONF_DHW_ENABLED") else {}, {c.CONF_DHW_WINDOWS: "nonsense"}),
    "hot_water_tank": ({}, {c.CONF_DHW_DISINFECTION_MODE: FREQ_MODE_CONTROL}),
    "building": ({c.CONF_WOOD_FURNACE_ENABLED: True}, {c.CONF_MIXING_VALVE_WRITE_TARGET_KIND: mixing_valve.WRITE_TARGET_FLOW}),
    "grid": ({}, {c.CONF_PEAK_TARIFF_MONTHS: "13-14"}),
    "grid_connection": ({}, {c.CONF_SILENT_MODE_WINDOWS: "nonsense"}),
    "grid_fees": ({}, {c.CONF_GRID_FEE_RULES: "nonsense"}),
}


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


async def page(step, null):
    base, bad = REJECT[step]
    rows = [r for r in cf._page_rows(step, {**base, c.CONF_WOOD_FURNACE_ENABLED: True}) if r.default is cf._STORED]
    stored = {r.key: f"sensor.stored_{i}" for i, r in enumerate(rows)}
    entry = FakeEntry(data={**base, **stored})
    flow = cf.HeatPumpOptimizerOptionsFlow(entry)
    flow.hass = FakeHass()
    submit = dict(bad) if not null else {**stored, **bad}
    if step == "building":
        submit[c.CONF_WOOD_FURNACE_ENABLED] = True
    res = await getattr(flow, f"async_step_{step}")(submit)
    rejected = res.get("type") in ("form",) and bool(res.get("errors"))
    if "data_schema" not in res:
        return len(rows), False, 0, res.get("type"), res.get("step_id")
    stale = sum(1 for k, v in stored.items() if suggested(res, k) == v)
    return len(rows), rejected, stale, res.get("type"), res.get("errors")


def main():
    null = "--null" in sys.argv
    tot_rows = tot_stale = tot_rej = 0
    for step in REJECT:
        n, rej, stale, typ, why = asyncio.run(page(step, null))
        tot_rows += n
        tot_stale += stale
        tot_rej += rej
        print(f"  {step}: stored_rows={n} rejected={int(rej)} {'shown_stored' if null else 'stale_slots'}={stale} [{typ} {why}]")
    print(f"RESULT pages={len(REJECT)} rejected={tot_rej} stored_rows={tot_rows} "
          f"{'shown_stored' if null else 'stale_slots'}={tot_stale} count")


if __name__ == "__main__":
    main()
