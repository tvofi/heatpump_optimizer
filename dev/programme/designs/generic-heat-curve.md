# generic-heat-curve design note (designer seat, note 2 of at most 3)

The group's architect note, extended (`dev/governance/roles/designer.md`). It lives on `design/generic-heat-curve`
and never merges. **There is no finding and no finder harness: the evidence is a user's feature request** (an
alpha innotec LWDV 91-1/3 owner, Luxtronik firmware 3.92.3). No roster group exists, so there are no predecessors
and no `after` briefs. `dev/governance/dimensions/D12.md` (Traps) classes a new control surface as a product
request: **whether to build it is `decision: owner`**.

**Note 2** answers `Design review: revise f8316155370f4b890ee3051e0516010739ae332a architecture-unsound`:
R1 in §Target contract (one slot, a declared target kind; kind `offset` is the first build, kind `persistent` a
specified follow-up), R1b in §Write policy (W1–W6 sized for volatile targets; the persistent budget is a
documented refusal), R2 in U4 and §Alternatives (A split into A1 and A2). The verdict's seven fixer carries are in
§Notes for the fixer as items ghc-r01…r07. The reviewer's verified points (seam, chokepoint, feeds, K-unit trap,
ratchet, sibling designs) stand unchanged. The user asked for "both" kinds and for use beyond his install.

**Read at.** `origin/main` = `28d46c4918285d36c409c1fb2f72eb77e04e569e`, unchanged since note 1. Outside the tree,
read-only: the user's `luxtronik_shi` at `1eb46953f3baf55f5e9f915f4a244e6ab9b8e49d` (`registers.py`, `README.md`),
and python-luxtronik, a shallow clone of Bouni/python-luxtronik at
`02afea84bd5bf3ee87445de6f2a42b8029983169` (2026-03-22, `git -C /home/claude/shi-re/pylux/src log -1`):
`luxtronik/definitions/holdings.py` and `luxtronik/definitions/parameters.py`.

**The request.** Steer the heat curve inside Home Assistant by writing `number` entities the user already has,
not only an ECL110 over MQTT. Reference hardware (user facts): the heating circuit's curve is two Luxtronik
parameters reached only over the parameter interface (TCP 8889), end point (30 °C) and parallel shift (22 °C),
and it targets the **return** temperature; a mixing circuit has its own pair.

## Value assessment and recommendation

**What the tree already has.**
- `async_publish_ecl110_command` (coordinator.py:7677) is the one chokepoint every displace passes: the plan's value
  (optimizer.py:5723), the fixed modes (coordinator.py:4062), the boost overlay (boost.py:346, fed `ecl_max` at
  coordinator.py:6081), the peak-guard nudge (coordinator.py:8859) and the curve-learning bias
  (coordinator.py:7688-7689). It clamps, rounds to an integer (7690-7693) and hands it to `_publish_ecl110_topics`
  (coordinator.py:3168), which is MQTT only.
- The pump-duty arbiter writes `space_setpoint_entity` as an **absolute** set-point (pump_arbiter.py:464
  `_space_target`, :656 `_flow_target`). It replaces the controller's weather compensation while active.
- Mixing-valve `smart_write` (coordinator.py:7722) writes a `number` only on a change of
  `MIXING_VALVE_WRITE_EPSILON`, to avoid flash wear.

**What a displace target adds.** The controller keeps its own curve, heating limit and hysteresis; the optimizer
only biases it through the chokepoint, so fixed modes, boost, peak guard and curve learning reach the target with
no new logic. Without MQTT that does not exist today. **For whom:** any integration exposing a whole-curve offset
as a `number`. On the reference controller one exists and is volatile: python-luxtronik SHI holding
`heating_offset` (holdings.py:75-89; index 2, address 10002, INT16 K/10, −200…200, default 0) is "Offset applied
to the current return temperature setpoint (tRL) for heating. Requires heating_mode = offset to apply";
`luxtronik_shi` exposes it as `cfg_heating_offset` (registers.py:363-375, −20…20 K, step 0.5) and quotes
python-luxtronik that SHI holdings are volatile (README.md:213-217, :229-231).

