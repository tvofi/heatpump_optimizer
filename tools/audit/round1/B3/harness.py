#!/usr/bin/env python3
"""Fix-group B3 harness: config-flow validation, currency, services example.

Re-measures the five round-1 findings this group closes, each as an executed
number taken by driving the production symbol (the config-flow step, the
coordinator's audit, the registered service schema) rather than by reading
source. Run from the repository root:

    PYTHONPATH=tests/hastub python tools/audit/round1/B3/harness.py

Every RESULT is exact (a count or a 0/1 flag), so the tolerance is zero.
Baseline measured against bbb698f (origin/main, v6.2.15) on the audit box
(8-core Apple M1, 8 GB, macOS 25.6, numpy on OpenBLAS); the fix branch's
head SHA and both value sets are in the PR body.

What each RESULT measures, and how it must move under the fix:

  D4-04 (#168), instrumented: HeatPumpOptimizerOptionsFlow.async_step_grid /
  async_step_tuning, HeatPumpOptimizerCoordinator._audit_grid_fee /
  _raise_cop_issue, rendered through strings.json the way the frontend does
  (placeholders substituted). Perturbation: hass.config.currency = "EUR".
    currency_leaks_at_eur           user-facing strings (field labels, field
                                    descriptions, selector units, the two
                                    Repairs notices) that still say "SEK"
                                    for an EUR instance          7 -> 0
    currency_units_following_hass   of the three money fields, how many
                                    carry a selector unit in the instance
                                    currency                     0 -> 3

  D4-05 (#169), instrumented: async_step_grid (form layer) and
  HeatPumpOptimizerCoordinator._fee_series (store layer).
    grid_rules_negative_accepted    the grid page stores "= -0.25"     1 -> 0
    grid_rules_implausible_accepted the grid page stores "= 25"        1 -> 0
    grid_rules_valid_accepted       the grid page stores "= 0.25"
                                    (null control)                     1 -> 1
    grid_store_negative_notices     Repairs notices the coordinator raises
                                    for a stored "= -0.25" rule        0 -> 1
    grid_store_negative_fee         the fee that store prices with
                                    (warn-only, must not move)   -0.25 -> -0.25

  D4-07 (#170), instrumented: the two comfort pages' rendered schemas and
  the submission path through comfort_band.violations.
    day_valid_schedules_forbidden_setup    valid start<end hour pairs
                                    (of 300) the setup sliders cannot
                                    express                          222 -> 0
    day_valid_schedules_forbidden_options  the same for the options page
                                                                     222 -> 0
    day_window_empty_reachable      1 if start=end=10 submitted through the
                                    options page reaches the validator and
                                    comes back as day_window_empty     0 -> 1

  D4-08 (#171), instrumented: async_step_dhw (setup) and async_step_hot_water
  (options), plus dhw_schedule.hour_in_windows over the planning grid.
    dhw_one_minute_accepted         both DHW pages store "06:05-06:06"  2 -> 0
    dhw_one_minute_steps_bound      quarter-hour step starts (of 96) that
                                    window binds -- why it is meaningless
                                                                       0 -> 0
    dhw_valid_accepted              both pages store "06:00-08:30"
                                    (null control)                     2 -> 2

  D6-02 (#172), instrumented: the schemas registered on hass.services by
  async_setup_entry, fed services.yaml's own `example:` values.
    manual_plan_example_passes      apply_manual_plan's examples pass its
                                    registered schema                  0 -> 1
    service_examples_failing        services whose documented examples fail
                                    their own registered schema        1 -> 0

The three trailing lines (thread_factor, load1, swapins) are the contract's
environment stamp; nothing here is a timing, so they gate nothing.
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

import asyncio  # noqa: E402
import json  # noqa: E402
import re  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from datetime import datetime, timedelta, timezone  # noqa: E402
from pathlib import Path  # noqa: E402

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT / "custom_components"))

import yaml  # noqa: E402
from harness import FakeEntry, FakeHass  # noqa: E402

import heatpump_optimizer as integration  # noqa: E402
from heatpump_optimizer import const  # noqa: E402
from heatpump_optimizer.config_flow import (  # noqa: E402
    HeatPumpOptimizerConfigFlow,
    HeatPumpOptimizerOptionsFlow,
)
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402
from heatpump_optimizer.dhw_schedule import hour_in_windows, parse_windows  # noqa: E402

PKG = ROOT / "custom_components" / "heatpump_optimizer"
STRINGS = json.loads((PKG / "strings.json").read_text())
ENTRY_DATA = {const.CONF_TIBBER_TOKEN: "x", const.CONF_WEATHER_ENTITY: "weather.home"}


def result(name: str, value, unit: str = "") -> None:
    print(f"RESULT {name}={value} {unit}".rstrip())


def _key(marker) -> str:
    return str(getattr(marker, "schema", marker))


def _render(text: str, placeholders: dict | None) -> str:
    """Substitute ``{name}`` the way the frontend's localize does."""
    placeholders = placeholders or {}
    return re.sub(
        r"\{(\w+)\}", lambda m: str(placeholders.get(m.group(1), m.group(0))), text
    )


