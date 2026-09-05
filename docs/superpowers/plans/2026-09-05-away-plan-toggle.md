# Away Plan-page toggle Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Plan-tab Away toggle and optional return datetime, written only through `set_away` into a coordinator store, with published switch and datetime entities and no user helpers.

**Architecture:** `away.py` owns `expire_override`, helper migration, and resolve-with-override. Coordinator persists `{active, return_time}`. Card, switch, and datetime call `set_away`. Person/calendar remain optional when the switch is off.

**Tech Stack:** Home Assistant custom component (Store, config flow, switch, new datetime platform, services), Lovelace card (`heatpump-optimizer-card.js`, no build step), `tests/features.py` + `tests/config_flow_steps.py` + `tests/entities.py` + `tests/card.mjs` (`R.check` / `check`, not pytest).

**Spec:** `docs/superpowers/specs/2026-09-05-away-plan-toggle-design.md`

## Global Constraints

- `claims-for:` stays `6.3.14`. Do not re-record value-bearing goldens.
- Do not raise `SOLVE_BUDGET_RATIO` or `SCENARIO_BUDGET_FACTOR`.
- Structure ratchet only moves down. Never re-record `cross_seam_fraction`. Re-measure at **this PR’s merge-base**. Pay `coordinator_loc` or stop and ask. Do not raise `coordinator_loc`, `max_class_loc`, `coordinator_attrs`, or `coordinator_methods` without the owner.
- Never hand-edit `VERSION`, the manifest version, `RELEASE_NOTES.md` headings, or `CARD_VERSION` — `tools/release/stamp.py` only.
- One PR. `Closes #465` on its own line. Do not reuse #457, #460, or #463. Do not `Closes #232` / `#234`.
- Gate lock `/tmp/hpo-gate.lock` if the select is `MODE: FULL` or names `tests/stress.py`. Default select is features / config_flow_steps / entities / card / structure — no lock.
- Three-dot diffs vs merge-base. `cp` backups for source mutation; restore and confirm md5.
- This repo’s tests are plain scripts, not pytest. Commands below are exact.
- Worktree under `~/wt/<branch>`. Never commit in `/Users/timmalmstrom/heatpump_optimizer`.
- Do not start production while W3-G3 or 3L-G8/G9 hold `coordinator.py` or the card. Cut the branch from `origin/main` after those seats. Re-measure structure at that merge-base.

## Seat (do not skip)

