#!/usr/bin/env python3
"""Recorded days, fed through the real coordinator one cycle at a time.

#1499 -- Heat Pump Action reading "off" all day while the pump heated the
tank -- was found by the owner in use, after seven audit rounds of synthetic
matrices had passed it. What those matrices never had was a day a real
install lives through: the inputs arriving together, in their real order, for
twenty-four hours. This lane replays such days.

A day is a fixture under ``tests/replay/``: the JSON ``tools/replay/export.py``
writes from a Home Assistant recorder (the config entry, and the state history
of every entity it maps). For each fixture, in its own interpreter with the
fixture's time zone:

* the clock is frozen at each cycle's instant, and every recorded input is set
  to the state it had then (``last_reported`` capped at that instant, so no
  row reports from the future);
* ``HeatPumpOptimizerCoordinator._async_update_data`` runs -- the real cycle:
  input reads, price fetch, weather fetch, solve, actuation;
* every entity the six platforms publish is read back, and judged.

WHAT IS SUBSTITUTED, and nothing else: the worker's child interpreter
(``_ensure_worker``) -- the job still goes through ``_await_optimize``, the
pickle transport and ``process_worker.run_worker``, but in this process, so
its CPU is on this process's clock (spawning the child is
``tests/deployment_shape.py``'s and ``tests/nightly_ha.py``'s subject, not this
lane's); the weather entity's ``get_forecasts`` answers from the recorded
weather itself -- the recorder keeps no forecast, so the forecast is the
weather that actually came; a Tibber install's price fetch answers from the
price sensor the export names (``price_series_entity``). A price-entity
install needs no substitution. Learned state starts from a fresh install:
the export carries no ``.storage`` store of this integration.

THE INVARIANTS, per cycle and per published entity:

``finite``           no NaN or infinity in a state or an attribute;
``unit``             the unit is one Home Assistant allows for the device
                     class, an enum's state is one of its options;
``no_default``       no temperature published as available that is a
                     ``ThermalState`` constructor default -- unless an input
                     read that same value this cycle (a real 21.0 is a
                     reading, not a default);
``agreement``        Heat Pump Action and the climate entity do not say "off"
                     while the pump runs: not ``off``/``idle`` beside
                     ``heat_pump_on``, not ``off`` while the plan's current
                     step draws (space ``power`` + ``dhw_power`` clears the
                     optimizer's own on threshold), and ``hvac_action`` not
                     idle while ``heat_pump_on`` (#1499's shape);
``cycle``            every cycle returns data and no entity property raises;

and once per fixture:

``not_frozen``       a published number that mirrors an input -- equal to it,
                     to 0.05, on at least three cycles and half the cycles
                     both were readable -- moves when that input moves by more
                     than 0.2;
``cycle_cost``       what one cycle costs (#1544: no budgeted script ran the
                     coordinator cycle). CPU is the mean process CPU of a
                     cycle -- the update and the sweep of every entity --
                     over the median ``tests/stress.py`` reference solve run
                     in the same process, so a busy or slow runner lifts
                     both; memory is the largest tracemalloc peak of one
                     cycle. Each lies in (budget / COST_DETECTION, budget]
                     of ``COST_BUDGETS``: over it is a regression, under it
                     a budget that could not see a doubling (stress.py's
                     rule). The first cycle is traced instead of timed, and
                     must run the five per-cycle files ``COST_FILES`` names;
                     the lane then replays the fixture twice more with the
                     cycle's CPU, then its memory peak, doubled in memory at
                     ``_async_update_data``, and each must turn it red.

Each invariant is also driven on a hand-built bad and good record before any
fixture runs (``control:*``), so a detector that cannot fire fails here
rather than passing every night. The lane further re-runs the export's
sanitiser (and ``tests/nightly_ha.py``'s A10 coordinate rule) over every
fixture, and regenerates the synthetic fixture through
``tools/replay/synthesize.py`` and requires it byte-identical to the committed
one.

The fixture replays are nightly, never per pull request (``tests/closure.py``
NOT_A_TEST). The cheap half is not: ``tests/entities.py`` runs the controls,
the sanitiser checks and the regeneration on every pull request that touches
this file, a fixture, or ``tools/replay/``.

    python3 tests/replay.py                  # every fixture
    python3 tests/replay.py --fixture F.json --step-minutes 60
"""
from __future__ import annotations

import argparse
import asyncio
import contextlib
import dataclasses
import importlib
import io
import json
import math
import os
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIXTURES = ROOT / "tests" / "replay"
REPLAY_TOOLS = ROOT / "tools" / "replay"
for _p in (ROOT / "tests" / "hastub", ROOT / "tests", ROOT / "custom_components", REPLAY_TOOLS):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

MARK = "<<<replay-json>>>"
MIRROR_TOL = 0.05
MIRROR_MIN_HITS = 3
INPUT_MOVE = 0.2

#: Home Assistant's ``DEVICE_CLASS_UNITS`` for the device classes this
#: integration publishes, copied from upstream's sensor ``const.py``. Used only
#: when the real table is not importable (``tests/hastub`` has none).
UNITS_FALLBACK = {
    "temperature": {"°C", "°F", "K"},
    "power": {"mW", "W", "kW", "MW", "GW", "TW", "BTU/h"},
    "energy": {"mWh", "Wh", "kWh", "MWh", "GWh", "TWh", "MJ", "GJ",
               "cal", "kcal", "Mcal", "Gcal"},
    "energy_storage": {"mWh", "Wh", "kWh", "MWh", "GWh", "TWh", "MJ", "GJ",
                       "cal", "kcal", "Mcal", "Gcal"},
    "battery": {"%"},
    "frequency": {"Hz", "kHz", "MHz", "GHz"},
    "irradiance": {"W/m²", "BTU/(h⋅ft²)"},
    "volume_storage": {"L", "mL", "gal", "fl. oz.", "m³", "ft³", "CCF"},
    "enum": {None},
    "timestamp": {None},
}


