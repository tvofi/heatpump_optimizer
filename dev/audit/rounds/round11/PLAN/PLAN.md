# Round 11 plan: moves, fitness functions, roster and risks

Steps 5 to 9 of `dev/governance/roles/architect-planner.md`, at the fork
`92d38ecb640bd462f2e19c0814d0f0b7df1ee692`. Steps 1, 3 and 4 are
`COMPONENTS.md`, step 2 is `SCENARIOS.md`, the decisions are `ADR-001` to
`ADR-010` beside this file, and `groups.json` is the machine copy of the
groups. `prototypes.py` re-derives every reading this file marks *prototype*.

## The target and what the fork allows

`score.py --diff <fork> <stamp>` must read dS >= +22.7, admissible end to
end, counters on, three scored classes improving, no metric above 40 % of the
dS, no holdout regressing.

The fork's vector (`holdouts/fork.json`, key `vector`) and the frozen weights
(`tools/audit/archscore/weights.json`) bound where the dS can come from:

| metric | class in `vector.py` | weight | at the fork | can it fall |
|---|---|---|---|---|
| `duplication_copies` | P2+P3 | 8.93 | 18 | yes: 14 clone classes |
| `shared_inplace_writes` | N-shared-config | 5.44 | 3 | yes: three sites |
| `hub_solve_writes` | N-shared-config | 5.44 | 1 | yes: one site |
| `untyped_payload_keys` | P6 | 6.90 | 0 | no |
| `family_splits` | N-name-sort | 5.47 | 0 | no |
| `dead_members` | N-structure-blind | 1.00 | 1 | no: see "Not planned" |
| `layer_violations` | none | 1.00 | 13 | yes |
| `private_cross_module` | none | 1.00 | 10 | three by a finding |
| `coordinator_private_reach` | none | 1.00 | 2 | yes |
| `params_over_10` | none | 1.00 | 6 | not planned |
| `coord_footprint` | none | 1.00 | 2496 | must not end above |
| `public_unused` | none | 1.00 | 1 | no: the same symbol as `dead_members` |
| `literal_clone_copies`, `card_clone_copies`, `coordinator_multiassigned_attrs` | none | 1.00 each | 118, 103, 104 | named, not predicted |

Two merges after the fork already moved the vector, each measured with
`score.py --diff <merge>^1 <merge>`: #3677 (`R11-SERVICE-SCHEMA`) reads
`literal_clone_copies` 118 to 114, and #3678 (`R11-OUTSIDE-ROOMS-P2`) reads
`coord_footprint` 2496 to 2502. **The round is inadmissible end to end at the
plan's own base** until six statements are paid back; ADR-004 and ADR-007 do
it.

## The moves

Every group has one entry; a group not listed in this table is score-neutral
(`metrics: {}`, dS 0) and its acceptance is the neutral rule under "Fitness
functions". A term is `w * log2((before + 1) / (after + 1))`, so the split of
one metric between two groups depends on merge order; the sum does not. The
order assumed is the projection's.

| group | ADR | metric, before to after | dS | evidence |
|---|---|---|---|---|
| `R11-SEAM-kernel` | 001 | `duplication_copies` 18 to 9 | +8.2671 | prototype: `D7/s1/m7_prototypes.py`, the nine GOOD clone arms combined |
| `R11-SEAM-kernel` | 002 | `layer_violations` 13 to 2 | +2.2224 | prototype: D7 s1's `layer` and `curr` arms (13 to 6); `prototypes.py --only clock` (13 to 10 alone); the union leaves `setpoint_check` and `snapshots` |
| `R11-SEAM-cycle-reporting` | 003 | `hub_solve_writes` 1 to 0 | +5.4429 | prototype: `--only hub` |
| `R11-SEAM-cycle-reporting` | 008 | `private_cross_module` 10 to 8 | +0.2895 | prediction: the two readers of `away._parse_return_time` in `layering.py`'s crossing list |
| `R11-SEAM-actuation-release` | 004 | `shared_inplace_writes` 3 to 2 | +2.2590 | prototype: `--only circ` |
| `R11-SEAM-actuation-release` | 004 | `coord_footprint` 2502 to 2496 | +0.0035 | prototype: `--only circ` reads six statements fewer |
| `R11-SEAM-learners` | 003 | `shared_inplace_writes` 2 to 1 | +3.1839 | prototype: `--only sysid` |
| `R11-ARCH-cycle-surface` | 005 | `coordinator_private_reach` 2 to 0 | +1.5850 | prototype: `--only reach` |
| `R11-ARCH-cycle-surface` | 005 | `shared_inplace_writes` 1 to 0 | +5.4429 | prototype: `--only tasks`; conditional (ADR-005 part 3) |
| `R11-SEAM-money` | 006 | `duplication_copies` 9 to 8 | +1.3570 | prototype: `--only topk`; conditional (ADR-006 part 2) |
| `R11-SEAM-plant-model` | 008 | `private_cross_module` 8 to 7 | +0.1699 | prediction: `config_flow`'s read of `thermal_model._dhw_enabled_from_config` |
| `R11-ARCH-fabric-learner` | 007 | `coord_footprint` down about 100 statements | +0.0590 | prediction: a statement count of the eight methods |
| `R11-SERVICE-SCHEMA` (merged) | none | `literal_clone_copies` 118 to 114 | +0.0493 | measured on #3677 |
| `R11-OUTSIDE-ROOMS-P2` (merged) | none | `coord_footprint` 2496 to 2502 | -0.0035 | measured on #3678 |