**Recommendation.** Build one slot with a declared target kind. **First build: kind `offset`** (§Target contract
(a)). **Kind `persistent` is a follow-up** specified to build level in (b), not part of the first build. Never two
slots, and never writes of two curve points (A1). If the owner sees no install class beyond the reference, the
zero-code stopgap C suffices and nothing is built. **`decision: owner`**: build at all; first build (a) only, or
(a) and later (b).

**Assumptions the tree cannot verify.**
- U1: `heating_offset` acts as a parallel shift of the return-target curve on FW 3.92.3 (python-luxtronik's text;
  not measured on the reference installation).
- U2: it applies only while `cfg_heating_mode` = offset, which the optimizer does not own; mode setpoint, which
  the arbiter's space set-point on this controller needs (`luxtronik_shi` README, "Heating setpoint (reg. 10001)"),
  excludes it.
- U3: the Luxtronik curve between its two points is linear. No source in reach states its shape.
- U4: what the persistent "parallel shift" parameter is on FW 3.92.3, a foot point (absolute return temperature at
  a warm reference) or a whole-curve offset. python-luxtronik gives no semantics for indices 1
  (`ID_Einst_WK_akt`), 11, 12 (`ID_Einst_HzHKRANH_akt`) and 13 (`ID_Einst_HzHKRABS_akt`): all `Celsius`, `°C/10`,
  `description: ''` (parameters.py:60-69, 158-187). Which index the user's Luxtronik entities map to is not stated
  by any source in reach. The user's values (shift 22 °C below end point 30 °C) read as a temperature at a
  reference point rather than an offset; that is an inference, not a measurement.

## Owning seam

`custom_components/heatpump_optimizer/heat_curve.py` (**new**) owns the fan-out of one displace to its outputs:
the two MQTT arms (moved verbatim from coordinator.py:3137 `_ecl110_legacy_payload` and :3168
`_publish_ecl110_topics`) and the entity arm with its write record, kept per coordinator in the
`pump_arbiter.state_for` shape (pump_arbiter.py:333), so the coordinator gains no attribute. Callers only:
`async_publish_ecl110_command` (computes the integer, unchanged), `config_flow.py`, `entry_config.py`, `sensor.py`
(`ECL110_TOPIC_SLOTS`, sensor.py:64), `diagnostics.py`, and for (b) the unload path. One owner; both kinds live in
the one module, so (b) adds no second owner.

## Target contract (R1)

**Options (first build).** `CONF_HEAT_CURVE_DISPLACE_ENTITY = "heat_curve_displace_entity"` and
`CONF_HEAT_CURVE_TARGET_KIND = "heat_curve_target_kind"` in const.py beside const.py:693; matching
`EntryConfig` keys beside entry_config.py:213 (`""` and `"offset"`); two `_F("heat_curve", ...)` rows after
config_flow.py:1752, the entity suggesting empty for the reason at config_flow.py:1745-1750, domains `number`,
`input_number` (`_entity_of`, config_flow.py:1040; `climate` is excluded, its target is absolute). The first build
accepts only `offset` for the kind, so (b) adds a value, not a key or a migration. The existing
`ecl110_displace_min/max` and `ecl110_pid_time_constant_hours` keys govern the arm; **no key is renamed**, the
page title loses "(ECL110)". `ECL110_TOPIC_SLOTS` gains the entity key so both diagnostic sensors enable for an
entity-only install.

**(a) Kind `offset`: zero-neutral and volatile (first build).** Invariants:
- T1 the target's neutral value is 0: written value = `displace_int`, as a temperature difference (identity for
  `K`, `°C`, `C`, `degC` or no unit; ×9/5 for `°F`, `F`, `degF`; any other unit refused).
- T2 the config flow refuses kind `offset` on an entity whose own `min`/`max` exclude 0. That catches an absolute
  curve point (for example a range 20…70) at save time; it cannot prove volatility, which is the user's declaration,
  stated as a requirement in docs/ecl110.md.
