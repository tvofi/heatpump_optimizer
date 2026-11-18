# Round 11 plan: moves, fitness functions, roster and risks

Steps 5 to 9 of `dev/governance/roles/architect-planner.md`, at the fork
`92d38ecb640bd462f2e19c0814d0f0b7df1ee692`. Steps 1, 3 and 4 are
`COMPONENTS.md`, step 2 is `SCENARIOS.md`, the decisions are `ADR-001` to
`ADR-010` beside this file, and `groups.json` is the machine copy of the
groups. `prototypes.py` re-derives every reading this file marks *prototype*,
and `projection.py` re-derives the projection, the hot-file order and the
file lists.

This is revision 2. The plan review returned `revise` twice, so the plan goes
to the owner with what is still open; the last section lists what this
revision changed for each review point and what it leaves for the owner.

The third review (`446a5aa904`, `revise`, no revision 3) went to the owner
with the open points. After an hour without an answer the orchestrator
decided them under mandate 6893738184 on 2026-11-18, pending owner
confirmation; "Open points" records each decision and "Applied 2026-11-18"
lists where each one changed this plan. No fourth review was run.

## The target and what the fork allows

`score.py --diff <fork> <stamp>` must read dS >= +22.7, admissible end to
end, counters on, three scored classes improving, no metric above 40 % of the
dS, no holdout regressing.

The fork's vector (`holdouts/fork.json`, key `vector`) and the frozen weights
(`tools/audit/archscore/weights.json`) bound where the dS can come from:

| metric | class in `vector.py` | weight | at the fork | can it fall |
|---|---|---|---|---|
| `duplication_copies` | P2+P3 | 8.93 | 18 | yes: 14 clone classes |
| `shared_inplace_writes` | N-shared-config | 5.44 | 3 | two of three sites; the third is left ("Not planned") |
| `hub_solve_writes` | N-shared-config | 5.44 | 1 | yes: one site |
| `untyped_payload_keys` | P6 | 6.90 | 0 | no |
| `family_splits` | N-name-sort | 5.47 | 0 | no |
| `dead_members` | N-structure-blind | 1.00 | 1 | no: see "Not planned" |
| `layer_violations` | none | 1.00 | 13 | yes |
| `private_cross_module` | none | 1.00 | 10 | named, not predicted (ADR-008) |
| `coordinator_private_reach` | none | 1.00 | 2 | yes |
| `params_over_10` | none | 1.00 | 6 | not planned |
| `coord_footprint` | none | 1.00 | 2496 | must not end above |
| `public_unused` | none | 1.00 | 1 | no: the same symbol as `dead_members` |
| `literal_clone_copies`, `card_clone_copies`, `coordinator_multiassigned_attrs` | none | 1.00 each | 118, 103, 104 | named, not predicted |

Three merges after the fork already moved the vector, each measured with
`score.py --diff <merge>^1 <merge>`: #3677 (`R11-SERVICE-SCHEMA`) reads
`literal_clone_copies` 118 to 114, #3678 (`R11-OUTSIDE-ROOMS-P2`) reads
`coord_footprint` 2496 to 2502, and #3662 (`R11-OUTSIDE-SELF-SETTING-PUMP`)
reads it 2502 to 2505. `plan_audit.py end-to-end --fork <fork> --head
origin/main` at main `f567988b51` reads dS +0.0441 WORSENS, `coord_footprint`
-0.0052. **The round is inadmissible end to end at main as it stands** until
nine statements are paid back; ADR-004 pays six and ADR-007 pays the rest and
what the round's own fixes add ("Admissibility" below).

## The moves

Every group has one entry; a group not listed in this table is score-neutral
and its acceptance is the neutral rule under "Fitness functions". A term is
`w * log2((before + 1) / (after + 1))`, so the split of one metric between two
groups depends on merge order; the sum does not. The order assumed is the
ORDERED projection's finish order ("Hot-file order"), and the `coord_footprint`
rows start from main's 2505.

| group | ADR | metric, before to after | dS | evidence |
|---|---|---|---|---|
| `R11-SEAM-kernel-layering` | 002 | `layer_violations` 13 to 6 | +1.0000 | prototype: `--only klayer` (D7 s1's `layer` and `curr` arms) |
| `R11-SEAM-kernel-step` | 001 | `duplication_copies` 18 to 16 | +1.4326 | prototype: `--only kstep` (the `note` and `step` arms) |
| `R11-SEAM-actuation-release` | 001 | `duplication_copies` 16 to 15 | +0.7808 | prototype: `--only notice` reads one copy |
| `R11-SEAM-actuation-release` | 004 | `shared_inplace_writes` 3 to 2 | +2.2590 | prototype: `--only circ` |
| `R11-SEAM-actuation-release` | 004 | `coord_footprint` 2505 to 2499 | +0.0035 | prototype: `--only circ` reads six statements fewer |
| `R11-SEAM-learners` | 001 | `duplication_copies` 15 to 14 | +0.8313 | prototype: `--only fdjac` reads one copy |
| `R11-SEAM-learners` | 003 | `shared_inplace_writes` 2 to 1 | +3.1839 | prototype: `--only sysid` |
| `R11-SEAM-money` | 001, 006 | `duplication_copies` 14 to 11 | +2.8741 | prototype: `--only owners` reads two copies (`day`, `entry`); `--only topk` one, conditional (ADR-006 part 2) |
| `R11-SEAM-cycle-reporting` | 003 | `hub_solve_writes` 1 to 0 | +5.4429 | prototype: `--only hub` |
| `R11-ARCH-fabric-learner` | 007 | `coord_footprint` 2499 to 2471 | +0.0162 | prototype: `--only fabric`, two of the folds; the bound is 137 statements (`--only ceiling`) |
| `R11-SEAM-entity-service` | 001 | `duplication_copies` 11 to 9 | +2.3483 | prototype: `--only avail` reads two copies |
| `R11-SEAM-inputs-freshness` | 001 | `duplication_copies` 9 to 8 | +1.3570 | prototype: `--only reader` reads one copy |
| `R11-SEAM-inputs-freshness` | 002 | `layer_violations` 6 to 2 | +1.2224 | prototype: `--only klayer,reader,clock --combined` reads 13 to 2; `--only clock` reads 13 to 10 alone |
| `R11-ARCH-cycle-surface` | 005 | `coordinator_private_reach` 2 to 0 | +1.5850 | prototype: `--only reach` |
| `R11-SERVICE-SCHEMA` (merged) | none | `literal_clone_copies` 118 to 114 | +0.0493 | measured on #3677 |
| `R11-OUTSIDE-ROOMS-P2` (merged) | none | `coord_footprint` 2496 to 2502 | -0.0035 | measured on #3678 |
| `R11-OUTSIDE-SELF-SETTING-PUMP` (merged) | none | `coord_footprint` 2502 to 2505 | -0.0017 | measured on #3662 |

**Projected dS +24.3811.** By metric: `duplication_copies` +9.6241 (39.5 %),
`shared_inplace_writes` +5.4429 (22.3 %), `hub_solve_writes` +5.4429 (22.3 %),
`layer_violations` +2.2224, `coordinator_private_reach` +1.5850,
`literal_clone_copies` +0.0493, `coord_footprint` +0.0145. Every planned term
is prototyped, and the planned moves are read in one tree at the fork:
`prototypes.py --case planned` reads +24.3372, fifteen arms, admissible,
`shape_copies` 40 to 35 and no tripwire rising. Already merged: +0.0441. The
total is the sum of the rows; the one-tree reading restated from main's 2505
plus the merged rows gives +24.3812, 0.0001 of rounding apart.

Revision 1 projected +30.2852. The difference is three terms the review
showed were counts moving without the property: the task set's clear (+5.4429,
ADR-005 part 3, withdrawn) and the two `private_cross_module` terms (+0.4594,
ADR-008, now named at 0.0). The seven per-seam clone and layer arms are the
same edits revision 1 planned in one group; they sum to the same +10.4895.

