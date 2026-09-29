#!/usr/bin/env python3
"""D1-s5 (round 9, D1.M6/M5): hostile-payload sweep of the external-input
parsers in this seat's files. Evidence for NON-findings (what held).

Metric (one line): per parser, of K hostile payloads, how many raise out of
the parser and how many deliver a non-finite number.

Parsers driven (production symbols):
  price_model:prices_from_tibber_payload, price_model:prices_from_entity_attributes,
  price_model:hourly_from_entities (via hourly_from_entries/quarters_from_entries),
  open_meteo:OpenMeteoSolar.async_refresh (with _get_json patched to the payload),
  inputs:InputReader.read / read_bool / read_power_kw.

Command:
  PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D1/s5/parsers_sweep.py [--perturb]
  --perturb removes open_meteo's #1519 defences in memory (the fence
  OpenMeteoSolar._fenced re-raises, and _parse_block loses its isinstance
  shape guard): open_meteo_raised rises above 0, which shows the sweep reaches
  the guards it credits.

Expected (baseline): see RESULT lines; nonfinite_delivered=0 for every parser,
open_meteo_raised=0, input_reader_raised=0, entity_attrs_raised=0;
tibber_payload_raised=4 (caught one level up by the coordinator's broad
except in _fetch_tibber_prices, outside this seat's cells).
Baseline SHA: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1. Machine: cloud container
(box B5, Linux x86_64), Python 3.14 venv. Counts are contention-immune.
Root rule: imports from the working directory (run from the export root).
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import asyncio
import math
import sys
import time
from datetime import datetime, timedelta, timezone
from unittest import mock

sys.path.insert(0, ".")
sys.path.insert(0, "tests")

_p0, _t0 = time.process_time(), time.thread_time()

from harness import FakeHass, FakeState  # noqa: E402
from custom_components.heatpump_optimizer import inputs  # noqa: E402
from custom_components.heatpump_optimizer import open_meteo as om  # noqa: E402
from custom_components.heatpump_optimizer import price_model as pm  # noqa: E402

PERTURB = "--perturb" in sys.argv
UTC = timezone.utc
NOW = datetime(2026, 1, 15, 12, 0, tzinfo=UTC)
HOSTILE_SCALARS = ["nan", "inf", "-inf", "1e999", float("nan"), float("inf"), None, "", "abc",
                   [], {}, {"a": 1}, True, "0x10", " 21 ", "٣", 1e308]


def _nonfinite(x):
    return isinstance(x, float) and not math.isfinite(x)


def sweep_tibber():
    payloads = [None, "x", [], {}, {"errors": []}, {"data": None}, {"data": {"viewer": None}},
                {"data": {"viewer": {"homes": "abc"}}}, {"data": {"viewer": {"homes": [None]}}},
                {"data": {"viewer": {"homes": [{"currentSubscription": {"priceInfo": []}}]}}}]
    rows = [{"total": v, "startsAt": "2026-01-15T00:00:00+01:00"} for v in HOSTILE_SCALARS]
    payloads.append({"data": {"viewer": {"homes": [{"currentSubscription": {"priceInfo": {"today": rows + ["x", None, 5]}}}]}}})
    raised = nonfinite = 0
    for p in payloads:
        try:
            out = pm.prices_from_tibber_payload(p)
        except Exception:  # noqa: BLE001
            raised += 1
            continue
        if isinstance(out, list):
            nonfinite += sum(_nonfinite(r["total"]) or not isinstance(r["total"], float) for r in out)
    return len(payloads), raised, nonfinite


def sweep_entity_attrs():
    items = [{"start": "2026-01-15T00:00:00+01:00", "value": v} for v in HOSTILE_SCALARS]
    attrs_list = [None, {}, {"raw_today": "abc"}, {"raw_today": [None, 1, "x"]},
                  {"raw_today": items, "unit_of_measurement": "öre/kWh"},
                  {"raw_today": items, "unit_of_measurement": "garbage"},
                  {"today": [{"start": object(), "value": 1.0}]}]
    raised = nonfinite = 0
    for a in attrs_list:
        for vat, sur in ((1.25, 0.1), (float("nan"), float("inf"))):
            try:
                out = pm.prices_from_entity_attributes(a, vat, sur)
            except Exception:  # noqa: BLE001
                raised += 1
                continue
            if isinstance(out, list):
                nonfinite += sum(_nonfinite(r["total"]) for r in out)
    # learners' day grouping on the delivered rows
    try:
        rows = pm.prices_from_entity_attributes({"raw_today": items}, 1.0, 0.0)
        pm.hourly_from_entries(rows if isinstance(rows, list) else [])
        pm.quarters_from_entries([{"starts_at": v, "total": v} for v in HOSTILE_SCALARS])
    except Exception:  # noqa: BLE001
        raised += 1
    return len(attrs_list) * 2 + 1, raised, nonfinite


def sweep_open_meteo():
    blocks = [None, "x", [], {"time": "abc"}, {"time": [1, 2], om._VARIABLE: "ab"},
              {"time": ["2026-01-15T00:00", "2026-01-15T01:00", "junk", None, 5],
               om._VARIABLE: ["nan", float("inf"), -1, 1e9, 100.0]},
              {"time": ["2026-01-15T00:00"] * 5, om._VARIABLE: [1, 2, 3, 4, 5]},
              {"time": [{"a": 1}, ["x"]], om._VARIABLE: [1, 2]}]
    payloads = [None, [], "str", {"error": True, "reason": "x"}]
    for b in blocks:
        payloads.append({"hourly": b, "minutely_15": b})
    raised = nonfinite = 0
    for p in payloads:
        async def fake(self, session, url, params, p=p):
            return p if isinstance(p, dict) and not p.get("error") else None
        solar = om.OpenMeteoSolar(object(), 60.0, 18.0)
        patches = [mock.patch.object(om, "async_get_clientsession", lambda h: object()),
                   mock.patch.object(om.OpenMeteoSolar, "_get_json", fake)]
        if PERTURB:
            async def _unfenced(fetch):
                return await fetch
            patches.append(mock.patch.object(om.OpenMeteoSolar, "_fenced", staticmethod(_unfenced)))
            _orig = om._parse_block

            def _unguarded(block, variable, max_value=om._MAX_PLAUSIBLE_GHI, _o=_orig):
                block.get("time")  # the shape guard, removed
                return _o(block, variable, max_value)
            patches.append(mock.patch.object(om, "_parse_block", _unguarded))
        try:
            for pt in patches:
                pt.start()
            asyncio.run(solar.async_refresh(NOW, force=True))
            for i in range(8):
                v = solar.irradiance_for(NOW + timedelta(hours=i), timedelta(minutes=15))
                nonfinite += _nonfinite(v)
        except Exception:  # noqa: BLE001
            raised += 1
        finally:
            for pt in patches:
                pt.stop()
    return len(payloads), raised, nonfinite


def sweep_input_reader():
    raised = nonfinite = n = 0
    for v in HOSTILE_SCALARS:
        for unit in (None, "°C", "°F", "W", "kW", "garbage"):
            n += 1
            st = FakeState(v, unit=unit, last_updated=NOW - timedelta(minutes=1))
            hass = FakeHass({"sensor.x": st})
            r = inputs.InputReader(hass, {"k": "sensor.x"}, now=lambda: NOW)
            try:
                for fn in (r.read, r.read_power_kw, r.read_bool):
                    rd = fn("k")
                    nonfinite += _nonfinite(rd.value)
            except Exception:  # noqa: BLE001
                raised += 1
    return n, raised, nonfinite


def _swapins():
    try:
        with open("/proc/vmstat") as f:
            for line in f:
                if line.startswith("pswpin"):
                    return int(line.split()[1])
    except OSError:
        pass
    return -1


if __name__ == "__main__":
    print(f"arm: {'PERTURBED (open_meteo fence removed)' if PERTURB else 'baseline'}")
    for name, fn in (("tibber_payload", sweep_tibber), ("entity_attrs", sweep_entity_attrs),
                     ("open_meteo", sweep_open_meteo), ("input_reader", sweep_input_reader)):
        k, raised, nf = fn()
        print(f"RESULT {name}_raised={raised} payloads (of {k})")
        print(f"RESULT {name}_nonfinite_delivered={nf} values")
    p, t = time.process_time() - _p0, time.thread_time() - _t0
    print(f"RESULT thread_factor={p / t if t > 0 else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print(f"RESULT swapins={_swapins()}")