- T3 persistent controller parameters are **out of scope for kind `offset`**, in this design and in the docs.
- T4 MODE_OFF and unload write nothing, the 2026-09-26 ruling (pump_arbiter.py:1131-1133). A volatile target falls
  back by itself on a controller restart.

**(b) Kind `persistent`: a stored controller parameter (follow-up, specified here).** For a curve parameter the
controller keeps in non-volatile memory, such as a single "parallel shift" parameter if U4 holds as an offset or
a foot point the user accepts as approximate (A2). Invariants:
- P1 **baseline captured at enable**: when the options flow saves kind `persistent` (or a new entity under it),
  it reads the entity's current value and stores it as `heat_curve_baseline` in the options, shown and editable on
  the same page. No Store: the options are the record, and an entity change re-captures.
- P2 written value = `baseline + displace`, clamped to `baseline ± heat_curve_persistent_band` (option, default
  narrow, the user's choice; the band bounds what a crash can leave behind) and to the entity's own min/max,
  on its step.
- P3 **restore**: the coordinator writes `baseline` on MODE_OFF, on unload while `hass.is_stopping` is false
  (option change, option removal, kind change, entry disable), and in `async_remove_entry` (__init__.py:429). A
  Home Assistant shutdown does not restore: the next start resumes within one cycle, and a restore there would
  cost two writes per restart. A crash leaves at most `baseline ± band`, the documented limit. Restores bypass the
  budget and dwell (P4, P5) and are counted.
- P4 a **daily write budget**, `heat_curve_persistent_writes_per_day` (option, low default). A write past it is
  refused until local midnight; the refusal is documented behaviour, shown as a diagnostics attribute, logged at
  INFO once per day, not a defect latch.
- P5 a **minimum dwell** between two writes, `heat_curve_persistent_min_dwell_minutes` (option). A changed
  target inside the dwell waits for the next publish after it; peak-guard nudges, boost and mode changes are
  subject to it too. No source in reach states the parameter memory's endurance; neither default may be presented
  as derived from one.
- P6 **edits at the controller**: a reading that matches neither the last written value nor the value before it,
  after the grace (W2), is a person's edit. The arm adopts it: `baseline = reading − last displace`, rewrites the
  stored baseline in the options, logs INFO, and does not overwrite it. A reading equal to the value before the
  write is a refusal: W3 applies.
- P7 a baseline outside the entity's range, or no readable value at enable, refuses the save.

## Shape

```
plan / fixed mode / boost / peak guard ──► async_publish_ecl110_command (coordinator.py:7677)
   + curve bias, clip(ecl110_displace_min, ecl110_displace_max), round ──► displace_int
before: _publish_ecl110_topics(hass, set_topic, command_topic, qos, retain, displace_int, payload)
after:  heat_curve.publish(hass, ctx._config, heat_curve.state_for(self), displace_int, payload)
          ├─ MQTT set topic, MQTT legacy topic (unchanged)
          └─ entity arm: kind offset -> displace_int        (a)
                         kind persistent -> baseline + d     (b, follow-up; restore hook on OFF/unload/remove)
```

**Mapping.** Never through the absolute set-point helpers (`write_setpoint_c`, `setpoint_range_c`,
`quantise_setpoint_c`, `read_setpoint`): `dev/programme/designs/generic-heat-curve-probes/k_unit_probe.py` (output
beside it) shows an entity in K reading −2 read as −275.15 °C and a −2 write sent as 271.15, because
`TEMPERATURE_UNIT_TO_C` maps `K` to −273.15 (const.py:225). Range is the entity's raw `min`/`max`; step
`inputs.setpoint_step` (inputs.py:539); the call `inputs.write_setpoint` (inputs.py:596), which takes a value in
the entity's own unit. Kind `persistent` (°C, absolute) may use the absolute helpers for its baseline arithmetic
only when the entity's unit is a temperature unit other than `K`.

## Write policy (R1b)

**W1–W6 are sized for volatile targets (kind `offset`).** They bound log noise and churn, not memory wear.
1. W1 write-on-change against the reading: no call while `|reading − target| ≤ step/2`.
2. W2 holds what it wrote, as pump_arbiter.py:59 states it: each write is recorded `(value, at)`; a differing
   reading inside the grace proves nothing; after it the first miss rewrites once (ghc-r05 on the grace constant).
3. W3 a second consecutive miss for the same target latches a warning via `log_held` (log_latch.py:28; the valve
   precedent at coordinator.py:7766) and stops rewriting that value until the target changes or the reading
   matches: a value the target clamps would otherwise be resent every cycle and never converge.
4. W4 a defect guard, `2 × 1440 / optimization_interval` writes per day; at `DEFAULT_OPTIMIZATION_INTERVAL`
   (const.py:1500) it does not bind in normal running. It guards a loop bug, not wear.
5. W5 the arm writes the same integer as the MQTT arms, exact on a 0.5 or 1 step.
6. W6 an entity range narrower than the configured displace range saturates the mapping; latched once, naming
   both ranges (`cfg_mk1_offset` is −5…5, registers.py:413-423, against the −20…20 default).
7. W7 with the entity option empty, every MQTT payload, sensor and golden is byte-identical; no planner change.

**Kind `persistent`** adds P4 and P5 on top of W1, W3, W5, W6, and replaces W2's rewrite-on-miss by P6.

**Interactions.** Fixed modes, boost, peak guard and curve bias reach both kinds through the chokepoint. MODE_OFF
writes nothing for (a) and restores for (b). Only `_apply_action` checks plan staleness (coordinator.py:7797-7808);
the peak-guard transition (coordinator.py:8846-8870) and a mode change (climate.py:291-296 → coordinator.py:7712)
publish without it, as for MQTT today. **Changed for the user:** curve learning on an entity-only install now moves
the real pump, where with no topic it moved nothing.

**Failure handling.** Entity absent, `unknown`/`unavailable`, wrong domain, unknown unit or a raising service: no
write, a latched reason, the cycle unaffected (each arm swallows its own failure, as coordinator.py:3177-3180
states for MQTT); the MQTT arms run first. The config flow refuses the entity when it equals any other written
entity (ghc-r03).

## Alternatives, and why each lost

- **A1. Two persistent curve points (end point and parallel shift), both moved by d.** Two non-atomic writes per
  change with a transient tilt between them, two non-volatile writes per change, and a two-point baseline the
  integration would own. Holds whatever U4 turns out to be. Lost on call count and state ownership.
- **A2. One persistent shift parameter through the same slot** (kind `persistent`). If U4 makes it an offset, a
  write is a true parallel shift and the geometric objection does not apply. If it is a foot point, writing
  `baseline + d` rotates the curve about the end point (shift `d·(x − x_end)/(x_base − x_end)` at outdoor x, under
  U3), so only the base point moves by d. Either way its remaining costs are persistence, baseline and wear,
  which P1–P7 answer. Not rejected: deferred to the follow-up, behind U4 and `decision: owner`.
- **B. A new `space_setpoint_unit` "offset" on the arbiter's slot.** The arbiter's value is per duty and per
  one-minute tick, and the displace chain does not pass through it: two owners of one concern. Lost on coupling.
- **B2. Two slots, one per kind.** Two writers on one concern, the objection to B. Lost on coupling.
- **C. No code: a user automation** mirroring a dummy `ecl110_displace_set_topic` into the number. Needs a
  broker, adds a writer outside the optimizer, and has none of W1–W6 or P1–P7. The answer if the owner declines.

## Sibling sites (step 5)

`grep -n "displace_value\|_publish_ecl110_topics\|ECL110_TOPIC_SLOTS\|ecl110_displace_set_topic\|_ecl110_displace_max\|_ecl110_displace_min" custom_components/heatpump_optimizer/*.py`

| Site | Disposition |
|---|---|
| coordinator.py:7702-7710, the topic call | replaced by `heat_curve.publish` |
| coordinator.py:3137, :3168 | moved verbatim to heat_curve.py |
| coordinator.py:4042, :4045 (`_ecl110_displace_set_topic`, `_ecl110_retain`) | read from `ctx._config`; both stores deleted (payment) |
| sensor.py:64, :1332, :1352 | slot tuple gains the entity key |
| coordinator.py:4046-4047, 4073-4079, 4156, 6081, 6547-6549, 7689-7691, 8860; boost.py:346; optimizer.py:5796, 5837, 5873 | upstream of the integer; unchanged |
| climate.py:235, sensor.py:862, coordinator.py:8114, payload.py:161 | readouts of the plan value; unchanged |
| coordinator.py:4511 (`curve_driven`), 6834-6835 (lag) | read the action, not the arm; unchanged |
| const.py:693, entry_config.py:213 | the new keys go beside them |
| (b) only: `async_unload_entry` (__init__.py:401), `async_remove_entry` (:429), MODE_OFF in coordinator.py:7714 | restore hook |

## Evidence plan (by file), first build (a)

- **Failing test first**, `tests/features.py` beside the `_publish_ecl110_topics` block (tests/features.py:40444):
  no topic, kind `offset`, entity `number.x` (unit K, −20…20, step 0.5, state 0);
  `async_publish_ecl110_command(5.0, True)` makes exactly one `number.set_value` with value 5. Red at base.
- Arms: K −2 sent as −2 (red if routed through `write_setpoint_c`, per the probe); °F ×1.8; entity −5…5 with
  displace 8 sends 5 and latches W6; W1 equal reading, no call; W2 inside grace no call, after grace one rewrite;
  W3 a second miss, no third call, a new target writes; W4; missing / unavailable / `sensor` domain / unit `%` /
  raising service, no write while the MQTT arm still publishes; MODE_OFF no call; peak-guard engage plan − nudge,
  release plan; boost maximum; curve bias applied.
- **Null control:** the option empty: identical `mqtt.publish` calls and payloads, no `number` call; the tests at
  tests/features.py:40498 and :40578 stay green except the import.
- `tests/config_flow_steps.py`: selector domains, kind `persistent` refused in the first build, T2 (range excluding
  0 refused), the cross-page refusals (ghc-r03), empty default; the config-flow floor in
  `tests/coverage_budgets.json` holds.
- **Goldens:** none move (W7); no claim file is touched.
- **Mutation targets** (heat_curve.py): the W1 comparator, the delta conversion, the clamp, the grace check, the W3
  give-up, the W4 guard, T2. New sites killed or triaged (`tests/mutation_budgets.json`).
- **Kind (b)**, in its later group, owes beyond these: P1 capture at save; P2 band clamp; P3 restore on OFF, on unload with and
  without `is_stopping`, on removal; P4 refusal past the budget with restores exempt; P5 dwell; P6 an edit adopted
  and not overwritten, a refusal treated as W3; P7. Carry: generic-heat-curve (item ghc-06)

## Cost against the ratchet, and how it is paid

`tests/structure_budgets.json` sits at zero headroom on every metric at base (`tests/structure.py` at `28d46c49`).
No coordinator method or attribute is added; heat_curve.py stays under `GOD_CLASS_LOC_LIMIT`. Payment: the shorter
call and the two deleted stores lower `class_excess_loc`, `max_class_loc` and `coordinator_attrs`; the moved
helpers leave the coordinator's helper count. Watch `duplication_copies` (do not clone `_command_valve_target`'s
epsilon-and-latch block) and `functions_cc_over_15` (split `write_displace` into read, convert, decide). Follow-up
(b)'s restore hook in `async_publish_current_action` and unload costs coordinator lines; it is paid in its own
group. No raise is expected; one needs the owner (CLAUDE.md, rule 2).

