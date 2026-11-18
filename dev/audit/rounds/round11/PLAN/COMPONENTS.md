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

220 findings: 153 keep, 23 merge, 39 defer,
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
confirmation**; if the owner rules the other way, the thirteen comment-only
rows and their ten merged rows become one text-only group after
`R11-SEAM-tests`.

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
| D5-s8-03 | D5-s9-01 | 11 | tests/closure.py comment paths: same move, same seam |
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
`pump_arbiter.py` or `config_flow.py` is a hot-file order for step 8.

| group | seam | size | severity | findings | after | hot files |
|---|---|---|---|---|---|---|
| `R11-SEAM-kernel` | shared kernel | L | medium | 5 + 0 merged | none | `plan_step.py` `const.py` `drift.py` `accuracy.py` `currency.py` |
| `R11-SEAM-plant-model` | plant model | L | critical | 11 + 0 merged | none | `thermal_model.py` `mixing_valve.py` `defrost.py` `presets.py` `topology.py` |
| `R11-SEAM-inputs-guards` | input boundary | M | critical | 7 + 0 merged | none | `inputs.py` `entry_config.py` `pump_signals.py` `open_meteo.py` `heat_curve.py` |
| `R11-SEAM-inputs-freshness` | input boundary | M | high | 6 + 0 merged | `kernel` | `coordinator.py` `inputs.py` |
| `R11-SEAM-store` | persisted store | M | medium | 5 + 0 merged | none | `store.py` `snapshots.py` `boost.py` |
| `R11-SEAM-money` | money | L | high | 9 + 0 merged | none | `price_model.py` `tariff.py` `grid_fee.py` `ledger.py` `power_guard.py` `currency.py` `config_flow.py` |
| `R11-SEAM-solver` | solver | M | medium | 4 + 0 merged | none | `optimizer.py` `plan_slots.py` |
| `R11-SEAM-learners` | learners | L | medium | 8 + 0 merged | `plant-model` | `sysid.py` `accuracy.py` `dhw_learning.py` `heat_energy.py` `draw_range.py` `coordinator.py` |
| `R11-SEAM-actuation-release` | actuation | L | high | 6 + 0 merged | none | `pump_arbiter.py` `off_restore.py` `coordinator.py` `legionella.py` |
| `R11-SEAM-actuation-writes` | actuation | L | medium | 9 + 0 merged | `kernel`, `actuation-release` | `pump_arbiter.py` `coordinator.py` `freq_control.py` `legionella.py` `setpoint_check.py` |
| `R11-SEAM-cycle-solve` | cycle | L | medium | 8 + 0 merged | none | `coordinator.py` `services.py` `whatif.py` `process_worker.py` |
| `R11-SEAM-cycle-reporting` | cycle | M | medium | 7 + 0 merged | none | `coordinator.py` `away.py` |
| `R11-SEAM-config` | config surface | L | high | 6 + 1 merged | none | `config_flow.py` `device_prefill.py` `__init__.py` |
| `R11-SEAM-entity-service` | entity and service surface | M | medium | 8 + 0 merged | none | `sensor.py` `button.py` `services.yaml` `debugger.py` |
| `R11-SEAM-card` | card | L | medium | 9 + 0 merged | none | `www/heatpump-optimizer-card.js` |
| `R11-SEAM-product-text` | product text | M | high | 7 + 1 merged | `plant-model`, `money`, `actuation-release`, `actuation-writes`, `config`, `entity-service` | `strings.json` `translations/de.json` `translations/sv.json` `translations/en.json` |
| `R11-SEAM-tests` | test suite | L | low | 13 + 3 merged | `kernel` | `tests/structure.py` `tests/stress.py` `tests/config_flow_steps.py` `tests/entities.py` `tests/features.py` |
| `R11-SEAM-docs` | reader docs | L | medium | 12 + 1 merged | `plant-model`, `money`, `learners`, `actuation-release`, `actuation-writes`, `config`, `entity-service`, `card`, `product-text` | `README.md` `docs/configuration.md` `docs/how-it-works.md` `docs/setup.md` `docs/CONTRIBUTING.md` `docs/img/` |
| `R11-SEAM-governance-text` | governance text | M | low | 10 + 3 merged | none | `dev/governance/rules/` `dev/governance/roles/` `dev/governance/dimensions/D15.md` `dev/audit/README.md` `tests/README.md` `dev/programme/` |
| `R11-SEAM-comments-production` | production comments | XL | low | 2 + 1 merged | `kernel`, `plant-model`, `inputs-guards`, `inputs-freshness`, `store`, `money`, `solver`, `learners`, `actuation-release`, `actuation-writes`, `cycle-solve`, `cycle-reporting`, `config`, `entity-service` | `custom_components/heatpump_optimizer/*.py` |
| `R11-SEAM-comments-tests` | test comments | XL | low | 1 + 3 merged | `tests` | `tests/*.py` |