def _options_flow(currency: str = "SEK") -> HeatPumpOptimizerOptionsFlow:
    flow = HeatPumpOptimizerOptionsFlow(FakeEntry(data=dict(ENTRY_DATA)))
    flow.hass = FakeHass()
    flow.hass.config.currency = currency
    return flow


def _setup_flow(currency: str = "SEK") -> HeatPumpOptimizerConfigFlow:
    flow = HeatPumpOptimizerConfigFlow()
    flow.hass = FakeHass()
    flow.hass.config.currency = currency
    return flow


def _submit(flow, step: str, overrides: dict) -> dict | str:
    """Render a page, fill its defaults, override, validate, submit.

    Returns the flow result, or the selector's rejection as a string when the
    schema itself refuses the payload -- which is how Home Assistant behaves:
    the selectors validate before the step handler ever sees the data.
    """
    handler = getattr(flow, f"async_step_{step}")
    form = asyncio.run(handler(None))
    schema = form["data_schema"]
    try:
        payload = schema({**schema({}), **overrides})
    except Exception as err:  # noqa: BLE001 - the rejection is the datum
        return f"selector: {err}"
    return asyncio.run(handler(payload))


def _accepted(res) -> bool:
    return isinstance(res, dict) and not res.get("errors")


# ---------------------------------------------------------------------------
# D4-04: currency
# ---------------------------------------------------------------------------
MONEY_FIELDS = {
    "tuning": (const.CONF_COMPRESSOR_REPLACEMENT_COST,),
    "grid": (const.CONF_GRID_FEE_FIXED, const.CONF_CONTRACT_FIXED_PRICE),
}

leaks: list[str] = []
units_following = 0
for step, money in MONEY_FIELDS.items():
    flow = _options_flow("EUR")
    form = asyncio.run(getattr(flow, f"async_step_{step}")(None))
    placeholders = form.get("description_placeholders")
    texts = STRINGS["options"]["step"][step]
    for marker, validator in form["data_schema"].schema.items():
        key = _key(marker)
        label = _render(texts.get("data", {}).get(key, ""), placeholders)
        helper = _render(texts.get("data_description", {}).get(key, ""), placeholders)
        unit = str((getattr(validator, "config", None) or {}).get("unit_of_measurement", ""))
        for kind, text in (("label", label), ("description", helper), ("unit", unit)):
            if "SEK" in text:
                leaks.append(f"{step}.{key}.{kind}")
        if key in money and unit.startswith("EUR"):
            units_following += 1

# The two Repairs notices, rendered from strings.json with the placeholders
# the coordinator actually passes, on an EUR instance.
eur_hass = FakeHass()
eur_hass.config.currency = "EUR"
steps = [datetime(2026, 1, 7, 12, 0, tzinfo=timezone.utc) + timedelta(minutes=15 * i) for i in range(8)]
coord = HeatPumpOptimizerCoordinator(
    eur_hass,
    FakeEntry(data={**ENTRY_DATA, "grid_fee_mode": "rules", "grid_fee_rules": "= 25"}),
)
coord._fee_series(steps)
coord._prices = [{"total": 1.2}]
coord._last_measured_cop = 2.4
coord._raise_cop_issue(3.0)
for domain, issue_id, kwargs in getattr(eur_hass, "issues", []):
    text = STRINGS["issues"][kwargs["translation_key"]]["description"]
    if "SEK" in _render(text, kwargs.get("translation_placeholders")):
        leaks.append(f"issue.{issue_id}")

result("currency_leaks_at_eur", len(leaks), "strings")
for leak in leaks:
    print(f"  leak: {leak}")
result("currency_units_following_hass", units_following, f"of {sum(len(v) for v in MONEY_FIELDS.values())} fields")

# ---------------------------------------------------------------------------
# D4-05: grid fee rules sign and magnitude
# ---------------------------------------------------------------------------
for name, spec in (
    ("grid_rules_negative_accepted", "= -0.25"),
    ("grid_rules_implausible_accepted", "= 25"),
    ("grid_rules_valid_accepted", "= 0.25"),
):
    res = _submit(
        _options_flow(),
        "grid",
        {const.CONF_GRID_FEE_MODE: "rules", const.CONF_GRID_FEE_RULES: spec},
    )
    result(name, int(_accepted(res)), f"(errors={res.get('errors') if isinstance(res, dict) else res})")

