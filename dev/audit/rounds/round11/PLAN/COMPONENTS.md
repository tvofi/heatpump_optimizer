# Round 11 plan: component view, triage and groups

Steps 1, 3 and 4 of `dev/governance/roles/architect-planner.md`, drawn at the
fork `92d38ecb640bd462f2e19c0814d0f0b7df1ee692` from the package's own import
statements and the 220 judged findings in `../JUDGE.json`. Step 2 is
`SCENARIOS.md`. The machine copy of the groups is `groups.json`;
`seam-groups.json` is P2's draft, kept as the input it was.

## Component view

Thirteen owning seams. A module is listed under the seam that owns its concern;
`coordinator.py` (11,415 lines, 63 package imports) is the cycle seam and still
holds code of six others, which is where most hot-file contention comes from.

| seam | owns | modules |
|---|---|---|
| shared kernel | small rules with no dependency: constants, the step covering an instant, elapsed time, latches | `const` `plan_step` `drift` `batchmath` `log_latch` `issues` `currency` |
| input boundary | every live value entering: unit scale, finiteness, age | `inputs` `entry_config` `pump_signals` `pump_mode` `running_signal` `open_meteo` `payload` `rooms` |
| persisted store | the schema of what is saved and what a load admits | `store` `snapshots` |
| plant model | physical laws and the plant's shape | `thermal_model` `mixing_valve` `flow_lift` `flow_meter` `defrost` `wood_fuel` `battery` `presets` `topology` `freq_control` `dhw_schedule` |
| learners | parameters fitted from observed intervals, and which intervals count | `sysid` `accuracy` `dhw_learning` `dhw_draws` `draw_range` `comfort_learning` `curve_learning` `heat_energy` `external_heat` `learner_progress` `slab_seed` `wear` |
| money | prices, fees, capacity windows, the ledger, currency | `price_model` `tariff` `grid_fee` `ledger` `price_tiles` `power_guard` |
| solver | the plan from inputs, model and money | `optimizer` `dhw_planner` `duty_legs` `runs` `slot_drivers` `manual_plan` `pv` `whatif` `plan_slots` `process_worker` |
| actuation | every write, hold and release on a pump entity | `pump_arbiter` `off_restore` `boost` `heat_curve` `duty_switch` `supply_hold` `early_cutoff` `legionella` `disinfection` `quiet_windows` `silent_mode` `setpoint_check` `pump_schedule` |
| cycle | when a solve runs, lifecycle, failure reporting | `coordinator` `__init__` `away` `notifier` `diagnosis` `narrative` `comfort_band` `driving_grade` |
| config surface | setup and options flows, where a setting is stored | `config_flow` `quick_setup` `device_prefill` `modbus_prefill` `prefill_offer` `name_match` |
| entity and service surface | entities, actions, repairs, diagnostics, product text | `sensor` `binary_sensor` `button` `switch` `climate` `datetime` `entity` `services` `repairs` `diagnostics` `debugger` `replay_doc` `strings.json` `translations/` |
| card | the dashboard card | `www/heatpump-optimizer-card.js` `frontend` |
| outside the package | test suite and ratchets (`tests/`); instruments (`tools/`, `.claude/`, `dev/audit/harnesses/`); reader docs (`README.md`, `docs/`); governance text (`dev/governance/`, `dev/programme/`) | |

### Calls between seams

- cycle calls every seam: `coordinator` imports 63 of the 95 other modules.
- solver reads plant model, money (`tariff`), kernel and `entry_config`; nothing
  in actuation, learners or the surfaces.
- actuation reads plant model, input boundary, store and kernel.
- learners read plant model and kernel; `sysid` also reads `quiet_windows`
  (actuation) and `mixing_valve`.
- money reads input boundary and kernel; `tariff` and `power_guard` read
  `accuracy` (learners).
- config surface reads plant model, money (`grid_fee`, `currency`), actuation
  (`heat_curve`, `freq_control`) and the cycle.
- entity and service surface reads the cycle and `payload`; `services` imports
  `config_flow`.

### Edges against the direction of ownership

- `off_restore` imports `coordinator`; the coordinator imports `off_restore`.
- `rooms` and `slot_drivers` import `optimizer`; `inputs` imports `rooms`, so
  the input boundary reaches the solver.
- `store` imports twelve learner and money modules to hold their schemas.
- `accuracy` imports `homeassistant.util.dt` and carries that boundary to
  `comfort_learning`, `external_heat`, `power_guard`, `sysid` and `tariff`
  (D7-s1-06; `layer_violations` 13 at the fork).
- `entry_config` imports `mixing_valve`; `services` imports `config_flow`.

### Seams with two owners

Each is a finding of its own and is planned at one owner.

| concern | owners at the fork | finding | planned owner |
|---|---|---|---|
| the plan step covering now | `coordinator._covering_index`, `pump_arbiter._step_index`, two copies with no end rule | D7-s3-03 | `plan_step` (kernel) |
| Carnot flow-lift factor | scalar `thermal_model.py:3391`, batch `:4483`, inverse of each other | D2-s1-01 | `thermal_model`, one expression |
| top-k capacity sum | `tariff` scalar takes the smallest, the batch twin the largest | D2-s3-06 | `tariff` |
| is the house two-zone | `ThermalParameters.from_config`, `coordinator._build_plan_views`, the options page, `set_thermal_parameters` | D12-s2-01, D12-s1-01, D17-s1-03, D17-s3-02 | `thermal_model` |
| may a learner ingest this interval | `coordinator._learning_frozen` and each learner's own test | D7-s2-01, D12-s3-03, D2-s3-08, D2-s3-09 | learners, one predicate |
| currency of a money figure | `coordinator` feed-first, `config_flow` instance currency | D14-s1-03 | `currency` |
| who restores a written entity | `off_restore`'s registered consumers, direct writes in `coordinator` and `pump_arbiter` with none | D16-s3-02, D16-s3-01, D16-s1-04 | `off_restore` registry |
| where a setting is stored | `entry.data` and `entry.options`, merged by every reader | D10-s1-03, D10-s2-01, D17-s2-05 | `entry.options`, by migration |
| store schema | `store.DOMAINS` and each writer's `as_dict` | D15-s1-04, D15-s1-05 | `store.DOMAINS` |
| unit scale of a live value | `inputs.normalize_temperature_c` and `temperature_from_c`; minor-unit price branch against its docstring | D7-s3-01, D2-s3-02 | `inputs` |
| block vocabulary of a verdict | `VERDICT_CLASSES` in `web-fix-wave.js`, `MECHANICAL_CLASSES` in `bus.sh` | D13-s2-01 | deferred with the instruments |

