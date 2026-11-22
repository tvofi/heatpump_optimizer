# Design note: R11-OWNER-EXTHEAT-OVERRIDE -- one switch that overrides the external-heat block

Revision 2. Answers `design-verdict/R11-OWNER-EXTHEAT-OVERRIDE` 2a019ea9 (revise:
R1 seam and names, R2 persistence cost), built on 1f9f94b2. Code read at
`origin/main` 8ef450936a1786abf4bb9610dc3336da4e77e8de. There is no predecessor
handoff head. Owner group, above every cap. Evidence: the owner's request,
verbatim (tvofi, 2026-11-22): "I want one new switch, an override switch that
overrides the external heat detection block." **No finder harness: owner
report.** The failing tests below are the harness.

## Two overrides, kept apart (R1)

`external_heat.py` already has an **override**: `ExternalHeatObservation.override`,
fed by `coordinator._external_heat_override` from the configured stove/flue
entity (`CONF_EXTERNAL_HEAT_ENTITY`) and applied first in `_update_activation`:
"yes" activates (`source="entity"`), "no" deactivates. It asserts or denies
**that a fire exists**. The module docstring, `docs/how-it-works.md` and the
log line "External heat override %s" use that word.

The new switch **ignores the block**: detection, the fire and the stove entity
keep their meaning; only the plan's reaction is lifted. Every new identifier
uses the stem `ignore_block`, never `override`: `BoostState.ignore_extheat_block`,
`boost.extheat_block_ignored`, `boost.set_extheat_block_ignored`,
`ExternalHeatDetector.ignore_effective` and `.blocking`, payload key
`block_ignored`, unique and translation key `external_heat_ignore_block`,
diagnostics row `external_heat_block_ignore`. The user-facing name keeps the
owner's word (Q9).

## What the block is today

`ExternalHeatDetector.suppressing` (active, or fading through the decay
window) is copied each cycle into `coordinator._external_heat_active`
(coordinator.py:5203). Its readers:

| site | effect | class |
|---|---|---|
| solve state `external_heat_active=self._external_heat_active` (coordinator.py:6225) → `dhw_planner` item 5 | discretionary DHW slots zeroed while coasting suffices | **planning** |
| `_external_heat_forecast` gate `if not self._external_heat.suppressing` (coordinator.py:5218) | space plan credited with the fire's free heat | **planning** |
| `_learning_frozen` (coordinator.py:6844), `DhwLearner` lambda (coordinator.py:3757) | learners freeze, draw attribution skipped | learning hygiene |
| `_external_heat_view` (coordinator.py:8089) → `suppressing_electric_dhw` | what the user sees | presentation |

No actuator reads detection: `grep -n external_heat custom_components/heatpump_optimizer/pump_arbiter.py custom_components/heatpump_optimizer/inputs.py custom_components/heatpump_optimizer/duty_switch.py`
is empty. Actuation follows the plan.

## Behaviour

**The planning set**, by rule: every solve input `coordinator.py` derives from
the detector, enumerated by
`grep -n "_external_heat\.\|_external_heat_active" custom_components/heatpump_optimizer/coordinator.py`
and filtered to the two planning rows above. While the switch is
**effective**, both see "no external heat". Residue, by category: detection
itself (`_update_external_heat_detection`, `_external_heat_config`,
`_external_heat_override`: unchanged); learning hygiene (raw value kept, Q6);
settlement of the fire's own heat (ledger `wood_heated`,
`wood_fuel_from_parts`, `simulate_wood_slots`).

**Effective** = switch on **and** `ExternalHeatConfig.enabled`. With detection
disabled `suppressing` is already False; the switch is inert and publishes
`block_ignored: false`.

**Precedence (R1b)**:

- **Inferred fire** (`source="inferred"`, or fading): the switch lifts the block.
- **Entity-sourced fire** (`source="entity"`, the stove entity says "yes"):
  **the switch lifts this block too.** `blocking` reads no `source`; the
  owner's request names "the external heat detection block", and the entity
  is one of detection's three signals. The binary sensor stays on with
  `source: entity`. Pinned by evidence test 3b. Q8 asks the owner to confirm;
  a "no" is one clause in `blocking` (`and self.state.source != "entity"`).
- **Entity says "no"**: there is no block; the switch changes nothing.
- Block DHW/Space switches, boosts, legionella, peak-guard suppression,
  FAULT-HOLD, FROST-HOLD, FLOWCAP: unchanged. A user block still wins.

## Owning seam and shape

