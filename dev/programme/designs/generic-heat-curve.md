# generic-heat-curve design note (designer seat, note 1 of at most 3)

The group's architect note, extended (`dev/governance/roles/designer.md`). It lives on `design/generic-heat-curve`
and never merges. **There is no finding and no finder harness: the evidence is a user's feature request** (an
alpha innotec LWDV 91-1/3 owner, Luxtronik firmware 3.92.3), quoted below. No roster group exists, so there are no
predecessors and no `after` briefs. `dev/governance/dimensions/D12.md` (Traps) classes a new control surface as a
product request, not an audit finding: **whether to build it is `decision: owner`**, and this note's first job is
to answer that honestly.

**Read at.** `origin/main` = `28d46c4918285d36c409c1fb2f72eb77e04e569e`. Outside the tree, two read-only sources:
the user's `luxtronik_shi` integration at `1eb46953f3baf55f5e9f915f4a244e6ab9b8e49d` (`registers.py`, `README.md`)
and a local copy of python-luxtronik (`luxtronik/definitions/holdings.py`, revision not recorded).

**The request.** Steer the heat curve Home-Assistant-internally by writing `number` entities the user already has,
instead of only an ECL110 over MQTT. Reference hardware (user facts): the heating circuit's curve is two Luxtronik
parameters reached only over the parameter interface (TCP 8889), end point and parallel shift (base point), and it
targets the **return** temperature; a mixing circuit has its own pair.

## Value assessment and recommendation

**What the tree already has.**
- `async_publish_ecl110_command` (coordinator.py:7677) is the one chokepoint every displace passes: the plan's value
  (optimizer.py:5723, `_power_to_displace_schedule`), the fixed modes (coordinator.py:4062), the boost overlay
  (boost.py:346, fed `ecl_max` at coordinator.py:6081), the peak-guard nudge (coordinator.py:8859, minus
  `PEAK_GUARD_DISPLACE_NUDGE_C`) and the curve-learning bias (coordinator.py:7688-7689). It clamps, rounds to an
  integer (7690-7693) and hands the integer to `_publish_ecl110_topics` (coordinator.py:3168), which is MQTT only.
- The pump-duty arbiter writes `space_setpoint_entity` (pump_arbiter.py:464, `_space_target`) as an **absolute**
  set-point: the planned room temperature, or with `space_setpoint_unit` = flow a flow level between
  `FLOW_GATE_C` and `FLOW_HEAT_C` (pump_arbiter.py:656, `_flow_target`). That replaces the controller's weather
  compensation while it is active; it does not bias it.
- Mixing-valve `smart_write` (coordinator.py:7722, `_command_valve_target`) is the closest sibling: a `number`
  written only on a change of at least `MIXING_VALVE_WRITE_EPSILON`, "avoids flash wear on every cycle".

**What a displace entity adds.** The controller keeps its own curve, heating limit and hysteresis, and the
optimizer only biases it, through the same chokepoint, so fixed modes, boost, peak guard and curve learning reach
the entity with no new logic. That combination does not exist today without MQTT. **For whom:** any install whose
integration exposes a whole-curve offset as a `number`. On the reference hardware that entity already exists and
is **volatile**: python-luxtronik's SHI holding `heating_offset` (index 2, address 10002, INT16 K/10, range
−200…200) is "Offset applied to the current return temperature setpoint (tRL) for heating. Requires heating_mode =
offset to apply"; `luxtronik_shi` exposes it as `cfg_heating_offset` (registers.py, number −20…20 K, step 0.5)
and quotes python-luxtronik that SHI holdings are volatile and reset when the controller restarts (README.md,
"Sources of the register map"). A volatile offset carries none of the non-volatile-memory risk the user raised.

**Recommendation: build the small variant, not the two-parameter one.** One optional `number`/`input_number` slot,
`heat_curve_displace_entity`, written as a third arm beside the two MQTT topics with the same integer they get. Do
**not** build writing of persistent curve points (alternative A below). If the owner sees no second install
class beyond the reference, the zero-code stopgap (alternative C) is enough and this group should not be built.

**Assumptions the tree cannot verify.**
- U1: `heating_offset` acts as a parallel shift of the return-target curve on FW 3.92.3 (python-luxtronik's text says
  so; not measured on the reference installation).