neg_hass = FakeHass()
neg = HeatPumpOptimizerCoordinator(
    neg_hass,
    FakeEntry(data={**ENTRY_DATA, "grid_fee_mode": "rules", "grid_fee_rules": "= -0.25"}),
)
neg_vec = neg._fee_series(steps)
result("grid_store_negative_notices", len(getattr(neg_hass, "issues", [])), "issues")
result("grid_store_negative_fee", float(neg_vec[0]), "per kWh")

# ---------------------------------------------------------------------------
# D4-07: day start / day end sliders
# ---------------------------------------------------------------------------
VALID_PAIRS = [(s, e) for s in range(0, 24) for e in range(1, 25) if s < e]


def _forbidden(schema) -> int:
    bounds = {}
    for marker, validator in schema.schema.items():
        key = _key(marker)
        if key in (const.CONF_DAY_START_HOUR, const.CONF_DAY_END_HOUR):
            cfg = validator.config
            bounds[key] = (cfg["min"], cfg["max"])
    s_lo, s_hi = bounds[const.CONF_DAY_START_HOUR]
    e_lo, e_hi = bounds[const.CONF_DAY_END_HOUR]
    return sum(
        1 for s, e in VALID_PAIRS if not (s_lo <= s <= s_hi and e_lo <= e <= e_hi)
    )


setup_form = asyncio.run(_setup_flow().async_step_temperature(None))
options_form = asyncio.run(_options_flow().async_step_comfort(None))
result("day_valid_schedules_forbidden_setup", _forbidden(setup_form["data_schema"]), f"of {len(VALID_PAIRS)}")
result("day_valid_schedules_forbidden_options", _forbidden(options_form["data_schema"]), f"of {len(VALID_PAIRS)}")

res = _submit(
    _options_flow(),
    "comfort",
    {const.CONF_DAY_START_HOUR: 10, const.CONF_DAY_END_HOUR: 10},
)
reachable = isinstance(res, dict) and res.get("errors") == {const.CONF_DAY_END_HOUR: "day_window_empty"}
result("day_window_empty_reachable", int(reachable), f"({res.get('errors') if isinstance(res, dict) else res})")

# ---------------------------------------------------------------------------
# D4-08: the one-minute hot-water window
# ---------------------------------------------------------------------------
ONE_MINUTE = "06:05-06:06"
VALID_WINDOWS = "06:00-08:30"


def _dhw_accepted(spec: str) -> int:
    setup_res = _submit(_setup_flow(), "dhw", {const.CONF_DHW_WINDOWS: spec})
    options_res = _submit(_options_flow(), "hot_water", {const.CONF_DHW_WINDOWS: spec})
    return int(_accepted(setup_res)) + int(_accepted(options_res))


result("dhw_one_minute_accepted", _dhw_accepted(ONE_MINUTE), "of 2 pages")
bound = sum(hour_in_windows(i / 4.0, parse_windows(ONE_MINUTE)) for i in range(96))
result("dhw_one_minute_steps_bound", bound, "of 96 step starts")
result("dhw_valid_accepted", _dhw_accepted(VALID_WINDOWS), "of 2 pages")

# ---------------------------------------------------------------------------
# D6-02: the documented service examples against the registered schemas
# ---------------------------------------------------------------------------
svc_hass = FakeHass()
svc_entry = FakeEntry(data=dict(ENTRY_DATA))
svc_hass.config_entries.entries.append(svc_entry)
asyncio.run(integration.async_setup_entry(svc_hass, svc_entry))
services = yaml.safe_load((PKG / "services.yaml").read_text())
failing: list[str] = []
manual_ok = 0
for name, spec in services.items():
    examples = {
        field: field_spec["example"]
        for field, field_spec in (spec.get("fields") or {}).items()
        if "example" in field_spec
    }
    if not examples:
        continue
    schema = svc_hass.services._schemas[(const.DOMAIN, name)]
    try:
        schema(dict(examples))
        if name == "apply_manual_plan":
            manual_ok = 1
    except Exception as err:  # noqa: BLE001 - the rejection is the datum
        failing.append(f"{name}: {type(err).__name__}: {str(err)[:80]}")
result("manual_plan_example_passes", manual_ok)
result("service_examples_failing", len(failing), "services")
for line in failing:
    print(f"  failing: {line}")

# ---------------------------------------------------------------------------
# environment stamp
# ---------------------------------------------------------------------------
thread = time.thread_time() or 1e-9
result("thread_factor", f"{time.process_time() / thread:.2f}")
result("load1", f"{os.getloadavg()[0]:.2f}")
swapins = 0
try:
    out = subprocess.run(["vm_stat"], capture_output=True, text=True, timeout=5).stdout
    m = re.search(r"Swapins:\s+(\d+)", out)
    swapins = int(m.group(1)) if m else 0
except Exception:  # noqa: BLE001 - not a macOS box
    pass
result("swapins", swapins)