**3L-G10**, after **3L-G9 (#463)**, before Wave 4.

| group | tasks | model | closes |
|---|---|---|---|
| **3L-G10** | 1–5 | Grok 4.6 extra high | `Closes #465` |

## File map

| File | Responsibility |
|---|---|
| `custom_components/heatpump_optimizer/away.py` | `expire_override`, `migrate_helper_override`, `resolve` override kwargs; drop `AwayConfig.enabled` |
| `custom_components/heatpump_optimizer/coordinator.py` | Store, `async_set_away`, expire-then-resolve, publish override keys, one-shot helper migration |
| `custom_components/heatpump_optimizer/services.py` | `handle_set_away`, schema |
| `custom_components/heatpump_optimizer/services.yaml` | `set_away` fields |
| `custom_components/heatpump_optimizer/const.py` | `SERVICE_SET_AWAY` |
| `custom_components/heatpump_optimizer/switch.py` | `AwaySwitch` |
| `custom_components/heatpump_optimizer/datetime.py` | `AwayReturnDateTime` (new platform) |
| `custom_components/heatpump_optimizer/__init__.py` | `Platform.DATETIME` |
| `custom_components/heatpump_optimizer/config_flow.py` | Slim Away page |
| `custom_components/heatpump_optimizer/{strings.json,translations/en.json,translations/sv.json,icons.json}` | Service, switch, datetime, card keys |
| `custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js` | Plan strip |
| `tests/features.py` | expire, resolve, migrate |
| `tests/config_flow_steps.py` | Slim Away page |
| `tests/entities.py` | Switch + datetime |
| `tests/card.mjs` | Plan strip |
| `tests/golden/claimed_drift.txt` | New `data[]` key paths |
| `tests/golden/coord_*.json` | Additive override keys |
| `tests/golden/config_flow.json` | Slim Away schema |

---

### Task 1: Store, expire, resolve override

**Files:**
- Modify: `custom_components/heatpump_optimizer/away.py`
- Modify: `custom_components/heatpump_optimizer/coordinator.py` (store + `async_set_away` + `_resolve_away`)
- Modify: `custom_components/heatpump_optimizer/const.py` (`SERVICE_SET_AWAY` only)
- Modify: `custom_components/heatpump_optimizer/services.py`, `services.yaml`
- Test: `tests/features.py` (Item 13 section)

**Interfaces:**
- Consumes: existing `AwayConfig` temperatures + optional `presence_entity`; `_parse_return_time`; `interpret_presence`; `estimate_recovery_hours`
- Produces:
  - `expire_override(active: bool, return_time: datetime | None, now: datetime) -> tuple[bool, datetime | None]`
  - `migrate_helper_override(presence_entity, presence_raw, presence_attributes, return_raw) -> dict` with keys `active`, `return_time` (iso or None), `drop_presence`
  - `resolve(..., override_active: bool = False, override_return_time: datetime | None = None)`
  - `AwayConfig` without `enabled` (and without `return_entity`)
  - `HeatPumpOptimizerCoordinator.async_set_away(active: bool | None = None, return_time: datetime | None | str | object = OMIT) -> None`
  - Store payload `{"active": bool, "return_time": iso | null, "migrated_helpers": bool}`
  - `data["away_override_active"]`, `data["away_override_return_time"]`

- [ ] **Step 1: Write the failing checks**

In `tests/features.py`, in the Item 13 section, **replace** the `disabled means the feature cannot cost anything` check and add:

```python
from datetime import datetime, timedelta, timezone

_now = datetime(2026, 9, 5, 12, 0, tzinfo=timezone.utc)
_past = _now - timedelta(hours=1)
_future = _now + timedelta(hours=8)

R.check(
    "a past return expires the override",
    away_mode.expire_override(True, _past, _now) == (False, None),
)
R.check(
    "a future return leaves the override",
    away_mode.expire_override(True, _future, _now) == (True, _future),
)
R.check(
    "no return time does not expire",
    away_mode.expire_override(True, None, _now) == (True, None),
)

_person_home = away_mode.resolve(
    away_mode.AwayConfig(presence_entity="person.alice", away_temperature=16.0),
    now=_now,
    presence_raw="home",
    presence_attributes=None,
    return_raw=None,
    comfort_temp=21.0,
    model=_away_model,
    thermal_state=_away_house(),
    outdoor_temp=0.0,
    override_active=True,
    override_return_time=_future,
)
R.check("the service override wins over a person at home", _person_home.active)
R.check("override source is service", _person_home.source == "service")

_person_only = away_mode.resolve(
    away_mode.AwayConfig(presence_entity="person.alice", away_temperature=16.0),
    now=_now,
    presence_raw="not_home",
    presence_attributes=None,
    return_raw=None,
    comfort_temp=21.0,
    model=_away_model,
    thermal_state=_away_house(),
    outdoor_temp=0.0,
    override_active=False,
    override_return_time=None,
)
R.check("person-away still works when the switch is off", _person_only.active)
R.check(
    "person-away source is the person entity",
    _person_only.source == "person.alice",
)

_mig = away_mode.migrate_helper_override(
    "input_boolean.holiday", "on", None, _future.isoformat()
)
R.check("boolean-on migrates to active", _mig["active"] is True)
R.check("boolean-on drops the presence key", _mig["drop_presence"] is True)
R.check("return helper is copied", _mig["return_time"] == _future.isoformat())
_mig_person = away_mode.migrate_helper_override(
    "person.alice", "not_home", None, None
)
R.check("a person id is not dropped", _mig_person["drop_presence"] is False)
R.check("a person id does not force the switch on", _mig_person["active"] is False)
```

Also update every `AwayConfig(enabled=True, ...)` / `AwayConfig(enabled=False, ...)` constructor in this file: drop `enabled`. The old disabled check is deleted, not rewritten.

- [ ] **Step 2: Run the Item 13 checks and confirm they fail**

Run: `PYTHONPATH=tests/hastub python3 tests/features.py` (or the smallest invocation this repo supports that still loads Item 13).

Expected: FAIL — `expire_override` / `migrate_helper_override` / unexpected `enabled` / missing `override_active`.

- [ ] **Step 3: Implement**

`away.py`:

```python
def expire_override(active, return_time, now):
    if active and return_time is not None and now >= return_time:
        return False, None
    return active, return_time


def migrate_helper_override(
    presence_entity, presence_raw, presence_attributes, return_raw
):
    drop_presence = bool(
        presence_entity and str(presence_entity).startswith("input_boolean.")
    )
    active = False
    if drop_presence:
        active = interpret_presence(
            presence_raw, presence_entity, presence_attributes
        ) is True
    parsed = _parse_return_time(return_raw)
    return {
        "active": active,
        "return_time": parsed.isoformat() if parsed else None,
        "drop_presence": drop_presence,
    }
```

Drop `enabled` and `return_entity` from `AwayConfig`. In `resolve()`, remove the `if not config.enabled: return` gate. After building the empty state, if `override_active` (already expired by the caller): set `active`, `source="service"`, `target_temperature`, `dhw_min_temperature`, then apply return-time / recovery from `override_return_time` (same block as today’s `return_raw`). Elif existing presence path; if that path is away and `return_raw` is empty, use `override_return_time` as the return.

Coordinator: new Store `f"{DOMAIN}_{entry.entry_id}_away"`. Load on setup next to the manual-plan load. `async_set_away` is the only writer; persist after every change. `_resolve_away`: expire, persist if changed, then `resolve(..., override_active=..., override_return_time=...)`. After `as_dict()`, also publish `away_override_active` and `away_override_return_time`. One-shot: if store lacks `migrated_helpers`, run `migrate_helper_override` against current config + entity states, apply, drop `CONF_AWAY_RETURN_ENTITY` and a boolean presence key via `async_update_entry` options, set `migrated_helpers`. Ignore `CONF_AWAY_ENABLED`. `_away_config()` no longer reads `enabled` or `return_entity`.

Service: `SERVICE_SET_AWAY = "set_away"`. Schema requires at least one of `active` (bool) or `return_time` (string, empty allowed). `handle_set_away` calls `coord.async_set_away`. Register in `async_register_services`. Add `services.yaml` fields matching `set_mode` style.

- [ ] **Step 4: Re-run features Item 13 — pass**

- [ ] **Step 5: Mutation**

`cp` `away.py`. Delete the `now >= return_time` comparison inside `expire_override` (always return `(active, return_time)`). The past-return check must FAIL. Restore. md5 must match.

- [ ] **Step 6: Commit**

```bash
git add custom_components/heatpump_optimizer/away.py \
  custom_components/heatpump_optimizer/coordinator.py \
  custom_components/heatpump_optimizer/const.py \
  custom_components/heatpump_optimizer/services.py \
  custom_components/heatpump_optimizer/services.yaml \
  tests/features.py
git commit -m "3L-G10: persist away override and expire it at return."
```

---

### Task 2: Switch and datetime entities

**Files:**
- Modify: `custom_components/heatpump_optimizer/switch.py`
- Create: `custom_components/heatpump_optimizer/datetime.py`
- Modify: `custom_components/heatpump_optimizer/__init__.py` (`PLATFORM_LIST`)
- Modify: `strings.json`, `translations/en.json`, `translations/sv.json`, `icons.json`
- Test: `tests/entities.py`

**Interfaces:**
- Consumes: `coordinator.data["away_override_active"]`, `away_override_return_time`; `async_set_away`
- Produces: `AwaySwitch` object id `switch.heat_pump_optimizer_away`; `AwayReturnDateTime` object id `datetime.heat_pump_optimizer_away_return`

- [ ] **Step 1: Write the failing entity checks**

Next to the existing optimizer switch checks in `tests/entities.py`. The current `the switch platform adds exactly one entity` check becomes **two**. Add:

```python
R.check("the switch platform adds the optimizer and away switches", len(switches) == 2)
away_sw = next(s for s in switches if getattr(s, "entity_id", "") == "switch.heat_pump_optimizer_away")
R.check("the away switch pins today's object id", away_sw.entity_id == "switch.heat_pump_optimizer_away")
R.check("the away switch is off when the override is off", not away_sw.is_on)

from custom_components.heatpump_optimizer import datetime as datetime_mod
dt_entities = collect(datetime_mod)
R.check("the datetime platform adds exactly one entity", len(dt_entities) == 1)
away_dt = dt_entities[0]
R.check(
    "the return datetime pins today's object id",
    away_dt.entity_id == "datetime.heat_pump_optimizer_away_return",
)
```

`FakeCoordinator` used by switch tests must grow `async_set_away` (record calls) and default data keys `away_override_active=False`, `away_override_return_time=None`.

- [ ] **Step 2: Run `PYTHONPATH=tests/hastub python3 tests/entities.py` — FAIL** (one switch, no datetime module)

- [ ] **Step 3: Implement**

`AwaySwitch(HeatPumpOptimizerEntity, SwitchEntity)`: `translation_key = "away"`, `entity_id = "switch.heat_pump_optimizer_away"`, unique_id `{entry_id}_away`. `is_on` from `data["away_override_active"]`. `async_turn_on/off` call `coordinator.async_set_away(active=True/False)`.

`datetime.py`: `PARALLEL_UPDATES = 1`. `AwayReturnDateTime` using HA `DateTimeEntity`. `translation_key = "away_return"`, `entity_id = "datetime.heat_pump_optimizer_away_return"`, unique_id `{entry_id}_away_return`. `native_value` parses `away_override_return_time`. `async_set_value` calls `async_set_away(return_time=value)`.

`PLATFORM_LIST` append `Platform.DATETIME`.

Translations: switch `away` name “Away” / “Borta”; datetime `away_return` “Expected return” / “Förväntad hemkomst”. Service `set_away` name + field labels. Icons: `mdi:walk` / `mdi:calendar-end` (match existing away_mode icon language).

Add `AwaySwitch` and `AwayReturnDateTime` to any entity-class rosters in `entities.py` that enumerate platforms (the `OptimizerEnableSwitch` frozenset and the platform tuple near the file’s sweep).

- [ ] **Step 4: Re-run `tests/entities.py` — PASS**

- [ ] **Step 5: Commit**

```bash
git add custom_components/heatpump_optimizer/switch.py \
  custom_components/heatpump_optimizer/datetime.py \
  custom_components/heatpump_optimizer/__init__.py \
  custom_components/heatpump_optimizer/strings.json \
  custom_components/heatpump_optimizer/translations \
  custom_components/heatpump_optimizer/icons.json \
  tests/entities.py
git commit -m "3L-G10: publish away switch and return datetime."
```

---

### Task 3: Config flow slim + golden keys

**Files:**
- Modify: `custom_components/heatpump_optimizer/config_flow.py` (`async_step_away`)
- Modify: `tests/config_flow_steps.py` (`AWAY_ANSWERS`, `opt_away`)
- Modify: `tests/golden/config_flow.json`
- Modify: `tests/golden/coord_minimal.json`, `coord_dhw.json`, `coord_two_zone.json`, `coord_grid_fee.json`, `coord_all_features.json`
- Modify: `tests/golden/claimed_drift.txt`
- Modify: any `tests/golden.py` / `tests/entities.py` option blobs that still set `away_enabled` or `away_return_entity` as required

**Interfaces:**
- Consumes: Task 1 store migration
- Produces: Away form without `away_enabled` / `away_return_entity`; presence selector domains `person`, `device_tracker`, `calendar`, `binary_sensor`

- [ ] **Step 1: Write the failing flow checks**

In `tests/config_flow_steps.py` `opt_away`:

```python
check(
    "opt_away",
    "happy",
    "the away page saves temperatures and keeps an optional person",
    shows_menu(result, "init")
    and entry.options.get(const.CONF_AWAY_TEMPERATURE) == 17.0
    and entry.options.get(const.CONF_AWAY_PRESENCE_ENTITY) == "person.home"
    and const.CONF_AWAY_ENABLED not in (await flow.async_step_away(None)).get("data_schema", vol.Schema({})).schema
    if False else True,
)
```

Do not use that `if False` stub. Instead: after `await flow.async_step_away(None)`, inspect `flow` / the shown schema the same way neighbouring pages do, and check:

```python
shown = {str(k) for k in result["data_schema"].schema}
# exact membership test used by this file for other pages — adapt to that helper
"away_enabled" not in shown
"away_return_entity" not in shown
```

Drop `CONF_AWAY_ENABLED` from `AWAY_ANSWERS`. Keep `CONF_AWAY_PRESENCE_ENTITY: "person.home"` and the two temperatures. Change `opt_away` so it no longer asserts `CONF_AWAY_RETURN_ENTITY is None` as a saved empty slot — the key is absent.

- [ ] **Step 2: Run `PYTHONPATH=tests/hastub python3 tests/config_flow_steps.py` — FAIL**

- [ ] **Step 3: Slim `async_step_away`**

Remove `CONF_AWAY_ENABLED` and `CONF_AWAY_RETURN_ENTITY` from the schema and from the empty-entity cleanup loop (presence only). Presence selector domains: `["person", "device_tracker", "calendar", "binary_sensor"]`. Update `strings.json` / translations: delete or stop referencing the removed field labels; presence description no longer mentions a holiday toggle helper.

Update `tests/golden/config_flow.json` away page to the slimmer keys (this is the options-schema snapshot, not a value-bearing plan golden).

Add to each `tests/golden/coord_*.json`:

```json
"away_override_active": false,
"away_override_return_time": null
```

`tests/golden/claimed_drift.txt` (note: reason after `#`, never `--`):

```
# claims-for: 6.3.14
coord_minimal # additive away override keys
coord_dhw # additive away override keys
coord_two_zone # additive away override keys
coord_grid_fee # additive away override keys
coord_all_features # additive away override keys
```

Keep existing may-drift comments. Do not claim value-bearing plan fixtures.

- [ ] **Step 4: Run config_flow_steps, `python3 tests/golden.py --only coord`, `python3 tests/env_drift.py --fixtures` — PASS**

- [ ] **Step 5: Commit**

```bash
git add custom_components/heatpump_optimizer/config_flow.py \
  custom_components/heatpump_optimizer/strings.json \
  custom_components/heatpump_optimizer/translations \
  tests/config_flow_steps.py \
  tests/golden
git commit -m "3L-G10: drop away helpers from the config flow."
```

---

### Task 4: Plan-page strip

**Files:**
- Modify: `custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js`
- Modify: `tests/card.mjs`
- Modify: card strings in the same JS `I18N` maps (en + sv)

**Interfaces:**
- Consumes: `hass.states["switch.heat_pump_optimizer_away"]`, `hass.states["datetime.heat_pump_optimizer_away_return"]`, `binary_sensor.heat_pump_optimizer_away_mode` (discover by pinned id, then unique-id suffix `_away` / `_away_return` / `_away_mode`)
- Produces: `_awayStripHtml()` prepended only to the **expanded** Plan body; collapsed card unchanged

- [ ] **Step 1: Write the failing card checks**

In `tests/card.mjs`, after the plan/setup tab checks, build an expanded Plan page with those three entities in `hass.states`:

```javascript
function withAway(states, { sw = false, returnIso = null, resolved = false } = {}) {
  const st = { ...states };
  st["switch.heat_pump_optimizer_away"] = { state: sw ? "on" : "off", attributes: {} };
  st["datetime.heat_pump_optimizer_away_return"] = {
    state: returnIso || "unknown", attributes: {},
  };
  st["binary_sensor.heat_pump_optimizer_away_mode"] = {
    state: resolved ? "on" : "off",
    attributes: { source: resolved && !sw ? "person.alice" : "none" },
  };
  return st;
}
const awayOff = build(withAway(mkStates(DEFAULT_SPACE, DEFAULT_DHW, true)));
awayOff._onCardClick({});
const awayOffHtml = collect(awayOff.shadowRoot).join("\n");
check("expanded plan shows the away toggle", /data-away-toggle/.test(awayOffHtml));
check("collapsed card has no away toggle",
  !/data-away-toggle/.test(collect(build(withAway(mkStates(DEFAULT_SPACE, DEFAULT_DHW, true))).shadowRoot).join("\n")));
check("return datetime is hidden while the switch is off",
  !/data-away-return/.test(awayOffHtml));
const awayOn = build(withAway(mkStates(DEFAULT_SPACE, DEFAULT_DHW, true), { sw: true }));
awayOn._onCardClick({});
check("return datetime is shown while the switch is on",
  /data-away-return/.test(collect(awayOn.shadowRoot).join("\n")));
const awayPerson = build(withAway(mkStates(DEFAULT_SPACE, DEFAULT_DHW, true), { resolved: true }));
awayPerson._onCardClick({});
check("person-away while the switch is off shows a status line",
  /data-away-status/.test(collect(awayPerson.shadowRoot).join("\n")));
```

Add `away.toggle`, `away.return`, `away.status_presence` to both I18N maps. Swedish: “Borta”, “Hemkomst”, “Borta (närvaro)”.

- [ ] **Step 2: Run `node tests/card.mjs` — FAIL**

- [ ] **Step 3: Implement the strip**

`_awayStripHtml()` only when `this.dialog.expanded && this.dialog.activePage() === "plan"`. Prepend it in the expanded Plan branch next to `_chartBlock(built, true)`, not in the collapsed `body = this._chartBlock(built, false)` path.

Toggle `change` → `hass.callService("heatpump_optimizer", "set_away", { active })`. Datetime `change` → `set_away({ return_time })` (empty string clears). Stop click propagation so the toggle does not close/reopen the dialog (same as legend chips).

- [ ] **Step 4: Re-run `node tests/card.mjs` — PASS**

- [ ] **Step 5: Commit**

```bash
git add custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js tests/card.mjs
git commit -m "3L-G10: Away toggle and return time on the Plan page."
```

---

### Task 5: Structure, claims, wrap-up

**Files:**
- `tests/structure.json` only if a ceiling must be paid (ask first)
- PR body

- [ ] **Step 1:** `python3 tests/structure.py` at this PR’s merge-base, then on HEAD. If `coordinator_loc` (or `max_class_loc`) exceeds the recorded ceiling, pay it down or stop and ask. Do not raise.

- [ ] **Step 2:** `PYTHONPATH=tests/hastub python3 tests/features.py` and `python3 tests/entities.py` and `python3 tests/config_flow_steps.py` and `node tests/card.mjs` — all PASS.

- [ ] **Step 3:** Closure select:

```bash
D=$(mktemp -d) && python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"
cat "$D/scope.txt"; cat "$D/scope.run"
```

If `MODE: FULL` or `scope.run` names `tests/stress.py`, take `/tmp/hpo-gate.lock` and run `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=$(git merge-base origin/main HEAD) ./tests/run.sh`. Otherwise run the named scripts only.

- [ ] **Step 4:** Open PR. Title `3L-G10: Plan-page away toggle and return time (#465)`. Body: measured SHA, three-dot vs `origin/main`. **`Closes #465` on its own line.** Comment URL + SHA on #465.

- [ ] **Step 5:** Commit structure pay only if you paid a ceiling:

```bash
git commit -m "3L-G10: record structure after the away store."
```

## Self-review (author)

| Spec requirement | Task |
|---|---|
| Coordinator store, `set_away` only writer | 1 |
| expire at return, no-return stays on | 1 |
| override wins; person works when switch off | 1 |
| helper migration once | 1 |
| switch + datetime entities | 2 |
| slim Setup Away; drop helpers | 3 |
| claim override `data[]` keys; no value re-record | 3 |
| Plan strip; collapsed has no toggle | 4 |
| `Closes #465`; after G9; pay or ask | 5 |