**Projected dS +30.3279.** By metric: `shared_inplace_writes` +10.8858
(35.9 %), `duplication_copies` +9.6241 (31.7 %), `hub_solve_writes` +5.4429,
`layer_violations` +2.2224, `coordinator_private_reach` +1.5850,
`private_cross_module` +0.4594, `coord_footprint` +0.0590,
`literal_clone_copies` +0.0493. Prototyped: +29.7637. Predicted without a
prototype: +0.5184. Already merged: +0.0458.

The seven arms of `prototypes.py` read +18.9616 combined and admissible at the
fork, each alone as its docstring records; D7 s1's combination reads +9.2671;
the two overlap on no site, and the remainder of the prototyped figure is the
log terms taken from the lower base the other move leaves
(`duplication_copies` 17 to 8, `layer_violations` 10 to 2).

**The floor case.** With both conditional parts dropped and both predictions
unrealised the reading is +23.0096 (`duplication_copies` 18 to 9 at 35.9 %,
`shared_inplace_writes` 3 to 1): above the target. One further prototyped
move failing puts the round short; "Risks" names the check.

**Named with a zero prediction.** The move ledger refuses a metric a merged
body moves that its move does not name (`plan_audit.py`, `reconcile`). So each
group whose hot files name `coordinator.py` names `coord_footprint` at 0.0,
`R11-SEAM-plant-model` names `duplication_copies`, `R11-SEAM-config` and
`R11-SEAM-entity-service` name `literal_clone_copies`, `R11-SEAM-card` names
`card_clone_copies`, and `R11-ARCH-fabric-learner` names
`coordinator_multiassigned_attrs`. A fall there is banked only with the
reviewer's `score.py --diff` and a stated reason; a rise is argued in the
body as the gate requires.

### Not planned, and why

| candidate | reading | disposition |
|---|---|---|
| deleting `const.ENTITY_FAMILY_OVERRIDES` | D7 s1's `famdel` arm: `family_splits` 0 to 2, inadmissible | the declaration feeds the family barrier in `tests/entities.py`; deleting it deletes a barrier. `dead_members` and `public_unused` stay at 1 |
| folding two clone bodies under one function | `fold` arm: +0.6964 with both bodies in the tree | `metric-gamed` (D7-s1-02); ADR-001's control |
| a note helper handed the detector's list | `note_helper` arm: `shared_inplace_writes` 3 to 9 | inadmissible; ADR-001's control |
| renaming the solver's cross-module private readers public | `private_cross_module` down seven | a rename with no new reader (ADR-008); left |
| a parameter object for `ThermalModel.simulate_step` and its two step functions | `params_over_10` 6 to 3, +0.8074 by the term | the solver's inner loop on the small host (tradeoff T1) and no prototype; not planned |
| the thermal model's and the optimizer's scalar and batch twins as one-row calls | five clone copies | equality there is measured, not by construction; solver floats and golden fixtures would move (ADR-006) |
| separating the store's schema from its persistence | `layer_violations` 2 to 1 | a split of `store.py` no finding asks for (ADR-002) |
| `counters.gapped_clones` keyed by place (D7-s1-02's scorer half) | none | the scorer; round-end proposal triage (ADR-009) |

## Fitness functions

**The five holdouts**, read at the stamp by `plan_audit.py compare --fork
holdouts/fork.json --stamp <snapshot>`, both sides on the fork's instrument:

1. structure budgets: every key of `tests/structure_budgets.json`; the one
   declared exception is `--allow structure:const_modules_over_50` (ADR-009);
2. the gate-only tripwires of `vector.py` (`GATE_ONLY`);
3. the behaviour inventory: entities, services, options and card pages of
   `holdouts/fork.json`; none may disappear;
4. mutation kill rate, not below the fork's (`holdouts/fork.json`, key
   `mutation`);