## Triage

220 findings: 152 keep, 23 merge, 40 defer,
5 refuse. Every id appears once here or in a group below.

The draft seamed each finding from the first module its mechanism names. That
put the price unit scale under learning, the stalled forecast under pricing,
a rule file under the entity surface and both arch-score prototypes under
tests; this triage re-seams by the concern's owner.

### Refused, back to the judge

| id | reason |
|---|---|
| D0-s3-03 | the judge refuted it: no credit breaches the tail floor at any learnable weight |
| D15-s2-04 | unreproduced at P2 |
| D15-s2-06 | unreproduced at P2 |
| D15-s2-07 | unreproduced at P2 |
| D7-s3-06 | unreproduced at P2 |

### Deferred to round 12

Instrument behaviour falls under the freeze. For comment-only edits to
instrument files two rulings meet: the freeze (card P11) and the 2026-11-13
text-scope ruling that this round covers instrument comments. This plan reads
the freeze as governing the fix and records that reading as **pending owner
confirmation**; if the owner rules the other way, the fourteen comment-only
rows and their ten merged rows become one text-only group with no edge.
D5-s6-02 (a docstring of `tools/audit/seat/replay_draws.py`) is one of the
fourteen: the first draft kept it in the tests group, which gave one kind of
edit two verdicts.