### The cases

Each case is one tree at the fork (`prototypes.py --case <name>`). "End to
end" restates the tree's `coord_footprint` from main's 2505 and adds the three
merged readings. The share is the largest metric's part of that dS; the last
column is how many further clone copies a sound fix may remove before
`duplication_copies` passes 40 %.

| case | `--case` at the fork | end to end | largest share | room under the 40 % cap |
|---|---|---|---|---|
| `planned`: every planned move | +24.3372 | +24.3812 | `duplication_copies` 39.5 % | none (to 7: 43.0 %) |
| `floor`: ADR-006 part 2 dropped | +22.9801 | +23.0241 | `duplication_copies` 35.9 % | one copy (to 8: 39.5 %; to 7: 43.0 %) |
| `one-copy-short`: the floor, one clone arm unrealised | +21.7525 | +21.7965 | | short of the target |
| `floor-no-fabric`: the floor, ADR-007 unrealised | +22.9638 | +23.0079 | | inadmissible, see below |
| `with-tasks`: the control, not planned | +29.7802 | | | ADR-005 part 3, withdrawn |
| `no-circ`: planned, the circ term not banked | +21.1498 | +21.1938 | `duplication_copies` 45.5 % | short of the target |
| `floor-no-circ`: the floor, the circ term not banked | +19.7927 | +19.8367 | `duplication_copies` 41.8 % | short of the target |

**The planned case** reads +24.3812, 1.68 above the target, with
`duplication_copies` at 39.5 % and no room under the cap.

**The floor case** reads +23.0241, 0.32 above the target. One clone arm
failing from there reads +21.7965, short by 0.90. The planned clone arms are
spread over six groups, so "one arm unrealised" is one group's part and is
seen at that group's merge, not at the round's end.

**Without the circ term the round is short.** The term is banked only when
the PR registers the real restoring owner (ADR-004; decided 2026-11-18, orchestrator under mandate, pending owner confirmation).
`no-circ` reads +21.1938 end to end, 1.51 below the target, and not the
+22.12 the review estimated by subtraction: without the circ arm
`shared_inplace_writes` ends at 2, not 1, and the log term of the sysid arm
from 3 to 2 is smaller than that of its fall from 2 to 1. `floor-no-circ`
reads +19.8367. The circ term is therefore a condition of the target, not a
margin: if D16's release cells do not pass on the PR, the plan returns to
the architect for a paying move before the last wave.

**With ADR-007 unrealised the round is inadmissible whatever dS reads.**
`floor-no-fabric` reads +23.0079, but `coord_footprint` then ends at 2499 plus
every statement the round's fixes add, and fourteen groups edit
`coordinator.py`. The target is not met in that case.

**The target cannot be declared reachable by this plan alone.** Two of its
conditions were the owner's ("Open points", 1 and 6) and are now decided 2026-11-18, orchestrator under mandate, pending owner confirmation: the unclassed floor metrics (`layer_violations`,
`coordinator_private_reach`) count as the third scored class, so the planned
case improves three classes; and the 40 % cap is checked at the stamp from
`plan_audit.py end-to-end`, not at plan time, so the planned case's 39.5 %
and the Carnot fix's expected 43.0 % are read there. The rest still rests on
ADR-007's measured `F` and on the circ term above.

### Admissibility: the footprint budget

The stamp reads `coord_footprint = 2496 + R - 6 - F`: `R` is every statement
added since the fork by any merge, the six are ADR-004's payment
(`prototypes.py --only circ`) and `F` is ADR-007's fall. The round is
admissible on this metric while `R <= 6 + F`.

- `F` is 28 by prototype (two folds as functions of values) and at most 137
  (all thirteen methods deleted). So the budget for `R` is 34 statements
  until a design carries a larger measured `F`.
- `R` is 9 at main `f567988b51`, before any of this plan's groups has merged:
  six from #3678 and three from #3662, both product merges. Revision 1 stated
  six; the review read nine, and the per-merge readings above account for
  them.
- `R` is kept by the orchestrator from `plan_audit.py end-to-end --fork
  <fork> --head origin/main` after every merge that touches `coordinator.py`.
  The neutral rule below holds each group to zero where its fix has an owning
  module; the open product groups that name `coord_footprint` count in `R`
  too.