5. change coupling per hundred merges over the snapshot's window, not above
   the fork's.

**Per move**, the counter its metric is gameable through and the harness that
shows the behaviour held; each ADR's last section carries the full list.

| metric | counters and controls | harness |
|---|---|---|
| `duplication_copies` | C3 (gapped window), C23 `shape_copies`, the `fold` and `note_helper` controls, D7 s1's `--fold-owner` | `D7/s1/m7_prototypes.py --suite`, `D7/s3/m8_agree.py` |
| `layer_violations` | C17 (function-scope and `TYPE_CHECKING` spellings), C18, C19 `unused_boundary_imports` | `D7/s1/m7_layer_edges.py` |
| `hub_solve_writes` | C13 (pre-solve step), C15, C16 and C16b (event callback) | `D7/s2/m4_order_context.py` |
| `shared_inplace_writes` | C12, C15, the borrow-and-restore shape, `reflective_writes`, `computed_attr_access` | D16's release cells; the identification arming and shutdown checks of `tests/features.py` |
| `coordinator_private_reach` | C5 (passthrough), C2b | a restart in boost mode; the diagnostics key set |
| `private_cross_module` | C18 (private read through a module binding) | the d12-cells enumerator; D10 s1's harness for D10-s1-01 |
| `coord_footprint` | C4 (class hierarchy), C11 and `params_over_10`, C25 (packing) | `tests/golden/` byte-identical; `D7/s2/m3_learner_freeze.py` |

**The neutral rule.** A group with no predicted metric passes when
`score.py --diff` over its PR reads NULL, or IMPROVES on a metric its move
names, with no tripwire rising. A group whose hot files name `coordinator.py`
does not raise `coord_footprint` where its fix has an owning module to land
in; an unavoidable rise is argued in the body and is counted against
ADR-007's fall. The class sweep of each class tag in `COMPONENTS.md` is that
group's fitness function for the class.

## Roster

Twenty-one finding groups (`COMPONENTS.md`) and two refactor groups.

| refactor group | seam | size | after | hot files | evidence | scenario |
|---|---|---|---|---|---|---|
| `R11-ARCH-cycle-surface` | cycle | S | none | `boost.py` `diagnostics.py` `coordinator.py` | prototype (`reach`, `tasks`) | S25, S5 |
| `R11-ARCH-fabric-learner` | learners | L | `R11-SEAM-learners` | `coordinator.py` `tests/structure_budgets.json` `tests/features.py` | prediction | S13, S8 |

### Edges added to `COMPONENTS.md`'s

- `R11-SEAM-learners` before `R11-ARCH-fabric-learner`: the extraction takes
  the freeze answer of ADR-008 as an input, so the predicate's owner exists
  first.
- both refactor groups before `R11-SEAM-comments-production`: it rewrites the
  comments of the code they move.

No other edge changes. The kernel's move of the reader's clock into
`inputs.py` is a file order with `R11-SEAM-inputs-guards`, not an edge.

### Designs

| group | design |
|---|---|
| `R11-SEAM-kernel` | ADR-001, ADR-002 (approved design) |
| `R11-SEAM-plant-model`, `R11-SEAM-learners` | ADR-008, with ADR-003 for the switch (approved design of the predicate work; law fixes are point fixes) |
| `R11-SEAM-actuation-release`, `R11-SEAM-actuation-writes` | ADR-004, with ADR-001 for the covering step (approved design) |
| `R11-SEAM-money` | ADR-006 (approved design) |
| `R11-SEAM-tests` | ADR-009 (approved design) |
| `R11-SEAM-docs`, both comment groups | ADR-010 (text; no design) |
| `R11-SEAM-card` | point fixes against the token scales; no design |
| `R11-SEAM-config` | **owed**: `designer.md`, for the entry migration (T18) |
| `R11-SEAM-cycle-solve` | **owed**: `designer.md`, for the one in-flight guard and budget (S14, T14) |
| `R11-ARCH-fabric-learner` | **owed**: `designer.md`, inside ADR-007 |

### Hot-file order

Merge order on a shared file; none of these is an edge.