**The block rule: `custom_components/heatpump_optimizer/external_heat.py`**
(gains no state and no Home Assistant import). **The held toggle and its
persistence: `custom_components/heatpump_optimizer/boost.py`**, which already
holds and stores every persisted user duty toggle (timed boosts, Block
DHW/Space) and owns the restore gate (`spawn_restore_session`,
`session_restored`) that the first refresh awaits (coordinator.py:6136). Today's
blocks already split this way: boost holds the toggle, the planner path applies
it. Neither module imports the other; `coordinator.py` and `switch.py` already
import `boost`. Callers only: `switch.py` (writer), `coordinator.py` (three
reads), `binary_sensor.py` and `diagnostics.py` (readers; `diagnostics.py` adds
`boost` to its `from . import` line).

`boost.py`:

- `BoostState.ignore_extheat_block: bool = False`.
- `extheat_block_ignored(coord) -> bool` = `held_for(coord).ignore_extheat_block`.
- `async set_extheat_block_ignored(coord, on, *, refresh=True)`: awaits
  `session_restored`, sets, `persist`, optional refresh, as `set_block` does.
- `_store_payload` adds `"ignore_extheat_block": True` **only when on**, so the
  store of an install that never touches the switch is byte-identical;
  `restore` adopts `bool(raw.get("ignore_extheat_block"))`. No timeout field (Q3).

`external_heat.py`:

- `ExternalHeatDetector.ignore_effective(ignored) -> bool` = `ignored and self.config.enabled`.
- `ExternalHeatDetector.blocking(ignored) -> bool` = `self.suppressing and not self.ignore_effective(ignored)`.
- `ExternalHeatDetector.view(ignored) -> ExternalHeatView`: `_external_heat_view`'s
  body, **moved**, with `"external_heat_suppressing": self.blocking(ignored)`.
- `ExternalHeatState.as_dict(block_ignored: bool | None = None)` adds
  `"block_ignored"` **only when not None**; `view` passes
  `self.ignore_effective(ignored)` when the switch is on, else None.
  `payload.ExternalHeat` (total=False) gains `block_ignored: bool`. Switch off
  ⇒ today's dict, so `tests/golden/coord_*.json` stay still. This answers
  carry switch-detection-attr: on-and-False means detection is off, so no
  `enabled` field is published.

`coordinator.py` (call sites line-neutral; no new import):

- coordinator.py:6225 → `external_heat_active=self._external_heat.blocking(boost.extheat_block_ignored(self))`.
- coordinator.py:5218 → `if not self._external_heat.blocking(boost.extheat_block_ignored(self)):`.
- `_external_heat_view` → `return self._external_heat.view(boost.extheat_block_ignored(self))`
  (the method stays; `tests/entities.py` lists it among the views).
- coordinator.py:5203, 3757 and 6844 unchanged (raw).

`switch.py`: `ExternalHeatIgnoreBlockSwitch(HeatPumpOptimizerEntity, SwitchEntity)`,
`_pin_identity(entry, "external_heat_ignore_block")`, `is_on` =
`boost.extheat_block_ignored(coordinator)`; on/off call
`set_extheat_block_ignored(..., refresh=False)` then `publish_then_refresh(self)`,
as `AwaySwitch` does. Attribute `block_ignored`, read from the published
`external_heat` payload. Created unconditionally. **No `RestoreEntity`.**

Diagnostics: `_VIEWS` row `("external_heat_block_ignore", lambda c: {"switch_on":
boost.extheat_block_ignored(c), "block_ignored": bool(((c.data or
{}).get("external_heat") or {}).get("block_ignored"))})`; no private reach.

```
user ─toggle─▶ switch.py ─set_extheat_block_ignored─▶ boost (await gate, set, persist)
                   └─publish_then_refresh─▶ coordinator cycle:
  _update_external_heat_detection (raw, unchanged)
  solve state / _external_heat_forecast ─blocking(ignored)─▶ external_heat.py
  _external_heat_view ─view(ignored)─▶ external_heat.py ─▶ payload external_heat.block_ignored
restart: spawn_restore_session ─▶ away + boost restore (flag included) ─▶ gate opens ─▶ first refresh
```

## Alternatives

