# Design note: R11-OWNER-EXTHEAT-OVERRIDE -- one switch that overrides the external-heat block

Code read at `origin/main` 8ef450936a1786abf4bb9610dc3336da4e77e8de. There is no predecessor
handoff head. Owner group, above every cap. Evidence: the owner's request,
verbatim (tvofi, 2026-11-22): "I want one new switch, an override switch that
overrides the external heat detection block." **No finder harness: owner
report.** The failing tests below are the harness.

## What the block is today

`ExternalHeatDetector.suppressing` (active, or fading through the decay
window) is copied each cycle into `coordinator._external_heat_active` by
`_update_external_heat_detection`. Five readers act on it:

| site | effect | class |
|---|---|---|
| `_solve_hubs` → `ThermalState.external_heat_active` → `dhw_planner` "External heat source (item 5)" | discretionary DHW slots zeroed for up to 2 h while coasting meets the requirement | **planning** |
| `_external_heat_forecast` (gate `if not ...suppressing`) → `external_heat_kw` into the solve | space plan credited with the fire's free heat | **planning** |
| `_learning_frozen` → `"external_heat_source"` | every learner freezes | learning hygiene |
| `DhwLearner` `external_heat_active` lambda (`dhw_learning.py`) | draw attribution skipped | learning hygiene |
| `_external_heat_view` → `external_heat_suppressing` → binary-sensor attribute `suppressing_electric_dhw` | what the user sees | presentation |

No actuator reads detection directly: `grep -rn external_heat custom_components/heatpump_optimizer/pump_arbiter.py custom_components/heatpump_optimizer/inputs.py custom_components/heatpump_optimizer/duty_switch.py`
finds nothing. Actuation follows the plan, so overriding the two planning
inputs overrides actuation.

## Behaviour

**The planning set**, defined by a rule: every solve input that
`coordinator.py` derives from the detector. It is enumerated by
`grep -n "_external_heat\.\|_external_heat_active" custom_components/heatpump_optimizer/coordinator.py`
and filtered to the call sites inside `_solve_hubs` and
`_external_heat_forecast`. While the override is **effective**, both see "no
external heat": `ThermalState.external_heat_active=False` and a forecast of
`None`. Everything else in the grep is in the residue, by category:

- **Detection itself**: `_update_external_heat_detection` and
  `_external_heat_config`. These keep running, unchanged.
- **Learning hygiene**: `_learning_frozen` and the `DhwLearner` lambda keep
  reading the raw `_external_heat_active`. A fire still contaminates the data
  whether or not the plan ignores it. (Q6 asks the owner.)
- **Presentation and settlement of the fire's own heat**: the ledger's
  `wood_heated` sample (`state.heating()`), `wood_fuel_from_parts` and the
  wood what-if `simulate_wood_slots`. These price the fire, not the plan's
  reaction to it.

**Effective** means the switch is on **and** detection is enabled
(`ExternalHeatConfig.enabled`: wood furnace on and the detection option on).
When detection is disabled, `suppressing` is already False, so the switch has
no effect, and the field reports `override_active: false`.

**Visible**: the External Heat Source binary sensor keeps its state from
`external_heat_active` (raw detection). It gains `override_active` (the
effective override). `suppressing_electric_dhw` now reports the **effective**
block, which is False while overridden. Today that attribute is identical to
the raw value, because no override exists.

**Precedence**: the user's Block DHW and Block Space switches, boosts, the
legionella cycle, peak-guard suppression (ORed into the same DHW gate in
`dhw_planner`), FAULT-HOLD, FROST-HOLD and FLOWCAP do not change. The
override only removes the external-heat term.

## Orchestrator defaults (each is an R-question, below)

1. Off by default.
2. Persists across restarts, as a `RestoreEntity`.
3. No automatic timeout.
4. No effect while detection is disabled.
5. The diagnostics bundle records its state.

## Owning seam and shape

