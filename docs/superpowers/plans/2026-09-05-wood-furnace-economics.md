# Wood furnace economics Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Advisory wood-vs-heat-pump price, a binary sensor, a Plan-tab banner, what-if wood slots, and a Wood lane for detected fires — without the live solver choosing wood.

**Architecture:** `wood_fuel.py` owns densities, SEK/kWh, readiness, and the cheaper-hour rule. Coordinator publishes `data["wood_fuel"]` and, on the shadow solve only, injects what-if liters as `external_heat_kw`. Config: `wood_furnace_enabled` hides the wood block. Card reads `data.wood_fuel`.

**Tech Stack:** Home Assistant custom component (config flow / coordinator / binary_sensor), Lovelace card (`heatpump-optimizer-card.js`, no build step), `tests/features.py` + `tests/config_flow_steps.py` + `tests/entities.py` + `tests/card.mjs` (`R.check` / `check`, not pytest).

**Spec:** `docs/superpowers/specs/2026-09-05-wood-furnace-economics-design.md`

## Global Constraints

- `claims-for:` stays `6.3.14`. Do not re-record value-bearing goldens.
- Do not raise `SOLVE_BUDGET_RATIO` or `SCENARIO_BUDGET_FACTOR`.
- Structure ratchet only moves down. Never re-record `cross_seam_fraction`. Re-measure at **this PR’s merge-base**. Pay `coordinator_loc` or stop and ask. Do not raise `coordinator_loc`, `max_class_loc`, `coordinator_attrs`, or `coordinator_methods` without the owner.
- Live `optimize()` / `_await_optimize` on the operational path do not receive what-if wood. What-if injection is `async_simulate` only.
- Never hand-edit `VERSION`, the manifest version, `RELEASE_NOTES.md` headings, or `CARD_VERSION` — `tools/release/stamp.py` only.
- Two PRs. **3L-G8** does not close the issue. **3L-G9** has `Closes #463` on its own line. Do not reuse #457 or #460. Do not `Closes #232` / `#234`.
- Gate lock `/tmp/hpo-gate.lock` if the select is `MODE: FULL` or names `tests/stress.py`. Default select is features / config_flow_steps / entities / card / structure — no lock.
- Three-dot diffs vs merge-base. `cp` backups for source mutation; restore and confirm md5.
- This repo’s tests are plain scripts, not pytest. Commands below are exact.
- Worktree under `~/wt/<branch>`. Never commit in `/Users/timmalmstrom/heatpump_optimizer`.

## Seat (do not skip)