1. **`RestoreEntity` on the switch** (revision 1's choice; R2). Lost: no entity
   uses it today; it needs a new stub `tests/hastub/homeassistant/helpers/restore_state.py`
   with closure classification, a new name in `tests/ha_floor_names.json` and an
   `ha_floor.py record` against the floor tag (`tests/ha_floor.py` fails closed
   on an unrecorded name); and it restores after the first refresh, so one
   solve plans with the block applied and the entity must request a refresh.
   The boost store costs none of these.
2. **A store owned by `external_heat.py`.** Lost: `store.py` imports
   `homeassistant.helpers.storage`, so `external_heat.py` would leave the
   own-import-free set the layering metric counts, and its load would be a new
   coordinator spawn outside the restore gate (a post-restart gap again).
3. **A new module for the toggle.** Lost: a new tracked file to classify, a
   new coordinator import, and a third home for user toggles beside `away.py`
   and `boost.py`.
4. **The switch forces `obs.override=False`** (R1a). Lost: `_deactivate` clears
   evidence and `since`, so detection goes dark (binary sensor off); the cached
   `_external_heat_active` drops, so the learners unfreeze during a real fire;
   the stove entity's "yes" is silently overruled; and `_decay` still fades
   `suppressing`, so the block lingers through the decay window instead of
   lifting at once.
5. **Clear the cached `_external_heat_active`.** Lost: that one attribute
   feeds planning and the learning freeze, and harnesses set it directly
   (`tests/features.py`, `dev/audit/harnesses/solve_inputs_parity.py`).
6. **Feed the detector `enabled=False`.** Lost: `_reset()` erases evidence and
   state; detection must stay visible.

## Sibling sites

`grep -rn "external_heat_active\|external_heat_kw" custom_components/heatpump_optimizer/dhw_planner.py custom_components/heatpump_optimizer/optimizer.py custom_components/heatpump_optimizer/thermal_model.py custom_components/heatpump_optimizer/diagnosis.py`
finds the two planning consumers, the field declaration and the re-run record;
all are covered through the two inputs. `mixing_valve.target_temp(free_heat_kw=...)`
has no detector caller: out of scope.

## Evidence plan (failing first; a null control in each)

In `tests/features.py` beside `_xh`/`_xh2`, unless named:

1. **Detector unit.** Active, then fading: `blocking(False)` True, `blocking(True)` False. Null: quiet detector, both False.
2. **Disabled.** `enabled=False`: `ignore_effective(True)` False; `as_dict(False)` carries `block_ignored: false`, `as_dict(None)` no key. Null: `enabled=True` gives True.
3. **DHW block.** Fixture with `external_heat_suppressed_steps > 0`: switch on ⇒ solve state `external_heat_active=False`, plan equal to the no-fire plan slot for slot. Null: switch off reproduces today's suppression.
   **3b. Entity fire.** Same with `override=True` (`source="entity"`): switch on lifts the block, binary sensor stays on with `source: entity`. Null: switch off, block applies.
4. **Free-heat credit.** Wood-tank fixture: switch on ⇒ `_external_heat_forecast` None. Null: switch off, today's array.
5. **Learning unchanged.** Switch on during a fire: `_learning_frozen()` is `"external_heat_source"`, the `DhwLearner` lambda True. Null: no fire.
6. **Visibility.** Switch on + fire: binary sensor on, `block_ignored` True, `suppressing_electric_dhw` False. Null: switch off, today's attributes, no `block_ignored` key.
7. **Persistence.** `_store_payload` with the flag on carries `ignore_extheat_block`; off equals today's payload (null). `restore` from a stored `true` sets the flag before `session_restored` returns, so the first refresh's solve sees it; stored absent or `false` ⇒ off. `set_extheat_block_ignored` waits on an unopened gate. In `tests/entities.py`: switch count 6 → 7 and its message, unique id and entity id pinned.
8. **Diagnostics.** The row reports both fields; an untouched coordinator gives `{"switch_on": false, "block_ignored": false}`.
9. **Goldens.** `coord_*.json` must not move (switch off in every fixture). A moved fixture is a defect, not a claim.

**Mutation targets**: `and not` in `blocking`; `and self.config.enabled` in
`ignore_effective`; `is not None` in `as_dict`; both coordinator call sites
(revert to `.suppressing`); the `if` guarding the store key; `restore`'s
`bool(raw.get(...))`; the `True` in the switch's `async_turn_on`.

## Hot files, serial position, ratchet, docs

**Hot files**: `coordinator.py`, `external_heat.py`, `boost.py`, `switch.py`,
`binary_sensor.py`, `diagnostics.py`, `payload.py`, `strings.json`,
`icons.json`, `translations/en.json`, `translations/sv.json`,
`translations/de.json`, `tests/features.py`, `tests/entities.py`, docs. **No
new tracked file and no new Home Assistant name** (`boost.py` already imports
`QuarantiningStore`): no closure classification, no stub, no floor re-record.

**Serial position**: no `after` edge. FROST-HOLD, FAULT-HOLD and FLOWCAP edit
`_write_supply`, the arbiter, `early_cutoff`, `inputs` and `config_flow`; none
touches these sites. The fixer rebases and re-measures at the merge base.
Interactions: FAULT-HOLD wins (plan-only change); FLOWCAP still clamps;
FROST-HOLD sees fewer idle steps; user blocks win.

**Ratchet (payment by a real move, never a raise)**: the coordinator class
loses `_external_heat_view`'s four-line dict body (moved to
`ExternalHeatDetector.view`); the call sites are line-neutral and no import is
added (`boost.` is already used). Net: `class_excess_loc`, `max_class_loc` and
`module_excess_loc` go down by about 4. `BoostState` (about 180 lines),
`boost.py` (820), `external_heat.py` (497) and `switch.py` (234) stay under
their limits. The fixer runs `tools/audit/archscore/` before and after and
records dS; a wrapped line is split by an extracted local, never a raise.