- U2: it applies only while `cfg_heating_mode` = offset, which the optimizer does not own. `cfg_heating_mode` =
  setpoint, which the arbiter's space set-point on this controller needs (`luxtronik_shi` README, "Heating
  setpoint (reg. 10001)"), excludes it, so one circuit uses one path or the other.
- U3: the Luxtronik curve between its two points is linear. No source in reach states its shape.

## Owning seam

`custom_components/heatpump_optimizer/heat_curve.py` (**new**) owns the fan-out of one displace to its outputs: the
two MQTT arms (moved verbatim from coordinator.py:3137 `_ecl110_legacy_payload` and :3168 `_publish_ecl110_topics`)
and the new entity arm with its write record. Its state is a per-coordinator side table, the
`pump_arbiter.state_for` shape (pump_arbiter.py:333), so the coordinator gains no attribute. Callers only:
`async_publish_ecl110_command` (computes the integer, unchanged), `config_flow.py` (one field), `entry_config.py`
(one key), `sensor.py` (`ECL110_TOPIC_SLOTS`, sensor.py:64), `diagnostics.py` (one view). One owner.

## Shape

**Options.** `CONF_HEAT_CURVE_DISPLACE_ENTITY = "heat_curve_displace_entity"` in const.py beside
`CONF_ECL110_DISPLACE_SET_TOPIC` (const.py:693); `EntryConfig.heat_curve_displace_entity: str = _key("", _text)`
beside entry_config.py:213; one `_F("heat_curve", ..., "", _entity_of(['number', 'input_number']))` after
config_flow.py:1752, suggesting empty for the reason the comment at config_flow.py:1745-1750 gives. `climate` is
excluded: its target is absolute. The existing `ecl110_displace_min/max` and `ecl110_pid_time_constant_hours` keys
govern the arm too; **keys unchanged**, the page title (`strings.json` `heat_curve`) loses "(ECL110)".
`ECL110_TOPIC_SLOTS` gains the new key, so both diagnostic sensors enable for an entity-only install.

**Data flow.**
```
plan / fixed mode / boost / peak guard ──► async_publish_ecl110_command (coordinator.py:7677)
   + curve bias, clip(ecl110_displace_min, ecl110_displace_max), round ──► displace_int
before: _publish_ecl110_topics(hass, set_topic, command_topic, qos, retain, displace_int, payload)
after:  heat_curve.publish(hass, ctx._config, heat_curve.state_for(self), displace_int, payload)
          ├─ MQTT set topic   (unchanged)
          ├─ MQTT legacy topic (unchanged)
          └─ entity arm: write_displace(hass, entity, displace_int, held, now) -> reason | None
```

**Mapping.** The arm writes `displace_int` itself as a **temperature difference**: identity for `K`, `°C`, `C`,
`degC` or no unit; ×9/5 for `°F`, `F`, `degF`; any other unit is refused. **It never goes through the absolute
set-point helpers** (`write_setpoint_c`, `setpoint_range_c`, `quantise_setpoint_c`, `read_setpoint`): measured by
`dev/programme/designs/generic-heat-curve-probes/k_unit_probe.py` (output beside it), an entity in K reading −2 is
read as −275.15 °C and a −2 write is sent as 271.15, because `TEMPERATURE_UNIT_TO_C` maps `K` to −273.15 (const.py:225).
Range is the entity's raw `min`/`max` attributes, step `inputs.setpoint_step` (inputs.py:539, unit-free); the value
is clamped into the range and put on the step. The raw service call is `inputs.write_setpoint` (inputs.py:596),
which takes a value already in the entity's unit.

**Write policy (invariants).**
1. W1 write-on-change against the reading: no call while `|reading − target| ≤ step/2`. A restart or reload writes
   nothing when the entity already holds the target; no persisted store is needed.
2. W2 holds what it wrote, as pump_arbiter.py:59 states it: every write is recorded `(value, at)`; a differing
   reading inside `pump_arbiter.ECHO_GRACE_S` proves nothing; after it, the first miss rewrites once.
3. W3 **a refused value is not retried forever** (deliberately unlike the arbiter's `RETRY_MINUTES` loop, because
   the target may be non-volatile): a second consecutive miss for the same target latches a warning through
   `log_held` (the valve-write precedent, coordinator.py:700) and stops rewriting that value until the target
   changes or the reading matches.
4. W4 a daily write ceiling, `2 × 1440 / optimization_interval`, twice the cycle count. Past it the arm writes
   nothing until local midnight and latches a warning; the count is in diagnostics. The publish path fires once
   per cycle (coordinator.py:7815) plus mode changes (climate.py:294) and guard transitions, so the ceiling binds
   only on a defect.