### Architect notes

- **`R11-SEAM-kernel`** — One owner per small rule: plan_step owns "the step covering now" with its end rule; water heat capacity, naive-instant zone and the finite test get one definition; accuracy.py stops carrying the Home Assistant import to five pure modules. D7-s1-05 and D7-s1-06 are the round's first score moves (duplication_copies, layer_violations); the four modules D7-s1-06 marks as needing a design stay out. 5 findings (0 merged in), size L; class tags N-duplicated-rule, N-leaf-imports-solver, N-no-expiry, N-structure-blind, P2. Findings: D7-s3-03, D7-s3-04, D7-s1-05, D7-s1-06, D7-s3-05.
- **`R11-SEAM-plant-model`** — Physical laws and the plant shape: the scalar Carnot factor agrees with its batch twin, delivery and derate keep their sign, and one predicate each answers "two zones", "modulating" and "has hot water" for the model, the plan views, the options page and the action. 11 findings (0 merged in), size L; class tags N-table-value, N-wrong-law, P2. Findings: D2-s1-01, D2-s1-02, D2-s2-02, D2-s1-51, D12-s2-01, D12-s3-01, D12-s1-01, D17-s1-03, D17-s3-02, D17-s2-03, D8-s1-01.
- **`R11-SEAM-inputs-guards`** — Every value entering through inputs.py is scaled once and tested finite and in domain: the minor-unit price scale, the Fahrenheit inverse, boolean and timestamp parsers, numeric options. The P1 sweep enumerator is the fitness function. 7 findings (0 merged in), size M; class tags N-missing-unit-scale, P1, P8. Findings: D2-s3-02, D7-s3-01, D1-s3-01, D1-s3-02, D1-s3-03, D1-s2-05, D1-s2-51.
- **`R11-SEAM-inputs-freshness`** — Age and expiry of live inputs: a forecast that stopped advancing, a silent PV meter, forecast row 0 read as now, push-mode flags aged on a polling limit, and the measured outdoor value joining the forecast series. The end rule is the kernel's step owner, hence the edge. 6 findings (0 merged in), size M; class tags N-dead-input, N-no-expiry, N-staleness, P2. Findings: D1-s2-03, D1-s2-02, D14-s2-02, D14-s2-01, D17-s2-02, D1-s2-52.
- **`R11-SEAM-store`** — store.DOMAINS is the one schema: writers and loaders agree with it, non-finite leaves are quarantined, and a restored value is tested before it is applied. 5 findings (0 merged in), size M; class tags N-silent-zero, P1, P2. Findings: D1-s2-01, D15-s1-04, D15-s1-05, D1-s2-06, D17-s3-03.
- **`R11-SEAM-money`** — Prices, fees, capacity windows and the ledger: whole-payload parse, weekday index, highest-window aggregate, scalar and batch top-k agreeing, open-window projection with a floor on settled time, one currency owner for the plan and the options dialog. 9 findings (0 merged in), size L; class tags I4, I5, N-inverted-aggregate, N-partial-payload-parse, N-partial-window-extrapolation, P2, P7, P8. Findings: D2-s3-03, D2-s3-04, D2-s3-05, D2-s3-06, D2-s3-07, D8-s1-02, D14-s1-03, D17-s1-05, D5-s3-01.
- **`R11-SEAM-solver`** — Start set brackets the all-off and wood-covered optima; the risk premium stays in the objective and out of every published money figure; the slot label tie is ordered. Fitness: D0 race harnesses, mutation kill rate on optimizer.py, shape_copies. 4 findings (0 merged in), size M; class tags N-objective-as-money, N-unordered-tiebreak, P4. Findings: D0-s2-01, D0-s3-02, D2-s3-01, D1-s1-51.
- **`R11-SEAM-learners`** — One freeze predicate owns which interval a learner may ingest (away, unplanned charge, load-limited probe, charge-start dip); the sysid adoption interval covers quantised readings. After the plant model: its law fixes move the residual every learner fits. 8 findings (0 merged in), size L; class tags I5, N-confounded-learner, N-event-misattribution, P5. Findings: D12-s3-03, D2-s3-08, D2-s3-09, D2-s3-10, D2-s3-11, D7-s2-01, D7-s2-02, D5-s4-02.
- **`R11-SEAM-actuation-release`** — One restore owner for every entity the optimizer writes: supply switch, frequency, valve, circulation, mode and tank set-point are handed back on Off, stale plan, unload and remove, with a retried restore and a load that completes before the first read. 6 findings (0 merged in), size L; class tags N-order-coupling, N-restore-race, N-unreleased-hold. Findings: D16-s1-04, D16-s3-01, D16-s3-02, D16-s3-03, D16-s3-04, D1-s2-04.
- **`R11-SEAM-actuation-writes`** — What is written and when: every actuator reads the step covering now from the kernel owner, values sit on the entity's grid and range, a write to an unavailable entity is not recorded, the lead mode is checked against the entity. After release: both use the arbiter's held record. 9 findings (0 merged in), size L; class tags N-mode-coupled-write, N-stale-step-actuation, N-step-grid, P11, P2, P3. Findings: D16-s1-01, D16-s1-02, D16-s1-03, D16-s1-05, D16-s2-01, D16-s2-02, D16-s2-03, D16-s2-04, D12-s3-02.
- **`R11-SEAM-cycle-solve`** — The cycle owns when a solve runs: a write during an in-flight refresh arms a trailing run, every solve request shares one in-flight guard and budget, the worker's failure arms are bounded, and the action and the button reach one refresh path. 8 findings (0 merged in), size L; class tags N-dropped-refresh, N-solve-recompute, N-unbudgeted-background, N-uncleared-issue, P10, P2. Findings: D1-s1-01, D1-s1-03, D1-s3-04, D9-s1-01, D9-s1-02, D9-s1-03, D9-s1-04, D17-s3-01.
- **`R11-SEAM-cycle-reporting`** — How a failure is reported: persist failures surface once above DEBUG, broad handlers leave a record, the generic arm is latched, an unparseable service argument raises, the context is write-once, the coordinator carries the typed entry and the strict-typing row is re-measured. 7 findings (0 merged in), size M; class tags I5, N-log-flood, N-shared-config, N-silent-zero, N-swallowed-failure. Findings: D1-s3-05, D1-s3-06, D1-s3-07, D10-s1-01, D7-s2-03, D10-s3-02, D10-s3-01.
- **`R11-SEAM-config`** — One place for a setting: options-flow settings leave entry.data by a versioned migration, so reconfigure, the options save and the reader agree; the weekend value survives a weekday change; the pre-fill pages render their placeholders and store only settings. 6 findings (1 merged in), size L; class tags I4, N-dead-input, N-entry-data-placement, P2. Findings: D17-s1-02, D10-s2-01, D10-s1-03, D17-s2-05, D4-s2-01, D17-s2-04; merged: D6-s3-01 into D4-s2-01.
- **`R11-SEAM-entity-service`** — Published metadata and outcomes: state_class and device_class match the value, a refused press raises, availability and value share a predicate, selectors sit on their grid. D8-s2-02 changes no entity id without a registry migration. 8 findings (0 merged in), size M; class tags N-entity-metadata, N-name-sort, N-silent-zero, N-step-grid, P2. Findings: D10-s1-02, D10-s2-04, D8-s1-03, D8-s2-02, D8-s3-01, D15-s3-01, D14-s1-01, D17-s3-51.
- **`R11-SEAM-card`** — Card: 24/44 px hit targets, the 12 px type floor, one colour per status role and type and spacing read from the token scales (card_rule_copies 70 at the fork may only fall), translated failure lines, bounded history rows. 9 findings (0 merged in), size L; class tags I4, N-unbounded-retention, N-untranslated-splice, P9. Findings: D4-s1-01, D4-s1-03, D4-s3-01, D4-s3-02, D4-s3-03, D4-s3-04, D4-s3-05, D6-s4-01, D9-s2-01.
- **`R11-SEAM-product-text`** — User-facing strings state what the code does after this round's behaviour groups have merged; placeholders match across languages; copy style is one convention. Verified against the text ledger. 7 findings (1 merged in), size M; class tags I4, I5, N-copy-style. Findings: D6-s2-01, D6-s6-01, D6-s4-02, D4-s3-06, D4-s3-07, D10-s2-03, D4-s2-51; merged: D4-s2-02 into D10-s2-03.
- **`R11-SEAM-tests`** — Ratchets that see what they claim (const fan-out through a module binding, same-function clones, unused imports, module size outside the class, .exception floods), flow recovery, stress over a coordinator cycle and every scenario, and resolvable citations. New rows are recorded at their measured value; after the kernel, whose removals set those values. 13 findings (3 merged in), size L; class tags I1, I5, N-log-flood, N-move-stale-path, N-structure-blind. Findings: D10-s1-05, D10-s1-06, D14-s2-03, D7-s1-01, D7-s1-02, D7-s1-03, D7-s1-04, D9-s3-01, D9-s3-02, D5-s6-02, D5-s8-04, D5-s8-05, D5-s9-01; merged: D5-s9-02 into D5-s9-01, D5-s9-03 into D5-s9-01, D5-s8-03 into D5-s9-01.
- **`R11-SEAM-docs`** — Reader docs carry each fact once and the number the code holds; verified last, after every user-facing change. 12 findings (1 merged in), size L; class tags I5, N-comment-style, N-orphan-doc. Findings: D5-s2-01, D5-s2-02, D5-s2-03, D5-s2-08, D5-s2-09, D5-s2-10, D5-s2-11, D6-s1-02, D6-s7-01, D5-s2-04, D5-s2-05, D5-s2-06; merged: D6-s1-01 into D5-s2-08.
- **`R11-SEAM-governance-text`** — Policy and programme prose with a false or unresolvable sentence. Policy files merge serially on the owner's approving review; no instrument code changes here. 10 findings (3 merged in), size M; class tags I4, I5, N-move-stale-path. Findings: D6-s5-02, D6-s5-03, D6-s5-01, D6-s5-05, D6-s5-06, D6-s5-07, D6-s5-08, D6-s7-02, D11-s2-04, D15-s1-02; merged: D6-s2-02 into D6-s5-02, D6-s2-03 into D6-s5-02, D6-s5-04 into D6-s5-02.
- **`R11-SEAM-comments-production`** — Criterion C5 over production comments (921 units in two seats' cells) and one false docstring. Text only; after every production group, since each rewrites the same hot files. A sentence-length count recorded as a ratchet lets it be paid per file. 2 findings (1 merged in), size XL; class tags I5, N-comment-style. Findings: D5-s4-01, D5-s3-02; merged: D5-s3-03 into D5-s4-01.
- **`R11-SEAM-comments-tests`** — Criterion C5 over the test suite, with the dead names and false count D5-s7-01 lists. Text only; after the tests group. 1 findings (3 merged in), size XL; class tags N-comment-style. Findings: D5-s9-04; merged: D5-s7-01 into D5-s9-04, D5-s7-02 into D5-s9-04, D5-s7-03 into D5-s9-04.

### Prerequisite edges

- kernel before `inputs-freshness` and `actuation-writes`: both read the step
  covering now from the owner D7-s3-03 creates.
- kernel before `tests`: new ratchet rows are recorded at the value the
  kernel's removals leave.
- `plant-model` before `learners`: the Carnot, delivery and derate fixes change
  the residual each learner fits, so a learner harness run before them measures
  the wrong plant.
- `actuation-release` before `actuation-writes`: D16-s2-03 and D16-s1-05 depend
  on what the held record means after a release.
- behaviour groups before `product-text`, and those plus `card` and
  `product-text` before `docs`: text is verified against merged behaviour.
- every production group before `comments-production`; `tests` before
  `comments-tests`.

Longest chain by edges: `actuation-release`, `actuation-writes`,
`product-text`, `docs`: depth 4.

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