**Docs**: `docs/how-it-works.md`, "Wood furnaces and other external heat": one
paragraph naming **both** controls and setting them apart: the stove/flue
entity says whether a fire burns; the switch keeps the fire detected but stops
the plan reacting (DHW suppression and free-heat credit), keeps the learning
freeze, persists, has no timeout, is inert with detection off, and lifts an
entity-reported fire's block too. `README.md`: entity-table row and a sentence
under the switch paragraphs. `docs/architecture.md`: the `switch.py` tree line.
`switch.py` docstring: "Six switches" → seven.

**Strings**: `entity.switch.external_heat_ignore_block.name`: "Override
external heat block" (en), "Åsidosätt blockering vid extern värme" (sv),
"Sperre bei Fremdwärme übersteuern" (de), in `strings.json` and the three
translations; `icons.json` `mdi:fire-off` / `mdi:fire`.

## Questions for the owner

- **Q1**: off by default?
- **Q2**: persists across restarts? (Stored with the boost/block toggles and restored before the first solve: no post-restart gap.)
- **Q3**: no automatic timeout?
- **Q4**: no effect while detection is disabled (the switch exists, inert, `block_ignored: false`)?
- **Q5**: the diagnostics bundle records `switch_on` and the effective `block_ignored`?
- **Q6**: the learners stay frozen during an ignored fire. Should the switch also lift the learning freeze?
- **Q7**: the switch drops the free-heat credit to the space plan as well as the DHW suppression. Confirm?
- **Q8**: when your stove/flue entity reports a fire, the switch lifts that block too. Confirm, or should the entity win?
- **Q9**: entity name "Override external heat block", while code identifiers say `ignore_block` to stay distinct from the stove-entity override. Keep the name?

## Notes for the fixer

- Carry: R11-OWNER-EXTHEAT-OVERRIDE (item attr-semantics) -- `tests/entities.py` asserts `suppressing_electric_dhw is True` under a fire; that holds with the switch off; add the ignored case beside it rather than editing it.
- Carry: R11-OWNER-EXTHEAT-OVERRIDE (item golden-still) -- if any `tests/golden/coord_*.json` moves, `block_ignored` was published unconditionally; fix the code, do not claim drift.
- Carry: R11-OWNER-EXTHEAT-OVERRIDE (item switch-detection-attr) -- answered in the shape: `block_ignored` is published only while the switch is on and is False when detection is off; no `enabled` field is published and the switch reads no private detector attribute.
- Carry: R11-OWNER-EXTHEAT-OVERRIDE (item seam-learners-rebase) -- design/R11-SEAM-learners rewrites `_learning_frozen` into a facts function; whichever lands second keeps the `external_heat_source` reason reading the raw detection, not `blocking(...)`, and evidence test 5 pins it.
- Carry: R11-OWNER-EXTHEAT-OVERRIDE (item switch-count-pin) -- tests/entities.py:11769 pins `len(switches) == 6` with a message naming the switches; update both the count and the message.
- Carry: R11-OWNER-EXTHEAT-OVERRIDE (item store-unchanged) -- the boost store payload of an install that never touches the switch must stay byte-identical; evidence test 7's null control pins it.
- Carry: R11-OWNER-EXTHEAT-OVERRIDE (item pre-gate-read) -- `extheat_block_ignored` read before the restore gate opens returns the `BoostState` default False, the safe direction (the block applies); only writers await the gate, readers do not, and the first refresh already awaits it at coordinator.py:6136.