| id | reason |
|---|---|
| D0-s3-01 | instrument under the freeze (RULINGS.md, card P11): a local overlay in-round where it blocks, the permanent fix as a proposal triaged at round end and built at round 12's start |
| D11-s1-01 | instrument under the freeze (RULINGS.md, card P11): a local overlay in-round where it blocks, the permanent fix as a proposal triaged at round end and built at round 12's start |
| D11-s1-02 | instrument under the freeze (RULINGS.md, card P11): a local overlay in-round where it blocks, the permanent fix as a proposal triaged at round end and built at round 12's start |
| D11-s1-03 | instrument under the freeze (RULINGS.md, card P11): a local overlay in-round where it blocks, the permanent fix as a proposal triaged at round end and built at round 12's start |
| D11-s1-04 | instrument under the freeze (RULINGS.md, card P11): a local overlay in-round where it blocks, the permanent fix as a proposal triaged at round end and built at round 12's start |
| D11-s1-05 | instrument under the freeze (RULINGS.md, card P11): a local overlay in-round where it blocks, the permanent fix as a proposal triaged at round end and built at round 12's start |
| D11-s1-06 | instrument under the freeze (RULINGS.md, card P11): a local overlay in-round where it blocks, the permanent fix as a proposal triaged at round end and built at round 12's start |
| D11-s2-01 | instrument under the freeze (RULINGS.md, card P11): a local overlay in-round where it blocks, the permanent fix as a proposal triaged at round end and built at round 12's start |
| D11-s2-02 | a governance design question the owner ruled on (card X1: the mandate stays as is); round-end proposal triage decides whether a provenance marker is built in round 12 |
| D11-s2-03 | instrument under the freeze (RULINGS.md, card P11): a local overlay in-round where it blocks, the permanent fix as a proposal triaged at round end and built at round 12's start |
| D11-s3-02 | instrument under the freeze (RULINGS.md, card P11): a local overlay in-round where it blocks, the permanent fix as a proposal triaged at round end and built at round 12's start |
| D11-s3-03 | instrument under the freeze (RULINGS.md, card P11): a local overlay in-round where it blocks, the permanent fix as a proposal triaged at round end and built at round 12's start |
| D11-s3-04 | instrument under the freeze (RULINGS.md, card P11): a local overlay in-round where it blocks, the permanent fix as a proposal triaged at round end and built at round 12's start |
| D13-s2-01 | instrument under the freeze (RULINGS.md, card P11): a local overlay in-round where it blocks, the permanent fix as a proposal triaged at round end and built at round 12's start |
| D13-s2-02 | instrument under the freeze (RULINGS.md, card P11): a local overlay in-round where it blocks, the permanent fix as a proposal triaged at round end and built at round 12's start |
| D14-s1-02 | instrument under the freeze (RULINGS.md, card P11): a local overlay in-round where it blocks, the permanent fix as a proposal triaged at round end and built at round 12's start |
| D15-s1-03 | instrument under the freeze (RULINGS.md, card P11): a local overlay in-round where it blocks, the permanent fix as a proposal triaged at round end and built at round 12's start |
| D15-s2-01 | instrument under the freeze (RULINGS.md, card P11): a local overlay in-round where it blocks, the permanent fix as a proposal triaged at round end and built at round 12's start |
| D15-s2-02 | instrument under the freeze (RULINGS.md, card P11): a local overlay in-round where it blocks, the permanent fix as a proposal triaged at round end and built at round 12's start |
| D15-s2-03 | instrument under the freeze (RULINGS.md, card P11): a local overlay in-round where it blocks, the permanent fix as a proposal triaged at round end and built at round 12's start |
| D15-s2-05 | instrument under the freeze (RULINGS.md, card P11): a local overlay in-round where it blocks, the permanent fix as a proposal triaged at round end and built at round 12's start |
| D15-s3-02 | instrument under the freeze (RULINGS.md, card P11): a local overlay in-round where it blocks, the permanent fix as a proposal triaged at round end and built at round 12's start |
| D17-s1-01 | instrument under the freeze (RULINGS.md, card P11): a local overlay in-round where it blocks, the permanent fix as a proposal triaged at round end and built at round 12's start |
| D3-s2-01 | function-level closures are a redesign of the scoped gate, an instrument under the freeze (card P11); round-end proposal triage with its cost test, built at round 12's start |
| D5-s10-03 | comment-only edit to an instrument file, read as inside the freeze (RULINGS.md, card P11); the 2026-11-13 text-scope ruling put instrument comments in this round's verification, so the reading is pending owner confirmation; round-end proposal triage, built at round 12's start |
| D5-s10-06 | comment-only edit to an instrument file, read as inside the freeze (RULINGS.md, card P11); the 2026-11-13 text-scope ruling put instrument comments in this round's verification, so the reading is pending owner confirmation; round-end proposal triage, built at round 12's start |
| D5-s2-07 | instrument under the freeze (RULINGS.md, card P11): a local overlay in-round where it blocks, the permanent fix as a proposal triaged at round end and built at round 12's start |
| D5-s5-01 | comment-only edit to an instrument file, read as inside the freeze (RULINGS.md, card P11); the 2026-11-13 text-scope ruling put instrument comments in this round's verification, so the reading is pending owner confirmation; round-end proposal triage, built at round 12's start |
| D5-s5-04 | comment-only edit to an instrument file, read as inside the freeze (RULINGS.md, card P11); the 2026-11-13 text-scope ruling put instrument comments in this round's verification, so the reading is pending owner confirmation; round-end proposal triage, built at round 12's start |
| D5-s5-05 | comment-only edit to an instrument file, read as inside the freeze (RULINGS.md, card P11); the 2026-11-13 text-scope ruling put instrument comments in this round's verification, so the reading is pending owner confirmation; round-end proposal triage, built at round 12's start |
| D5-s5-06 | comment-only edit to an instrument file, read as inside the freeze (RULINGS.md, card P11); the 2026-11-13 text-scope ruling put instrument comments in this round's verification, so the reading is pending owner confirmation; round-end proposal triage, built at round 12's start |
| D5-s5-07 | comment-only edit to an instrument file, read as inside the freeze (RULINGS.md, card P11); the 2026-11-13 text-scope ruling put instrument comments in this round's verification, so the reading is pending owner confirmation; round-end proposal triage, built at round 12's start |
| D5-s6-01 | comment-only edit to an instrument file, read as inside the freeze (RULINGS.md, card P11); the 2026-11-13 text-scope ruling put instrument comments in this round's verification, so the reading is pending owner confirmation; round-end proposal triage, built at round 12's start |
| D5-s6-02 | comment-only edit to an instrument file, read as inside the freeze (card P11); pending owner confirmation against the 2026-11-13 text-scope ruling; round-end proposal triage |
| D5-s6-04 | comment-only edit to an instrument file, read as inside the freeze (RULINGS.md, card P11); the 2026-11-13 text-scope ruling put instrument comments in this round's verification, so the reading is pending owner confirmation; round-end proposal triage, built at round 12's start |
| D5-s6-05 | comment-only edit to an instrument file, read as inside the freeze (RULINGS.md, card P11); the 2026-11-13 text-scope ruling put instrument comments in this round's verification, so the reading is pending owner confirmation; round-end proposal triage, built at round 12's start |
| D5-s6-06 | comment-only edit to an instrument file, read as inside the freeze (RULINGS.md, card P11); the 2026-11-13 text-scope ruling put instrument comments in this round's verification, so the reading is pending owner confirmation; round-end proposal triage, built at round 12's start |
| D5-s6-07 | comment-only edit to an instrument file, read as inside the freeze (RULINGS.md, card P11); the 2026-11-13 text-scope ruling put instrument comments in this round's verification, so the reading is pending owner confirmation; round-end proposal triage, built at round 12's start |
| D5-s8-01 | comment-only edit to an instrument file, read as inside the freeze (RULINGS.md, card P11); the 2026-11-13 text-scope ruling put instrument comments in this round's verification, so the reading is pending owner confirmation; round-end proposal triage, built at round 12's start |
| D5-s8-07 | instrument under the freeze (RULINGS.md, card P11): a local overlay in-round where it blocks, the permanent fix as a proposal triaged at round end and built at round 12's start |

### Merged

