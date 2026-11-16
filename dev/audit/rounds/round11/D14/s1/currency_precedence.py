"""D14-s1 detector for class P8 (currency half): a money unit resolved by a
different precedence on different surfaces.

Metric: money_seams = count of money-bearing surfaces whose currency differs
from the price feed's declared currency, on a SEK instance (hass.config.currency
= "SEK") priced by a EUR/kWh entity feed. Surfaces enumerated, not named:
(a) every live entity (platform async_setup_entry on a coord_all_features
coordinator switched to the entity price source) whose native unit or
`currency` attribute names a money code; (b) every config_flow._OPTION_FIELDS
widget built by hass (_ByHass) whose unit names a money code; (c) the grid-fee
page placeholders (config_flow._fee_placeholders) and the fee bound the page
validates with (grid_fee.fee_bound via config_flow's resolve_currency).
Key = the unit string the surface delivers, never the config key.
Null control (--null): the same run with a SEK/kWh feed: every surface agrees.

Command:   PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D14/s1/currency_precedence.py [--null] [--perturb] [--instance HUF] [--tree DIR]
Expected at 92d38ecb: money_seams=5 (SEK instance), 6 (--instance HUF: the fee bound too),
           --null -> 0, --perturb -> 0 (exact counts). At an export of 3490cb16 (pre-#1657,
           --tree) the entity units are the re-found instances.
Baseline:  92d38ecb640bd462f2e19c0814d0f0b7df1ee692; machine: box B7 (x86_64, 4 vCPU).
Hooked:    custom_components.heatpump_optimizer.config_flow:_money / _fee_placeholders /
           resolve_currency, coordinator:_feed_currency, sensor units of the live entities.
Perturbation (--perturb, one line): config_flow.resolve_currency bound to the
           coordinator's precedence (feed first: coordinator._feed_currency(hass, cfg) or
           the instance's) -> money_seams to 0 (to_zero).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import asyncio
import importlib
import re
import sys
import time

argv = sys.argv[1:]
NULL = "--null" in argv
PERTURB = "--perturb" in argv
INSTANCE = argv[argv.index("--instance") + 1] if "--instance" in argv else "SEK"
FEED = INSTANCE if NULL else "EUR"
TREE = os.path.abspath(argv[argv.index("--tree") + 1]) if "--tree" in argv else os.getcwd()
sys.path[:0] = [os.path.join(TREE, d) for d in ("tests/hastub", "tests", "custom_components")]

from harness import FakeHass, FakeEntry, FakeState  # noqa: E402
import golden  # noqa: E402
from heatpump_optimizer import const, coordinator as cm, config_flow as cf, grid_fee  # noqa: E402
from homeassistant.helpers import selector  # noqa: E402

CODE = re.compile(r"\b([A-Z]{3})\b")
NOT_MONEY = {"COP", "MQT", "ECL"}


def money_code(text):
    for m in CODE.findall(str(text or "")):
        if m not in NOT_MONEY:
            return m
    return None


def main():
    t0 = time.process_time(); th0 = time.thread_time()
    hass = FakeHass()
    hass.config.currency = INSTANCE
    hass.states.set("sensor.indoor", FakeState("21.4"))
    hass.states.set("sensor.outdoor", FakeState("-3.0"))
    hass.states.set("sensor.feed", FakeState("0.21", attributes={"unit_of_measurement": f"{FEED}/kWh"}))
    cfg = dict(golden.coordinator_scenarios()["coord_all_features"])
    cfg.update({const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor", const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
                const.CONF_PRICE_SOURCE: const.PRICE_SOURCE_ENTITY, const.CONF_PRICE_ENTITY: "sensor.feed"})
    entry = FakeEntry(data=cfg)
    if PERTURB:
        cf.resolve_currency = lambda h: (cm._feed_currency(h, cfg) if hasattr(cm, "_feed_currency") else FEED) or cm.resolve_currency(h)
    coord = cm.HeatPumpOptimizerCoordinator(hass, entry)
    asyncio.run(coord._update_current_state())
    coord.data = coord._build_data_dict()
    entry.runtime_data = coord
    feed = cm._feed_currency(hass, cfg) if hasattr(cm, "_feed_currency") else FEED
    ents = []

    def add(es, *a, **k):
        for e in es:
            e.hass = hass
        ents.extend(es)
    for plat in ("sensor", "binary_sensor", "button", "switch", "climate", "datetime"):
        asyncio.run(importlib.import_module(f"heatpump_optimizer.{plat}").async_setup_entry(hass, entry, add))
    surfaces = []
    for e in ents:
        key = getattr(e, "_attr_translation_key", type(e).__name__)
        unit = getattr(e, "native_unit_of_measurement", None)
        c = money_code(unit)
        if c:
            surfaces.append((f"entity:{key}:unit", c, unit))
        try:
            attrs = e.extra_state_attributes or {}
        except Exception:
            attrs = {}
        if isinstance(attrs, dict) and isinstance(attrs.get("currency"), str):
            surfaces.append((f"entity:{key}:attr.currency", attrs["currency"], attrs["currency"]))
    for f in cf._OPTION_FIELDS:
        w = f.widget
        if hasattr(cf, "_ByHass") and isinstance(w, cf._ByHass):
            w = w.of(hass)
        if isinstance(w, selector.NumberSelector):
            unit = dict(w.config).get("unit_of_measurement")
            c = money_code(unit)
            if c:
                surfaces.append((f"options:{f.step}:{f.key}:unit", c, unit))
    if hasattr(cf, "_fee_placeholders"):
        ph = cf._fee_placeholders(hass)
        surfaces.append(("options:grid_fees:placeholder.currency", ph["currency"], ph["currency"]))
        bound_used = float(ph["fee_bound"]); bound_feed = grid_fee.fee_bound(feed)
        surfaces.append(("options:grid_fees:fee_bound", ph["currency"] if bound_used != bound_feed else feed,
                         f"{bound_used:g} (feed-scaled {bound_feed:g})"))
    surfaces.append(("coordinator:currency", coord.currency, coord.currency))
    seams = [s for s in surfaces if s[1] != feed]
    for s in seams:
        print("SEAM", f"{s[0]} -> {s[2]!s} (feed {feed})")
    print(f"RESULT instance={INSTANCE} feed_declared={feed}")
    print(f"RESULT money_surfaces={len(surfaces)} surfaces")
    print(f"RESULT entity_surfaces={sum(1 for s in surfaces if s[0].startswith('entity:'))} surfaces")
    print(f"RESULT options_surfaces={sum(1 for s in surfaces if s[0].startswith('options:'))} surfaces")
    print(f"RESULT money_seams={len(seams)} surfaces")
    pc = time.process_time() - t0; tc = time.thread_time() - th0
    print(f"RESULT thread_factor={pc / tc if tc else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