def units_table() -> dict:
    try:
        from homeassistant.components.sensor.const import DEVICE_CLASS_UNITS
    except ImportError:
        return UNITS_FALLBACK
    return {str(k): {None if u is None else str(u) for u in v}
            for k, v in DEVICE_CLASS_UNITS.items()}


# --- the invariants, pure over records ----------------------------------------
#
# A record is one published entity at one cycle: entity_id, available, state,
# attributes, device_class, unit, options. Each function returns offenders.


def _nonfinite(node: object, path: str, out: list[str]) -> None:
    if isinstance(node, bool):
        return
    if isinstance(node, dict):
        for key, value in node.items():
            _nonfinite(value, f"{path}.{key}", out)
    elif isinstance(node, (list, tuple)):
        for i, value in enumerate(node):
            _nonfinite(value, f"{path}[{i}]", out)
    elif isinstance(node, (int, float)) and not math.isfinite(float(node)):
        out.append(f"{path}={node!r}")


def inv_finite(records: list[dict]) -> list[str]:
    out: list[str] = []
    for rec in records:
        _nonfinite(rec["state"], rec["entity_id"], out)
        _nonfinite(rec["attributes"], rec["entity_id"], out)
    return out


def inv_unit(records: list[dict], table: dict) -> list[str]:
    out = []
    for rec in records:
        dc = rec.get("device_class")
        if not dc or not rec["available"]:
            continue
        allowed = table.get(str(dc))
        if str(dc) == "monetary":
            unit = rec.get("unit")
            if unit is not None and not (isinstance(unit, str) and len(unit) == 3):
                out.append(f"{rec['entity_id']}: monetary unit {unit!r}")
            continue
        if allowed is not None and rec.get("unit") not in allowed:
            out.append(f"{rec['entity_id']}: {dc} in {rec.get('unit')!r}")
        if str(dc) == "enum" and rec["state"] is not None:
            options = rec.get("options")
            if options is not None and rec["state"] not in options:
                out.append(f"{rec['entity_id']}: state {rec['state']!r} not in its options")
    return out


def thermal_defaults() -> list[float]:
    from heatpump_optimizer.thermal_model import ThermalState

    state = ThermalState()
    out = []
    for field in dataclasses.fields(state):
        value = getattr(state, field.name)
        if isinstance(value, (int, float)) and not isinstance(value, bool) \
                and math.isfinite(float(value)):
            out.append(float(value))
    return out


def _is(a: object, b: float, tol: float = 1e-9) -> bool:
    return isinstance(a, (int, float)) and not isinstance(a, bool) and abs(float(a) - b) <= tol


def inv_no_default(records: list[dict], defaults: list[float], readings: list[float]) -> list[str]:
    """A temperature equal to a constructor default, which no input read."""
    out = []

    def judge(label: str, value: object) -> None:
        try:
            v = float(value)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            return
        if any(_is(v, d) for d in defaults) and not any(_is(v, r) for r in readings):
            out.append(f"{label}={v}")

    for rec in records:
        if not rec["available"]:
            continue
        if str(rec.get("device_class")) == "temperature":
            judge(rec["entity_id"], rec["state"])
        if rec["entity_id"].startswith("climate."):
            # The readings only: a target is a setpoint the config supplies.
            judge(f"{rec['entity_id']}.current_temperature",
                  (rec["attributes"] or {}).get("current_temperature"))
    return out


POWER_TOL = 0.05


def inv_agreement(records: list[dict], plan_draws: bool | None,
                  plan_kw: float | None = None) -> list[str]:
    """Heat Pump Action and hvac_action agree with the pump actually running.

    ``plan_draws`` is whether the plan's current step clears the optimizer's
    own on threshold on space + DHW power, or None when no plan exists.
    ``plan_kw`` is that step's space + DHW draw, read from the plan's own
    space action and DHW forecast; Heat Pump Action's ``power_kw`` must equal
    it (#1499's power half: a DHW-only step published 0 kW).
    """
    out = []
    for rec in records:
        if not rec["available"]:
            continue
        attrs = rec["attributes"] or {}
        if rec.get("key") == "heat_pump_action":
            if rec["state"] in ("off", "idle") and attrs.get("heat_pump_on") is True:
                out.append(f"{rec['entity_id']}: state {rec['state']!r} "
                           "while its heat_pump_on attribute is true")
            if rec["state"] == "off" and plan_draws:
                out.append(f"{rec['entity_id']}: state 'off' while the plan's "
                           "current step draws space + DHW power")
            published = attrs.get("power_kw")
            if plan_kw is not None and isinstance(published, (int, float)) \
                    and abs(float(published) - plan_kw) > POWER_TOL:
                out.append(f"{rec['entity_id']}: power_kw {published} while the "
                           f"plan's current step draws {plan_kw:.2f} kW")
        if rec["entity_id"].startswith("climate."):
            action = attrs.get("hvac_action")
            if action in ("idle", "off") and attrs.get("_heat_pump_on") is True \
                    and rec["state"] not in ("off", None):
                out.append(f"{rec['entity_id']}: hvac_action {action!r} "
                           "while the current action has heat_pump_on")
    return out