| id | into | round | same root |
|---|---|---|---|
| D4-s2-02 | D10-s2-03 | 11 | same de.json row and placeholder as the canonical finding |
| D5-s10-01 | D5-s8-01 | 12 | pre-move path in an instrument; the canonical is deferred under the freeze |
| D5-s10-04 | D5-s8-01 | 12 | pre-move path in a harness docstring; the canonical is deferred under the freeze |
| D5-s10-05 | D5-s8-01 | 12 | pre-move path in a harness docstring; the canonical is deferred under the freeze |
| D5-s10-07 | D5-s5-07 | 12 | criterion C5 over hook and harness files; the canonical is deferred under the freeze |
| D5-s3-03 | D5-s4-01 | 11 | criterion C5 over production comments, no detector; one count over the seam |
| D5-s5-02 | D5-s8-01 | 12 | pre-move path in an instrument; the canonical is deferred under the freeze |
| D5-s5-03 | D5-s8-01 | 12 | pre-move path in an instrument; the canonical is deferred under the freeze |
| D5-s6-03 | D5-s8-01 | 12 | pre-move path in an instrument; the canonical is deferred under the freeze |
| D5-s6-08 | D5-s5-07 | 12 | criterion C5 over instrument and harness files; the canonical is deferred under the freeze, and test files among its cells are counted by D5-s9-04's detector |
| D5-s7-01 | D5-s9-04 | 11 | criterion C5 over tests/; its three dead names and false count are acceptance rows of the canonical |
| D5-s7-02 | D5-s9-04 | 11 | criterion C5 over tests/ |
| D5-s7-03 | D5-s9-04 | 11 | criterion C5 over tests/ |
| D5-s8-02 | D5-s8-01 | 12 | pre-move path in an instrument; the canonical is deferred under the freeze |
| D5-s8-03 | D5-s9-01 | 11 | tests/closure.py comment paths: same move, same seam (test comments) |
| D5-s8-06 | D5-s5-07 | 12 | criterion C5 over instrument and harness files; the canonical is deferred under the freeze, and test files among its cells are counted by D5-s9-04's detector |
| D5-s9-02 | D5-s9-01 | 11 | R9-RO move left prose paths in tests/; one moved_paths sweep over the seam |
| D5-s9-03 | D5-s9-01 | 11 | R9-RO move left prose paths in tests/; one moved_paths sweep over the seam |
| D6-s1-01 | D5-s2-08 | 11 | same drifted numbers (legionella interval, echo grace) in the reader docs; its rows are acceptance rows of the canonical |
| D6-s2-02 | D6-s5-02 | 11 | pre-move path cited in a policy file; one sweep over dev/governance |
| D6-s2-03 | D6-s5-02 | 11 | pre-move path cited in a policy file; one sweep over dev/governance |
| D6-s3-01 | D4-s2-01 | 11 | same root in config_flow._device_prefill_form: the setup twin omits the placeholders the options twin passes |
| D6-s5-04 | D6-s5-02 | 11 | pre-move path cited in a policy file; one sweep over dev/governance |

## Groups by owning seam

Edges are prerequisites only. Two groups sharing `coordinator.py`,
`pump_arbiter.py` or `config_flow.py` is a hot-file order for step 8. The
test suite seam is cut in three by who must act: what the suite exercises
(`tests`), rows and barriers nobody need approve (`ratchets`), and the two
rows the owner sets (`ratchet-raise`). Paths a test comment cites belong to
the test comments seam.

### The kernel's findings, cut by seam

Revision 1 put five D7 findings in one group, `R11-SEAM-kernel`, named for
the shared kernel. The plan review showed it was the N-duplicated-rule and P2
class as one group: 34 files, and five of the eight clone owners of D7-s1-05
sit in other seams by the component table above. Step 4 cuts a class spanning
seams into one group per seam. The cut:

| what | seam of the owner | group |
|---|---|---|
| D7-s3-03, the step covering now | kernel (`plan_step.py`) | `R11-SEAM-kernel-step` |
| D7-s3-04, three small rules with disagreeing copies | kernel (`const.py`, `drift.py`) | `R11-SEAM-kernel-step` |
| D7-s1-05, arms `note` and `step` | kernel (`drift.py`, `plan_step.py`) | `R11-SEAM-kernel-step` |
| D7-s1-05, arm `avail` | entity surface (`entity.py`) | `R11-SEAM-entity-service` |
| D7-s1-05, arms `day` and `entry` | money (`price_model.py`, `ledger.py`) | `R11-SEAM-money` |
| D7-s1-05, arm `fdjac` | learners (`sysid.py`) | `R11-SEAM-learners` |
| D7-s1-05, arm `notice` | actuation (`legionella.py`) | `R11-SEAM-actuation-release` |
| D7-s1-05, arm `reader` | input boundary (`inputs.py`) | `R11-SEAM-inputs-freshness` |
| D7-s1-06, the imports with a pure owner | kernel (`drift.py`, `const.py`, `currency.py`) | `R11-SEAM-kernel-layering` |
| D7-s1-06's open design, the reader's clock (ADR-002 part 2) | input boundary (`inputs.py`) | `R11-SEAM-inputs-freshness` |
| D7-s3-05, state nothing reads | none | `R11-SEAM-dead-state` |

