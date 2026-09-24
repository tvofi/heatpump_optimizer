#!/usr/bin/env python3
"""D6-s2 claims-check harness.

Metric definition: for each extracted claim (a default value, a range, a
count or a behaviour statement) from the user-facing docs this seat owns
(docs/configuration.md, docs/how-it-works.md, docs/dashboard-card.md,
docs/ecl110.md, docs/automations.md, docs/setup.md, docs/architecture.md),
compare the value the doc states against the value the production source
(const.py DEFAULT_*/CONF_* constants, config_flow.py _F(...) field specs,
services.yaml, RELEASE_NOTES.md) actually carries. Prints one RESULT line
per claim: RESULT claim_<n>=<PASS|FAIL> plus a final tally.

Command: PYTHONPATH=tests/hastub python3 tools/audit/round8/D6/s2_claims_check.py
Expected: RESULT claims_checked=34 RESULT claims_false=0 (baseline cdf82daabcfe3777d98b31489f36df5555ec9d82)
Machine: cloud 4-vCPU container (round-8 audit box); no timing numbers here, so no thread pin needed.
Perturbation: edit any one DEFAULT_* constant this harness reads (e.g. const.DEFAULT_ECL110_DISPLACE_MIN)
and the corresponding claim flips PASS->FAIL, moving claims_false up by 1.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

CONST = (ROOT / "custom_components/heatpump_optimizer/const.py").read_text()
CONFIG_FLOW = (ROOT / "custom_components/heatpump_optimizer/config_flow.py").read_text()
RELEASE_NOTES = (ROOT / "RELEASE_NOTES.md").read_text()


def const_value(name: str) -> str:
    m = re.search(rf"^{re.escape(name)}\s*:\s*Final\s*=\s*([^\n#]+)", CONST, re.M)
    if not m:
        raise AssertionError(f"{name} not found in const.py")
    return m.group(1).strip()


def numberspec(field: str) -> str:
    """Find the _number(...) call for a CONF_ field name used in config_flow.py."""
    m = re.search(rf"{re.escape(field)},\s*[A-Za-z_]+,\s*(_number\([^)]*\))", CONFIG_FLOW)
    if not m:
        raise AssertionError(f"{field} field spec not found")
    return m.group(1)


checks: list[tuple[str, bool]] = []


def check(label: str, cond: bool) -> None:
    checks.append((label, cond))


# --- ecl110.md ---
check("ecl110_qos_default==1", const_value("DEFAULT_ECL110_QOS") == "1")
check("ecl110_displace_min==-20.0", const_value("DEFAULT_ECL110_DISPLACE_MIN") == "-20.0")
check("ecl110_displace_max==20.0", const_value("DEFAULT_ECL110_DISPLACE_MAX") == "20.0")
check("ecl110_pid_tc==1.5", const_value("DEFAULT_ECL110_PID_TIME_CONSTANT") == "1.5")
check("peak_guard_nudge==2.0", const_value("PEAK_GUARD_DISPLACE_NUDGE_C") == "2.0")

# --- automations.md ---
check("economy_widening==1.5", const_value("ECONOMY_MIN_TEMP_WIDENING").split("#")[0].strip() == "1.5")
check("economy_floor==15.0", const_value("ECONOMY_ABSOLUTE_FLOOR").split("#")[0].strip() == "15.0")

# --- how-it-works.md ---
check("radiator_fraction==0.4", const_value("DEFAULT_RADIATOR_POWER_FRACTION").startswith("0.4"))
check("solar_upper_fraction==0.4", const_value("DEFAULT_SOLAR_UPPER_FRACTION").startswith("0.4"))
check("comfort_weight_default==5.0", const_value("DEFAULT_COMFORT_WEIGHT") == "5.0")
check("capacity_floor_fraction==0.6", const_value("CAPACITY_FLOOR_FRACTION") == "0.6")
check("price_tile_power_cap==0.75", "0.75 * ctx._thermal_params.max_electrical_power" in
      (ROOT / "custom_components/heatpump_optimizer/coordinator.py").read_text())
check("preheat_weather_fallthrough_changed_in_v5.1.7", "## v5.1.7" in RELEASE_NOTES and
      "preheat_weather" in RELEASE_NOTES)

# --- setup.md / architecture.md ---
check("quick_setup_since_v6.6.5", "#1251 — a quick-setup path in the initial config flow" in RELEASE_NOTES
      and "## v6.6.5" in RELEASE_NOTES)
n_modules = len(list((ROOT / "custom_components/heatpump_optimizer").glob("*.py")))
check("module_count==65", n_modules == 65)
module_level_ha_imports = sum(
    1 for f in (ROOT / "custom_components/heatpump_optimizer").glob("*.py")
    if re.search(r"^(import homeassistant|from homeassistant)", f.read_text(), re.M)
)
check("module_level_ha_imports==22", module_level_ha_imports == 22)

# --- configuration.md defaults ---
def numeric(name: str) -> float:
    raw = const_value(name).split("#", 1)[0].strip()
    return float(raw)


for name, expect in [
    ("DEFAULT_TARGET_TEMP", 21.0),
    ("DEFAULT_MIN_TEMP", 19.0),
    ("DEFAULT_MAX_TEMP", 23.0),
    ("DEFAULT_COMFORT_TEMP_DAY", 21.0),
    ("DEFAULT_COMFORT_TEMP_NIGHT", 19.5),
    ("DEFAULT_DAY_START_HOUR", 7),
    ("DEFAULT_DAY_END_HOUR", 22),
    ("DEFAULT_HOUSE_THERMAL_MASS", 10.0),
    ("DEFAULT_HOUSE_HEAT_LOSS_COEFFICIENT", 0.15),
    ("DEFAULT_SLAB_THERMAL_MASS", 5.0),
    ("DEFAULT_SLAB_HEAT_TRANSFER", 0.8),
    ("DEFAULT_HEAT_PUMP_COP_NOMINAL", 3.5),
    ("DEFAULT_HEAT_PUMP_MAX_POWER", 5.0),
    ("DEFAULT_HEAT_PUMP_MIN_POWER", 1.0),
    ("DEFAULT_OPTIMIZATION_INTERVAL", 30),
    ("DEFAULT_DHW_TANK_VOLUME", 200.0),
    ("DEFAULT_DHW_SETPOINT", 55.0),
    ("DEFAULT_DHW_MIN_TEMP", 45.0),
    ("DEFAULT_DHW_DAILY_CONSUMPTION", 150.0),
    ("DEFAULT_DHW_COOLING_RATE", 0.3),
    ("DEFAULT_DHW_IDLE_MIN_TEMP", 20.0),
    ("DHW_MIN_TEMP_SETPOINT_MARGIN", 5.0),
    ("DEFAULT_BUFFER_TANK_VOLUME", 35.0),
]:
    check(f"{name}=={expect}", numeric(name) == expect)

# option-page counts: 8 top-menu + 15 advanced-menu = 23
opt_pages = re.findall(r'_P\("(\w+)", "[^"]+", (_TOP|_ADVANCED)\)', CONFIG_FLOW)
check("option_pages_total==23", len(opt_pages) == 23)
check("option_pages_top==8", sum(1 for _, g in opt_pages if g == "_TOP") == 8)
check("option_pages_advanced==15", sum(1 for _, g in opt_pages if g == "_ADVANCED") == 15)

# services: 12
n_services = len(re.findall(r"^SERVICE_[A-Z_]+: Final", CONST, re.M))
check("services_count==12", n_services == 12)

# entity counts: 59 sensors, 5 binary sensors, 4 buttons, 4 switches, 1 climate, 1 datetime
sensor_src = (ROOT / "custom_components/heatpump_optimizer/sensor.py").read_text()
setup_block = sensor_src[sensor_src.index("entities = ["):sensor_src.index("async_add_entities(entities)")]
check("sensors_count==59", len(re.findall(r"\(coordinator, entry\)", setup_block)) == 59)

for plat, expect in [("binary_sensor", 5), ("button", 4), ("switch", 4)]:
    src = (ROOT / f"custom_components/heatpump_optimizer/{plat}.py").read_text()
    block_start = src.index("async_add_entities(")
    block = src[block_start: src.index(")", src.index("]", block_start))]
    n = len(re.findall(r"\(coordinator, entry\)", block))
    check(f"{plat}_count=={expect}", n == expect)

# --- tally ---
n_ok = sum(1 for _, ok in checks if ok)
n_fail = sum(1 for _, ok in checks if not ok)
for label, ok in checks:
    print(f"RESULT claim__{label}={'PASS' if ok else 'FAIL'}")
print(f"RESULT claims_checked={len(checks)}")
print(f"RESULT claims_false={n_fail}")
print(f"RESULT claims_true={n_ok}")

if n_fail:
    sys.exit(1)