def frozen_offenders(
    published: dict[str, list[float | None]],
    inputs: dict[str, list[float | None]],
) -> list[str]:
    """A published number that mirrors an input and stayed put when it moved."""
    out = []
    for pkey, pvals in published.items():
        for ikey, ivals in inputs.items():
            both = [(p, i) for p, i in zip(pvals, ivals) if p is not None and i is not None]
            matched = [i for p, i in both if abs(p - i) <= MIRROR_TOL]
            # Two distinct matched values at least: a published 0.0 beside an
            # input idling at 0.0 is a coincidence of zeros, not a mirror.
            if len(matched) < MIRROR_MIN_HITS or len(matched) * 2 < len(both) \
                    or len({round(v, 3) for v in matched}) < 2:
                continue
            for k in range(1, len(pvals)):
                p0, p1, i0, i1 = pvals[k - 1], pvals[k], ivals[k - 1], ivals[k]
                if None in (p0, p1, i0, i1):
                    continue
                if abs(i1 - i0) > INPUT_MOVE and abs(p1 - p0) < 1e-9:
                    out.append(f"{pkey} stayed {p1} at cycle {k} while {ikey} "
                               f"moved {i0} -> {i1}")
                    break
    return out


#: The five files of the per-cycle path #1544 found no budgeted script ran.
COST_FILES = ("coordinator.py", "sensor.py", "process_worker.py",
              "price_model.py", "narrative.py")
#: The multiple a budget must be able to see, as ``tests/stress.py``'s
#: DETECTION_TARGET: a budget is recorded at sqrt(2) x the measured cost, so
#: the measurement sits in (budget / 2, budget] and a doubled cycle is over it.
COST_DETECTION = 2.0
#: Per fixture: ``cpu_ratio`` (cycle CPU / reference-solve CPU, mean over the
#: timed cycles) and ``peak_kib`` (largest per-cycle tracemalloc peak), each
#: sqrt(2) x a clean run's figure, which the lane's ``record:`` line prints.
#: One-sided: re-record down when the cycle got cheaper; a raise is a
#: regression argued in the commit message. The commit that records a figure
#: names the machine; the band check validates it on whichever runner reads
#: it, since a run outside (budget / 2, budget] is red and prints its own.
#: Across several runs, record the largest ``record:`` value, and keep it
#: under every doubled arm's figure.
COST_BUDGETS: dict[str, dict[str, float]] = {
    "synthetic-dhw-only.json": {"cpu_ratio": 3.576, "peak_kib": 2686.0},
}
#: A reference solve after every this many cycles, beside the ones before
#: and after the day, so the unit tracks the runner through the replay.
COST_REF_EVERY = 8