**Owner: `custom_components/heatpump_optimizer/external_heat.py`.** It owns
the detector and the published `ExternalHeat` shape, and it gains the
override's state and the one rule that composes the two. It stays free of
Home Assistant imports (`weakref` is stdlib). These only call it:
`custom_components/heatpump_optimizer/switch.py` (writer),
`custom_components/heatpump_optimizer/coordinator.py` (three reads),
`custom_components/heatpump_optimizer/binary_sensor.py` and
`custom_components/heatpump_optimizer/diagnostics.py` (readers). There is one
owner and no import cycle.

The new API is in `external_heat.py`:

- `_OVERRIDES: WeakKeyDictionary[Any, bool]` holds the switch state per
  coordinator, on boost's `_STATES` pattern. The coordinator grows no
  attribute, so `coordinator_attrs` is unchanged.
- `override_on(coord) -> bool` and `set_override(coord, on: bool) -> None`.
- `ExternalHeatDetector.override_effective(on: bool) -> bool` returns
  `on and self.config.enabled`.
- `ExternalHeatDetector.blocking(on: bool) -> bool` returns
  `self.suppressing and not self.override_effective(on)`.
- `ExternalHeatDetector.view(on: bool) -> ExternalHeatView` is the body of
  `coordinator._external_heat_view`, **moved**, with
  `"external_heat_suppressing": self.blocking(on)`.
- `ExternalHeatState.as_dict(override_active: bool = False)` adds
  `"override_active": True` **only when true**, as `_displacement_dict` does.
  An install that never touches the switch then publishes exactly today's
  dictionary, and the `tests/golden/coord_*.json` captures stay still.
  `payload.ExternalHeat` gains `override_active: bool`.

The coordinator's edits change no lines anywhere else:

- `_solve_hubs`: `external_heat_active=self._external_heat.blocking(override_on(self))`.
- `_external_heat_forecast`: `if not self._external_heat.blocking(override_on(self)):`.
- `_external_heat_view`: its body becomes
  `return self._external_heat.view(override_on(self))`. The method stays,
  because `tests/entities.py` lists it among the views.
- `override_on` joins the existing `from .external_heat import (...)` tuple.

The switch is `ExternalHeatOverrideSwitch(HeatPumpOptimizerEntity,
SwitchEntity, RestoreEntity)` in `switch.py`, with unique key
`external_heat_override` and translation key `external_heat_override`.
`is_on` is `override_on(coordinator)`. Turning it on or off calls
`set_override`, then `publish_then_refresh(self)`, as `AwaySwitch` does.
`async_added_to_hass` calls super, reads `async_get_last_state()`, adopts
`state == "on"` and, only when the result is on, calls
`coordinator.async_request_refresh()`. Its attributes are
`detection_enabled` and `override_active`, read from the published payload.
The switch is created unconditionally, beside the binary sensor, which is
also unconditional.

**Diagnostics**: a `_VIEWS` row,
`("external_heat_override", lambda c: {"switch_on": override_on(c), "override_active": bool(((c.data or {}).get("external_heat") or {}).get("override_active"))})`.
It does no private reach (`coordinator_private_reach`).

**Flow**: user toggles → `set_override` → `publish_then_refresh` → cycle:
`_update_external_heat_detection` (unchanged) → `_solve_hubs` and
`_external_heat_forecast` read `blocking(on)` → solve → `_external_heat_view`
publishes the raw `active` plus `override_active`. Restart: the platform
setup restores the state after the first refresh, and one refresh follows
when it is on.

## Alternatives

1. **HA-free store (`QuarantiningStore`, boost or away pattern), loaded in the
   coordinator's `for load in (...)` set.** It is durable at once and present
   before the first solve. It lost because it adds a coordinator line and a
   store file, against `RestoreEntity`'s zero. The gap it closes is at most
   one cycle after a restart, in the safe direction (the block applies), plus
   a crash within HA's restore-state save interval. This is Q2's fallback if
   the owner wants no gap.