- The plan returns to the owner when `R` passes 26 (eight short of the
  budget; revision 1's "20 of 28" counted from 2502), or when design review
  reads an `F` that leaves `6 + F` below the `R` merged by then (ADR-007
  part 5).

So admissibility of the whole round rests on ADR-007: on a prototype of 28
statements and on a design that is still owed. ADR-007 says so in its own
context. Its designer starts in the first wave ("Open points" 4, decided 2026-11-18, orchestrator under mandate, pending owner confirmation), so `F` is measured before most of `R` has merged.

**No other metric has a payment.** The budget covers `coord_footprint` only.
A rise in any other scored metric or gate-only tripwire, argued in a PR body
as the per-PR gate allows, also makes the round inadmissible end to end, and
no move of this plan pays it back. The ones a fix here can plausibly raise,
at the fork: `coordinator_multiassigned_attrs` 104, `card_clone_copies` 103,
`literal_clone_copies` 118 (114 at main), `computed_attr_access` 27,
`reflective_writes` 10, `shape_copies` 40. For a group of this roster such a
rise is a review block, not an argued rise: the fix is reshaped until
`score.py --diff` over the PR reads no rise, or the orchestrator returns the
plan to the architect for a paying move before the PR merges.

**Named with a zero prediction.** The move ledger refuses a metric a merged
body moves that its move does not name (`plan_audit.py`, `reconcile`). So each
group whose files name `coordinator.py` names `coord_footprint` at 0.0;
`R11-SEAM-plant-model` names `duplication_copies` and `private_cross_module`;
`R11-SEAM-cycle-reporting` names `private_cross_module`; `R11-ARCH-cycle-surface`
names `shared_inplace_writes`; `R11-SEAM-config` and `R11-SEAM-entity-service`
name `literal_clone_copies`; `R11-SEAM-card` names `card_clone_copies`; and
`R11-ARCH-fabric-learner` names `coordinator_multiassigned_attrs`. A fall
there is banked only with the reviewer's `score.py --diff` and a stated
reason that the priced property moved; a rise is handled as above.

### Not planned, and why

| candidate | reading | disposition |
|---|---|---|
| dropping `async_shutdown`'s clear of the task set (revision 1's ADR-005 part 3) | `--case with-tasks`: `shared_inplace_writes` 1 to 0, +5.4429 | the count falls and the hazard does not: no `await` follows the clear, and `_spawn`'s `.add` and the done-callback's `.discard` still write the same set in place from sync code the metric does not count. It also breaks S36: a task that outlives the 5 s wait would stay in the set. Withdrawn; the metric is named at 0.0 |
| the two `private_cross_module` crossings of ADR-008 as a prediction | 10 to 7, +0.4594 by the terms | the count falls because two names lose an underscore; the readers that cross today still cross. The public predicates are still built, for their new readers; the terms are named at 0.0 and banked only on review |
| the kernel as one group (revision 1's `R11-SEAM-kernel`) | 34 files in at least six seams | a class, not a seam (step 4). Cut into three groups and six arms carried by their owning seams (`COMPONENTS.md`) |
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
holdouts/fork.json --stamp <snapshot>`, both sides on the fork's instrument
(`plan_audit.py snapshot --instrument <fork>`):

1. structure budgets: every key of `tests/structure_budgets.json`. No
   exception is declared: a row this round repairs is read on both sides by
   the fork's `tests/structure.py`, so the repair cannot move the compare
   (ADR-009);
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
| `duplication_copies` | C3 (gapped window), C23 `shape_copies`, the `fold` and `note_helper` controls, D7 s1's `--fold-owner`; the clone census `m7_sites.py` as the class sweep of every group that carries an arm | `D7/s1/m7_prototypes.py --suite`, `D7/s3/m8_agree.py` |
| `layer_violations` | C17 (function-scope and `TYPE_CHECKING` spellings), C18, C19 `unused_boundary_imports` | `D7/s1/m7_layer_edges.py` |
| `hub_solve_writes` | C13 (pre-solve step), C15, C16 and C16b (event callback) | `D7/s2/m4_order_context.py` |
| `shared_inplace_writes` | C12, C15, the borrow-and-restore shape, `reflective_writes`, `computed_attr_access`; **a site moved into a new owner is banked only with the D16 release cells passing on the PR** (ADR-004) | D16's release cells; the identification arming checks of `tests/features.py` |
| `coordinator_private_reach` | C5 (passthrough), C2b | a restart in boost mode; the diagnostics key set |
| `private_cross_module` | named at 0.0. C18 (private read through a module binding); **the new reader in the PR's diff, else `metric-gamed`** (ADR-008) | the d12-cells enumerator; D10 s1's harness for D10-s1-01; D8 s1's for D8-s1-01 |
| `coord_footprint` | C4 (class hierarchy), C11 and `params_over_10`, C25 (packing); `dead_members` and `public_unused` flat (a method left with no caller) | `tests/golden/` byte-identical; `D7/s2/m3_learner_freeze.py`; the running `R` against `6 + F` |

**The neutral rule.** A group with no predicted metric passes when
`score.py --diff` over its PR reads NULL, or IMPROVES on a metric its move
names, with no tripwire rising. A group whose files name `coordinator.py`
does not raise `coord_footprint` where its fix has an owning module to land
in; an unavoidable rise is argued in the body and is counted in `R`. A rise
in any other scored metric or tripwire is a review block ("No other metric
has a payment"). The class sweep of each class tag in `COMPONENTS.md` is that
group's fitness function for the class.

## Roster

Twenty-five finding groups (`COMPONENTS.md`) and two refactor groups. The
published draft is `.claude/workflows/wave-r11-groups.json`.

| refactor group | seam | size | after | files | evidence | scenario |
|---|---|---|---|---|---|---|
| `R11-ARCH-cycle-surface` | cycle | S | none | `boost.py` `diagnostics.py` `coordinator.py` | prototype (`reach`) | S25 |
| `R11-ARCH-fabric-learner` | learners | L | `R11-SEAM-learners` | `coordinator.py` `tests/structure.py` `tests/structure_budgets.json` `tests/features.py` | prototype (`fabric`) for two folds; the design owes the rest | S13 |

### Edges

`COMPONENTS.md` lists the prerequisite edges between finding groups. This
file adds one: `R11-SEAM-learners` before `R11-ARCH-fabric-learner`. D2-s3-11
and D7-s2-01 fix the arithmetic and the freeze of the folds ADR-007 then
moves unchanged, so the code is moved once, after it is right.

Revision 2 changed four things in the edges:

- **Text after every behaviour it states.** `R11-SEAM-product-text` and
  `R11-SEAM-docs` now also wait on `R11-SEAM-inputs-guards`,
  `R11-SEAM-inputs-freshness`, `R11-SEAM-cycle-solve` and
  `R11-SEAM-cycle-reporting`. Three of the four edit `strings.json`,
  `README.md` or `docs/configuration.md` themselves, and ADR-010's own
  context names the Fahrenheit write of the fourth. Revision 1's projection
  ran product text before `R11-SEAM-inputs-freshness` on `strings.json`; the
  rows below now end in the text groups.
- **The step owner's edge is on the step owner.** `R11-SEAM-kernel-step`
  before `R11-SEAM-actuation-writes` and `R11-SEAM-inputs-freshness`.
- **The deletion's edge is on the deletion.** `R11-SEAM-dead-state` before
  `R11-SEAM-ratchets`.
- **`R11-SEAM-ratchet-raise` has no edge.** D7-s1-04's row moves with every
  group that edits `coordinator.py` and D7-s1-01's with every group that
  edits `const.py`; an edge from one of them was an ordering preference. Each
  row is recorded at the value measured when the owner confirms it, and a
  later merge that lowers it re-records the row downward.

**The deletion's edge is dropped** (decided 2026-11-18, orchestrator under mandate, pending owner confirmation). `R11-SEAM-dead-state` before
`R11-SEAM-ratchets` was an ordering preference by the same reasoning as the
ratchet-raise edge: `R11-SEAM-ratchets` records the import row at the value
measured when it merges, and if `R11-SEAM-dead-state` merges later its
deletions re-record the row downward. `R11-SEAM-ratchets` now has no edge.

Neither comment group carries an edge: a comment rewrite depends on no
behaviour (ADR-010). Both are in the hot-file order below and are released
per file.

**Critical chain by edges, depth 4:** `R11-SEAM-actuation-release`,
`R11-SEAM-actuation-writes`, `R11-SEAM-product-text`, `R11-SEAM-docs`. Two
others are as deep: `R11-SEAM-kernel-step` in the first place, and
`R11-SEAM-kernel-step`, `R11-SEAM-inputs-freshness`, then the two text
groups. Every edge on them is a prerequisite: the held record before the
writes that read it, the step owner before its readers, and text after the
behaviour it states.

### Designs

| group | design |
|---|---|
| `R11-SEAM-kernel-step` | ADR-001 (approved design) |
| `R11-SEAM-kernel-layering` | ADR-002 parts 1 and 3 (approved design) |
| `R11-SEAM-dead-state` | ADR-001 part 4: deletions, no design |
| `R11-SEAM-inputs-freshness` | ADR-002 part 2 for the reader's clock (approved design); the findings are point fixes |
| `R11-SEAM-plant-model`, `R11-SEAM-learners` | ADR-008, with ADR-003 for the switch (approved design of the predicate work; law fixes are point fixes) |
| `R11-SEAM-actuation-release`, `R11-SEAM-actuation-writes` | ADR-004, with ADR-001 for the covering step (approved design) |
| `R11-SEAM-money` | ADR-006 (approved design) |
| `R11-SEAM-ratchets`, `R11-SEAM-ratchet-raise` | ADR-009 (approved design) |
| `R11-ARCH-cycle-surface` | ADR-005 (approved design) |
| `R11-SEAM-tests` | **owed**: `designer.md`; size L with no approved design (decided 2026-11-18, orchestrator under mandate, pending owner confirmation) |
| `R11-SEAM-docs`, both comment groups | ADR-010 (text; no design) |
| `R11-SEAM-card` | **owed**: `designer.md`; size L with no approved design (decided 2026-11-18, orchestrator under mandate, pending owner confirmation) |
| `R11-SEAM-config` | **owed**: `designer.md`, for the entry migration (T18) |
| `R11-SEAM-cycle-solve` | **owed**: `designer.md`, for the one in-flight guard and budget (S14, T14) |
| `R11-ARCH-fabric-learner` | **owed**: `designer.md`, inside ADR-007, with a measured `F`; the designer starts in the first wave, the fixer after `R11-SEAM-learners` (decided 2026-11-18, orchestrator under mandate, pending owner confirmation) |

### Hot-file order

Merge order on a shared file; none of these is an edge. The table is
`projection.py --order`: every file two or more groups name, in the finish
order of the ORDERED cap-3 projection below, so the order stated here is the
one the projection runs. A group's files are its findings' own `files` fields
and what its ADR adds (`COMPONENTS.md`, "Files").

| file | order |
|---|---|
| `coordinator.py` | kernel-step, plant-model, actuation-release, cycle-solve, learners, actuation-writes, money, cycle-reporting, R11-ARCH-fabric-learner, inputs-freshness, entity-service, dead-state, R11-ARCH-cycle-surface, store |
| `const.py` | kernel-layering, kernel-step, config, inputs-freshness, entity-service, dead-state, product-text |
| `config_flow.py` | plant-model, config, tests, money, entity-service, dead-state |
| `pump_arbiter.py` | kernel-step, actuation-release, actuation-writes, cycle-reporting, dead-state, product-text |
| `optimizer.py` | solver, plant-model, cycle-solve, cycle-reporting, dead-state |
| `strings.json` | plant-model, cycle-solve, cycle-reporting, inputs-freshness, product-text |
| `sysid.py` | kernel-layering, ratchets, learners, entity-service, dead-state |
| `accuracy.py` | kernel-layering, learners, dead-state, store |
| `dhw_learning.py` | learners, cycle-reporting, dead-state, store |
| `sensor.py` | kernel-step, plant-model, money, entity-service |
| `thermal_model.py` | inputs-guards, plant-model, actuation-writes, dead-state |
| `boost.py` | cycle-reporting, R11-ARCH-cycle-surface, store |
| `debugger.py` | cycle-reporting, entity-service, store |
| `docs/configuration.md` | cycle-solve, inputs-freshness, docs |
| `heat_curve.py` | inputs-guards, actuation-writes, product-text |
| `legionella.py` | actuation-release, actuation-writes, cycle-reporting |
| `off_restore.py` | actuation-release, cycle-reporting, store |
| `power_guard.py` | kernel-layering, kernel-step, money |
| `services.py` | plant-model, cycle-solve, cycle-reporting |
| `tariff.py` | kernel-layering, money, dead-state |
| `tests/features.py` | learners, R11-ARCH-fabric-learner, inputs-freshness |
| `tests/structure.py` `tests/structure_budgets.json` | ratchet-raise, ratchets, R11-ARCH-fabric-learner |
| `README.md` | cycle-solve, docs |
| `__init__.py` | inputs-guards, config |
| `binary_sensor.py` | inputs-freshness, entity-service |
| `button.py` | cycle-solve, entity-service |
| `comfort_learning.py` `store.py` | kernel-layering, store |
| `currency.py` | kernel-layering, money |
| `diagnostics.py` | cycle-reporting, R11-ARCH-cycle-surface |
| `drift.py` | kernel-layering, kernel-step |
| `entity.py` | kernel-step, entity-service |
| `external_heat.py` | kernel-layering, dead-state |
| `inputs.py` | inputs-guards, inputs-freshness |
| `open_meteo.py` | kernel-step, inputs-guards |
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

What the rows show:

- **No group is first on most rows.** Revision 1's kernel headed about twenty
  rows with five low findings. `R11-SEAM-kernel-step` heads five,
  `R11-SEAM-kernel-layering` heads nine and names no `coordinator.py`, and
  `R11-SEAM-dead-state`, a deletion nothing waits on since its edge into
  `R11-SEAM-ratchets` was dropped, is in eleven rows and first on none.
- **Text is last on the files it shares with behaviour.** `strings.json` and
  `const.py` end in `R11-SEAM-product-text`, `docs/configuration.md` and
  `README.md` in `R11-SEAM-docs`.
- **`R11-SEAM-inputs-guards` is in no `coordinator.py` order.** Its one
  finding there, D1-s3-02 (low), is carried by `R11-SEAM-inputs-freshness` of
  the same seam, so the critical price-scale fix (D2-s3-02) starts at the
  first dispatch and waits on no coordinator slot.
- **`R11-ARCH-fabric-learner` is ninth of fourteen on `coordinator.py`**, not
  last. The footprint budget is read end to end, so a rise merged after it
  counts the same as one merged before.
- **`R11-ARCH-cycle-surface` is thirteenth on `coordinator.py`.** Revision 1
  wanted a proof from it at the first dispatch, for the conditional task-set
  part. That part is withdrawn; what is left is unconditional, size S, and
  nothing waits on it.

### Groups open at P3's start

`check_scopes.py --repo . --round 11 --open-cards` lists them; each appears
here once. The plan adds no edge to or from any of them. A product group lands
before the finding group that shares its file, by the owner's priority for
outside and owner items.

| open group | lane | placement |
|---|---|---|
| `R11-OUTSIDE-ROOMS-P3` | product | before plant-model on `thermal_model.py`, before kernel-step on `coordinator.py`; names `coord_footprint` |
| `R11-OUTSIDE-HONEST-STARTS-RUNS-P3` | product | before solver on `optimizer.py`, before config on `config_flow.py`; names `coord_footprint` |
| `R11-OUTSIDE-HONEST-DHW-RUNS` | product | before solver and plant-model on their files |
| `R11-OUTSIDE-HONEST-METERED-FLOOR` | product | before store on `store.py`; names `coord_footprint` |
| `R11-OUTSIDE-SELF-SETTING-PUMP` | product | before kernel-layering on `accuracy.py`; names `coord_footprint` |
| `R11-VALVE-REFERENCE` | product | before plant-model on `mixing_valve.py` |
| `R11-PRODUCT-TEXT-PINS` | product | before product-text; before config on `config_flow.py` |
| `R11-CARRY-DRAWMAP` | product | before kernel-step or after actuation-writes on `pump_arbiter.py`, never between |
| `R11-CARRY-ROOM-LIFT` | product | no shared file with a finding group |
| `R11-PRE-SHARED-FILES` | instrument | before ratchets and ratchet-raise on `tests/structure_budgets.json` |
| `R11-INTAKE-R10-RESIDUE`, `R11-PRE-TOKEN-LEDGER`, `R11-PREPR-STEP-TIMING` | instrument | the roster's own order; no shared file |
| `R10-NUDGE-RETIRE`, `R11-PRE-HANDOFF-BOOKKEEPING`, `R11-PRE-SECURITY-PRIVACY` | policy | serial, on the owner's approving review; before governance-text where a rule file is shared |
| `R11-CLOSEOUT-CLEANUP` | instrument | last, at the round's end |

Four of the product groups have merged since P3 started, each read with
`score.py --diff <merge>^1 <merge>`: #3697 (`R11-OUTSIDE-HONEST-STARTS-RUNS-P3`),
#3670 (`R11-OUTSIDE-HONEST-METERED-FLOOR`) and #3685 (`R11-VALVE-REFERENCE`)
read NULL, and #3662 (`R11-OUTSIDE-SELF-SETTING-PUMP`) reads `coord_footprint`
2502 to 2505, which is in the moves table and in `R`.

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
same roster with the comment groups' file order written as edges. **Every
figure is a lower bound**: the model leaves out the five owed designs and
the open product groups. The figures below are re-run after the
`dead-state` to `ratchets` edge was dropped (2026-11-18).

| roster | cap 3 | cap 2 (the tool's default) |
|---|---|---|
| PUBLISHED: the draft as it is | 175.63 h | 243.53 h |
| ORDERED: both comment groups after every group sharing a file | 209.62 h | 278.67 h |

- 27 groups, 14 of them touching `coordinator.py`; fourteen start at once on
  the published roster at cap 3 (thirteen before the edge was dropped), and the coordinator cap binds from the first
  wave.
- Published, cap 3: critical path 173.63 h on the chain by edges above; the
  last groups to finish are `R11-SEAM-docs` and `R11-ARCH-fabric-learner`.
  In revision 1 the last was a coordinator group held by the cap alone.
- Revision 1 read 174.05 h (published) and 209.62 h (ordered) at cap 3.
  `projection.py --rev1` adds the four text edges to that roster and nothing
  else: 209.58 h and 210.77 h. (The review stated 176.78 h for the published
  row; this run does not reproduce it.) On revision 1's roster the edges made
  both text groups wait for `R11-SEAM-inputs-freshness`, which ran 104.15 h
  to 138.10 h behind the kernel. The rows above have the edges, the kernel's
  cut and `R11-SEAM-inputs-guards` out of the coordinator order.
- ORDERED, cap 3: the critical chain is `R11-SEAM-plant-model`,
  `R11-SEAM-learners`, `R11-ARCH-fabric-learner`, `R11-SEAM-comments-tests`.
  It was 210.77 h and 279.82 h with the edge.
- The round's figure lies between the two rows. PUBLISHED lets a comment
  group finish while files are still held; ORDERED holds the whole group for
  its last file. Parts released per file (ADR-010) are what moves it toward
  the first row.

**How the coordinator queue is ordered.** `replan.py` gives a coordinator
slot by its dispatch key: tier, then the longest remaining path behind the
group, then duration, then name. Severity is not in the key. The plan does
not edit the model, so it shapes what the key sees:

| group | severity | starts | finishes | why there |
|---|---|---|---|---|
| `R11-SEAM-inputs-guards` | critical | 0 h | 33.95 h | no `coordinator.py` in its files; revision 1 ran it 105.30 h to 139.25 h behind one low finding |
| `R11-SEAM-plant-model` | critical | 0 h | 35.10 h | first coordinator wave, by the path behind it (learners, the fabric group, docs) |
| `R11-SEAM-actuation-release` | high | 0 h | 35.10 h | first coordinator wave, on the critical chain |
| `R11-SEAM-kernel-step` | low | 0 h | 33.95 h | first coordinator wave: two groups wait on the step owner |
| `R11-ARCH-cycle-surface` | none | 138.10 h | 164.02 h | size S with nothing behind it; unconditional since ADR-005 part 3 was withdrawn |

`R11-SEAM-money` (high) and `R11-SEAM-inputs-freshness` (high) take the
second and third coordinator waves, 35.10 h and 70.20 h on the published
roster. The orchestrator may start either ahead of a medium group when a
slot frees: no edge forbids it, and the hot-file rows they are in end the
same way.

Not in the model: the five designs owed (designer, design review, then the
fixer), the open groups above, which share the slots and the coordinator cap,
and any part cut from a group. `R11-SEAM-config`, `R11-SEAM-cycle-solve`,
`R11-SEAM-tests` and `R11-SEAM-card` each start later than drawn by their
design's duration. `R11-ARCH-fabric-learner`'s design runs from the first
wave beside `R11-SEAM-learners`, so it delays the group only if it outlasts
that predecessor.

**Against the template.** `dev/programme/round11/phases.json` carries no
forecast for the fix waves and the playbook states no hours for them, so
there is no template figure to compare with; the comparison this plan can
state is the cap sensitivity above. The orchestrator's replan on the merged
roster is the round's figure.

## Risks

| risk | check |
|---|---|
| **Admissibility: `coord_footprint`.** Main reads nine above the fork before any group of this plan has merged, fourteen groups and the open product groups add statements, and the fall that pays for them (ADR-007) is prototyped at 28 statements behind a design that is still owed. Without it the round is inadmissible whatever dS reads. | ADR-007's designer starts in the first wave (decided 2026-11-18, orchestrator under mandate, pending owner confirmation). `plan_audit.py end-to-end --fork <fork> --head origin/main` after every coordinator merge; the running `R` against `6 + F`; the plan returns to the owner when `R` passes 26 or the designer's `F` leaves the budget below `R` (ADR-007 part 5). |
| **Admissibility: every other metric.** An argued rise in any other scored metric or tripwire makes the round inadmissible end to end, and no move pays it back. | Such a rise is a review block for a group of this roster; the orchestrator reads the tripwire lines of each merged body and of the end-to-end reading. |
| **The spread rule's "three scored classes" cannot be met by the instrument's own classes.** `vector.py` gives a class to six metrics; two classes can improve (N-shared-config, P2+P3). P6 and N-name-sort read 0 at the fork and N-structure-blind's one member is a barrier's declaration. The third improving group is the unclassed floor metrics (`layer_violations`, `coordinator_private_reach`), which `weights.json` describes as guarding no single register class. | The floor metrics count as the third scored class (decided 2026-11-18, orchestrator under mandate, pending owner confirmation). If the owner rules they do not count, the condition cannot be met at this fork without deleting behaviour, and the plan says so here and does not plan the deletion. |
| **The 40 % cap is expected to fail in the planned case.** `duplication_copies` supplies 39.5 %, and one further clone removed by a sound fix (the Carnot expression in `R11-SEAM-plant-model`, D2-s1-01, the round's critical finding) reads 43.0 %: dS rises and the spread condition fails. In the floor case there is room for one copy. | The cap is checked at the stamp, not at plan time (decided 2026-11-18, orchestrator under mandate, pending owner confirmation): the share is read at each stamp from `plan_audit.py end-to-end`. The plan does not hold a sound removal back to protect a share. If the share passes 40 % the target is reported not met on spread, with the per-metric table, and the owner rules. |
| **One prototyped move is conditional** (the one-row scalar, ADR-006 part 2). | `tests/golden/` byte-identical and the solve-time harness. A dropped part is recorded; "The cases" states the floor. |
| **A further failure puts the round short.** The floor case is 0.32 above the target, and one clone arm unrealised from there reads 0.90 short. | The orchestrator reads `plan_audit.py end-to-end --fork <fork>` at each stamp; each clone arm is one group's part and is seen at that group's merge. A prototyped move reported UNREALISED returns the plan to the architect before the last wave. |
| **One finding is carried by six groups.** D7-s1-05's arms merge at six times, and an arm can be forgotten by a group whose own findings are larger. | Each carrying group's roster entry names its arm; the clone census (`m7_sites.py`) is the class sweep at every one of those merges; the finding closes when the census reads the planned count. |
| **The two `private_cross_module` crossings are a rename unless the new reader lands.** | Named at 0.0. The reviewer finds the reader in the PR's diff (ADR-008); otherwise `metric-gamed`, not banked. |
| **The score reading better than the code: an in-place write moved, not removed.** ADR-004 lowers `shared_inplace_writes` by moving the circulation pumps' post-await store into a new owner class. The metric's definition reads that as encapsulation and D16-s3-02 asks for the owner, but the count would fall the same way for a wrapper that owns nothing. | The move is banked only when the PR registers the real restoring owner with `off_restore.py` and D16's release cells pass on the PR: the owner must be the one that restores on Off, stale plan, unload and remove (decided 2026-11-18, orchestrator under mandate, pending owner confirmation). A class that only holds the dict is `metric-gamed`. Not banked, the round reads `no-circ`, +21.1938 end to end, short of the target ("The cases"), and the plan returns to the architect for a paying move. |
| **The score reading better than the code: clones.** An in-function copy is not counted (D7-s1-02), and the scorer's repair is deferred. | Fix review step 14 runs `m7_floor_plants.py`'s place-keyed owner on every PR that lowers `duplication_copies`. |
| **The score reading better than the code: values not handles.** A wrapper, an accessor or a rebind lowers `coordinator_private_reach` or `shared_inplace_writes` with the coupling unchanged. | ADR-003, ADR-004 and ADR-005 each name the refused spelling; the reviewer re-runs the arm with the fixer's diff and reads the tripwires. |
| **Sensitivity S6, T6: the Carnot fix moves every learned correction and golden fixture.** | Claimed drift with its direction (`tests/golden/claimed_drift.txt`); learners run after plant-model so each is re-measured once. |
| **Sensitivity S9, S11: the held record.** Release and writes both redefine it; `R11-CARRY-DRAWMAP` edits the same file. | The D16 enumerator's release and write cells after each of the three merges. |
| **Seams likely to need redesign: the config migration (T18) and the solve admission (T14).** Both are designer-owed and irreversible or user-visible. `R11-SEAM-tests` and `R11-SEAM-card` (both L) are designer-owed too. | Design review at the handoff SHA; a third `revise` re-cuts the group (`design-review.md`). |
| **`R11-SEAM-dead-state` is cut by kind of edit, across seams.** A deletion that a reader found later needs is a behaviour change, and a group merging before it may add such a reader. | Each deletion's proof, re-run at the PR's head, is that no production code and no stored document reads the name; the suite and `tests/golden/` unchanged. It is first on none of its rows, so the groups that could add a reader have mostly merged by then. |
| **Fourteen groups on `coordinator.py` at a cap of three.** The cap, not an edge, sets most of the wall: cap 2 costs 68 h more. | The orchestrator's replan at each wave edge; a group whose fix lands wholly in its owning module leaves the coordinator order when its fixer says so. |
| **A ratchet repair reads as a budget raise** (`const_modules_over_50`), and D7-s1-04's limit is the owner's to choose. | The owner's confirmation before the push (ADR-009); `budget-raise-gate`. Both are in `R11-SEAM-ratchet-raise`, so nothing else waits on it. |
| **T7, T16, T18 change what an existing install does at upgrade.** | Each PR's release-notes step, first in the notes; the docs group verifies them last. |
| **The instrument-comment reading is pending owner confirmation** (`COMPONENTS.md`, "Deferred"): fourteen rows and ten merged into them. | The deferral to round 12 under the tooling freeze stands (decided 2026-11-18, orchestrator under mandate, pending owner confirmation). If the owner rules the other way, one text-only group joins with no edge; no move changes. |
| **Holdout 5, change coupling.** One-owner moves add import edges. | `plan_audit.py compare` at the stamp; the kernel's work is three PRs and six arms, not one PR over 34 files. |

## Open points for the owner

Points 1, 2, 4 and 6, and the review's remaining blocking and noted points,
were decided 2026-11-18, orchestrator under mandate, pending owner confirmation. Each stands until the owner confirms or rules otherwise.

1. **The spread rule.** Whether the unclassed floor metrics count as the
   third scored class (the instrument gives them no class). **Decided
   2026-11-18, orchestrator under mandate, pending owner confirmation:** they
   count as the third scored class.
2. **The deferral of comment-only edits to instrument files**, fourteen rows
   and the ten merged into them, to round 12 under the freeze, against the
   2026-11-13 text-scope ruling. **Decided 2026-11-18, orchestrator under
   mandate, pending owner confirmation:** the 24 rows stay deferred to round
   12 under the tooling freeze.
3. `const_modules_over_50` rising under D7-s1-01's repair, and the limit of
   D7-s1-04's module-span row: both owed before `R11-SEAM-ratchet-raise`
   pushes.
4. **`coord_footprint` and ADR-007.** Main reads nine above the fork; ADR-007
   is the payment, prototyped at 28 statements, and its design is owed.
   `designer.md` pipelines a designer behind the group's last predecessor,
   here `R11-SEAM-learners`, which finishes between 70 h and 138 h into the
   projection. Whether this
   group's designer may start at the first wave, so that `F` is measured
   before most coordinator merges. **Decided 2026-11-18, orchestrator under
   mandate, pending owner confirmation:** the designer starts in the first
   wave, so `F` is measured before `R` is spent; the fixer still waits on
   `R11-SEAM-learners`.
5. D6-s1-01's intended values: whether the legionella default returns to 7
   days or the docs say 10, and whether a write gets the 60 s echo grace the
   docs state. The docs group aligns the text to the merged code unless the
   owner decides the code changes, which is then the owning seam's fix.
6. **The 40 % cap.** The planned case reads `duplication_copies` at 39.5 %,
   and the Carnot fix is expected to take it to 43.0 %. Whether a sound clone
   removal that takes a metric past 40 % fails the target. **Decided
   2026-11-18, orchestrator under mandate, pending owner confirmation:** the
   40 % cap is checked at the stamp, not at plan time.
7. **`R11-SEAM-dead-state` is one group across seams**, a stated deviation
   from step 4 (`COMPONENTS.md`, "Cut by kind of edit"). The alternative is
   its deletions carried per seam by six groups, with six edges into
   `R11-SEAM-ratchets`.
8. **The circ term** (review point 7). **Decided 2026-11-18, orchestrator
   under mandate, pending owner confirmation:** it is banked only when the
   PR registers the real restoring owner; "The cases" carries `no-circ` and
   `floor-no-circ`, both short of the target.
9. **Review points 4, 5 and 9**, applied without a fourth review.
   **Decided 2026-11-18, orchestrator under mandate, pending owner
   confirmation:** designs are owed for `R11-SEAM-tests` and `R11-SEAM-card`
   (both L); the `dead-state` to `ratchets` edge is dropped; the hub move's
   fixer brief and ADR-003 carry a stale-holder acceptance check
   (`early_cutoff`'s `held.wiring`).

## What revision 2 changed, by review point

The review at `6a73d86e43` is the second `revise`. Its blocking points were
2a, 2b, 3a and 3b.

| point | what changed | where |
|---|---|---|
| 1, triage | Recount unchanged: 220 ids, 152 keep, 23 merge, 40 defer, 5 refuse. Six kept ids changed group with the kernel's cut and D1-s3-02's move. The instrument-comment deferral stays the owner's (open point 2). | `COMPONENTS.md`; `PLAN.json` |
| 2a, text edges | Four edges added into each text group; the projection re-run with them. | "Edges"; ADR-010 part 1; `projection.py` |
| 2b, the kernel | Cut into `R11-SEAM-kernel-step`, `R11-SEAM-kernel-layering` and `R11-SEAM-dead-state`; six arms of D7-s1-05 and the reader's clock carried by the groups of their owning seams; each out-edge on the part that satisfies it. Each per-seam arm re-read alone. | `COMPONENTS.md`; ADR-001, ADR-002; `prototypes.py` (`SEAM_ARMS`) |
| 2, the weak edge | The edge into `R11-SEAM-ratchet-raise` removed. | "Edges"; ADR-009 |
| 3a, the task set | ADR-005 part 3 withdrawn; the term is out of the projection and the metric is named at 0.0. S36 rewritten to what the code does. | ADR-005; `SCENARIOS.md`; "Not planned" |
| 3b, the renamed count | Both `private_cross_module` terms at 0.0 in the moves and out of the projected dS. | ADR-008; `PLAN.json` |
| 3, the consequence | The planned case is the review's no-tasks case; the floor and one arm short of it are stated with their readings. The circulation move's check is written as a risk and an acceptance condition. | "The cases"; "Risks"; ADR-004 |
| 4, spread | Stated as not declarable until the owner rules; the 40 % cap stated as expected to fail. | "The cases"; open points 1 and 6 |
| 4, admissibility | Re-read at main `f567988b51`: nine above, `R` at 9 of 34. Every other metric: no payment, so a rise is a review block. | "Admissibility"; ADR-007 |
| 4, the allow | The `--allow` declaration removed; both sides are read on the fork's instrument. | "Fitness functions"; ADR-009 |
| 5, order | `R11-SEAM-inputs-guards` leaves the coordinator order; the dispatch key and the placement of the critical and high groups are stated; the lower bound is stated in the projection's first lines. | "Projection" |
| 6, ADRs | ADR-005 matches its scenarios. ADR-007 states its driver, the footprint payment, and that its decisive content, the measured `F`, is owed. | ADR-005; ADR-007 |

## Applied 2026-11-18, the decided open points

Decided 2026-11-18, orchestrator under mandate, pending owner confirmation, after the third review at `446a5aa904`; no
fourth review was run.

| decision | what changed | where |
|---|---|---|
| floor metrics are the third class (open point 1) | the target's spread condition no longer waits on a ruling | "The cases"; "Risks" |
| 40 % cap checked at the stamp (open point 6) | the share is read at each stamp, not held at plan time | "The cases"; "Risks" |
| 24 instrument comment rows to round 12 (open point 2) | the deferral stands under the tooling freeze | "Risks"; open point 2 |
| ADR-007's designer in the first wave (open point 4) | the designer runs beside `R11-SEAM-learners`; the fixer still waits on it | "Designs"; "Admissibility"; ADR-007; the fabric group's brief |
| circ banked only with the registered restoring owner (open point 8) | `no-circ` +21.1938 and `floor-no-circ` +19.8367 end to end added | "The cases"; "Risks"; ADR-004; `prototypes.py`; the actuation-release brief |
| designs owed for `R11-SEAM-tests` and `R11-SEAM-card` | both L groups listed as designer-owed; the projection's omissions are five designs | "Designs"; "Projection"; both groups' briefs |
| `dead-state` to `ratchets` edge dropped | `R11-SEAM-ratchets` has no edge; ORDERED re-run 209.62 h / 278.67 h, PUBLISHED unchanged | "Edges"; "Hot-file order"; "Projection"; ADR-009; `COMPONENTS.md`; the three roster files |
| stale-holder acceptance check | `early_cutoff`'s `held.wiring` reads the replaced context's values before the next re-arm | ADR-003; the cycle-reporting brief |

## Revision 3, 2026-11-18: the objective (decision 0018)

Started on the owner's order of 2026-11-18, as the dispatch brief relays it:
re-plan from the current state so that decision 0018's objective ranks the
work. `REVIEW.md` point 0 stands otherwise (`plan-review.md` starts no third
revision by itself). Revisions 1 and 2 ran the contract copies of the round
branch, which lacked `architect-planner.md`'s objective clause
(`dev/audit/rca/R11-RCA-PLAN-OBJECTIVE-MISSING.md` on
`rca/r11-plan-objective-missing`). This branch now merges main, so every
contract, checker and `tools/plan/replan.py` is read at the plan SHA as main
has it.

Everything above this section is revision 2 and stands, except where a row of
`CHANGES-R3.md` names it: the groups, the moves, the ADRs, the cases and the
nine decided open points are unchanged.

### What was measured, and where it differs from the brief

- **Roster.** `handoff/audit-r11-roster` does not exist on origin. The newest
  `wave-r11-groups.json` is on `handoff/audit-r10-roster` at `c7e683a6d4`; the
  draft `wave-r11-groups.json` beside this file is that blob with the two
  order changes below. `build_objective.py` rebuilds both from that commit.
- **Stages lag the refs.** The roster reads `R11-INTAKE-R10-RESIDUE`,
  `R11-SEAM-cycle-solve`, and others `not-started` while
  `dispatch/fixer-r11-intake-r10-residue` and `dispatch/fixer-r11-seam-cycle-solve`
  exist. The projection reads the roster's stage word, so it prices those
  groups whole; the figures are upper bounds for them.
- **The pin.** `objective.pin` in `PLAN.json`: the draft's blob, the start
  (the instant of the build, not the fork) and the blob of
  `tools/plan/durations.json`.

### The block

`PLAN.json`'s `objective` block holds `plan_audit.py`'s `OBJECTIVE_KEYS` and
nothing else. `PLAN.json`'s `groups` now names every open group of the draft:
the 27 seam and architecture groups of revision 2, all still open, and the 13
other open roster groups, each marked `origin: roster` (ranked and projected
here; brief, files and edges stay the roster's).

- **Terms.** Twelve of the thirteen are NO-READ in
  `dev/audit/yardstick/round10/OBJECTIVE.json`, so each is `undecided` with the
  baseline's own builder. `first_pass` is the one term read; predicted `hold`,
  since this plan changes no review rule.
- **Ranks.** Derived, never typed: `removes` is the group's findings; `classes`
  is keyed only where a verified `bug` finding of the group carries that class
  (a hygiene finding's class tag keys nothing); `cards` is keyed for
  `R11-INTAKE-R10-RESIDUE` alone (`E11-N-INTAKE-BUILDER`, the builder of the
  reads behind eight layer-1 terms). Rank 1: 19 groups. Rank 2: 21 groups,
  each naming the close pass that examines its merged diff.
- **Edges.** None: no rank-1 group waits on a rank-2 group through `after`.
- **Dispositions.** None: no earlier plan was settled.

### What the objective changed

1. **Thirteen verified `bug` findings were deferred with no card.** All are
   defects of audit instruments, deferred under the instrument freeze. Their
   triage rows now carry `card: P11`, the owner card that rules the deferral
   (`dev/programme/RULINGS.md`: "P11: Freeze, except production defects, owner
   orders and red main"). None is moved into round 11: P11's shape is a local
   in-round overlay where one blocks and a proposal at round-end triage. Three
   are read through by a term and lead that triage: D0-s3-01 and D17-s1-01
   (a finder universe that prints short, so `coverage`'s denominator), and
   D11-s2-01 (two merges admitted while `gate` was red, `product_green`).
   D11-s1-06 (`wt_sync.sh --self-test` runs the production push) owes the
   overlay now.
2. **`R11-SEAM-store` (rank 1, five bug findings) was last on the coordinator
   turn, behind `R11-SEAM-dead-state` (rank 2, one hygiene finding).** Both are
   M, both have no edge, and `replan.py` breaks the tie by name. The draft
   orders `R11-SEAM-dead-state` after `R11-SEAM-store`.
3. **`R11-INTAKE-R10-RESIDUE` (rank 1) waited for a slot behind first-wave
   rank-2 work.** `R11-SEAM-comments-production` (XL, rank 2, not dispatched)
   held a first-wave slot. The draft gives it `R11-SEAM-product-text`'s
   predecessors: comments are text, and ADR-010 already orders text after the
   behaviour it states. Its approved design stays valid; its line anchors are
   re-read at the later base.
4. **Every rank-2 group owes an examination before the close** (`unexamined`):
   a finder pass of the named dimension over the merged diff, reporting its
   universe and denominator. Eight dimensions are named (D2, D5, D6, D7, D11,
   D13, D16, D17). `replan.py` does not price these passes.

`CHANGES-R3.md` holds one row per change with its effect on in-flight work.

### The projection, and the floor's cost

`python3 -I tools/audit/seat/plan_audit.py objective-check --ref <plan SHA>
--plan dev/audit/rounds/round11/PLAN/PLAN.json --register
dev/audit/rounds/round11/JUDGE.json` prints every figure below;
`PROJECTION.json` is its record and `OBJECTIVE-CHECK.txt` its output.

| reading | figure |
|---|---|
| projection A (the draft): critical path, wall | 139.68 h, 202.27 h |
| projection A: closure | 2026-11-27T02:56Z |
| projection A: `lead_time` p50, p90 over production groups | 35.1 h, 174.35 h |
| projection B (A less the 21 rank-2 groups): critical path | 104.15 h |
| floor cost, A less B: critical path, wall | 35.53 h, 38.75 h |
| largest delay of a rank-1 group against B | 0.2 h |

The floor cost is what the score target and the other rank-2 work add to the
round's closure. It delays no rank-1 group by more than 0.2 h, which is the
stamp cadence. Against the unchanged roster at the same pin (the same
`replan.py`, run on `c7e683a6d4`'s blob): the last rank-1 group finishes
161.7 h after the pin and not 195.7 h, closure and wall are unchanged, and the
two delays the check printed (34.15 h on `R11-SEAM-store`, 14.22 h on
`R11-INTAKE-R10-RESIDUE`) are gone.

These hours supersede revision 2's `projection.py` figures as the round's
projection: `replan.py` at the pin prices started work at its remaining
fraction and holds the coordinator cap of two, which `projection.py` did not.
`PLAN.json`'s `hours`, `critical_chain` and `depth` are revision 2's and are
kept as that revision's record.

### The score target

Unchanged by revision 3: no move, metric, ADR or prediction changed, so the
cases stand as revision 2 states them (planned +24.3811, floor +22.9801,
`no-circ` +21.1938, `floor-no-circ` +19.8367). The two order changes move no
dS; `R11-SEAM-dead-state` and `R11-SEAM-comments-production` carry none.
Re-read at main `8751943e17`: `plan_audit.py end-to-end --fork 92d38ecb64
--head origin/main` reads dS +0.0430 WORSENS with `coord_footprint` -0.0063,
against -0.0052 at the third review. Admissibility is still unshown, and
ADR-007 is still its payment. `R11-ARCH-fabric-learner` and
`R11-ARCH-cycle-surface` are rank 2 and are the last two coordinator turns:
the objective ranks them behind every bug fix, and the floor still needs them.

### Limits of this revision

- **An outside report of this window ranks 2.** `R11-OUTSIDE-HONEST-DHW-RUNS`
  and `R11-OUTSIDE-SELF-SETTING-PUMP` fix reported defects, and the grammar
  keys an escape only by an `in` row of the baseline's ledger, which holds
  round 10's. Both are started, so the rank moves nothing.
- **`R11-PRE-TOKEN-LEDGER` ranks 2** though it builds `tokens_per_change`'s
  read: no open card names it.
- **The two order changes are written as `after` in the draft** because
  `replan.py` reads no other order. Each is a turn order, not a prerequisite:
  it lapses if its predecessor is stopped or deferred.
- **Eleven open cards name no group** (`check_scopes.py --round 11
  --open-cards` lists twelve; one is keyed above). They stay the owner's.