| file | order |
|---|---|
| `coordinator.py` | kernel; then actuation-release, cycle-solve, plant-model; then actuation-writes, learners, cycle-reporting; then inputs-freshness, money, cycle-surface; then fabric-learner; then comments-production |
| `pump_arbiter.py`, `legionella.py` | kernel, actuation-release, actuation-writes |
| `inputs.py` | kernel, inputs-guards, inputs-freshness |
| `tariff.py`, `price_model.py`, `ledger.py`, `currency.py` | kernel, money |
| `sysid.py`, `accuracy.py` | kernel, learners |
| `thermal_model.py`, `mixing_valve.py` | plant-model, learners |
| `config_flow.py` | plant-model, money, config |
| `sensor.py`, `binary_sensor.py`, `climate.py` | kernel, entity-service, plant-model |
| `optimizer.py` | kernel, solver |
| `store.py`, `boost.py` | store, cycle-surface |
| `strings.json`, `translations/` | config, entity-service, cycle-reporting, then product-text |
| `tests/structure.py`, `tests/structure_budgets.json` | kernel, tests, fabric-learner |

The kernel is first on most of these rows; its fixer may land it in parts
(ADR-001's consequences) so that a slow part holds only the files it touches.

### Groups open at P3's start

`check_scopes.py --repo . --round 11 --open-cards` lists them; each appears
here once. The plan adds no edge to or from any of them. A product group lands
before the finding group that shares its file, by the owner's priority for
outside and owner items.

| open group | lane | placement |
|---|---|---|
| `R11-OUTSIDE-ROOMS-P3` | product | before plant-model on `thermal_model.py`, before the kernel on `coordinator.py`; names `coord_footprint` |
| `R11-OUTSIDE-HONEST-STARTS-RUNS-P3` | product | before solver on `optimizer.py`, before config on `config_flow.py`; names `coord_footprint` |
| `R11-OUTSIDE-HONEST-DHW-RUNS` | product | before solver and plant-model on their files |
| `R11-OUTSIDE-HONEST-METERED-FLOOR` | product | before store on `store.py`; names `coord_footprint` |
| `R11-OUTSIDE-SELF-SETTING-PUMP` | product | before the kernel on `accuracy.py` |
| `R11-VALVE-REFERENCE` | product | before plant-model on `mixing_valve.py` |
| `R11-PRODUCT-TEXT-PINS` | product | before product-text; before config on `config_flow.py` |
| `R11-CARRY-DRAWMAP` | product | before the kernel or after actuation-writes on `pump_arbiter.py`, never between |
| `R11-CARRY-ROOM-LIFT` | product | no shared file with a finding group |
| `R11-PRE-SHARED-FILES` | instrument | before tests on `tests/structure_budgets.json` |
| `R11-INTAKE-R10-RESIDUE`, `R11-PRE-TOKEN-LEDGER`, `R11-PREPR-STEP-TIMING` | instrument | the roster's own order; no shared file |
| `R10-NUDGE-RETIRE`, `R11-PRE-HANDOFF-BOOKKEEPING`, `R11-PRE-SECURITY-PRIVACY` | policy | serial, on the owner's approving review; before governance-text where a rule file is shared |
| `R11-CLOSEOUT-CLEANUP` | instrument | last, at the round's end |

The twelve open evaluation cards (`E11-GATE-REDS`, `E11-INJECTED`,
`E11-N-GATE-CAUSE`, `E11-N-INSTRUMENT-YIELD`, `E11-N-INTAKE-BUILDER`,
`E11-N-NULL-REVIEWER`, `E11-N-ROLE-CLAUSE`, `E11-N-RULE-YIELD`,
`E11-R-WORKFLOWS`, `E11-S-SEATS`, `E11-SCORECARD`,
`E11-T-product_green_floor`) are instrument work of the evaluation; none gates
a fixer here and the plan adds no edge to them.

### Projection

`tools/plan/replan.py --roster-file <the 23 groups> --coordinator-cap 3`,
with `tools/plan/durations.json` as it stands:

- wall 167.63 h from the first dispatch; critical path 140.85 h;
- critical chain `R11-SEAM-plant-model`, `R11-SEAM-learners`,
  `R11-ARCH-fabric-learner`, `R11-SEAM-comments-production`: depth 4;
- eleven groups start at once; the coordinator cap binds from the second wave;
- at `--coordinator-cap 2` (the tool's default) the wall is 210.77 h.

Not in the model: the three designs owed (designer, design review, then the
fixer), the open groups above, which share the slots and the coordinator cap,
and any part cut from an XL group. The figure is a lower bound for
`R11-SEAM-config`, `R11-SEAM-cycle-solve` and `R11-ARCH-fabric-learner`.

**Against the template.** `dev/programme/round11/phases.json` carries no
forecast for the fix waves and the playbook states no hours for them, so
there is no template figure to compare with; the comparison this plan can
state is the cap sensitivity above. The orchestrator's replan on the merged
roster is the round's figure.

## Risks

| risk | check |
|---|---|
| **Admissibility: `coord_footprint`.** Main reads six above the fork, fixes add statements, and the only large fall (ADR-007) is a prediction behind a design. | `score.py --diff <fork> origin/main` after every coordinator merge; the running sum of the bodies' `coord_footprint` lines against ADR-007's fall; ADR-007 part 4 if it cannot close. |
| **The spread rule's "three scored classes".** `vector.py` gives a class to six metrics; two classes can improve (N-shared-config, P2+P3). P6 and N-name-sort read 0 at the fork and N-structure-blind's one member is a barrier's declaration. The third improving group is the unclassed floor metrics (`layer_violations`, `coordinator_private_reach`, `private_cross_module`). | The plan reviewer and the owner rule whether the floor metrics count as a class. If not, the condition cannot be met at this fork without deleting behaviour, and the plan says so here rather than plan the deletion. |
| **Two prototyped moves are conditional** (the task set, the one-row scalar). | The fixer's proof that the clear is redundant; `tests/golden/` byte-identical and the solve-time harness. Dropped parts are recorded; the floor case still reads above the target. |
| **A third failure puts the round short.** The floor case has no further margin. | The orchestrator reads `plan_audit.py end-to-end --fork <fork>` at each stamp; a prototyped move reported UNREALISED returns the plan to the architect before the last wave. |
| **A sound fix may lower `duplication_copies` further** (the Carnot expression in `R11-SEAM-plant-model`) and push its share toward 40 %. | The share is read at the stamp. The plan does not refuse a sound removal to protect a share; the projected total leaves room for two more copies (`duplication_copies` to 6 reads 38.3 % of the then total). |
| **The score reading better than the code: clones.** An in-function copy is not counted (D7-s1-02), and the scorer's repair is deferred. | Fix review step 14 runs `m7_floor_plants.py`'s place-keyed owner on every PR that lowers `duplication_copies`. |
| **The score reading better than the code: values not handles.** A wrapper, an accessor or a rebind lowers `coordinator_private_reach` or `shared_inplace_writes` with the coupling unchanged. | ADR-003, ADR-004 and ADR-005 each name the refused spelling; the reviewer re-runs the arm with the fixer's diff and reads the tripwires. |
| **Sensitivity S6, T6: the Carnot fix moves every learned correction and golden fixture.** | Claimed drift with its direction (`tests/golden/claimed_drift.txt`); learners run after plant-model so each is re-measured once. |
| **Sensitivity S9, S11: the held record.** Release and writes both redefine it; `R11-CARRY-DRAWMAP` edits the same file. | The D16 enumerator's release and write cells after each of the three merges. |
| **Seams likely to need redesign: the config migration (T18) and the solve admission (T14).** Both are designer-owed and irreversible or user-visible. | Design review at the handoff SHA; a third `revise` re-cuts the group (`design-review.md`). |
| **The kernel is first in file order on most hot files.** A slow kernel holds most merges. | It lands in parts; the orchestrator watches its first part as critical path. |
| **A ratchet repair reads as a budget raise** (`const_modules_over_50`). | The owner's confirmation before the push (ADR-009); `budget-raise-gate`. |
| **T7, T16, T18 change what an existing install does at upgrade.** | Each PR's release-notes step, first in the notes; the docs group verifies them last. |
| **The instrument-comment reading is pending owner confirmation** (`COMPONENTS.md`, "Deferred"). | If the owner rules the other way, one text-only group joins after `R11-SEAM-tests`; no move changes. |
| **Holdout 5, change coupling.** One-owner moves add import edges and the kernel touches many files in one PR. | `plan_audit.py compare` at the stamp; the kernel in parts lowers the co-change of one merge. |

## Open points for the plan reviewer and the owner

1. Whether the unclassed floor metrics count as the third scored class.
2. The deferral of comment-only edits to instrument files (pending owner
   confirmation since step 3).
3. `const_modules_over_50` rising under D7-s1-01's repair: the owner's
   confirmation is owed before `R11-SEAM-tests` pushes.
4. `coord_footprint`: the round starts six above the fork; ADR-007 is the
   payment and is a prediction until its design exists.