## Docs

`docs/ecl110.md`: "Without MQTT: a number entity" (option, kind `offset` contract T1–T4, delta units, W1–W6, the
Luxtronik SHI example with U1, U2 and ghc-r04 stated); `docs/configuration.md:358` page row; `README.md:243` surface
row and the "ECL110 control is MQTT-only" limit at README.md:273; `strings.json`, `translations/en.json`,
`translations/sv.json`. Follow-up (b) adds its own section with P1–P7 and the no-endurance-source caveat.

## Hot files and serial position

coordinator.py, config_flow.py, const.py, entry_config.py, sensor.py, diagnostics.py, strings and translations,
docs/ecl110.md, docs/configuration.md, README.md, tests/features.py, tests/config_flow_steps.py, heat_curve.py; (b)
adds `__init__.py`. `design/R10-USER-DOCS-FINAL` edits docs/ecl110.md and docs/configuration.md: this group goes
after it. `design/r10-livestate` touches `_async_handle_ecl110_state_message`, a different seam: no edge. Roster
group, size (L by file count, M by logic), and (b) as its own later group are `decision: orchestrator`.

## Notes for the fixer

- `write_setpoint` sends an integer when the stepped value is whole (inputs.py:612); read it back in the test.
  Carry: generic-heat-curve (item ghc-01)
