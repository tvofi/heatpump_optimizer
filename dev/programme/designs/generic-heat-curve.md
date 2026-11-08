# generic-heat-curve design note (designer seat, note 5)

The group's architect note, extended (`dev/governance/roles/designer.md`). It lives on `design/generic-heat-curve`
and never merges. **There is no finding and no finder harness: the evidence is a user's feature request** (an
alpha innotec LWDV 91-1/3 owner, Luxtronik firmware 3.92.3). No roster group exists, so there are no predecessors
and no `after` briefs. `dev/governance/dimensions/D12.md` (Traps) classes a new control surface as a product
request: whether to build it was `decision: owner`, settled by the owner on 2026-11-07 (note 4).

**State of the design.** Kind `offset` is the first build (§Target contract (a)); kind `persistent` is a sketch
whose later group owes its own design note and design review (§Target contract (b)). The fixer carries are in
§Notes for the fixer (ghc-r01…r08, ghc-01…05); ghc-r09 (instrument and outdoor temperature of the measurements) is
resolved in U1, ghc-r10 (leftover wording that made `persistent` more than a sketch) throughout. The user asked
for "both" kinds and for use beyond his install.

**Owner decisions** (tvofi, 2026-11-07, comment on PR tvofi/heatpump_optimizer#3284):
- The feature is accepted for this round.
- Kind `offset` is built first, from this note, through the single displace path.
- Kind `persistent` follows in the same round with its **own design note and design review**. That note must solve
  O1–O4 and take its defaults (band, daily write budget, minimum dwell) from a sourced study across many
  controllers, not only Luxtronik (O5).
- The 2026-09-26 ruling "off writes nothing" is **retracted**: kind `offset` writes a neutral 0 on MODE_OFF and on
  unload; kind `persistent` restores its captured baseline; the pump arbiter's space set-point also restores the
  user's value on off.

**Author additions** (not owner decisions; open for the owner): see T4. **Separate item:** the arbiter restore is
not part of this note's first build (§Sibling sites).

**Read at.** `origin/main` = `28d46c4918285d36c409c1fb2f72eb77e04e569e`, unchanged since note 1. Outside the tree,
read-only: the user's `luxtronik_shi` at `362955143b58da2dc037981bd3266cd409463831` (`registers.py`, `README.md`; every line number cited below was verified at this commit),
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
`luxtronik_shi` exposes it as `cfg_heating_offset` (registers.py:402-414, −20…20 K, step 0.5) and quotes
python-luxtronik that SHI holdings are volatile (README.md:425, :438).

**Recommendation.** Build one slot with a declared target kind. **First build: kind `offset`** (§Target contract
(a)). **Kind `persistent` is a later group in the same round** sketched in (b), not part of the first build and
not build-level: its group owes its own design note and design review before any fixer starts. Never two
slots, and never writes of two curve points (A1). **Owner decision (tvofi, 2026-11-07, PR #3284):** the feature
is accepted for this round, `offset` first, `persistent` after with its own note and review; the zero-code
stopgap C is no longer the answer.

**Assumptions the tree cannot verify.**
- U1: `heating_offset` acts as a parallel shift of the return-target curve on FW 3.92.3. **Measured by the user**
  on the reference installation (LWDV 91-1/3, FW 3.92.3, `luxtronik_shi`; SHI heating mode holding 10000 =
  `offset`, heating offset holding 10002). Instrument: `luxtronik_shi` sensor key `return_target` (SHI input
  register 10101, registers.py:189 at the pinned `luxtronik_shi` commit), entity `sensor.lwdv_shi_return_target`, resolution
  0.1 K.
  - M1, 2026-11-07 14:18 local, outdoor 5.7–5.8 °C: offset +2 K, return target 27.7 → 29.7 °C; mode set back to
    `off`: 27.7 °C again; the offset was then set to 0 with the mode left at `offset`.
  - M2, 2026-11-08 12:17 local, outdoor 7.6 °C: baseline 27.2 °C; offset +1 K → 28.2 °C; offset 0 → 27.2 °C.
  Result: at two outdoor temperatures and two offset values the offset shifted the return target by the offset,
  within the 0.1 K resolution. This covers **5.7–7.6 °C outdoor only**; other, colder outdoor temperatures stay open. It says nothing
  about the shape of the curve (U3).
- U2: it applies only while `cfg_heating_mode` = offset, which the optimizer does not own; mode setpoint, which
  the arbiter's space set-point on this controller needs (`luxtronik_shi` README, "Heating setpoint (reg. 10001)"),
  excludes it.
- U3: the Luxtronik curve between its two points is linear. **Unverified, and contradicted by the user's
  statement (2026-11-07) that the curve itself is not linear** while the offset shift (U1) is. No source in reach
  states its shape; nothing below may rely on linearity.
- U4: what the persistent "parallel shift" parameter is on FW 3.92.3, a foot point (absolute return temperature at
  a warm reference) or a whole-curve offset. python-luxtronik gives no semantics for indices 1
  (`ID_Einst_WK_akt`), 11, 12 (`ID_Einst_HzHKRANH_akt`) and 13 (`ID_Einst_HzHKRABS_akt`): all `Celsius`, `°C/10`,
  `description: ''` (parameters.py:60-69, 158-187). **One operating point measured** on the reference
  installation (parameter index 12 `ID_Einst_HzHKRANH_akt`, entity
  `number.luxtronik_341120_089_heating_curve_parallel_shift_temperature` "Heiz Heizkurve Parallelverschiebung",
  written through the BenPru luxtronik2 integration, port 8889; the controller screen shows end point 30 °C and
  this parameter 22 °C), 2026-11-08 12:36 local, outdoor 7.9 °C, resolution 0.1 K. User-run procedure: SHI mode `offset` with SHI
  offset 0 (so the SHI offset does not interfere); the reading was taken about 90 s after the write: baseline return target 27.2 °C; parameter 22 → 23 °C; after about 90 s
  return target 28.4 °C (+1.2 K); parameter back to 22 °C: 27.1 °C at 8.0 °C outdoor.
  - Reading: +1 K on the parameter moved the return target by about +1.2 K at 7.9 °C; +1.2 is not +1.0, so one
    point does not decide between a foot point and a parallel shift. The curve is non-linear (user statement,
    U3), so no model of it is assumed here.
  - User statement (2026-11-07, not a measurement): the parameter is a real offset.
  - Still open: one point, no second outdoor temperature, no check of the end-point parameter. The semantics of
    the parameter are not otherwise stated here.

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
- T2 a **plausibility check**, not proof: the config flow refuses kind `offset` on an entity whose own `min`/`max`
  exclude 0. It catches an absolute curve point only when the exposing integration declares a tight range (for
  example 20…70); an absolute entity whose declared range includes 0 passes. The behaviour when the entity is
  unavailable at save time is open (ghc-r08). Volatility is the user's declaration, stated as a requirement in
  docs/ecl110.md, and that declaration carries the contract.
- T3 persistent controller parameters are **out of scope for kind `offset`**, in this design and in the docs.
- T4 MODE_OFF and unload write the neutral 0. **Owner decision (tvofi, 2026-11-07)** retracting the 2026-09-26
  "off writes nothing" ruling (pump_arbiter.py:1131-1133): the user's offset is not left at the last displace. A
  volatile target also falls back by itself on a controller restart. **Author additions, not owner decisions, open
  for the owner:**
  - The unload write needs a hook in `async_unload_entry` (__init__.py:401), which costs lines there.
  - It must run after the coordinator is torn down, so that no later publish overwrites it.
  - There is no `hass.is_stopping` carve-out for kind `offset`: the write happens on **every** unload, so a Home
    Assistant shutdown is one write. Proposal (author, the safer reading for the heating): keep it, best effort,
    because a stale displace left on the pump is the worse outcome; the alternative is to skip it while Home
    Assistant stops, as (b)'s P3 sketch does. Open for the owner.
  - The arbiter's space set-point restore on off is a separate item (§Sibling sites).

**(b) Kind `persistent`: a stored controller parameter (sketch only, own note and review in the same round, owner
decision 2026-11-07).** For a curve parameter
the controller keeps in non-volatile memory, such as a single "parallel shift" parameter if U4 holds as an offset
or a foot point the user accepts as approximate (A2). **P1–P7 are a sketch, not a design on record**: the later
group owes its own design note and design review before any fixer starts, starting from P1–P7 and solving O1–O4 listed
after them, with the O5 defaults taken from a sourced study across many controllers, not only Luxtronik. Sketch:
- P1 **baseline captured at enable**: when the options flow saves kind `persistent` (or a new entity under it),
  it reads the entity's current value and stores it as `heat_curve_baseline` in the options, shown and editable on
  the same page. No Store: the options are the record, and an entity change re-captures.
- P2 written value = `baseline + displace`, clamped to `baseline ± heat_curve_persistent_band` (option, default
  open, O5; the band bounds what a crash can leave behind) and to the entity's own min/max,
  on its step.
- P3 **restore**: the coordinator writes `baseline` on MODE_OFF, on unload while `hass.is_stopping` is false
  (option change, option removal, kind change, entry disable), and in `async_remove_entry` (__init__.py:429). A
  Home Assistant shutdown does not restore: the next start resumes within one cycle, and a restore there would
  cost two writes per restart. A crash leaves at most `baseline ± band`, the documented limit. Restores bypass the
  budget and dwell (P4, P5) and are counted.
- P4 a **daily write budget**, `heat_curve_persistent_writes_per_day` (option, default open, O5). A write past it is
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

**Open problems the later group's note must solve** (design review V1 of dd331b64; the options listener reloads
the entry on any changed option, __init__.py:345 and :372-398; O1–O4 are the owner's required solves, 2026-11-07):
- O1 P6 writes the baseline into the options, which triggers a reload; each reload costs a restore (P3) plus a
  rewrite of `baseline + d`, and any other options save while kind `persistent` is active costs the same.
- O2 the budget and dwell state (P4, P5) lives per coordinator and does not survive a reload or a restart, so P4 is
  not a budget across either.
- O3 baseline capture after a crash: an entity left at `baseline ± band` is read back as a new baseline by P1;
  nothing detects or prevents it.
- O4 two restore hooks with no single owner: `async_remove_entry` (__init__.py:429) runs after the unload, finds no
  coordinator and duplicates the unload restore.
- O5 the band, budget and dwell defaults have no numbers and no source in reach derives them. Owner decision
  (2026-11-07): they come from a sourced study across many controllers, not only Luxtronik; until it exists they
  stay open.

## Shape

```
plan / fixed mode / boost / peak guard ──► async_publish_ecl110_command (coordinator.py:7677)
   + curve bias, clip(ecl110_displace_min, ecl110_displace_max), round ──► displace_int
before: _publish_ecl110_topics(hass, set_topic, command_topic, qos, retain, displace_int, payload)
after:  heat_curve.publish(hass, ctx._config, heat_curve.state_for(self), displace_int, payload)
          ├─ MQTT set topic, MQTT legacy topic (unchanged)
          └─ entity arm: kind offset -> displace_int        (a)
                         kind persistent -> baseline + d     (b, later group; restore hook on OFF/unload/remove)
```

**Mapping.** Never through the absolute set-point helpers (`write_setpoint_c`, `setpoint_range_c`,
`quantise_setpoint_c`, `read_setpoint`): `dev/programme/designs/generic-heat-curve-probes/k_unit_probe.py` (output
beside it) shows an entity in K reading −2 read as −275.15 °C and a −2 write sent as 271.15, because
`TEMPERATURE_UNIT_TO_C` maps `K` to −273.15 (const.py:225). Range is the entity's raw `min`/`max`; step
`inputs.setpoint_step` (inputs.py:539); the call `inputs.write_setpoint` (inputs.py:596), which takes a value in
the entity's own unit. A later design for kind `persistent` may use the absolute helpers only when the entity's unit
is a temperature unit other than `K`; that is not permitted in the first build.

## Write policy (R1b)

**W1–W7 are sized for volatile targets (kind `offset`).** They bound log noise and churn, not memory wear.
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
   both ranges (`cfg_mk1_offset` is −5…5, registers.py:453-463, against the −20…20 default).
7. W7 with the entity option empty, every MQTT payload, sensor and golden is byte-identical; no planner change.

**Kind `persistent`** adds P4 and P5 on top of W1, W3, W5, W6, and replaces W2's rewrite-on-miss by P6.

**Interactions.** Fixed modes, boost, peak guard and curve bias reach both kinds through the chokepoint. MODE_OFF
writes the neutral 0 for (a) and restores the baseline for (b) (owner decision, 2026-11-07, retracting "off writes
nothing"); the arbiter's space set-point restores the user's value on off. Only `_apply_action` checks plan staleness (coordinator.py:7797-7808);
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
  which the later group's note must answer from the P1–P7 sketch and O1–O5. Not rejected: it is kind `persistent`, built in the later group with its own note, behind U4.
- **B. A new `space_setpoint_unit` "offset" on the arbiter's slot.** The arbiter's value is per duty and per
  one-minute tick, and the displace chain does not pass through it: two owners of one concern. Lost on coupling.
- **B2. Two slots, one per kind.** Two writers on one concern, the objection to B. Lost on coupling.
- **C. No code: a user automation** mirroring a dummy `ecl110_displace_set_topic` into the number. Needs a
  broker, adds a writer outside the optimizer, and has none of W1–W7 or P1–P7. Rejected: the owner accepted the feature (2026-11-07).

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
| pump_arbiter.py:78, :106, :1131-1133 (restore of the space set-point on off, owner decision 2026-11-07) | **not this build**: a separate item owed by its own group, which also owes the stale "off writes nothing" comments at pump_arbiter.py:78, :106, :1132 and coordinator.py:3768, :4533, :7795, :8855; coordinator.py:7714 changes here |
| `async_unload_entry` (__init__.py:401) and MODE_OFF in coordinator.py:7714: neutral-0 write for (a), T4; (b) only: `async_remove_entry` (:429) | restore hook; (b)'s ownership is O4 |

## Evidence plan (by file), first build (a)

- **Failing test first**, `tests/features.py` beside the `_publish_ecl110_topics` block (tests/features.py:40444):
  no topic, kind `offset`, entity `number.x` (unit K, −20…20, step 0.5, state 0);
  `async_publish_ecl110_command(5.0, True)` makes exactly one `number.set_value` with value 5. Red at base.
- Arms: K −2 sent as −2 (red if routed through `write_setpoint_c`, per the probe); °F ×1.8; entity −5…5 with
  displace 8 sends 5 and latches W6; W1 equal reading, no call; W2 inside grace no call, after grace one rewrite;
  W3 a second miss, no third call, a new target writes; W4; missing / unavailable / `sensor` domain / unit `%` /
  raising service, no write while the MQTT arm still publishes; MODE_OFF one write of 0, and one on every unload (T4); peak-guard engage plan − nudge,
  release plan; boost maximum; curve bias applied.
- **Null control:** the option empty: identical `mqtt.publish` calls and payloads, no `number` call; the tests at
  tests/features.py:40498 and :40578 stay green except the import.
- `tests/config_flow_steps.py`: selector domains, kind `persistent` refused in the first build, T2 (range excluding
  0 refused), the cross-page refusals (ghc-r03), empty default; the config-flow floor in
  `tests/coverage_budgets.json` holds.
- **Goldens:** none move (W7); no claim file is touched.
- **Mutation targets** (heat_curve.py): the W1 comparator, the delta conversion, the clamp, the grace check, the W3
  give-up, the W4 guard, T2. New sites killed or triaged (`tests/mutation_budgets.json`).
- **Kind (b)** has no evidence plan here: its later group's own design note owes one, with O1–O5 solved first.

## Cost against the ratchet, and how it is paid

`tests/structure_budgets.json` sits at zero headroom on every metric at base (`tests/structure.py` at `28d46c49`).
No coordinator method or attribute is added; heat_curve.py stays under `GOD_CLASS_LOC_LIMIT`. Payment: the shorter
call and the two deleted stores lower `class_excess_loc`, `max_class_loc` and `coordinator_attrs`; the moved
helpers leave the coordinator's helper count. Watch `duplication_copies` (do not clone `_command_valve_target`'s
epsilon-and-latch block) and `functions_cc_over_15` (split `write_displace` into read, convert, decide). The
neutral-0 write on unload (T4) costs lines in unload and is paid inside heat_curve.py; (b)'s restore hook in
`async_publish_current_action` costs coordinator lines and is paid in its own group. No raise is expected; one needs the owner (CLAUDE.md, rule 2).

## Docs

`docs/ecl110.md`: "Without MQTT: a number entity" (option, kind `offset` contract T1–T4, delta units, W1–W7, the
Luxtronik SHI example with U1, U2 and ghc-r04 stated); `docs/configuration.md:358` page row; `README.md:243` surface
row and the "ECL110 control is MQTT-only" limit at README.md:273; `strings.json`, `translations/en.json`,
`translations/sv.json`. The later group for kind `persistent` writes its own docs section from its own note.

## Hot files and serial position

coordinator.py, config_flow.py, const.py, entry_config.py, sensor.py, diagnostics.py, strings and translations,
docs/ecl110.md, docs/configuration.md, README.md, tests/features.py, tests/config_flow_steps.py, heat_curve.py; `__init__.py` (the unload write of T4, kind `offset`); (b)'s
later group adds the restore hook there too. pump_arbiter.py is not touched by this build. `design/R10-USER-DOCS-FINAL` edits docs/ecl110.md and docs/configuration.md: this group goes
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
- Settled by the owner (tvofi, 2026-11-07): build, `offset` first and `persistent` later with its own note; off
  and unload write the neutral 0 for `offset` (T4). Still the user's to measure before the docs name the Luxtronik
  example: U1 at colder outdoor temperatures (measured only at 5.7–7.6 °C) and U4 (one point only). The docs'
  Luxtronik example quotes M1, M2 and the instrument `return_target` with their outdoor temperatures. Carry:
  generic-heat-curve (item ghc-05; ghc-r09 and ghc-r10 are folded into this note)
- Only `_apply_action` checks staleness (coordinator.py:7797-7808); the peak-guard transition
  (coordinator.py:8846-8870) and a mode change (climate.py:291-296 → coordinator.py:7712-7720) publish without it.
  Unchanged from MQTT, but the docs must not promise "a stale plan writes nothing". Carry: generic-heat-curve
  (item ghc-r01)
- `log_held` is log_latch.py:28 and the valve precedent coordinator.py:7766; note 1 cited coordinator.py:700, which
  is `_valve_write_problem`. Corrected in §Write policy. Carry: generic-heat-curve (item ghc-r02)
- The equal-entity refusal is cross-page: judge it also where the other half is saved: the entities page
  (config_flow.py:1590), the building page (:1693), the pre-fill save (`_prefill_errors`, config_flow.py:2165-2200)
  and the DHW set-point entity (:1667). Carry: generic-heat-curve (item ghc-r03)
- After a controller restart `cfg_heating_mode` can fall back to off (luxtronik_shi README.md:438); W1 rewrites
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
- T2 is only as strong as the exposing integration's declared range. A `number` that declares no range most likely
  gets Home Assistant's default range; that is unverified at this SHA (Home Assistant is not installed in the CI
  venv). Define T2 when the entity is unavailable at save time, and re-check the range at runtime under W6.
  Carry: generic-heat-curve (item ghc-r08)