**A finding is still triaged once.** D7-s1-05 is kept in
`R11-SEAM-kernel-step`, which builds two of its arms. The other six arms are
listed on the group that builds each (`groups.json`, key `arms`; the roster
entry's note) and are not a second triage row. The finding closes when its
last arm has merged, and the clone census (`D7/s1/m7_sites.py`) is the class
sweep at each of the six merges. `prototypes.py --only
kstep,avail,owners,fdjac,notice,reader` reads each group's arms alone at the
fork: two, two, two, one, one and one copies.

**Cut by kind of edit: `R11-SEAM-dead-state`.** D7-s3-05's fifty pieces of
unread state and D7-s1-03's fourteen unused import bindings sit in modules of
six seams. They are one group all the same, and that is a deviation from
step 4, stated here and in `PLAN.md`'s open point 7. The reason: every edit
deletes a name in the module that holds it; none creates, moves or consults
an owner, so no seam's design is touched and no seam's group is the better
judge of it. Cut by seam it would be six groups of a few deletions each, and
`R11-SEAM-ratchets`, which records the import row at the value they leave,
would wait on all six. The group's proof per deletion is that no production
code and no stored document reads the name.

**D1-s3-02 moved inside its seam.** The ECL110 parser it fixes is an input
guard that lives in `coordinator.py`. It was the only finding that put
`R11-SEAM-inputs-guards`, with the round's critical price-scale finding
(D2-s3-02), in the `coordinator.py` order. It is now carried by
`R11-SEAM-inputs-freshness`, the same seam's group that already edits that
file.

| group | seam | size | severity | findings | after | files |
|---|---|---|---|---|---|---|
| `R11-SEAM-kernel-step` | shared kernel | M | low | 3 + 0 merged | none | 12 |
| `R11-SEAM-kernel-layering` | shared kernel | S | low | 1 + 0 merged | none | 10 |
| `R11-SEAM-dead-state` | none: see "Cut by kind of edit" | M | low | 1 + 0 merged | none | 17 |
| `R11-SEAM-plant-model` | plant model | L | critical | 11 + 0 merged | none | 13 |
| `R11-SEAM-inputs-guards` | input boundary | M | critical | 6 + 0 merged | none | 8 |
| `R11-SEAM-inputs-freshness` | input boundary | M | high | 7 + 0 merged + 2 carried arms | `kernel-step` | 8 |
| `R11-SEAM-store` | persisted store | M | medium | 5 + 0 merged | none | 9 |
| `R11-SEAM-money` | money | L | high | 9 + 0 merged + 2 carried arms | none | 9 |
| `R11-SEAM-solver` | solver | M | medium | 4 + 0 merged | none | 2 |
| `R11-SEAM-learners` | learners | L | medium | 8 + 0 merged + 1 carried arm | `plant-model` | 8 |
| `R11-SEAM-actuation-release` | actuation | L | high | 6 + 0 merged + 1 carried arm | none | 4 |
| `R11-SEAM-actuation-writes` | actuation | L | medium | 9 + 0 merged | `kernel-step`, `actuation-release` | 10 |
| `R11-SEAM-cycle-solve` | cycle | L | medium | 8 + 0 merged | none | 10 |
| `R11-SEAM-cycle-reporting` | cycle | M | medium | 7 + 0 merged | none | 17 |
| `R11-SEAM-config` | config surface | L | high | 6 + 1 merged | none | 6 |
| `R11-SEAM-entity-service` | entity and service surface | M | medium | 8 + 0 merged + 1 carried arm | none | 11 |
| `R11-SEAM-card` | card | L | medium | 9 + 0 merged | none | 1 |
| `R11-SEAM-product-text` | product text | M | high | 7 + 1 merged | `plant-model`, `money`, `actuation-release`, `actuation-writes`, `config`, `entity-service`, `inputs-guards`, `inputs-freshness`, `cycle-solve`, `cycle-reporting` | 10 |
| `R11-SEAM-tests` | test suite | L | low | 4 + 0 merged | none | 7 |
| `R11-SEAM-ratchets` | test suite | M | low | 3 + 0 merged | none (edge dropped 2026-11-18) | 4 |
| `R11-SEAM-ratchet-raise` | test suite | S | low | 2 + 0 merged | none | 2 |
| `R11-SEAM-docs` | reader docs | L | medium | 12 + 1 merged | `plant-model`, `money`, `learners`, `actuation-release`, `actuation-writes`, `config`, `entity-service`, `inputs-guards`, `inputs-freshness`, `cycle-solve`, `cycle-reporting`, `card`, `product-text` | 9 |
| `R11-SEAM-governance-text` | governance text | M | low | 10 + 3 merged | none | 28 |
| `R11-SEAM-comments-production` | production comments | XL | low | 2 + 1 merged | none | 2 |
| `R11-SEAM-comments-tests` | test comments | XL | low | 4 + 6 merged | none | 3 |

### Architect notes

- **`R11-SEAM-kernel-step`** — The kernel's owners and their readers: plan_step owns "the step covering now" with its half-open end rule, read by the coordinator, the arbiter and both planned-room copies; water heat capacity, a naive instant's zone and the finite test get one definition each in const.py and drift.py; the two evidence-note methods share drift.py's owner. D7-s1-05 is kept here with its note and step arms; each other arm is carried by the group of the seam that owns the rule (entity-service, money, learners, actuation-release, inputs-freshness), and the finding closes when the last arm has merged. 3 findings (0 merged in), size M; class tags N-duplicated-rule, N-no-expiry, P2. Findings: D7-s3-03, D7-s3-04, D7-s1-05; arms carried: note, step of D7-s1-05.
- **`R11-SEAM-kernel-layering`** — What the pure layer offers its importers: utc_elapsed_seconds is imported from drift.py, its owner, HISTORY_LENGTH moves to const.py, and currency.py imports HomeAssistant for its annotation only, so the pure modules that reached Home Assistant through accuracy.py and currency.py stop doing so. The reader's clock, the design ADR-002 part 2 gives four of the six modules D7-s1-06 left open, is carried by R11-SEAM-inputs-freshness in inputs.py; setpoint_check and snapshots stay. 1 finding (0 merged in), size S; class tags N-leaf-imports-solver. Findings: D7-s1-06.
- **`R11-SEAM-dead-state`** — State production stores and nothing reads (D7-s3-05): constants named only by tests, parameters a function never loads, locals, attributes and fields only tests read, each deleted in the module that holds it and at its callers, and the fourteen import bindings D7-s1-03 lists. No owner is created or moved and no behaviour changes, so this one group is cut by kind of edit and not by seam; COMPONENTS.md states the deviation. 1 finding (0 merged in), size M; class tags N-structure-blind. Findings: D7-s3-05.
- **`R11-SEAM-plant-model`** — Physical laws and the plant shape: the scalar Carnot factor agrees with its batch twin, delivery and derate keep their sign, and one predicate each answers "two zones", "modulating" and "has hot water" for the model, the plan views, the options page and the action. 11 findings (0 merged in), size L; class tags N-table-value, N-wrong-law, P2. Findings: D2-s1-01, D2-s1-02, D2-s2-02, D2-s1-51, D12-s2-01, D12-s3-01, D12-s1-01, D17-s1-03, D17-s3-02, D17-s2-03, D8-s1-01.
- **`R11-SEAM-inputs-guards`** — Every value entering through inputs.py is scaled once and tested finite and in domain: the minor-unit price scale, the Fahrenheit inverse, boolean and timestamp parsers, numeric options. The P1 sweep enumerator is the fitness function. 6 findings (0 merged in), size M; class tags N-missing-unit-scale, P1, P8. Findings: D2-s3-02, D7-s3-01, D1-s3-01, D1-s3-03, D1-s2-05, D1-s2-51.
- **`R11-SEAM-inputs-freshness`** — Age and expiry of live inputs: a forecast that stopped advancing, a silent PV meter, forecast row 0 read as now, push-mode flags aged on a polling limit, and the measured outdoor value joining the forecast series. The end rule is the kernel's step owner, hence the edge from R11-SEAM-kernel-step. 7 findings (0 merged in), size M; class tags N-dead-input, N-no-expiry, N-staleness, P1, P2. Findings: D1-s2-03, D1-s2-02, D14-s2-02, D14-s2-01, D17-s2-02, D1-s2-52, D1-s3-02; arms carried: reader of D7-s1-05; clock (ADR-002 part 2) of D7-s1-06.
- **`R11-SEAM-store`** — store.DOMAINS is the one schema: writers and loaders agree with it, non-finite leaves are quarantined, and a restored value is tested before it is applied. 5 findings (0 merged in), size M; class tags N-silent-zero, P1, P2. Findings: D1-s2-01, D15-s1-04, D15-s1-05, D1-s2-06, D17-s3-03.
- **`R11-SEAM-money`** — Prices, fees, capacity windows and the ledger: whole-payload parse, weekday index, highest-window aggregate, scalar and batch top-k agreeing, open-window projection with a floor on settled time, one currency owner for the plan and the options dialog. 9 findings (0 merged in), size L; class tags I4, I5, N-inverted-aggregate, N-partial-payload-parse, N-partial-window-extrapolation, P2, P7, P8. Findings: D2-s3-03, D2-s3-04, D2-s3-05, D2-s3-06, D2-s3-07, D8-s1-02, D14-s1-03, D17-s1-05, D5-s3-01; arms carried: day, entry of D7-s1-05.
- **`R11-SEAM-solver`** — Start set brackets the all-off and wood-covered optima; the risk premium stays in the objective and out of every published money figure; the slot label tie is ordered. Fitness: D0 race harnesses, mutation kill rate on optimizer.py, shape_copies. 4 findings (0 merged in), size M; class tags N-objective-as-money, N-unordered-tiebreak, P4. Findings: D0-s2-01, D0-s3-02, D2-s3-01, D1-s1-51.
- **`R11-SEAM-learners`** — One freeze predicate owns which interval a learner may ingest (away, unplanned charge, load-limited probe, charge-start dip); the sysid adoption interval covers quantised readings. After the plant model: its law fixes move the residual every learner fits. 8 findings (0 merged in), size L; class tags I5, N-confounded-learner, N-event-misattribution, P5. Findings: D12-s3-03, D2-s3-08, D2-s3-09, D2-s3-10, D2-s3-11, D7-s2-01, D7-s2-02, D5-s4-02; arms carried: fdjac of D7-s1-05.
- **`R11-SEAM-actuation-release`** — One restore owner for every entity the optimizer writes: supply switch, frequency, valve, circulation, mode and tank set-point are handed back on Off, stale plan, unload and remove, with a retried restore and a load that completes before the first read. 6 findings (0 merged in), size L; class tags N-order-coupling, N-restore-race, N-unreleased-hold. Findings: D16-s1-04, D16-s3-01, D16-s3-02, D16-s3-03, D16-s3-04, D1-s2-04; arms carried: notice of D7-s1-05.
- **`R11-SEAM-actuation-writes`** — What is written and when: every actuator reads the step covering now from the kernel owner, values sit on the entity's grid and range, a write to an unavailable entity is not recorded, the lead mode is checked against the entity. After release: both use the arbiter's held record. 9 findings (0 merged in), size L; class tags N-mode-coupled-write, N-stale-step-actuation, N-step-grid, P11, P2, P3. Findings: D16-s1-01, D16-s1-02, D16-s1-03, D16-s1-05, D16-s2-01, D16-s2-02, D16-s2-03, D16-s2-04, D12-s3-02.
- **`R11-SEAM-cycle-solve`** — The cycle owns when a solve runs: a write during an in-flight refresh arms a trailing run, every solve request shares one in-flight guard and budget, the worker's failure arms are bounded, and the action and the button reach one refresh path. 8 findings (0 merged in), size L; class tags N-dropped-refresh, N-solve-recompute, N-unbudgeted-background, N-uncleared-issue, P10, P2. Findings: D1-s1-01, D1-s1-03, D1-s3-04, D9-s1-01, D9-s1-02, D9-s1-03, D9-s1-04, D17-s3-01.
- **`R11-SEAM-cycle-reporting`** — How a failure is reported: persist failures surface once above DEBUG, broad handlers leave a record, the generic arm is latched, an unparseable service argument raises, the context is write-once, the coordinator carries the typed entry and the strict-typing row is re-measured. 7 findings (0 merged in), size M; class tags I5, N-log-flood, N-shared-config, N-silent-zero, N-swallowed-failure. Findings: D1-s3-05, D1-s3-06, D1-s3-07, D10-s1-01, D7-s2-03, D10-s3-02, D10-s3-01.
- **`R11-SEAM-config`** — One place for a setting: options-flow settings leave entry.data by a versioned migration, so reconfigure, the options save and the reader agree; the weekend value survives a weekday change; the pre-fill pages render their placeholders and store only settings. 6 findings (1 merged in), size L; class tags I4, N-dead-input, N-entry-data-placement, P2. Findings: D17-s1-02, D10-s2-01, D10-s1-03, D17-s2-05, D4-s2-01, D17-s2-04; merged: D6-s3-01 into D4-s2-01.
- **`R11-SEAM-entity-service`** — Published metadata and outcomes: state_class and device_class match the value, a refused press raises, availability and value share a predicate, selectors sit on their grid. D8-s2-02 changes no entity id without a registry migration. 8 findings (0 merged in), size M; class tags N-entity-metadata, N-name-sort, N-silent-zero, N-step-grid, P2. Findings: D10-s1-02, D10-s2-04, D8-s1-03, D8-s2-02, D8-s3-01, D15-s3-01, D14-s1-01, D17-s3-51; arms carried: avail of D7-s1-05.
- **`R11-SEAM-card`** — Card: 24/44 px hit targets, the 12 px type floor, one colour per status role and type and spacing read from the token scales (card_rule_copies 70 at the fork may only fall), translated failure lines, bounded history rows. 9 findings (0 merged in), size L; class tags I4, N-unbounded-retention, N-untranslated-splice, P9. Findings: D4-s1-01, D4-s1-03, D4-s3-01, D4-s3-02, D4-s3-03, D4-s3-04, D4-s3-05, D6-s4-01, D9-s2-01.
- **`R11-SEAM-product-text`** — User-facing strings state what the code does after this round's behaviour groups have merged; placeholders match across languages; copy style is one convention. Verified against the text ledger. 7 findings (1 merged in), size M; class tags I4, I5, N-copy-style. Findings: D6-s2-01, D6-s6-01, D6-s4-02, D4-s3-06, D4-s3-07, D10-s2-03, D4-s2-51; merged: D4-s2-02 into D10-s2-03.
- **`R11-SEAM-tests`** — What the suite exercises: a flow test follows each rendered error to its recovery, the coverage register row states the measured tier, the stress memory channel probes every scenario and one lane drives coordinator cycles. 4 findings (0 merged in), size L; class tags I1, I5. Findings: D10-s1-05, D10-s1-06, D9-s3-01, D9-s3-02.
- **`R11-SEAM-ratchets`** — Ratchet rows and barriers that see what they name: a rule written twice in one function, a package import nothing loads, and an unlatched .exception or .critical log site. Each new row is recorded at its measured value when the group merges; no edge waits on R11-SEAM-dead-state, whose later deletions re-record the import row downward (the edge dropped, decided 2026-11-18, orchestrator under mandate, pending owner confirmation). 3 findings (0 merged in), size M; class tags N-log-flood, N-structure-blind. Findings: D7-s1-02, D7-s1-03, D14-s2-03.
- **`R11-SEAM-ratchet-raise`** — The two rows whose value the owner sets: const fan-out read through a module binding (the corrected row reads 4 against a budget of 3) and module lines outside the class, whose limit the owner chooses. Cut from the other ratchet rows so the owner's confirmation holds only these two findings. 2 findings (0 merged in), size S; class tags N-structure-blind. Findings: D7-s1-01, D7-s1-04.
- **`R11-SEAM-docs`** — Reader docs carry each fact once and the number the code holds; verified last, after every user-facing change. 12 findings (1 merged in), size L; class tags I5, N-comment-style, N-orphan-doc. Findings: D5-s2-01, D5-s2-02, D5-s2-03, D5-s2-08, D5-s2-09, D5-s2-10, D5-s2-11, D6-s1-02, D6-s7-01, D5-s2-04, D5-s2-05, D5-s2-06; merged: D6-s1-01 into D5-s2-08.
- **`R11-SEAM-governance-text`** — Policy and programme prose with a false or unresolvable sentence. Policy files merge serially on the owner's approving review; no instrument code changes here. 10 findings (3 merged in), size M; class tags I4, I5, N-move-stale-path. Findings: D6-s5-02, D6-s5-03, D6-s5-01, D6-s5-05, D6-s5-06, D6-s5-07, D6-s5-08, D6-s7-02, D11-s2-04, D15-s1-02; merged: D6-s2-02 into D6-s5-02, D6-s2-03 into D6-s5-02, D6-s5-04 into D6-s5-02.
- **`R11-SEAM-comments-production`** — Criterion C5 over production comments (921 units in two seats' cells, 155 of them in the card's script) and one false docstring. Text only. A sentence-length count recorded as a ratchet lets it be paid per file. 2 findings (1 merged in), size XL; class tags I5, N-comment-style. Findings: D5-s4-01, D5-s3-02; merged: D5-s3-03 into D5-s4-01.
- **`R11-SEAM-comments-tests`** — Text in the test suite: criterion C5 over tests/ with the dead names and false count D5-s7-01 lists, and the paths a test comment cites that do not resolve (one moved_paths sweep). Text only. 4 findings (6 merged in), size XL; class tags I5, N-comment-style, N-move-stale-path. Findings: D5-s9-04, D5-s9-01, D5-s8-04, D5-s8-05; merged: D5-s7-01 into D5-s9-04, D5-s7-02 into D5-s9-04, D5-s7-03 into D5-s9-04, D5-s9-02 into D5-s9-01, D5-s9-03 into D5-s9-01, D5-s8-03 into D5-s9-01.

### Files

A group's files are every file its findings' `files` fields name
(`../JUDGE-INPUT.json`) and those its ADR adds; `groups.json` carries the
lists and `projection.py` refuses a file a finding names that its group
neither lists nor excludes. The first draft listed five files per group by
hand and missed 113 of them, `coordinator.py` in five groups: `store` and
`entity-service` edit it and list it; `inputs-guards` listed it for D1-s3-02
alone, which `inputs-freshness` now carries; `tests` and `docs` name it
without editing it. A file a finding names and its group does not edit is
excluded with the reason:

| group | file | named, not edited, because |
|---|---|---|
| `ratchets` | `coordinator.py` `config_flow.py` `thermal_model.py` `optimizer.py` `pump_arbiter.py` `modbus_prefill.py` | D7-s1-03's bindings are deleted by R11-SEAM-dead-state; this group adds the row |
| `ratchets` | `tools/audit/archscore/counters.py` | the scorer; ADR-009 part 3, round-end proposal triage |
| `ratchets` | `tools/audit/archscore/planted/redteam` | the scorer's planted cases; ADR-009 part 3, round-end proposal triage |
| `ratchet-raise` | `entry_config.py` | the module D7-s1-01 measures; the row is re-recorded, the module is not edited (ADR-009 part 2) |
| `ratchet-raise` | `thermal_model.py` | the module D7-s1-01 measures; not edited |
| `ratchet-raise` | `coordinator.py` | the module D7-s1-04 measures; not edited |
| `tests` | `coordinator.py` | D9-s3-02's lane drives coordinator cycles from tests/stress.py; the module is not edited |
| `docs` | `const.py` | D6-s1-01 and D6-s1-02 state the constant; the docs group edits text (ADR-010), and a changed default is the owner's decision (open point 5) |
| `docs` | `coordinator.py` | D6-s1-02's learner sentence: the learner is fixed by R11-SEAM-learners; this group re-runs the claim |
| `docs` | `pump_arbiter.py` | D6-s1-01's echo sentence: the text is aligned to the merged code; a changed window is the owner's decision (open point 5) |
| `governance-text` | `replay_doc.py` | D15-s1-02 names the module the gate reads; its own scope says no production change |
| `governance-text` | `tools/replay/debug_ingest.py` | D15-s1-02 names the gate D15.md should cite; an instrument, not edited (freeze) |
| `kernel-step` | `binary_sensor.py` `climate.py` | D7-s1-05's avail arm is carried by R11-SEAM-entity-service, the group of the seam that owns the rule (ADR-001 part 1) |
| `kernel-step` | `price_model.py` | D7-s1-05's day arm is carried by R11-SEAM-money, the group of the seam that owns the rule (ADR-001 part 1) |
| `kernel-step` | `ledger.py` | D7-s1-05's entry arm is carried by R11-SEAM-money, the group of the seam that owns the rule (ADR-001 part 1) |
| `kernel-step` | `inputs.py` | D7-s1-05's reader arm is carried by R11-SEAM-inputs-freshness, the group of the seam that owns the rule (ADR-001 part 1) |
| `kernel-step` | `sysid.py` | D7-s1-05's fdjac arm is carried by R11-SEAM-learners, the group of the seam that owns the rule (ADR-001 part 1) |
| `kernel-step` | `legionella.py` | D7-s1-05's notice arm is carried by R11-SEAM-actuation-release, the group of the seam that owns the rule (ADR-001 part 1) |

### Prerequisite edges

- `kernel-step` before `inputs-freshness` and `actuation-writes`: both read the
  step covering now from the owner D7-s3-03 creates.
- `dead-state` before `ratchets`: dropped (decided 2026-11-18, orchestrator under mandate, pending owner confirmation). It was an ordering preference: the import row is
  recorded when `ratchets` merges and a later deletion re-records it
  downward (ADR-009 part 1).
- `plant-model` before `learners`: the Carnot, delivery and derate fixes change
  the residual each learner fits, so a learner harness run before them measures
  the wrong plant.
- `actuation-release` before `actuation-writes`: D16-s2-03 and D16-s1-05 depend
  on what the held record means after a release.
- every behaviour group that edits a text file or changes a number a string
  states before `product-text`, and those plus `learners`, `card` and
  `product-text` before `docs`: text is verified against merged behaviour.
  The ten are `plant-model`, `money`, `actuation-release`, `actuation-writes`,
  `config`, `entity-service`, `inputs-guards`, `inputs-freshness`,
  `cycle-solve` and `cycle-reporting`; revision 1 left the last four out.

Not edges: `tests`, `ratchets` and `ratchet-raise` wait on nothing, `kernel-layering`
has no edge in or out, and neither comment group carries an edge. A comment
rewrite depends on no behaviour; its order against the groups that edit the
same file is a hot-file order (`PLAN.md`), released per file (ADR-010 part 2).
`ratchet-raise` lost revision 1's edge from the kernel: its two rows move
with every group that edits `coordinator.py` or `const.py`, so the edge was an
ordering preference (ADR-009 part 2).

Longest chains by edges, depth 4: `actuation-release` or `kernel-step`, then
`actuation-writes`, `product-text`, `docs`; `kernel-step`,
`inputs-freshness`, `product-text`, `docs`; and `plant-model`, `learners`,
`R11-ARCH-fabric-learner` at depth 3 (`PLAN.md` adds that edge).

### Open at P3's start, not findings

`check_scopes.py --round 11 --open-cards` lists 12 evaluation cards and 17
roster groups. They are placed in the roster by step 8. Two touch seams above:
`R11-PRODUCT-TEXT-PINS` (product text) and `R11-VALVE-REFERENCE` (plant model,
`mixing_valve.py`).

### Seat assignments to confirm from the verifier report

Three sweep-converted findings carry no mechanism text in the judge's input:
D1-s2-51 (inputs-guards), D1-s2-52 (inputs-freshness) and D17-s3-51
(entity-service) are seamed from their scope and class. The fixer reads the
verifier report first and reports a wrong seam before building.