2. **The override state in a new module (`external_heat_override`, not created).** It
   lost because it splits one concern, the block and its override, across two
   owners (`dev/governance/roles/designer.md` step 2), and it needs closure classification and a
   new import in the coordinator.
3. **Clear the cached `_external_heat_active` when overridden.** It lost
   because that one attribute feeds both planning and the learning freeze, so
   the override would silently unfreeze the learners during a real fire. It
   would also break the harnesses that set it directly to drive the freeze
   (`tests/features.py`, `dev/audit/harnesses/solve_inputs_parity.py`).
4. **Feed the detector `enabled=False` while overridden.** It lost because
   `_reset()` erases the evidence and the state, and detection must stay
   visible.

## Sibling sites

- `grep -rn "external_heat_active\|external_heat_kw" custom_components/heatpump_optimizer/dhw_planner.py custom_components/heatpump_optimizer/optimizer.py`
  finds the two planning consumers. Both are covered through their two
  inputs.
- The same grep over `thermal_model.py` and `diagnosis.py` finds the field
  declaration and the re-run input. The re-run records whatever was passed,
  so it is covered.
- The coordinator grep above is classified in Behaviour.
- `mixing_valve.target_temp(free_heat_kw=...)` has no detector caller. It is
  out of scope.

## Evidence plan (failing first; a null control in each)

In `tests/features.py`, beside the existing external-heat cases (`_xh`,
`_xh2`):

1. **Detector unit.** Drive an active detector, then a fading one.
   `blocking(False)` is True and `blocking(True)` is False. The null control
   is a quiet detector, which gives False for both.
2. **Disabled.** With `enabled=False`, `override_effective(True)` is False
   and `as_dict(...)` carries no `override_active`. The null control is
   `enabled=True`, which gives True.
3. **DHW block.** Use a fixture where `dhw_planner` suppresses slots
   (`external_heat_suppressed_steps > 0`). With the switch on, the solve
   state has `external_heat_active=False` and the plan equals the no-fire
   plan, slot for slot. With the switch off (the null control), the
   suppression is reproduced unchanged.
4. **Free-heat credit.** With a wood-tank fixture where
   `_external_heat_forecast` returns an array, the switch on gives `None`.
   The switch off gives the same array as today.
5. **Learning unchanged.** With the switch on during an active fire,
   `_learning_frozen()` still returns `"external_heat_source"` and the
   `DhwLearner` lambda is True. The null control is no fire.
6. **Visibility.** With the switch on and a fire, the binary sensor is on,
   `override_active` is True and `suppressing_electric_dhw` is False. With
   the switch off, today's attributes apply and `override_active` is False.
7. **Switch.** Turning it on and off flips `override_on`. A restored `"on"`
   adopts and requests one refresh. A restored `"off"` or `None` adopts off
   and requests no refresh. In `tests/entities.py`, the platform count of
   switches moves to seven, and the unique id and entity id are pinned.
8. **Diagnostics.** The row reports both fields. A coordinator never touched
   reports `{"switch_on": false, "override_active": false}`.
9. **Goldens.** The `coord_*.json` captures must not move, because the switch
   is off in every fixture. A moved fixture is a defect here, not a claim.

**Mutation targets**: the `and not` in `blocking`, the `and
self.config.enabled` in `override_effective`, the `if override_active` in
`as_dict`, the two coordinator call sites (revert either one to
`.suppressing`), the restore's `== "on"`, and the switch's
`set_override(..., True)`.

## Hot files, serial position, ratchet, docs

**Hot files**: `coordinator.py`, `external_heat.py`, `switch.py`,
`binary_sensor.py`, `diagnostics.py`, `payload.py`, `strings.json`,
`icons.json`, `translations/en.json`, `translations/sv.json`,
`translations/de.json`, `tests/features.py` and `tests/entities.py`, plus the
docs. No new tracked file, so nothing needs closure classification.