5. W5 integer granularity: the arm writes the same integer the MQTT arms get, on a 0.5 or 1 step exactly, so one
   value serves every arm and sensor.
6. W6 an entity range narrower than the configured displace range saturates the plan's mapping; that is latched
   once as a warning naming both ranges (luxtronik_shi's mixing-circuit offset is −5…5 against a −20…20 default).
7. W7 with the option empty, every MQTT payload, sensor and golden is byte-identical; no planner code changes.

**Interactions** (all through the chokepoint, no new code): fixed modes as today; MODE_OFF writes nothing
(coordinator.py:7714), the tvofi ruling of 2026-09-26 the arbiter carries (pump_arbiter.py:1132-1133); a stale plan
writes nothing (coordinator.py:7797-7810), so the entity holds its last value as an ECL110 does; boost writes the
configured maximum; the peak guard writes plan − nudge and re-publishes on release; curve learning applies its
bias. **Changed for the user:** curve learning on an entity-only install now moves the real pump, where with no
topic it moved nothing.

**Failure handling.** Entity absent, `unknown`/`unavailable`, wrong domain, unknown unit, or a raising service: no
write, latched reason, cycle unaffected (each arm swallows its own failure, as coordinator.py:3177-3180 states for
MQTT); the MQTT arms run first and are independent. Config flow refuses `heat_curve_displace_entity` equal to
`space_setpoint_entity` or `mixing_valve_write_entity` (two writers on one entity).

## Alternatives, and why each lost

- **A. Two persistent curve points (end point and parallel shift).** A parallel shift by d moves both points by d.
  Moving only the base point by d rotates the curve about the end point: at outdoor x the shift is
  `d·(x − x_end)/(x_base − x_end)`, d only at the base point, zero at the end point, which breaks "a parallel shift
  of the whole curve" (docs/ecl110.md) under U3. Moving both needs a persisted baseline (installer curve) the
  integration would own and lose on any user edit at the controller, two non-atomic writes per change (a
  transient tilt between them), two non-volatile writes per change, and a shifted curve that survives the
  optimizer crashing or being removed. Lost on state ownership, call count and fail-safety.
- **B. A new `space_setpoint_unit` "offset" on the arbiter's slot.** The arbiter's value is per duty and per
  one-minute tick (gate on non-heating steps, DHW rows), and the displace chain (fixed modes, peak guard, curve
  bias) does not pass through it. Two owners of one concern. Lost on coupling.
- **C. No code: a user automation.** Store a dummy `ecl110_displace_set_topic` and mirror it from MQTT into the
  number. Works today, but needs a broker, adds a second writer outside the optimizer, and has none of W1–W6.
  Lost on the wear policy; it remains the right answer if the owner declines the group.

## Sibling sites (step 5)

`grep -n "displace_value\|_publish_ecl110_topics\|ECL110_TOPIC_SLOTS\|ecl110_displace_set_topic\|_ecl110_displace_max\|_ecl110_displace_min" custom_components/heatpump_optimizer/*.py`

| Site | Disposition |
|---|---|
| coordinator.py:7702-7710, the topic call | replaced by `heat_curve.publish` (shape above) |
| coordinator.py:3137, :3168 | moved verbatim to heat_curve.py |
| coordinator.py:4042, :4045 (`_ecl110_displace_set_topic`, `_ecl110_retain`) | read from `ctx._config` in heat_curve.py; both stores deleted (payment) |
| sensor.py:64, :1332, :1352 | slot tuple gains the entity key |
| coordinator.py:4073-4079, 4156, 6081, 6547-6549, 7689-7691, 8860; boost.py:346; optimizer.py:5796, 5837, 5873 | upstream of the integer; unchanged |
| climate.py:235, sensor.py:862, coordinator.py:8114, payload.py:161 | readouts of the plan value; unchanged |
| coordinator.py:4511 (`curve_driven`), 6834-6835 (lag) | read the action, not the arm; unchanged |
| const.py:693, entry_config.py:213 | the new key goes beside them |

## Evidence plan (by file)

- **Failing test first**, `tests/features.py` beside the `_publish_ecl110_topics` block (tests/features.py:40444):
  an install with no topic and the entity `number.x` (unit K, −20…20, step 0.5, state 0);
  `async_publish_ecl110_command(5.0, True)` makes exactly one `number.set_value` with value 5. Red at base: no call.
- Arms in the same block: K value −2 sent as −2 (red if routed through `write_setpoint_c`, per the probe); °F
  sends ×1.8; entity −5…5 with displace 8 sends 5 and latches W6; W1 equal reading, no call; W2 inside grace, no call,
  after grace one rewrite; W3 a second miss, no third call for that target, a new target writes; W4 the ceiling;
  missing / unavailable / `sensor` domain / unit `%` / raising service, no write and the MQTT arm still publishes;
  MODE_OFF no call; peak-guard engage plan − nudge, release plan; boost maximum; curve bias applied.
- **Null control:** the same install with the option empty: identical MQTT `mqtt.publish` calls and payloads, no
  `number` call; the existing tests at tests/features.py:40498 and :40578 stay green unchanged except the import.
- Config flow, `tests/config_flow_steps.py`: selector domains, the equal-entity refusal, empty default; the
  config-flow coverage floor in `tests/coverage_budgets.json` holds.
- **Goldens:** none move (W7); no claim file is touched.
- **Mutation targets** (heat_curve.py): the W1 comparator, the delta conversion, the clamp to the entity range,
  the grace check, the W3 give-up, the W4 ceiling. New sites must be killed or triaged (`tests/mutation_budgets.json`).

## Cost against the ratchet, and how it is paid

`tests/structure_budgets.json` sits at zero headroom on every metric at base (`tests/structure.py`, run at
`28d46c49`). The design adds no coordinator method and no coordinator attribute; heat_curve.py stays far under
`GOD_CLASS_LOC_LIMIT`, so a new small module is free. Payment, in order: the shorter call and the two deleted
stores lower `class_excess_loc`, `max_class_loc` and `coordinator_attrs`; moving the two helpers out of coordinator.py
removes their lines from the coordinator's helper count. Watch `duplication_copies` (the entity arm must not clone
`_command_valve_target`'s epsilon-and-latch block) and `functions_cc_over_15` (split `write_displace` into
read/convert/decide if its CC nears it). No budget raise is expected; one would need the owner (CLAUDE.md, rule 2).