- tests/features.py:40606-40609 read `_ecl110_displace_set_topic` off the coordinator; re-point them at
  `EntryConfig` when the store is deleted. Carry: generic-heat-curve (item ghc-02)
- docs/ecl110.md's last paragraph says the effective displace lets "the model price the heat that has actually
  arrived"; `ecl110_effective_displace` is read only by sensor.py:1355, climate.py:236 and coordinator.py:8116.
  Carry: dismissed: documentation claim outside scope, for a D6 round (item ghc-03)
- sensor.py:63 and config_flow.py:1750 cite `coordinator._ecl110_topic`, which no longer exists. Carry: dismissed:
  stale comment outside scope, for a D5 round (item ghc-04)
- Questions only the owner or the user can answer: build at all, and (a) only versus (a) then (b)
  (`decision: owner`); for (b), restore the baseline on OFF and unload as P3 specifies, against the 2026-09-26
  "off writes nothing" ruling, which (a) keeps (`decision: owner`); U1 and U4 measured on the reference
  installation before the docs name the Luxtronik example (the user). Carry: generic-heat-curve (item ghc-05)
- Only `_apply_action` checks staleness (coordinator.py:7797-7808); the peak-guard transition
  (coordinator.py:8846-8870) and a mode change (climate.py:291-296 → coordinator.py:7712-7720) publish without it.
  Unchanged from MQTT, but the docs must not promise "a stale plan writes nothing". Carry: generic-heat-curve
  (item ghc-r01)