**Serial position**: there is no `after` edge. FROST-HOLD, FAULT-HOLD and
FLOWCAP edit `_write_supply`, the arbiter, `early_cutoff`, `inputs` and
`config_flow`, and none touches these sites. A design-ref scan for
`_external_heat_view`, `_external_heat_forecast`, `external_heat.py` and
`external_heat_suppressing` found no other round-11 note. This group
therefore lands after whichever of them merge first, and the fixer rebases
and re-measures at the merge base.

**Interactions**:

- **FROST-HOLD**: no shared state. With the block applied, idle steps below
  the threshold are held by the frost hold as for any idle step. With the
  override on, fewer steps are idle.
- **FAULT-HOLD**: suspends writes while a fault is latched. The override
  changes only the plan, so the fault hold wins.
- **FLOWCAP**: clamps every space write. A larger plan without the
  free-heat credit is still clamped.
- **Manual blocks and boosts**: these are unchanged, and a block wins.

**Ratchet (payment by a real move, never a raise)**: the coordinator class
loses the four lines of `_external_heat_view`'s dict body, which are moved
into `ExternalHeatDetector.view`, the module that already owns `as_dict`. At
module level it gains one import name. The two call-site edits are
line-neutral. Net: `class_excess_loc` and `max_class_loc` go down by about 4,
and `module_excess_loc` goes down by about 3. `external_heat.py` and
`switch.py` stay under the module limit. No claimed move is used:
quiet_windows, duty_ledger, grid_fee, flow_anchor, the config_flow helpers
and dhw_start are all untouched. The fixer runs `tools/audit/archscore/`
before and after and records dS. If a wrapped call line erases the margin,
the line is split by an extracted local, never by a raise.

**Docs**:

- `docs/how-it-works.md`, "Wood furnaces and other external heat": one
  paragraph on the override. It covers what it overrides (the DHW suppression
  and the free-heat credit) and what it does not (detection, the learning
  freeze). It states that it persists and has no timeout, and that it is
  inert with detection off.
- `README.md`: a row in the entity table (Override External Heat Block,
  switch) and a sentence under the switch paragraphs.
- `docs/architecture.md`: the `switch.py` tree line names the override switch.
- `switch.py`'s module docstring: "Six switches" becomes seven.

**Strings**: `entity.switch.external_heat_override.name` is "Override External
Heat Block" (en), "Åsidosätt blockering vid extern värme" (sv) and "Sperre bei
Fremdwärme übersteuern" (de), in `strings.json` and the three translations.
`icons.json` gets a `mdi:fire-off` / `mdi:fire` state pair.

## Questions for the owner (R-questions)

- **Q1**: off by default?
- **Q2**: persist across restarts as a `RestoreEntity`, accepting at most
  one post-restart cycle with the block applied (alternative 1 closes it,
  with one coordinator line and a store)?
- **Q3**: no automatic timeout?
- **Q4**: no effect while detection is disabled (the switch exists but is
  inert, and reports `override_active: false`)?
- **Q5**: does the diagnostics bundle record `switch_on` and the effective
  `override_active`?
- **Q6 (the designer's)**: the learners stay frozen during a detected fire
  even when it is overridden. Should the override also lift the learning
  freeze, for a detector the owner judges to be a false positive?
- **Q7 (the designer's)**: does the override also drop the free-heat credit
  to the space plan, not only the DHW suppression, as "as if no external heat
  were detected" reads?

## Notes for the fixer

- Carry: R11-OWNER-EXTHEAT-OVERRIDE (item restore-order) -- `HeatPumpOptimizerEntity` already defines `async_added_to_hass` via `CoordinatorEntity`; call super before reading the last state.
- Carry: R11-OWNER-EXTHEAT-OVERRIDE (item attr-semantics) -- `tests/entities.py` asserts `suppressing_electric_dhw is True` under a fire; that holds with the switch off; add the overridden case beside it rather than editing it.
- Carry: R11-OWNER-EXTHEAT-OVERRIDE (item golden-still) -- if any `tests/golden/coord_*.json` moves, `override_active` was published unconditionally; fix the code, do not claim drift.
