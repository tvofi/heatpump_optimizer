# Round 11 plan: moves, fitness functions, roster and risks

Steps 5 to 9 of `dev/governance/roles/architect-planner.md`, at the fork
`92d38ecb640bd462f2e19c0814d0f0b7df1ee692`. Steps 1, 3 and 4 are
`COMPONENTS.md`, step 2 is `SCENARIOS.md`, the decisions are `ADR-001` to
`ADR-010` beside this file, and `groups.json` is the machine copy of the
groups. `prototypes.py` re-derives every reading this file marks *prototype*,
and `projection.py` re-derives the projection, the hot-file order and the
file lists.

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
plan's own base** until six statements are paid back; ADR-004 pays the six
and ADR-007 pays for what the round's own fixes add ("Admissibility" below).

## The moves

Every group has one entry; a group not listed in this table is score-neutral
(`metrics: {}`, dS 0) and its acceptance is the neutral rule under "Fitness
functions". A term is `w * log2((before + 1) / (after + 1))`, so the split of
one metric between two groups depends on merge order; the sum does not. The
order assumed is the projection's.

| group | ADR | metric, before to after | dS | evidence |
|---|---|---|---|---|
| `R11-SEAM-kernel` | 001 | `duplication_copies` 18 to 9 | +8.2671 | prototype: `--only kernel` (D7 s1's nine GOOD clone arms from its own edit list) |
| `R11-SEAM-kernel` | 002 | `layer_violations` 13 to 2 | +2.2224 | prototype: `--case full` reads 13 to 2 in one tree; `--only kernel` 13 to 6, `--only clock` 13 to 10 alone |
| `R11-SEAM-cycle-reporting` | 003 | `hub_solve_writes` 1 to 0 | +5.4429 | prototype: `--only hub` |
| `R11-SEAM-cycle-reporting` | 008 | `private_cross_module` 10 to 8 | +0.2895 | prediction, **banked only with the new reader** (ADR-008): the reviewer finds `services.py`'s call in the PR |
| `R11-SEAM-actuation-release` | 004 | `shared_inplace_writes` 3 to 2 | +2.2590 | prototype: `--only circ` |
| `R11-SEAM-actuation-release` | 004 | `coord_footprint` 2502 to 2496 | +0.0035 | prototype: `--only circ` reads six statements fewer |
| `R11-SEAM-learners` | 003 | `shared_inplace_writes` 2 to 1 | +3.1839 | prototype: `--only sysid` |
| `R11-ARCH-cycle-surface` | 005 | `coordinator_private_reach` 2 to 0 | +1.5850 | prototype: `--only reach` |
| `R11-ARCH-cycle-surface` | 005 | `shared_inplace_writes` 1 to 0 | +5.4429 | prototype: `--only tasks`; conditional (ADR-005 part 3) |
| `R11-SEAM-money` | 006 | `duplication_copies` 9 to 8 | +1.3570 | prototype: `--only topk`; conditional (ADR-006 part 2) |
| `R11-SEAM-plant-model` | 008 | `private_cross_module` 8 to 7 | +0.1699 | prediction, **banked only with the new reader** (ADR-008): the gap advisor's call in the PR |
| `R11-ARCH-fabric-learner` | 007 | `coord_footprint` 2496 to 2468 | +0.0163 | prototype: `--only fabric`, two of the folds; the bound is 137 statements (`--only ceiling`) |
| `R11-SERVICE-SCHEMA` (merged) | none | `literal_clone_copies` 118 to 114 | +0.0493 | measured on #3677 |
| `R11-OUTSIDE-ROOMS-P2` (merged) | none | `coord_footprint` 2496 to 2502 | -0.0035 | measured on #3678 |

**Projected dS +30.2852.** By metric: `shared_inplace_writes` +10.8858
(35.9 %), `duplication_copies` +9.6241 (31.8 %), `hub_solve_writes` +5.4429,
`layer_violations` +2.2224, `coordinator_private_reach` +1.5850,
`private_cross_module` +0.4594, `literal_clone_copies` +0.0493,
`coord_footprint` +0.0163. Prototyped: +29.7802, read in one tree at the fork
(`prototypes.py --case full`: nineteen arms, admissible, `shape_copies` 40 to
35 and no tripwire rising). Predicted without a prototype: +0.4594, the two
`private_cross_module` terms. Already merged: +0.0458. The total is the sum of
the rows; the one-tree reading plus the other two differs from it by 0.0002
of rounding.

The first draft predicted +30.3279. The difference is ADR-007: its fall was
stated as about 100 statements from a count; the prototype reads 28.

### The cases

Each case is one tree at the fork (`prototypes.py --case <name>`). "End to
end" adds the two merged readings and leaves both `private_cross_module`
terms out, since they are banked only on review. The share is the largest
metric's part of that dS; the last column is how many further clone copies a
sound fix may remove before `duplication_copies` passes 40 %.

| case | `--case` at the fork | end to end | largest share | room under the 40 % cap |
|---|---|---|---|---|
| `full`: every prototyped move | +29.7802 | +29.8258 | `shared_inplace_writes` 36.5 % | two copies (to 6: 38.9 %; to 5: 42.4 %) |
| `no-tasks`: ADR-005 part 3 dropped | +24.3372 | +24.3829 | `duplication_copies` 39.5 % | none (to 7: 43.0 %) |
| `no-topk`: ADR-006 part 2 dropped | +28.4231 | +28.4688 | `shared_inplace_writes` 38.2 % | three copies (to 6: 38.9 %) |
| `floor`: both dropped | +22.9801 | +23.0259 | `duplication_copies` 35.9 % | one copy (to 8: 39.5 %; to 7: 43.0 %) |
| `floor-no-fabric`: and ADR-007 unrealised | +22.9638 | +23.0096 | | inadmissible, see below |

**The floor case** reads +23.0259, 0.33 above the target, and is admissible
only while ADR-007's budget holds. One further prototyped move failing puts
the round short; "Risks" names the check.

**With ADR-007 unrealised the round is inadmissible whatever dS reads.**
`floor-no-fabric` reads +23.0096, but `coord_footprint` then ends at the
fork's 2496 plus every statement the round's fixes added, and fourteen groups
edit `coordinator.py`. The target is not met in that case.

### Admissibility: the footprint budget

The stamp reads `coord_footprint = 2496 + 6 - 6 - F + R`: main's six
statements (#3678), the six ADR-004 pays back, ADR-007's fall `F` and the sum
`R` of the rises in every other merge. The round is admissible on this metric
while `R <= F`.

- `F` is 28 by prototype (two folds as functions of values) and at most 137
  (all thirteen methods deleted). The designer's note for
  `R11-ARCH-fabric-learner` carries the measured `F` of its own cut.
- `R` is kept by the orchestrator from each merged body's `coord_footprint`
  line. The neutral rule below holds each group to zero where its fix has an
  owning module; the three open product groups that name `coord_footprint`
  count in `R` too.
- The plan returns to the owner when `R` passes 20, or when design review
  reads an `F` below the `R` merged by then (ADR-007 part 5).

So admissibility of the whole round rests on ADR-007: on a prototype of 28
statements instead of the first draft's unprototyped 100, and on a design
that is still owed.

**Named with a zero prediction.** The move ledger refuses a metric a merged
body moves that its move does not name (`plan_audit.py`, `reconcile`). So each
group whose files name `coordinator.py` names `coord_footprint` at 0.0
(`R11-SEAM-inputs-guards`, `R11-SEAM-store` and `R11-SEAM-entity-service`
among them, which the first draft's file lists had missed),
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
| `private_cross_module` | C18 (private read through a module binding); **the new reader in the PR's diff, else `metric-gamed`** (ADR-008) | the d12-cells enumerator; D10 s1's harness for D10-s1-01; D8 s1's for D8-s1-01 |
| `coord_footprint` | C4 (class hierarchy), C11 and `params_over_10`, C25 (packing); `dead_members` and `public_unused` flat (a method left with no caller) | `tests/golden/` byte-identical; `D7/s2/m3_learner_freeze.py`; the running `R` against `F` |

**The neutral rule.** A group with no predicted metric passes when
`score.py --diff` over its PR reads NULL, or IMPROVES on a metric its move
names, with no tripwire rising. A group whose files name `coordinator.py`
does not raise `coord_footprint` where its fix has an owning module to land
in; an unavoidable rise is argued in the body and is counted in `R`. The
class sweep of each class tag in `COMPONENTS.md` is that group's fitness
function for the class.

## Roster

Twenty-three finding groups (`COMPONENTS.md`) and two refactor groups. The
published draft is `.claude/workflows/wave-r11-groups.json`.

| refactor group | seam | size | after | files | evidence | scenario |
|---|---|---|---|---|---|---|
| `R11-ARCH-cycle-surface` | cycle | S | none | `boost.py` `diagnostics.py` `coordinator.py` | prototype (`reach`, `tasks`) | S25, S36 |
| `R11-ARCH-fabric-learner` | learners | L | `R11-SEAM-learners` | `coordinator.py` `tests/structure.py` `tests/structure_budgets.json` `tests/features.py` | prototype (`fabric`) for two folds; the design owes the rest | S13, S8 |

### Edges

`COMPONENTS.md` lists the prerequisite edges between finding groups. This
file adds one: `R11-SEAM-learners` before `R11-ARCH-fabric-learner`. D2-s3-11
and D7-s2-01 fix the arithmetic and the freeze of the folds ADR-007 then
moves unchanged, so the code is moved once, after it is right.

The first draft's sixteen edges into `R11-SEAM-comments-production`, and the
one from the tests group into `R11-SEAM-comments-tests`, are removed. Their
stated reason was a shared file, which is an order, not a prerequisite; a
comment rewrite depends on no behaviour (ADR-010). Both comment groups are in
the hot-file order below instead and are released per file.

**Critical chain by edges, depth 4:** `R11-SEAM-kernel`,
`R11-SEAM-actuation-writes`, `R11-SEAM-product-text`, `R11-SEAM-docs`
(`R11-SEAM-actuation-release` in the kernel's place is as long). Every edge on
it is a prerequisite: the step owner before its readers, and text after the
behaviour it states.

### Designs

| group | design |
|---|---|
| `R11-SEAM-kernel` | ADR-001, ADR-002 (approved design) |
| `R11-SEAM-plant-model`, `R11-SEAM-learners` | ADR-008, with ADR-003 for the switch (approved design of the predicate work; law fixes are point fixes) |
| `R11-SEAM-actuation-release`, `R11-SEAM-actuation-writes` | ADR-004, with ADR-001 for the covering step (approved design) |
| `R11-SEAM-money` | ADR-006 (approved design) |
| `R11-SEAM-ratchets`, `R11-SEAM-ratchet-raise` | ADR-009 (approved design) |
| `R11-SEAM-tests` | point additions to the suite; no design |
| `R11-SEAM-docs`, both comment groups | ADR-010 (text; no design) |
| `R11-SEAM-card` | point fixes against the token scales; no design |
| `R11-SEAM-config` | **owed**: `designer.md`, for the entry migration (T18) |
| `R11-SEAM-cycle-solve` | **owed**: `designer.md`, for the one in-flight guard and budget (S14, T14) |
| `R11-ARCH-fabric-learner` | **owed**: `designer.md`, inside ADR-007, with a measured `F` |

### Hot-file order

Merge order on a shared file; none of these is an edge. The table is
`projection.py --order`: every file two or more groups name, in the finish
order of the ORDERED cap-3 projection below, so the order stated here is the
one the projection runs. A group's files are its findings' own `files` fields
and what its ADR adds (`COMPONENTS.md`, "Files").

| file | order |
|---|---|
| `coordinator.py` | kernel, plant-model, actuation-release, money, learners, actuation-writes, entity-service, cycle-solve, R11-ARCH-fabric-learner, cycle-reporting, inputs-guards, inputs-freshness, R11-ARCH-cycle-surface, store |
| `config_flow.py` | kernel, plant-model, config, tests, money, entity-service |
| `const.py` | kernel, config, entity-service, product-text, inputs-freshness |
| `optimizer.py` | solver, kernel, plant-model, cycle-solve, cycle-reporting |
| `pump_arbiter.py` | kernel, actuation-release, actuation-writes, cycle-reporting, product-text |
| `strings.json` | plant-model, cycle-solve, cycle-reporting, product-text, inputs-freshness |
| `dhw_learning.py` | kernel, learners, cycle-reporting, store |
| `legionella.py` | kernel, actuation-release, actuation-writes, cycle-reporting |
| `sensor.py` | kernel, plant-model, money, entity-service |
| `sysid.py` | kernel, ratchets, learners, entity-service |
| `thermal_model.py` | kernel, plant-model, actuation-writes, inputs-guards |
| `accuracy.py` | kernel, learners, store |
| `boost.py` | cycle-reporting, R11-ARCH-cycle-surface, store |
| `debugger.py` | entity-service, cycle-reporting, store |
| `docs/configuration.md` | cycle-solve, inputs-freshness, docs |
| `heat_curve.py` | actuation-writes, product-text, inputs-guards |
| `inputs.py` | kernel, inputs-guards, inputs-freshness |
| `off_restore.py` | actuation-release, cycle-reporting, store |
| `services.py` | plant-model, cycle-solve, cycle-reporting |
| `tests/features.py` | learners, R11-ARCH-fabric-learner, inputs-freshness |
| `tests/structure.py` `tests/structure_budgets.json` | ratchet-raise, ratchets, R11-ARCH-fabric-learner |
| `README.md` | cycle-solve, docs |
| `__init__.py` | config, inputs-guards |
| `binary_sensor.py` | kernel, inputs-freshness |
| `button.py` | entity-service, cycle-solve |
| `comfort_learning.py` | kernel, store |
| `currency.py` `ledger.py` `power_guard.py` `price_model.py` `tariff.py` | kernel, money |
| `diagnostics.py` | cycle-reporting, R11-ARCH-cycle-surface |
| `entity.py` | kernel, entity-service |
| `open_meteo.py` | kernel, inputs-guards |
| `quality_scale.yaml` | tests, cycle-reporting |
| `services.yaml` | plant-model, entity-service |
| `tests/entities.py` | ratchets, inputs-freshness |
| `translations/en.json` | config, product-text |
| `www/heatpump-optimizer-card.js` | card, product-text |

Both comment groups are left out of the rows: `R11-SEAM-comments-production`
is last on every package module and on the card's script,
`R11-SEAM-comments-tests` last on every test script, each released per file
(ADR-010 part 2). `tests/structure_budgets.json` is also re-recorded downward
by any PR that lowers a row; the row above lists the groups that change what
a row measures.

Three things the rows show:

- **The kernel is first on most rows.** Its fixer lands it in parts
  (ADR-001's consequences); the dead-state part is the small PR that frees
  `config_flow.py`, `optimizer.py`, `thermal_model.py` and `modbus_prefill.py`.
- **`R11-ARCH-fabric-learner` is ninth of fourteen on `coordinator.py`**, not
  last. The first draft said last, and its own projection did not run that.
  ADR-007 no longer needs it: the footprint budget is read end to end.
- **`services.py`**: plant-model (D17-s3-02), cycle-solve, cycle-reporting
  (ADR-008 part 3). The first draft had no row for it.

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
| `R11-PRE-SHARED-FILES` | instrument | before ratchets and ratchet-raise on `tests/structure_budgets.json` |
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

`python3 dev/audit/rounds/round11/PLAN/projection.py`, which runs
`tools/plan/replan.py --roster-file <roster> --coordinator-cap <cap>` with
`tools/plan/durations.json` as it stands, on the published roster and on the
same roster with the comment groups' file order written as edges:

| roster | cap 3 | cap 2 (the tool's default) |
|---|---|---|
| PUBLISHED: the draft as it is | 174.05 h | 244.25 h |
| ORDERED: both comment groups after every group sharing a file | 209.62 h | 279.82 h |

- 25 groups, 14 of them touching `coordinator.py`; ten start at once on the
  published roster at cap 3, and the coordinator cap binds from the first
  wave.
- Published, cap 3: critical path 139.68 h on the chain by edges above; the
  last group to finish is `R11-SEAM-store`, held by the coordinator cap, not
  by an edge.
- The round's figure lies between the two rows. PUBLISHED lets a comment
  group finish while files are still held; ORDERED holds the whole group for
  its last file. Parts released per file (ADR-010) are what moves it toward
  the first row.

The first draft stated 167.63 h and 210.77 h for 23 groups; those figures did
not reproduce (the reviewer read 175.67 h and 237.83 h on the published
roster) and its file lists left `coordinator.py` out of three groups that
edit it. The rows above are from the lists `projection.py` checks.

Not in the model: the three designs owed (designer, design review, then the
fixer), the open groups above, which share the slots and the coordinator cap,
and any part cut from a group. The figure is a lower bound for
`R11-SEAM-config`, `R11-SEAM-cycle-solve` and `R11-ARCH-fabric-learner`.

**Against the template.** `dev/programme/round11/phases.json` carries no
forecast for the fix waves and the playbook states no hours for them, so
there is no template figure to compare with; the comparison this plan can
state is the cap sensitivity above. The orchestrator's replan on the merged
roster is the round's figure.

## Risks

| risk | check |
|---|---|
| **Admissibility: `coord_footprint`.** Main reads six above the fork, fourteen groups and three open product groups add statements, and the fall that pays for them (ADR-007) is prototyped at 28 statements behind a design that is still owed. Without it the round is inadmissible whatever dS reads. | `score.py --diff <fork> origin/main` after every coordinator merge; the running `R` against `F`; the plan returns to the owner when `R` passes 20 or the designer's `F` is below `R` (ADR-007 part 5). |
| **The spread rule's "three scored classes".** `vector.py` gives a class to six metrics; two classes can improve (N-shared-config, P2+P3). P6 and N-name-sort read 0 at the fork and N-structure-blind's one member is a barrier's declaration. The third improving group is the unclassed floor metrics (`layer_violations`, `coordinator_private_reach`, `private_cross_module`), which `weights.json` describes as guarding no single register class. | Counting the floor metrics as a class changes the contract, so it is pending owner confirmation. If the owner rules they do not count, the condition cannot be met at this fork without deleting behaviour, and the plan says so here rather than plan the deletion. |
| **The 40 % cap binds when the task-set part is dropped.** In the `no-tasks` case `duplication_copies` supplies 39.5 %, and one further clone removed by a sound fix (the Carnot expression in `R11-SEAM-plant-model`) reads 43.0 %: dS rises and the spread condition fails. In the floor case there is room for one copy; in the full case for two. | The share is read at each stamp from `plan_audit.py end-to-end`. The plan does not hold a sound removal back to protect a share. If the share passes 40 % the target is reported not met on spread, with the per-metric table, and the owner rules. |
| **Two prototyped moves are conditional** (the task set, the one-row scalar). | The fixer's proof that the clear is redundant; `tests/golden/` byte-identical and the solve-time harness. Dropped parts are recorded; "The cases" states each outcome. `R11-ARCH-cycle-surface` is thirteenth on `coordinator.py` in the projection, so the orchestrator asks its fixer for the proof of part 3 at dispatch of the first wave, before the PR's turn. |
| **A further failure puts the round short.** The floor case is 0.33 above the target. | The orchestrator reads `plan_audit.py end-to-end --fork <fork>` at each stamp; a prototyped move reported UNREALISED returns the plan to the architect before the last wave. |
| **The two `private_cross_module` terms are a rename unless the new reader lands.** | The reviewer finds the reader in the PR's diff (ADR-008); otherwise `metric-gamed`, not banked. No case above counts them. |
| **The score reading better than the code: clones.** An in-function copy is not counted (D7-s1-02), and the scorer's repair is deferred. | Fix review step 14 runs `m7_floor_plants.py`'s place-keyed owner on every PR that lowers `duplication_copies`. |
| **The score reading better than the code: values not handles.** A wrapper, an accessor or a rebind lowers `coordinator_private_reach` or `shared_inplace_writes` with the coupling unchanged. | ADR-003, ADR-004 and ADR-005 each name the refused spelling; the reviewer re-runs the arm with the fixer's diff and reads the tripwires. |
| **Sensitivity S6, T6: the Carnot fix moves every learned correction and golden fixture.** | Claimed drift with its direction (`tests/golden/claimed_drift.txt`); learners run after plant-model so each is re-measured once. |
| **Sensitivity S9, S11: the held record.** Release and writes both redefine it; `R11-CARRY-DRAWMAP` edits the same file. | The D16 enumerator's release and write cells after each of the three merges. |
| **Seams likely to need redesign: the config migration (T18) and the solve admission (T14).** Both are designer-owed and irreversible or user-visible. | Design review at the handoff SHA; a third `revise` re-cuts the group (`design-review.md`). |
| **The kernel is first in file order on most hot files**, 34 files in all. A slow kernel holds most merges. | It lands in parts; the orchestrator watches its first part as critical path. |
| **Fourteen groups on `coordinator.py` at a cap of three.** The cap, not an edge, sets the wall: cap 2 costs 70 h more. | The orchestrator's replan at each wave edge; a group whose fix lands wholly in its owning module leaves the coordinator order when its fixer says so. |
| **A ratchet repair reads as a budget raise** (`const_modules_over_50`), and D7-s1-04's limit is the owner's to choose. | The owner's confirmation before the push (ADR-009); `budget-raise-gate`. Both are in `R11-SEAM-ratchet-raise`, so nothing else waits on it. |
| **T7, T16, T18 change what an existing install does at upgrade.** | Each PR's release-notes step, first in the notes; the docs group verifies them last. |
| **The instrument-comment reading is pending owner confirmation** (`COMPONENTS.md`, "Deferred"): fourteen rows and ten merged into them. | If the owner rules the other way, one text-only group joins with no edge; no move changes. |
| **Holdout 5, change coupling.** One-owner moves add import edges and the kernel touches many files in one PR. | `plan_audit.py compare` at the stamp; the kernel in parts lowers the co-change of one merge. |

## Open points for the owner

1. Whether the unclassed floor metrics count as the third scored class
   (pending owner confirmation; the instrument gives them no class).
2. The deferral of comment-only edits to instrument files, fourteen rows
   (pending owner confirmation since step 3).
3. `const_modules_over_50` rising under D7-s1-01's repair, and the limit of
   D7-s1-04's module-span row: both owed before `R11-SEAM-ratchet-raise`
   pushes.
4. `coord_footprint`: the round starts six above the fork; ADR-007 is the
   payment, prototyped at 28 statements, and its design is owed.
5. D6-s1-01's intended values: whether the legionella default returns to 7
   days or the docs say 10, and whether a write gets the 60 s echo grace the
   docs state. The docs group aligns the text to the merged code unless the
   owner decides the code changes, which is then the owning seam's fix.
6. The 40 % cap in the `no-tasks` case: whether a sound clone removal that
   takes `duplication_copies` past 40 % fails the target.