- `log_held` is log_latch.py:28 and the valve precedent coordinator.py:7766; note 1 cited coordinator.py:700, which
  is `_valve_write_problem`. Corrected in §Write policy. Carry: generic-heat-curve (item ghc-r02)
- The equal-entity refusal is cross-page: judge it also where the other half is saved: the entities page
  (config_flow.py:1590), the building page (:1693), the pre-fill save (`_prefill_errors`, config_flow.py:2165-2200)
  and the DHW set-point entity (:1667). Carry: generic-heat-curve (item ghc-r03)
- After a controller restart `cfg_heating_mode` can fall back to off (luxtronik_shi README.md:229-231); W1 rewrites
  the offset, the reading matches, and the offset has no effect under U2. The arm cannot detect it; docs/ecl110.md's
  Luxtronik example must say so. Carry: generic-heat-curve (item ghc-r04)
- W2 reuses `ECHO_GRACE_S`, calibrated for the Tuya fork's 8 s sent-value window (pump_arbiter.py:186-188). State
  in code why it fits an SHI number, or give the arm its own constant. Carry: generic-heat-curve (item ghc-r05)
- heat_curve.py and any new test script are new tracked files: classify them in `tests/closures.json` (re-derive on
  Linux, `gate-scoping.md`) or on `tests/closure.py`'s INERT list, or `tests/entities.py` refuses.
  Carry: generic-heat-curve (item ghc-r06)
- python-luxtronik is cited at `02afea84bd5bf3ee87445de6f2a42b8029983169` (2026-03-22), verified by
  `git -C /home/claude/shi-re/pylux/src log -1`; name that commit, not an unnamed copy, where the docs quote it.
  Carry: generic-heat-curve (item ghc-r07)