**3L-G8** then **3L-G9**, after **3L-G7 (#460)**, before Wave 4. Do not start production while W3-G3 holds `coordinator.py`. Do not merge G8/G9 ahead of W3-G3 or 3L-G5 (#408).

| group | tasks | model | closes |
|---|---|---|---|
| **3L-G8** | 1–4 | Grok 4.6 extra high | no |
| **3L-G9** | 5–7 | Grok 4.6 extra high | `Closes #463` |

Cut each branch from `origin/main` **after** those seats. Re-measure structure at that merge-base.

## File map

| File | Responsibility |
|---|---|
| `custom_components/heatpump_optimizer/wood_fuel.py` | Densities, `useful_kwh_m3`, `wood_sek_per_kwh`, `wood_furnace_on`, `wood_fuel_ready`, `wood_cheaper`, `detected_wood_slots`, `wood_slots_to_kw` |
| `custom_components/heatpump_optimizer/const.py` | New CONF_* keys and defaults |
| `custom_components/heatpump_optimizer/thermal_model.py` | Gate `wood_tank_configured` / volume / coil on `wood_furnace_on` |
| `custom_components/heatpump_optimizer/coordinator.py` | `_wood_fuel_view`; gate `_external_heat_config.enabled`; `async_simulate` wood inject |
| `custom_components/heatpump_optimizer/config_flow.py` | Toggle + move detection off Learning |
| `custom_components/heatpump_optimizer/binary_sensor.py` | `WoodCheaperBinarySensor` |
| `custom_components/heatpump_optimizer/{strings.json,translations/en.json,translations/sv.json}` | Options + sensor + card keys |
| `custom_components/heatpump_optimizer/services.yaml` | `simulate_plan` wood fields |
| `custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js` | Banner, Wood lane, what-if wood section |
| `tests/features.py` | Math, ready, cheaper, view, what-if |
| `tests/config_flow_steps.py` | Toggle hide + infer |
| `tests/entities.py` | Sensor unavailable/on/off |
| `tests/card.mjs` | Banner + lane |
| `tests/claimed_drift.txt` | New `data[]` key paths |

---

### Task 1: `wood_fuel.py` math and readiness

**Files:**
- Create: `custom_components/heatpump_optimizer/wood_fuel.py`
- Modify: `custom_components/heatpump_optimizer/const.py` (keys only)
- Test: `tests/features.py` (new section immediately before `sys.exit(R.close("FEATURE CHECKS"))`)

**Interfaces:**
- Consumes: config dict keys from const
- Produces:
  - `WOOD_KWH_M3: dict[str, dict[str, float]]`
  - `useful_kwh_m3(wood_type: str, packing: str, efficiency: float) -> float`
  - `wood_sek_per_kwh(price_sek_m3: float, wood_type: str, packing: str, efficiency: float) -> float`
  - `liters_to_kwh(liters: float, wood_type: str, packing: str, efficiency: float) -> float`
  - `wood_furnace_inferred(config: dict) -> bool`
  - `wood_furnace_on(config: dict) -> bool`
  - `wood_fuel_ready(config: dict) -> bool`
  - `wood_cheaper(wood_sek: float, prices, cops, space_kw, dhw_kw, threshold: float = 0.05) -> bool`
  - `cheaper_hour_count(...) -> int`

- [ ] **Step 1: Write the failing checks**

Append before `sys.exit(R.close("FEATURE CHECKS"))` in `tests/features.py`:

```python
R.section("3L-G8 — wood fuel math")

from heatpump_optimizer.wood_fuel import (
    WOOD_KWH_M3 as _wf_table,
    cheaper_hour_count as _wf_count,
    liters_to_kwh as _wf_liters,
    useful_kwh_m3 as _wf_useful,
    wood_cheaper as _wf_cheaper,
    wood_fuel_ready as _wf_ready,
    wood_furnace_inferred as _wf_inferred,
    wood_furnace_on as _wf_on,
    wood_sek_per_kwh as _wf_sek,
)

R.check("birch packed is 1900 kWh/m3", _wf_table["birch"]["packed"] == 1900.0)
R.check("pine packed is 1500 kWh/m3", _wf_table["pine"]["packed"] == 1500.0)
R.check("mixed packed is 1700 kWh/m3", _wf_table["mixed"]["packed"] == 1700.0)
R.check(
    "loose is 0.60 of packed",
    _wf_table["birch"]["loose"] == 1140.0
    and _wf_table["pine"]["loose"] == 900.0
    and _wf_table["mixed"]["loose"] == 1020.0,
)
R.check(
    "useful kWh applies efficiency",
    abs(_wf_useful("birch", "packed", 75.0) - 1425.0) < 1e-9,
)
R.check(
    "SEK/kWh is price over useful",
    abs(_wf_sek(1425.0, "birch", "packed", 75.0) - 1.0) < 1e-9,
)
R.check(
    "50 L of that birch is 71.25 kWh",
    abs(_wf_liters(50.0, "birch", "packed", 75.0) - 71.25) < 1e-9,
)
R.check(
    "500 L volume alone does not infer a furnace",
    not _wf_inferred({"wood_tank_volume": 500.0}),
)
R.check(
    "a top probe infers on",
    _wf_inferred({"wood_tank_top_entity": "sensor.wood_top"}),
)
R.check(
    "explicit off wins over a probe",
    not _wf_on(
        {
            "wood_furnace_enabled": False,
            "wood_tank_top_entity": "sensor.wood_top",
        }
    ),
)
_wf_cfg = {
    "wood_furnace_enabled": True,
    "wood_tank_top_entity": "sensor.wood_top",
    "external_heat_detection_enabled": True,
    "wood_type": "mixed",
    "wood_packing": "packed",
    "wood_price_sek_m3": 800.0,
    "wood_furnace_efficiency": 75.0,
}
R.check("complete config is ready", _wf_ready(_wf_cfg))
_wf_no_price = dict(_wf_cfg, wood_price_sek_m3=0.0)
R.check("price 0 is not ready", not _wf_ready(_wf_no_price))
R.check(
    "idle plan is not cheaper",
    not _wf_cheaper(1.0, [2.0], [3.0], [0.0], [0.0]),
)
R.check(
    "one pump hour above 0.05 kW cheaper is on",
    _wf_cheaper(1.0, [4.0], [2.0], [0.2], [0.0]),
)
R.check(
    "that hour counts",
    _wf_count(1.0, [4.0], [2.0], [0.2], [0.0]) == 1,
)
```

- [ ] **Step 2: Run the checks and confirm they fail**

```bash
cd /Users/timmalmstrom/wt/<branch>
PYTHONPATH=tests/hastub python3 tests/features.py
```

Expected: FAIL on import of `wood_fuel` or the first missing name.

- [ ] **Step 3: Add const keys and `wood_fuel.py`**

In `const.py`, after the wood-tank block:

```python
CONF_WOOD_FURNACE_ENABLED: Final = "wood_furnace_enabled"
DEFAULT_WOOD_FURNACE_ENABLED: Final = False
CONF_WOOD_TYPE: Final = "wood_type"
CONF_WOOD_PACKING: Final = "wood_packing"
CONF_WOOD_PRICE_SEK_M3: Final = "wood_price_sek_m3"
CONF_WOOD_FURNACE_EFFICIENCY: Final = "wood_furnace_efficiency"
DEFAULT_WOOD_TYPE: Final = "mixed"
DEFAULT_WOOD_PACKING: Final = "packed"
DEFAULT_WOOD_FURNACE_EFFICIENCY: Final = 75.0
WOOD_TYPES: Final = ("birch", "pine", "mixed")
WOOD_PACKINGS: Final = ("packed", "loose")
```

Create `wood_fuel.py`:

```python
"""Firewood price and the cheaper-than-pump rule. Does not detect fires."""
from __future__ import annotations

from .const import (
    CONF_DHW_WOOD_COIL_ENABLED,
    CONF_EXTERNAL_HEAT_ENABLED,
    CONF_EXTERNAL_HEAT_ENTITY,
    CONF_WOOD_FURNACE_EFFICIENCY,
    CONF_WOOD_FURNACE_ENABLED,
    CONF_WOOD_PACKING,
    CONF_WOOD_PRICE_SEK_M3,
    CONF_WOOD_TANK_BOTTOM_ENTITY,
    CONF_WOOD_TANK_TOP_ENTITY,
    CONF_WOOD_TYPE,
)

WOOD_KWH_M3 = {
    "birch": {"packed": 1900.0, "loose": 1140.0},
    "pine": {"packed": 1500.0, "loose": 900.0},
    "mixed": {"packed": 1700.0, "loose": 1020.0},
}
PUMP_HOUR_KW = 0.05


def useful_kwh_m3(wood_type: str, packing: str, efficiency: float) -> float:
    return WOOD_KWH_M3[wood_type][packing] * float(efficiency) / 100.0


def wood_sek_per_kwh(
    price_sek_m3: float, wood_type: str, packing: str, efficiency: float
) -> float:
    useful = useful_kwh_m3(wood_type, packing, efficiency)
    if useful <= 0.0:
        raise ValueError("useful_kwh_m3 must be positive")
    return float(price_sek_m3) / useful


def liters_to_kwh(
    liters: float, wood_type: str, packing: str, efficiency: float
) -> float:
    return float(liters) / 1000.0 * useful_kwh_m3(wood_type, packing, efficiency)


def wood_furnace_inferred(config: dict) -> bool:
    if config.get(CONF_WOOD_TANK_TOP_ENTITY) or config.get(
        CONF_WOOD_TANK_BOTTOM_ENTITY
    ):
        return True
    if config.get(CONF_DHW_WOOD_COIL_ENABLED):
        return True
    if config.get(CONF_EXTERNAL_HEAT_ENABLED):
        return True
    if config.get(CONF_EXTERNAL_HEAT_ENTITY):
        return True
    return False


def wood_furnace_on(config: dict) -> bool:
    if CONF_WOOD_FURNACE_ENABLED in config:
        return bool(config[CONF_WOOD_FURNACE_ENABLED])
    return wood_furnace_inferred(config)


def wood_fuel_ready(config: dict) -> bool:
    if not wood_furnace_on(config):
        return False
    if not (
        config.get(CONF_WOOD_TANK_TOP_ENTITY)
        or config.get(CONF_WOOD_TANK_BOTTOM_ENTITY)
    ):
        return False
    if not (
        config.get(CONF_EXTERNAL_HEAT_ENABLED)
        or config.get(CONF_DHW_WOOD_COIL_ENABLED)
    ):
        return False
    if config.get(CONF_WOOD_TYPE) not in WOOD_KWH_M3:
        return False
    packing = config.get(CONF_WOOD_PACKING)
    if packing not in WOOD_KWH_M3["birch"]:
        return False
    try:
        price = float(config.get(CONF_WOOD_PRICE_SEK_M3) or 0.0)
        eff = float(config.get(CONF_WOOD_FURNACE_EFFICIENCY) or 0.0)
    except (TypeError, ValueError):
        return False
    return price > 0.0 and 10.0 <= eff <= 95.0


def cheaper_hour_count(
    wood_sek: float,
    prices,
    cops,
    space_kw,
    dhw_kw,
    threshold: float = PUMP_HOUR_KW,
) -> int:
    n = 0
    for price, cop, space, dhw in zip(prices, cops, space_kw, dhw_kw, strict=False):
        if max(float(space or 0.0), float(dhw or 0.0)) <= threshold:
            continue
        cop_f = float(cop or 0.0)
        if cop_f <= 0.0:
            continue
        if wood_sek < float(price) / cop_f:
            n += 1
    return n


def wood_cheaper(
    wood_sek: float,
    prices,
    cops,
    space_kw,
    dhw_kw,
    threshold: float = PUMP_HOUR_KW,
) -> bool:
    return cheaper_hour_count(
        wood_sek, prices, cops, space_kw, dhw_kw, threshold
    ) > 0
```

- [ ] **Step 4: Re-run features.py**

```bash
PYTHONPATH=tests/hastub python3 tests/features.py
```

Expected: PASS on the new section.

- [ ] **Step 5: Mutation**

```bash
cp custom_components/heatpump_optimizer/wood_fuel.py /tmp/wood_fuel.py.bak
# delete the `wood_sek < price/cop` comparison (return False)
PYTHONPATH=tests/hastub python3 tests/features.py
# "one pump hour above 0.05 kW cheaper is on" must FAIL
cp /tmp/wood_fuel.py.bak custom_components/heatpump_optimizer/wood_fuel.py
md5 custom_components/heatpump_optimizer/wood_fuel.py /tmp/wood_fuel.py.bak
```

- [ ] **Step 6: Commit**

```bash
git add custom_components/heatpump_optimizer/wood_fuel.py \
  custom_components/heatpump_optimizer/const.py tests/features.py
git commit -m "3L-G8: wood_fuel densities, SEK/kWh, readiness, cheaper hours."
```

---

### Task 2: Gate the model on the toggle

**Files:**
- Modify: `custom_components/heatpump_optimizer/thermal_model.py` (`from_config` wood block ~907–921)
- Modify: `custom_components/heatpump_optimizer/coordinator.py` (`_external_heat_config`)
- Test: `tests/features.py` (same section)

**Interfaces:**
- Consumes: `wood_furnace_on`
- Produces: `wood_tank_configured` false and detection `enabled` false when the toggle is off, even if probes/volume remain in the entry

- [ ] **Step 1: Write the failing checks**

```python
from heatpump_optimizer.thermal_model import ThermalParameters as _WfTP

_wf_off = {
    "wood_furnace_enabled": False,
    "wood_tank_top_entity": "sensor.wood_top",
    "wood_tank_volume": 500.0,
    "dhw_wood_coil_enabled": True,
}
_wf_params = _WfTP.from_config(_wf_off)
R.check(
    "toggle off means no wood tank even if a probe is stored",
    _wf_params.wood_tank_configured is False,
)
```

Also assert coordinator `_external_heat_config().enabled` is False when toggle is off and `external_heat_detection_enabled` is True. Build the smallest coordinator the existing features helpers already use (copy the pattern near other `_external_heat_config` checks in `tests/features.py`).

- [ ] **Step 2: Run — expect FAIL** (`wood_tank_configured` still True)

- [ ] **Step 3: Gate `from_config`**

```python
from .wood_fuel import wood_furnace_on

values["wood_tank_configured"] = wood_furnace_on(config) and bool(
    config.get(const.CONF_WOOD_TANK_TOP_ENTITY)
    or config.get(const.CONF_WOOD_TANK_BOTTOM_ENTITY)
)
if not wood_furnace_on(config):
    values["wood_tank_volume"] = 0.0
    values["dhw_wood_coil_enabled"] = False
else:
    values["wood_tank_volume"] = float(
        config.get(const.CONF_WOOD_TANK_VOLUME)
        or const.DEFAULT_WOOD_TANK_VOLUME
    )
    values["dhw_wood_coil_enabled"] = bool(
        config.get(
            const.CONF_DHW_WOOD_COIL_ENABLED,
            const.DEFAULT_DHW_WOOD_COIL_ENABLED,
        )
    )
```

In `_external_heat_config`, `enabled` is `wood_furnace_on(self._config) and` the existing enabled read.

- [ ] **Step 4: Re-run features.py — PASS**

- [ ] **Step 5: Commit**

```bash
git commit -m "3L-G8: toggle off is one-tank; 500 L is not a tank."
```

---

### Task 3: Building-page toggle; move detection off Learning

**Files:**
- Modify: `custom_components/heatpump_optimizer/config_flow.py` (`async_step_building`, `async_step_learning`)
- Modify: `custom_components/heatpump_optimizer/strings.json`
- Modify: `custom_components/heatpump_optimizer/translations/en.json`
- Modify: `custom_components/heatpump_optimizer/translations/sv.json`
- Test: `tests/config_flow_steps.py`

**Interfaces:**
- Consumes: `wood_furnace_on`, `wood_furnace_inferred`
- Produces: Building schema is toggle-only when off; full wood block when on. Learning schema has no `external_heat_*` keys.

- [ ] **Step 1: Write the failing options-flow checks**

Follow the existing `tests/config_flow_steps.py` harness (it already drives options pages). Add:

- Building with empty config: schema has `wood_furnace_enabled`, does **not** have `wood_tank_top_entity` or `wood_price_sek_m3`.
- Building with `wood_tank_top_entity` set and no `wood_furnace_enabled` key: schema includes the wood block (infer on).
- Building with only `wood_tank_volume: 500`: schema is toggle-only.
- After submit `wood_furnace_enabled: True`, next show includes probes, volume, coil, detection, flue, min-rise, decay, type, packing, price, efficiency.
- Learning schema does not list `external_heat_detection_enabled`.

- [ ] **Step 2: Run `PYTHONPATH=tests/hastub python3 tests/config_flow_steps.py` — FAIL**

- [ ] **Step 3: Implement**

`async_step_building`: always include `wood_furnace_enabled`. Compute `show_wood = wood_furnace_on({**current, **(user_input or {})})` after applying infer when the key is absent. If `show_wood`, append the existing wood-tank fields **plus** the four detection fields moved from Learning **plus** type / packing / price / efficiency (`_select(WOOD_TYPES)`, `_select(WOOD_PACKINGS)`, `_number` for price 0–10000 SEK/m³, slider 10–95 for efficiency, defaults mixed / packed / 75, price omitted so empty).

On save, persist `wood_furnace_enabled` explicitly (inferred True becomes a stored True on first Building save of an existing wood install). Do not write inferred False onto entries that never opened Building.

`async_step_learning`: delete the four `external_heat_*` schema entries. Keep the clearable-entity wipe for `CONF_EXTERNAL_HEAT_ENTITY` only if that key can still arrive (it should not).

Copy the existing en/sv/strings data_descriptions for the moved keys; add:

- `wood_furnace_enabled`: "Wood furnace" / "Vedpanna"
- `wood_type`, `wood_packing`, `wood_price_sek_m3`, `wood_furnace_efficiency` (en + sv)

- [ ] **Step 4: Re-run config_flow_steps.py — PASS**

- [ ] **Step 5: Commit**

```bash
git commit -m "3L-G8: wood-furnace toggle hides the wood block; detection leaves Learning."
```

---

### Task 4: Publish `data["wood_fuel"]` and the binary sensor

**Files:**
- Modify: `custom_components/heatpump_optimizer/coordinator.py` (`_wood_fuel_view`, add to `_build_data_dict`)
- Modify: `custom_components/heatpump_optimizer/binary_sensor.py`
- Modify: translations + `icons.json`
- Modify: `tests/entities.py` holes list (pin new attribute names)
- Test: `tests/features.py`, `tests/entities.py`

**Interfaces:**
- Consumes: `wood_fuel_ready`, `wood_sek_per_kwh`, `wood_cheaper`, `cheaper_hour_count`, last plan’s `space_power` / `dhw_power` / prices / outdoor, `compute_cop`, `_external_heat.suppressing`, `forecast_free_heat`
- Produces: `data["wood_fuel"]` as in the spec; `WoodCheaperBinarySensor`

`_wood_fuel_view` — a new method grows `coordinator_methods`. **Pay** (extract a helper into `wood_fuel.py` named `build_wood_fuel_view(...)` so the coordinator method is a thin caller) or stop and ask. Prefer the helper:

```python
def build_wood_fuel_view(
    config: dict,
    *,
    prices: list[float],
    outdoor: list[float],
    space_kw: list[float],
    dhw_kw: list[float],
    cop_at,
    timestamps: list,
    forecast_kw: list[float],
    suppressing: bool,
) -> dict:
    """Ready/cheaper/slots. cheaper is False when not ready."""
```

`detected_wood_slots(timestamps, forecast_kw) -> list[dict]`: merge consecutive steps with `forecast_kw > 0` into `{start, end, source: "detected"}`. Empty when not suppressing.

Sensor:

```python
class WoodCheaperBinarySensor(_OptimizerBinarySensorBase):
    def __init__(self, coordinator, entry) -> None:
        super().__init__(coordinator, entry, "wood_cheaper", "wood_cheaper")

    @property
    def available(self) -> bool:
        fuel = self._data().get("wood_fuel") or {}
        return bool(fuel.get("ready"))

    @property
    def is_on(self) -> bool:
        fuel = self._data().get("wood_fuel") or {}
        return bool(fuel.get("cheaper"))

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        fuel = self._data().get("wood_fuel") or {}
        return {
            "sek_per_kwh": fuel.get("sek_per_kwh"),
            "cheaper_hour_count": fuel.get("cheaper_hour_count"),
        }
```

Register it in `async_setup_entry`. No device class.

- [ ] **Step 1: Failing features + entities checks** — not ready → sensor unavailable; ready + one cheaper hour → on; ready + idle plan → off; `data["wood_fuel"]["cheaper"]` is False when not ready.

- [ ] **Step 2: Run — FAIL**

- [ ] **Step 3: Implement helper + view + sensor + translations** (`wood_cheaper` name: "Wood cheaper than heat pump" / "Ved billigare än värmepump")

- [ ] **Step 4: Claim new `data[]` keys** (`wood_fuel.ready`, `wood_fuel.cheaper`, …) in `tests/claimed_drift.txt` as `name # reason` (`claims-for: 6.3.14`). `golden.py --record --only` only for **new key paths**, not value-bearing goldens.

- [ ] **Step 5: `PYTHONPATH=tests/hastub python3 tests/features.py` and `python3 tests/entities.py` — PASS**

- [ ] **Step 6: Mutation** — `cp` coordinator; delete the `data.update` of the wood view; features “ready publishes cheaper” check FAIL; restore; md5 match.

- [ ] **Step 7: `python3 tests/structure.py`** — pay if `coordinator_loc` / `coordinator_methods` moved up; do not raise.

- [ ] **Step 8: Commit**

```bash
git commit -m "3L-G8: publish wood_fuel and WoodCheaperBinarySensor."
```

G8 PR: title `3L-G8: wood furnace config, price, cheaper sensor (#463)`. Body names the measured SHA. **Do not** put `Closes #463` on this PR. Comment the PR URL on #463.

---

### Task 5: What-if wood slots (3L-G9)

**Files:**
- Modify: `custom_components/heatpump_optimizer/wood_fuel.py` (`wood_slots_to_kw`)
- Modify: `custom_components/heatpump_optimizer/coordinator.py` (`async_simulate`)
- Modify: `custom_components/heatpump_optimizer/services.yaml` (`simulate_plan` fields)
- Test: `tests/features.py`

**Interfaces:**
- Consumes: overrides `wood_slots` (`[{start, end, liters}]`), optional `wood_type`, `wood_packing`, `wood_price_sek_m3`, `wood_furnace_efficiency`
- Produces: shadow `external_heat_kw` for those hours; payload `wood_sek`, `cost_delta` includes wood SEK; overrides are not written to the config entry

```python
def wood_slots_to_kw(
    slots: list[dict],
    timestamps: list,
    dt_hours: float,
    wood_type: str,
    packing: str,
    efficiency: float,
) -> list[float]:
    """kW-thermal per step. liters<=0 or hours<=0 skipped (caller may refuse)."""
```

`kW = liters_to_kwh(...) / slot_hours` on steps overlapping `[start, end)`.

In `async_simulate`, after the existing scratch solve inputs are assembled and **before** `_await_optimize`:

- If `wood_slots` in overrides: validate each slot (`liters > 0`, `end > start`); else return `{"error": "invalid_wood_slots", "rate_limited": False}`.
- Fuel params = override if present else config. If still not computable, return `{"error": "wood_fuel_not_ready", "rate_limited": False}`.
- `ext = wood_slots_to_kw(...)`.
- Pass `external_heat_kw=numpy.array(ext)` into `_await_optimize` (add the kwarg next to the other inherited inputs). Do **not** pass this on `async_run_optimization`.
- `wood_sek = price_sek_m3 * sum(liters)/1000`.
- `cost_delta` / `simulated_cost` add `wood_sek` (electricity delta stays the solve’s `predicted_cost` difference; published `cost_delta = elec_delta + wood_sek`).
- `payload["wood_sek"] = round(wood_sek, 2)`.
- Confirm `self._config` is unchanged after the call (identity of type/packing/price/efficiency).

- [ ] **Step 1: Failing checks** — inject path used; SEK adds wood; config keys unchanged; liters 0 → error.

- [ ] **Step 2: Run — FAIL**

- [ ] **Step 3: Implement**

- [ ] **Step 4: Mutation** — `cp` coordinator; force `external_heat_kw=None` in the simulate call; inject check FAIL; restore; md5 match.

- [ ] **Step 5: Commit**

```bash
git commit -m "3L-G9: what-if wood slots inject shadow external_heat_kw only."
```

---

### Task 6: Plan banner and Wood lane

**Files:**
- Modify: `custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js`
- Modify: en/sv strings already in the card’s `I18N` object (top of the file)
- Test: `tests/card.mjs`

**Interfaces:**
- Consumes: `data.wood_fuel.cheaper`, `data.wood_fuel.slots`
- Produces: banner above the chart; third display lane `wood` (not in `laneSpecs()` editor list — not pinable)

Keys:

```javascript
"wood.alert": "Burning wood is cheaper than at least one remaining heat-pump hour.",
"slots.lane_wood": "Wood",
"series.wood_slots": "Wood fire",
"whatif.wood": "Wood fire",
"whatif.wood_liters": "Liters",
"whatif.add_wood_slot": "Add a wood slot",
```

Swedish counterparts in the `sv` map.

Banner: if `this.plan.attr` / coordinator data `wood_fuel.cheaper`, render a `div.wood-alert` above the chart. Not dismissible.

Display lane: draw `wood_fuel.slots` the same way space/DHW slots are drawn. `laneSpecs()` stays two channels. What-if wood editor is a new `wi-section` under Today's slots, shown when `wood_fuel` exists and the toggle is on (`wood_fuel.ready` or `wood_furnace` published — if only `ready` is false for missing price, still show the section when `data.wood_fuel` is present and `wood_furnace_enabled` is on; publish `wood_fuel.show_whatif: wood_furnace_on(config)` for this).

What-if submit includes `wood_slots` and optional fuel overrides from the draft. Draft fields do not write HA config.

- [ ] **Step 1: card.mjs checks** — banner present when `cheaper`; absent when not; Wood lane renders one detected slot; `laneSpecs` length still 2.

- [ ] **Step 2: Run `node tests/card.mjs` — FAIL**

- [ ] **Step 3: Implement**

- [ ] **Step 4: Re-run card.mjs — PASS**

- [ ] **Step 5: Commit**

```bash
git commit -m "3L-G9: Plan wood alert, Wood lane, what-if wood editor."
```

---

### Task 7: Structure, claims, wrap-up (3L-G9)

**Files:**
- Modify: `tests/structure_budgets.json` only if a metric **improved**
- Modify: `tests/claimed_drift.txt` if G9 added keys (`wood_fuel.slots`, `wood_fuel.show_whatif`)

- [ ] **Step 1:** `python3 tests/structure.py` at this PR’s merge-base vs HEAD. Pay or ask. Do not raise.

- [ ] **Step 2:** `GOLDEN_MODE=drift GOLDEN_REF=$(git merge-base origin/main HEAD) PYTHONPATH=tests/hastub python3 tests/env_drift.py --fixtures` — empty unexpected claims.

- [ ] **Step 3:** Gate select; take `/tmp/hpo-gate.lock` only if `MODE: FULL` or `tests/stress.py`.

- [ ] **Step 4:** Open PR. Title `3L-G9: wood alert, Wood lane, what-if slots (#463)`. Body: measured SHA, three-dot vs `origin/main`. **`Closes #463` on its own line.** Comment URL + SHA on #463.

---

## Self-review

| Spec requirement | Task |
|---|---|
| Densities / SEK/kWh / liters | 1 |
| Cheaper-hour rule, 0.05 kW, plan price / COP | 1, 4 |
| Toggle default off; 500 L is not a tank | 2, 3 |
| Infer-on from probe/coil/detection/flue | 1, 3 |
| Detection leaves Learning | 3 |
| Sensor unavailable until ready | 4 |
| `data.wood_fuel`; cheaper false when not ready | 4 |
| Live slots = suppressing + fade | 4 |
| What-if inject shadow only; SEK = elec delta + wood | 5 |
| Banner + Wood lane; not pinable | 6 |
| No live solver wood; no store; claims 6.3.14 | Global + 7 |
| G8 does not close; G9 closes #463 | 4, 7 |