def cost_figures(cycle_cpu: list[float], ref_cpu: list[float],
                 peaks: list[int]) -> dict[str, float]:
    ref = sorted(ref_cpu)[len(ref_cpu) // 2] if ref_cpu else 0.0
    return {"cpu_ratio": round(sum(cycle_cpu) / len(cycle_cpu) / ref, 4)
            if cycle_cpu and ref > 0 else float("nan"),
            "peak_kib": round(max(peaks) / 1024.0, 1) if peaks else float("nan")}


def cost_offenders(figures: dict[str, float], budget: dict[str, float] | None,
                   detection: float = COST_DETECTION) -> list[str]:
    """A cycle over its budget, or a budget too loose to see ``detection``x."""
    if not budget or not all(budget.get(k, 0) > 0 for k in figures):
        return [f"no recorded budget: record {k}={math.sqrt(detection) * v:.4g}"
                for k, v in figures.items()]
    out = []
    for key, value in figures.items():
        cap = budget[key]
        if not math.isfinite(value):
            out.append(f"{key} not measured")
        elif value > cap:
            out.append(f"{key} {value:.4g} over its budget {cap:.4g}")
        elif value * detection < cap:
            out.append(f"{key} {value:.4g}: budget {cap:.4g} cannot see a "
                       f"{detection:g}x cycle; re-record {math.sqrt(detection) * value:.4g}")
    return out


def uncovered_files(traced: set[str]) -> list[str]:
    """COST_FILES no function of which ran in the traced cycle."""
    names = {Path(f).name for f in traced if "heatpump_optimizer" in Path(f).parts}
    return [f"{name}: no function ran in the traced cycle"
            for name in COST_FILES if name not in names]


# --- the controls: every invariant can fire, and does not fire on good data ----


def controls() -> list[tuple[str, bool, str]]:
    def rec(**kw):
        base = {"entity_id": "sensor.x", "key": "x", "available": True, "state": None,
                "attributes": {}, "device_class": None, "unit": None, "options": None}
        base.update(kw)
        return base

    table = UNITS_FALLBACK
    defaults = [21.0, 22.0, 5.0]
    res = []

    def pair(name, bad, good):
        res.append((f"control:{name}", bool(bad) and not good,
                    f"bad={bad[:2]} good={good[:2]}"))

    pair("finite", inv_finite([rec(state=float("nan"))]),
         inv_finite([rec(state=1.0, attributes={"a": [1, 2]})]))
    pair("unit",
         inv_unit([rec(device_class="temperature", unit="kW", state=1.0),
                   rec(device_class="enum", state="hot_water", options=["off"])], table),
         inv_unit([rec(device_class="temperature", unit="°C", state=1.0),
                   rec(device_class="enum", state="off", options=["off"])], table))
    pair("no_default",
         inv_no_default([rec(device_class="temperature", state=22.0)], defaults, [20.4]),
         inv_no_default([rec(device_class="temperature", state=21.0)], defaults, [21.0]))
    hpa = dict(entity_id="sensor.hpa", key="heat_pump_action")
    pair("agreement:attribute",
         inv_agreement([rec(**hpa, state="off", attributes={"heat_pump_on": True})], None),
         inv_agreement([rec(**hpa, state="hot_water", attributes={"heat_pump_on": True})], None))
    pair("agreement:plan",
         inv_agreement([rec(**hpa, state="off", attributes={"heat_pump_on": False})], True),
         inv_agreement([rec(**hpa, state="off", attributes={"heat_pump_on": False})], False))
    pair("agreement:power",
         inv_agreement([rec(**hpa, state="hot_water", attributes={"power_kw": 0.0})], True, 2.0),
         inv_agreement([rec(**hpa, state="hot_water", attributes={"power_kw": 2.0})], True, 2.0))
    pair("agreement:climate",
         inv_agreement([rec(entity_id="climate.x", state="auto",
                            attributes={"hvac_action": "idle", "_heat_pump_on": True})], None),
         inv_agreement([rec(entity_id="climate.x", state="auto",
                            attributes={"hvac_action": "heating", "_heat_pump_on": True})], None))
    inp = {"sensor.in": [1.0, 3.0, 1.0, 3.0, 2.0]}
    pair("not_frozen",
         frozen_offenders({"sensor.out": [1.0, 3.0, 1.0, 3.0, 3.0]}, inp),
         frozen_offenders({"sensor.out": [1.0, 3.0, 1.0, 3.0, 2.0]}, inp)
         + frozen_offenders({"sensor.zero": [0.0] * 5}, {"sensor.idle": [0.0] * 4 + [2.0]}))
    ref, clean = [10.0, 11.0, 9.0], cost_figures([20.0, 22.0], [10.0, 11.0, 9.0], [4096])
    budget = {k: math.sqrt(COST_DETECTION) * v for k, v in clean.items()}
    pair("cycle_cost:cpu", cost_offenders(cost_figures([40.0, 44.0], ref, [4096]), budget),
         cost_offenders(clean, budget))
    pair("cycle_cost:memory", cost_offenders(cost_figures([20.0, 22.0], ref, [8192]), budget),
         cost_offenders(clean, budget))
    pair("cycle_cost:loose_budget",
         cost_offenders(clean, {k: 3 * v for k, v in clean.items()}),
         cost_offenders(clean, budget))
    pair("cycle_cost:unrecorded", cost_offenders(clean, {"cpu_ratio": 0.0, "peak_kib": 0.0}),
         cost_offenders(clean, budget))
    pkg = "/x/custom_components/heatpump_optimizer/"
    pair("cycle_cost:coverage", uncovered_files({pkg + f for f in COST_FILES[1:]}),
         uncovered_files({pkg + f for f in COST_FILES}))
    return res


def sanitiser_checks(paths: list[Path]) -> list[tuple[str, bool, str]]:
    """The export's rules, and nightly_ha's A10 coordinate rule, on each fixture."""
    import export
    import nightly_ha

    res = []
    for path in paths:
        found = export.check_file(path)
        res.append((f"sanitised:{path.name}", not found, "; ".join(found[:3])))
        checks = nightly_ha.Checks()
        nightly_ha.check_a10_no_precise_location(checks, json.loads(path.read_text()))
        res.append((f"a10_location:{path.name}", not checks.failures(),
                    str(checks.results)))
    # The null control: an unsanitised payload is refused by the same rules.
    raw = {"format": export.FORMAT, "entry": {"data": {"tibber_token": "abc123xyz",
           "solar_location": {"latitude": 59.334591}}, "options": {}},
           "states": {"camera.x": [["t", "idle", {"entity_picture": "/p?token=q"}, None]]}}
    found = export.violations(raw)
    joined = "; ".join(found)
    res.append(("control:sanitiser_refuses",
                all(k in joined for k in ("tibber_token", "latitude", "entity_picture")),
                joined))
    dropped: list[str] = []
    conf = export.entry_keys(*export.default_const_paths())
    res.append(("control:sanitise_clears",
                not export.violations(export.sanitise(raw, conf, dropped), conf),
                f"dropped {len(dropped)} value(s)"))
    return res + leak_probes()


#: The review of #1508's leak probe (the first eleven): shapes of private data a recorder
#: row or a config entry can carry, each of which passed the first exporter.
#: Every one must be dropped by the export AND refused by ``--check`` when it
#: is put back into a committed fixture by hand.
LEAK_PROBES = {
    "capital_Latitude": {"Latitude": 59.334591, "Longitude": 18.063240},
    "lat_lon_short": {"lat": 59.334591, "lon": 18.063240},
    "coord_list": {"location": [59.334591, 18.063240]},
    "coord_string": {"gps": "59.334591,18.063240"},
    "basic_auth_url": {"stream_source": "rtsp://admin:hunter2pass@192.168.1.5/live"},
    "apikey_query": {"url": "https://api.example.com/v1?apikey=ABCDEF0123456789"},
    "pin_code": {"pin": "482913", "access_code": "771234"},
    "psk": {"wifi_psk": "correct-horse-battery",
            "private_key": "-----BEGIN PRIVATE KEY-----MIIE"},
    "email": {"account_email": "owner@example.com"},
    "serial_mac": {"serial_number": "SN-0098-7766", "mac": "aa:bb:cc:dd:ee:ff"},
    "entry_address": {"tibber_home": "Storgatan 12, 111 22 Stockholm"},
    # Two more, each in a place the key allowlist lets through, so only the
    # value rule (``export.text_ok``) stands between them and the file.
    "entry_url_in_allowed_key": {"ecl110_state_topic": "mqtt://ecl:s3cretpw@10.0.0.7/ecl"},
    "state_address": {"state": "Storgatan 12, 111 22 Stockholm"},
    # The review's second probe (leakprobe2, round 2 of #1508): the right key
    # holding the wrong shape, a host without a scheme, a MAC without colons.
    "n1_options_dict": {"options": {"home_owner": "Anna Exempel", "street": "Storgatan"}},
    "n2_currency_name": {"currency": "Anna Exempel"},
    "n3_options_address": {"options": ["Storgatan 12", "Sodermalm 11"]},
    "n4_token_in_series": {"today": ["abcDEFghiJKLmnoPQRstu9vWX7yz"]},
    "state_n10_host_path": {"state": "nas.exempel.se/cam/front"},
    "n11_host_path_unit": {"unit_of_measurement": "home.local/api/x"},
    "entry_n13_text_in_entity_key": {"weather_entity": "Storgatan 12 Stockholm"},
    "n14_mac_no_colons": {"options": ["aabbccddeeff"]},
}
PROBE_ENTITY = "sensor.heat_pump_power"


def _probe_texts(values: object) -> list[str]:
    """Every leaf string of a probe, which must not appear in the export."""
    if isinstance(values, dict):
        return [t for v in values.values() for t in _probe_texts(v)]
    if isinstance(values, list):
        return [t for v in values for t in _probe_texts(v)]
    return [str(values)]


def leak_probes() -> list[tuple[str, bool, str]]:
    import export
    import synthesize

    res = []
    committed = json.loads((FIXTURES / "synthetic-dhw-only.json").read_text())
    conf = export.entry_keys(*export.default_const_paths())
    for name, values in LEAK_PROBES.items():
        in_entry = name.startswith("entry_")
        in_state = name.startswith("state_")
        series, data = synthesize._series, synthesize.ENTRY_DATA
        if in_entry:
            synthesize.ENTRY_DATA = {**data, **values}
        else:
            def patched(values=values, series=series, in_state=in_state):
                out = series()
                out[PROBE_ENTITY] = [
                    (t, values["state"], a) if in_state else (t, st, {**a, **values})
                    for t, st, a in out[PROBE_ENTITY]]
                return out
            synthesize._series = patched
        try:
            with tempfile.TemporaryDirectory() as tmp:
                db = synthesize.write_install(Path(tmp))
                payload = export.build_export(
                    Path(tmp), db, 1, (synthesize.DAY + timedelta(days=1)).date().isoformat(),
                    None, [], None)
            blob = json.dumps(payload)
            survived = [t for t in _probe_texts(values) if t in blob]
            outcome = f"written, survived={survived}"
        except SystemExit as err:
            survived, outcome = [], f"refused: {err}"
        finally:
            synthesize._series, synthesize.ENTRY_DATA = series, data
        res.append((f"leak_probe:{name}:export_drops", not survived, outcome))
        # Put back by hand into a committed fixture: --check must refuse it.
        planted = json.loads(json.dumps(committed))
        if in_entry:
            planted["entry"]["data"].update(values)
        elif in_state:
            planted["states"][PROBE_ENTITY][0][1] = values["state"]
        else:
            planted["states"][PROBE_ENTITY][0][2] = {
                **(planted["states"][PROBE_ENTITY][0][2] or {}), **values}
        found = export.violations(planted, conf)
        res.append((f"leak_probe:{name}:check_refuses", bool(found), "; ".join(found[:3])))
    return res


def synthetic_reproduces() -> tuple[str, bool, str]:
    """In this process, so a recorder of this interpreter sees both files read."""
    import synthesize

    committed = FIXTURES / "synthetic-dhw-only.json"
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "again.json"
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                rc = synthesize.main(["--out", str(out)])
        except (SystemExit, Exception) as err:  # noqa: BLE001 - one red check
            # The exporter refuses with SystemExit; inside tests/entities.py
            # that would end the whole run, not fail this one check.
            rc = f"{type(err).__name__}: {err}"
        same = rc == 0 and out.read_bytes() == committed.read_bytes()
        size = out.stat().st_size if out.exists() else None
    return ("synthetic_reproduces", same,
            f"rc={rc} regenerated={size} B committed={committed.stat().st_size} B")


# --- one fixture, in this interpreter -----------------------------------------


def _ts(raw: str | None) -> datetime | None:
    return datetime.fromisoformat(raw) if raw else None


class Recording:
    """The fixture's state rows, answerable as 'what was true at t'."""

    def __init__(self, states: dict[str, list[list]]) -> None:
        self.rows: dict[str, list[tuple[datetime, str, dict, datetime | None]]] = {}
        for entity_id, rows in states.items():
            attrs: dict = {}
            out = []
            for updated, state, maybe_attrs, reported in rows:
                if maybe_attrs is not None:
                    attrs = maybe_attrs
                out.append((_ts(updated), state, attrs, _ts(reported)))
            self.rows[entity_id] = out

    def at(self, entity_id: str, t: datetime):
        chosen = None
        for row in self.rows.get(entity_id, ()):
            if row[0] <= t:
                chosen = row
            else:
                break
        return chosen

    def after(self, entity_id: str, t: datetime):
        """The rows from the one in force at ``t`` onwards."""
        rows = self.rows.get(entity_id, [])
        first = max(0, sum(1 for r in rows if r[0] <= t) - 1)
        return rows[first:]


def _num(value: object) -> float | None:
    try:
        v = float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None
    return v if math.isfinite(v) else None


class InProcessWorker:
    """``_ensure_worker``'s child, as ``process_worker.run_worker`` in this process.

    ``_run_in_process`` pickles the job into ``stdin`` and flushes; the flush
    hands that one job to the worker's own loop, which answers into ``stdout``
    and returns at the end of its input, as the child does at EOF.
    """

    def __init__(self) -> None:
        worker = self

        class Pipe(io.BytesIO):
            def flush(self) -> None:
                job = self.getvalue()
                self.seek(0)
                self.truncate()
                if job:
                    worker.serve(job)

        self.stdin = Pipe()
        self.stdout = io.BytesIO()

    def poll(self) -> None:
        return None

    def serve(self, job: bytes) -> None:
        from types import SimpleNamespace
        from heatpump_optimizer import process_worker

        reply = io.BytesIO()
        saved = sys.stdin, sys.stdout
        sys.stdin = SimpleNamespace(buffer=io.BytesIO(job))  # type: ignore[assignment]
        sys.stdout = SimpleNamespace(buffer=reply)  # type: ignore[assignment]
        try:
            process_worker.run_worker()
        finally:
            sys.stdin, sys.stdout = saved
        self.stdout.seek(0)
        self.stdout.truncate()
        self.stdout.write(reply.getvalue())
        self.stdout.seek(0)


def inject_cost(cm, kind: str | None) -> None:
    """The perturbation: double one cycle's CPU or its memory peak, in memory.

    Wraps ``_async_update_data`` rather than editing ``coordinator.py`` on
    disk, which a concurrent run in the same tree would import.
    """
    if kind is None:
        return
    import tracemalloc

    real = cm.HeatPumpOptimizerCoordinator._async_update_data

    async def doubled(self):
        began = time.process_time()
        out = await real(self)
        if kind == "cpu":
            until = time.process_time() + (time.process_time() - began)
            while time.process_time() < until:
                pass
        elif tracemalloc.is_tracing():
            current, peak = tracemalloc.get_traced_memory()
            ballast = bytearray(max(0, 2 * peak - current))
            del ballast
        return out

    cm.HeatPumpOptimizerCoordinator._async_update_data = doubled


def run_fixture(path: Path, step_minutes: int | None, inject: str | None = None) -> dict:
    import tracemalloc
    from stress import reference_solve  # first: it pins BLAS threads before numpy loads
    from homeassistant.util import dt as dt_util
    from homeassistant.helpers.update_coordinator import UpdateFailed
    from harness import FakeEntry, FakeHass, FakeState
    import heatpump_optimizer as integration
    from heatpump_optimizer import const
    from heatpump_optimizer import coordinator as cm

    fixture = json.loads(path.read_text())
    rec = Recording(fixture["states"])
    entry_data = dict(fixture["entry"]["data"])
    entry_options = dict(fixture["entry"]["options"])
    config = {**entry_data, **entry_options}
    start = _ts(fixture["window"]["start"])
    end = _ts(fixture["window"]["end"])
    step = timedelta(minutes=step_minutes or int(
        config.get(const.CONF_OPTIMIZATION_INTERVAL, const.DEFAULT_OPTIMIZATION_INTERVAL)))

    worker = InProcessWorker()
    cm._ensure_worker = lambda: worker
    inject_cost(cm, inject)

    hass = FakeHass()
    weather_id = config.get(const.CONF_WEATHER_ENTITY)

    async def forecasts(call):
        now = dt_util.now()
        rows = rec.after(weather_id, now)
        out = []
        for h in range(48):
            t = now + timedelta(hours=h)
            row = next((r for r in reversed(rows) if r[0] <= t), rows[0] if rows else None)
            if row is None:
                break
            attrs = row[2]
            out.append({"datetime": t.isoformat(),
                        "temperature": attrs.get("temperature"),
                        "wind_speed": attrs.get("wind_speed", 0.0),
                        "precipitation": attrs.get("precipitation", 0.0),
                        "condition": row[1]})
        return {weather_id: {"forecast": out}} if out else {}

    if weather_id:
        hass.services.async_register("weather", "get_forecasts", forecasts)

    entry = FakeEntry(data=entry_data, options=entry_options)
    coord = cm.HeatPumpOptimizerCoordinator(hass, entry)
    entry.runtime_data = coord

    price_series = fixture.get("price_series_entity")
    if not cm._entity_price_source(config):
        async def recorded_prices() -> None:
            now = dt_util.now()
            day0 = now.replace(hour=0, minute=0, second=0, microsecond=0)
            span = 2 if now.hour >= 13 else 1
            rows = []
            t = day0
            while t < day0 + timedelta(days=span):
                row = rec.at(price_series, t) if price_series else None
                value = _num(row[1]) if row else None
                if value is not None:
                    rows.append({"total": value, "starts_at": t.isoformat(),
                                 "level": "NORMAL"})
                t += timedelta(minutes=15)
            if not rows:
                raise UpdateFailed("the fixture records no price series")
            coord._prices = rows

        coord._fetch_tibber_prices = recorded_prices

    entities: list = []
    for platform in integration.PLATFORM_LIST:
        module = importlib.import_module(f"heatpump_optimizer.{str(platform)}")
        asyncio.run(module.async_setup_entry(hass, entry, entities.extend))

    table = units_table()
    defaults = thermal_defaults()
    results: dict[str, list[str]] = {k: [] for k in
                                     ("finite", "unit", "no_default", "agreement", "cycle")}
    pub_series: dict[str, list[float | None]] = {}
    inp_series: dict[str, list[float | None]] = {}
    cycles = 0
    t = start
    started = time.monotonic()
    reference_solve()  # scipy's first-call costs, thrown away as stress.py does
    ref_cpu = [reference_solve()[1] for _ in range(3)]
    cycle_cpu: list[float] = []
    peaks: list[int] = []
    traced: set[str] = set()
    while t < end:
        dt_util.freeze(t)
        readings: list[float] = []
        for entity_id in fixture["inputs"]:
            row = rec.at(entity_id, t)
            if row is None:
                continue
            updated, state, attrs, reported = row
            last_reported = min(t, reported) if reported else updated
            hass.states.set(entity_id, FakeState(
                state, last_updated=updated, last_reported=last_reported, attributes=attrs))
            v = _num(state)
            inp_series.setdefault(entity_id, [None] * cycles)
            inp_series[entity_id].append(v)
            if v is not None:
                readings.append(v)
        for series in inp_series.values():
            if len(series) < cycles + 1:
                series.append(None)
        # Cycle 0 is traced for coverage, odd cycles for memory, even ones
        # timed: a tracer or tracemalloc inside a timed cycle would be timed.
        mode = "trace" if cycles == 0 else ("memory" if cycles % 2 else "cpu")
        if mode == "trace":
            sys.setprofile(lambda frame, event, arg: traced.add(frame.f_code.co_filename)
                           if event == "call" else None)
        elif mode == "memory":
            tracemalloc.start()
        began = time.process_time()
        try:
            data = asyncio.run(coord._async_update_data())
            coord.data = data
            coord.last_update_success = True
        except Exception as err:  # noqa: BLE001 - a raise is the observation
            results["cycle"].append(f"{t.isoformat()}: {type(err).__name__}: {err}")
            coord.last_update_success = False
            data = coord.data or {}

        action = data.get("current_action") or {}
        records = sweep(entities, action, results["cycle"], t)
        if mode == "cpu":
            cycle_cpu.append((time.process_time() - began) * 1000.0)
        elif mode == "memory":
            peaks.append(tracemalloc.get_traced_memory()[1])
            tracemalloc.stop()
        else:
            sys.setprofile(None)
        if cycles % COST_REF_EVERY == COST_REF_EVERY - 1:
            ref_cpu.append(reference_solve()[1])
        results["finite"] += inv_finite(records)
        results["unit"] += inv_unit(records, table)
        results["no_default"] += inv_no_default(records, defaults, readings)
        results["agreement"] += [f"{t.isoformat()} {o}" for o in
                                 inv_agreement(records, plan_draws(coord, data, t),
                                               plan_draw_kw(data, t))]
        for r in records:
            for key, value in [("state", r["state"])] + list((r["attributes"] or {}).items()):
                label = f"{r['entity_id']}.{key}"
                pub_series.setdefault(label, [None] * cycles)
                pub_series[label].append(_num(value) if r["available"] else None)
        for series in pub_series.values():
            if len(series) < cycles + 1:
                series.append(None)
        cycles += 1
        t += step
    dt_util.freeze(None)
    ref_cpu += [reference_solve()[1] for _ in range(3)]
    results["not_frozen"] = frozen_offenders(pub_series, inp_series)
    figures = cost_figures(cycle_cpu, ref_cpu, peaks)
    results["cycle_cost"] = uncovered_files(traced) + cost_offenders(
        figures, COST_BUDGETS.get(path.name))
    return {"fixture": path.name, "cycles": cycles, "entities": len(entities),
            "cost": {**figures, "timed": len(cycle_cpu), "traced": len(peaks),
                     "ref_ms": sorted(ref_cpu)[len(ref_cpu) // 2]},
            "seconds": round(time.monotonic() - started, 1),
            "results": {k: v[:12] + ([f"... {len(v) - 12} more"] if len(v) > 12 else [])
                        for k, v in results.items()},
            "counts": {k: len(v) for k, v in results.items()}}


def _plan_step(data: dict, t: datetime) -> tuple[float, float] | None:
    """(space, DHW) kW of the plan's step covering ``t``: space from the
    current action, DHW from the plan's own DHW forecast -- not the action's
    ``dhw_power``, which is what the published power reads."""
    forecast = ((data.get("dhw_plan") or {}).get("forecast")) or []
    dhw = 0.0
    for row in forecast:
        start = _ts(row.get("t"))
        if start is not None and start <= t:
            dhw = float(row.get("dhw_power") or 0.0)
    action = data.get("current_action") or {}
    if "power" not in action:
        return None
    return float(action.get("power") or 0.0), dhw


def plan_draws(coord, data: dict, t: datetime) -> bool | None:
    """Whether the plan's step covering ``t`` runs the pump, by the optimizer's
    own helper -- the same call ``_build_result`` makes for its on schedule."""
    step = _plan_step(data, t)
    if step is None:
        return None
    return bool(coord._optimizer._power_to_heat_pump_schedule([step[0]], [step[1]])[0])


def plan_draw_kw(data: dict, t: datetime) -> float | None:
    step = _plan_step(data, t)
    return None if step is None else step[0] + step[1]


def sweep(entities: list, action: dict, errors: list[str], t: datetime) -> list[dict]:
    records = []
    for e in entities:
        entity_id = getattr(e, "entity_id", None) or getattr(e, "_attr_unique_id", repr(e))
        try:
            available = bool(e.available)
            if entity_id.startswith("climate."):
                state = e.hvac_mode
                attrs = dict(e.extra_state_attributes or {})
                attrs.update({"hvac_action": e.hvac_action,
                              "current_temperature": e.current_temperature,
                              "target_temperature": e.target_temperature,
                              # Not published: the value the climate entity is
                              # judged against, carried under a private key.
                              "_heat_pump_on": action.get("heat_pump_on")})
                unit = None
            elif hasattr(e, "native_value"):
                state = e.native_value
                attrs = dict(getattr(e, "extra_state_attributes", None) or {})
                unit = getattr(e, "native_unit_of_measurement", None)
            elif hasattr(e, "is_on"):
                state = e.is_on
                attrs = dict(getattr(e, "extra_state_attributes", None) or {})
                unit = None
            else:
                continue
            if isinstance(state, datetime):
                state = state.isoformat()
            records.append({
                "entity_id": entity_id,
                "key": getattr(e, "_attr_translation_key", None)
                or getattr(e, "translation_key", None),
                "available": available,
                "state": state,
                "attributes": attrs,
                "device_class": getattr(e, "device_class", None)
                or getattr(e, "_attr_device_class", None),
                "unit": unit,
                "options": getattr(e, "options", None) or getattr(e, "_attr_options", None),
            })
        except Exception as err:  # noqa: BLE001 - a raise is the observation
            errors.append(f"{t.isoformat()} {entity_id}: {type(err).__name__}: {err}")
    return records


# --- the driver ---------------------------------------------------------------


def replay_one(R, path: Path, step_minutes: int | None, inject: str | None) -> dict | None:
    """One fixture in its own interpreter, BLAS pinned to one thread."""
    tz = json.loads(path.read_text()).get("time_zone") or "UTC"
    env = {**os.environ, "HASTUB_TZ": tz,
           "PYTHONPATH": os.pathsep.join(
               [str(ROOT / "tests" / "hastub"), os.environ.get("PYTHONPATH", "")])}
    for var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
                "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
        env.setdefault(var, "1")
    cmd = [sys.executable, str(Path(__file__).resolve()), "--one", str(path)]
    if step_minutes:
        cmd += ["--step-minutes", str(step_minutes)]
    if inject:
        cmd += ["--inject-cost", inject]
    proc = subprocess.run(cmd, capture_output=True, text=True, env=env, cwd=ROOT)
    line = next((ln for ln in proc.stdout.splitlines() if ln.startswith(MARK)), None)
    label = f"{path.name}: the replay ran to the end" + (f" ({inject} doubled)" if inject else "")
    if not R.check(label, line is not None,
                   f"rc={proc.returncode}: {proc.stderr.strip()[-600:]}"):
        return None
    return json.loads(line[len(MARK):])


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--fixture", action="append", type=Path)
    ap.add_argument("--step-minutes", type=int)
    ap.add_argument("--one", type=Path, help=argparse.SUPPRESS)
    ap.add_argument("--inject-cost", choices=("cpu", "memory"), help=argparse.SUPPRESS)
    args = ap.parse_args(argv)

    if args.one:
        print(MARK + json.dumps(run_fixture(args.one, args.step_minutes, args.inject_cost)))
        return 0

    from harness import Results

    R = Results("Replay: recorded days through the real coordinator")
    began = time.monotonic()
    paths = args.fixture or sorted(FIXTURES.glob("*.json"))
    R.check("at least one fixture", bool(paths), str(FIXTURES))

    R.section("controls: each invariant fires on bad data and not on good")
    for name, ok, detail in controls():
        R.check(name, ok, detail)

    R.section("sanitising: the export's rules and nightly_ha's A10 rule")
    for name, ok, detail in sanitiser_checks(paths):
        R.check(name, ok, detail)
    name, ok, detail = synthetic_reproduces()
    R.check("the synthetic fixture is what synthesize.py + export.py write", ok, detail)

    for path in paths:
        R.section(f"replay {path.name}")
        out = replay_one(R, path, args.step_minutes, None)
        if out is None:
            continue
        print(f"  {out['cycles']} cycles over {out['entities']} entities "
              f"in {out['seconds']} s; cost {out['cost']}")
        print(f"  record: {path.name} " + " ".join(
            f"{k}={math.sqrt(COST_DETECTION) * out['cost'][k]:.4g}"
            for k in ("cpu_ratio", "peak_kib")))
        R.check(f"{path.name}: at least one cycle and one entity",
                out["cycles"] > 0 and out["entities"] > 0, str(out["cycles"]))
        for name, offenders in out["results"].items():
            R.check(f"{path.name}: {name}", not offenders,
                    f"{out['counts'][name]} offender(s): " + " | ".join(offenders[:6]))
        # The perturbation, every night: a doubled cycle must be over budget.
        for kind, key in (("cpu", "cpu_ratio"), ("memory", "peak_kib")):
            hot = replay_one(R, path, args.step_minutes, kind)
            if hot is None:
                continue
            print(f"  {kind} doubled at _async_update_data: cost {hot['cost']}")
            fired = [o for o in hot["results"]["cycle_cost"]
                     if o.startswith(f"{key} ") and "over its budget" in o]
            R.check(f"{path.name}: cycle_cost sees a doubled cycle {kind}", bool(fired),
                    f"{key} {hot['cost'][key]} against clean {out['cost'][key]}: "
                    + " | ".join(hot["results"]["cycle_cost"][:3]))
    print(f"\nreplay lane wall time {time.monotonic() - began:.1f} s")
    return R.close("replay checks")


if __name__ == "__main__":
    sys.exit(main())
