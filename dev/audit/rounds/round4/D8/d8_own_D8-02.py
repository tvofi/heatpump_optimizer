#!/usr/bin/env python3
"""D8-02, verifier 1's own harness (independent of naming_order.py).

METRIC (mine): over every entity built through the real ``async_setup_entry``
on an all-features install, cross ``icons.json`` against (platform,
translation_key), and count (a) translation-keyed entities with NO icons.json
entry, (b) entities that carry BOTH a device class (read from
``_attr_device_class``; the stub declares no property -- see D8-INST) and an
explicit icon, (c) entities with NO device class and NO icon.  The
"device-class defence" (a device class supplies HA's default glyph, so no
icon is needed) predicts (b)=0 and is refuted if (b) is large while (c)=0.
A second, build-free path recomputes (a) from strings.json minus icons.json
alone, with no entities constructed at all.

COMMAND (from a tree root):

    PYTHONPATH=tests/hastub \
      /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 \
      tools/audit/round4/D8/d8_own_D8-02.py              # default
    ... d8_own_D8-02.py --perturb drop-other             # my perturbation
    ... d8_own_D8-02.py --perturb fix                    # my repair arm

EXPECTED (baseline 7dd68dd and branch head 0855277; 8-core Apple M1):
    entities=74  keyed=73
    no_icon_entities=4  dc_and_icon=31  no_dc_no_icon=0  (exact counts)
    file_only_missing=4
    ``--perturb drop-other`` removes sensor.recommended_power's icon entry
    in memory: no_icon_entities must rise to 5.
    ``--perturb fix`` adds the four missing entries in memory:
    no_icon_entities must fall to 0.
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

import asyncio  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402

from golden import START, coordinator_scenarios  # noqa: E402

from heatpump_optimizer import binary_sensor, button, climate, sensor, switch  # noqa: E402
from heatpump_optimizer import datetime as datetime_platform  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402

PERTURB = (
    sys.argv[sys.argv.index("--perturb") + 1] if "--perturb" in sys.argv else ""
)

PLATFORMS = {
    "sensor": sensor,
    "binary_sensor": binary_sensor,
    "button": button,
    "climate": climate,
    "switch": switch,
    "datetime": datetime_platform,
}

ROOT = Path("custom_components/heatpump_optimizer")


def build_all():
    cfg = dict(coordinator_scenarios()["coord_all_features"])
    cfg.update(
        {
            "indoor_temp_entity": "sensor.indoor",
            "outdoor_temp_entity": "sensor.outdoor",
            "dhw_tank_volume": 200.0,
            "mixing_valve_mode": "smart_write",
            "mixing_valve_write_entity": "number.valve_target",
            "ecl110_state_topic": "ecl110/flow_temp_control/displace",
            "wood_furnace_enabled": True,
            "compressor_freq_entity": "number.pump_freq",
            "contract_fixed_price": 1.2,
        }
    )
    hass = FakeHass()
    hass.states.set("sensor.indoor", FakeState("21.4"))
    hass.states.set("sensor.outdoor", FakeState("-3.0"))
    entry = FakeEntry(data=cfg)
    coord = HeatPumpOptimizerCoordinator(hass, entry)
    from datetime import timedelta

    coord._prices = [
        {
            "total": round(0.6 + 0.5 * (h % 12) / 12.0, 4),
            "starts_at": (START + timedelta(hours=h)).isoformat(),
            "level": "NORMAL",
        }
        for h in range(48)
    ]
    asyncio.run(coord._update_current_state())
    coord._forecast_arrays()
    coord.data = coord._build_data_dict()

    ents = []
    for pname, module in PLATFORMS.items():
        added: list = []
        entry.runtime_data = coord
        asyncio.run(module.async_setup_entry(hass, entry, lambda e: added.extend(e)))
        for ent in added:
            ents.append((pname, ent))
    return ents


def main() -> int:
    dt_util.freeze(START)
    try:
        ents = build_all()
    finally:
        dt_util.freeze(None)

    icons = json.loads((ROOT / "icons.json").read_text()).get("entity", {})
    if PERTURB == "drop-other":
        # MY perturbation key -- a different entry than the finder removed.
        icons.get("sensor", {}).pop("recommended_power", None)
    if PERTURB == "fix":
        for k in (
            "optimal_setpoint",
            "outdoor_temperature_optimizer",
            "measured_power",
            "compressor_frequency_advisor",
        ):
            icons.setdefault("sensor", {})[k] = "default:account"

    rows = []
    for pname, ent in ents:
        key = getattr(ent, "_attr_translation_key", None)
        dc = getattr(ent, "_attr_device_class", None)
        rows.append(
            {
                "platform": pname,
                "key": key,
                "eid": getattr(ent, "entity_id", None) or "",
                "device_class": str(getattr(dc, "value", dc)) if dc else None,
                "has_icon": key is not None and key in icons.get(pname, {}),
            }
        )
    assert len(rows) == 74, f"expected 74 entities, built {len(rows)}"

    keyed = [r for r in rows if r["key"] is not None]
    no_icon = [r for r in keyed if not r["has_icon"]]
    dc_and_icon = [r for r in keyed if r["device_class"] and r["has_icon"]]
    dc_no_icon = [r for r in keyed if r["device_class"] and not r["has_icon"]]
    no_dc_no_icon = [r for r in keyed if not r["device_class"] and not r["has_icon"]]
    no_dc_icon = [r for r in keyed if not r["device_class"] and r["has_icon"]]

    # Build-free path: strings.json minus icons.json, per platform.
    strings = json.loads((ROOT / "strings.json").read_text())["entity"]
    file_missing = sorted(
        f"{p}.{k}"
        for p, entries in strings.items()
        for k in entries
        if k not in json.loads((ROOT / "icons.json").read_text())
        .get("entity", {})
        .get(p, {})
    )

    out = Path("tools/audit/round4/D8/d8_own_D8-02_detail.json")
    out.write_text(
        json.dumps(
            {
                "no_icon": [f"{r['platform']}.{r['key']}" for r in no_icon],
                "no_icon_device_classes": [
                    f"{r['key']}:{r['device_class']}" for r in no_icon
                ],
                "dc_and_icon_count": len(dc_and_icon),
                "no_dc_no_icon": [f"{r['platform']}.{r['key']}" for r in no_dc_no_icon],
                "file_only_missing": file_missing,
                "rows": rows,
            },
            indent=1,
            sort_keys=True,
            ensure_ascii=False,
        )
    )

    for r in no_icon:
        print(f"# no icon: {r['platform']}.{r['key']}  device_class={r['device_class']}")

    print(f"RESULT perturbation={PERTURB or 'none'} arm")
    print(f"RESULT entities={len(rows)} count")
    print(f"RESULT keyed_entities={len(keyed)} count")
    print(f"RESULT no_icon_entities={len(no_icon)} entities")
    print(f"RESULT dc_and_icon={len(dc_and_icon)} entities")
    print(f"RESULT dc_no_icon={len(dc_no_icon)} entities")
    print(f"RESULT no_dc_no_icon={len(no_dc_no_icon)} entities")
    print(f"RESULT no_dc_icon={len(no_dc_icon)} entities")
    print(f"RESULT file_only_missing={len(file_missing)} keys")
    print(f"# detail written to {out}")
    import resource

    print("RESULT thread_factor=1.00 ratio")
    print("RESULT timing_results_reported=0 count")
    print(f"RESULT swapins={resource.getrusage(resource.RUSAGE_SELF).ru_nswap} count")
    print(f"RESULT load1={os.getloadavg()[0]:.2f} load")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