## Docs

`docs/ecl110.md`: a section "Without MQTT: a number entity" (option, delta units, W1–W6, the Luxtronik SHI example
with U1/U2 stated as assumptions); `docs/configuration.md:358` page row; `README.md:243` surface row and the
"ECL110 control is MQTT-only" limit at README.md:273; `strings.json`, `translations/en.json`, `translations/sv.json`.

## Hot files and serial position

coordinator.py, config_flow.py, const.py, entry_config.py, sensor.py, diagnostics.py, strings and translations,
docs/ecl110.md, docs/configuration.md, README.md, tests/features.py, tests/config_flow_steps.py, plus heat_curve.py.
`design/R10-USER-DOCS-FINAL` edits docs/ecl110.md and docs/configuration.md: this group goes after it.
`design/r10-livestate` touches `_async_handle_ecl110_state_message`, a different seam in the same file: no edge.
Roster group, size (L by file count, M by logic) and edges are `decision: orchestrator`.

## Notes for the fixer

- `write_setpoint` sends an integer when the stepped value is whole (inputs.py:612); the SHI accepts it, but
  read it back in the test. Carry: generic-heat-curve (item ghc-01)
- tests/features.py:40606-40609 read `_ecl110_displace_set_topic` off the coordinator; re-point them at
  `EntryConfig` when the store is deleted. Carry: generic-heat-curve (item ghc-02)
- docs/ecl110.md's last paragraph says the coordinator tracks the effective displace "so the model prices the heat
  that has actually arrived"; `ecl110_effective_displace` is read only by sensor.py:1355, climate.py:236 and
  coordinator.py:8116, never by the model. Out of this group's scope. Carry: dismissed: documentation claim
  outside scope, for a D6 round (item ghc-03)
- sensor.py:63 and config_flow.py:1750 cite `coordinator._ecl110_topic`, which no longer exists. Carry: dismissed:
  stale comment outside scope, for a D5 round (item ghc-04)
- Questions only the owner or the user can answer: build at all (`decision: owner`); whether MODE_OFF or unload
  should write 0 to a non-volatile entity, against the 2026-09-26 "off writes nothing" ruling (`decision: owner`);
  U1 measured on the reference installation before the docs name the Luxtronik example (the user). Carry:
  generic-heat-curve (item ghc-05)
