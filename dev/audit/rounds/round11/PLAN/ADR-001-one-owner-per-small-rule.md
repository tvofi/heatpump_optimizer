# ADR-001: a small rule has one owner, and a copy is removed by sharing it

Groups: `R11-SEAM-kernel-step` (D7-s3-03, D7-s3-04, D7-s1-05) and
`R11-SEAM-dead-state` (D7-s3-05). Six arms of D7-s1-05 are carried by
`R11-SEAM-entity-service`, `R11-SEAM-money`, `R11-SEAM-learners`,
`R11-SEAM-actuation-release` and `R11-SEAM-inputs-freshness`. The step owner
is read by `R11-SEAM-actuation-writes` and `R11-SEAM-inputs-freshness`.

## Context

`counters.gapped_clones` lists 14 clone classes at the fork (D7 s1's
`m7_sites.py`). Eight are a rule of a few statements with no owner. D7-s3-03
and D7-s3-04 show copies that already disagree: the step covering now has two
copies with no end rule, water's heat capacity has three values, a naive
instant has two zones and "finite number" four domains.

The eight rules are one class (N-duplicated-rule, P2) and not one seam. The
owner of each already exists, and by `COMPONENTS.md`'s table five of the
eight sit outside the kernel: `price_model.py` and `ledger.py` in money,
`sysid.py` in the learners, `legionella.py` in actuation, `entity.py` in the
entity surface and `inputs.py` at the input boundary. Only `plan_step.py`,
`const.py` and `drift.py` are the kernel's.

## Decision

1. Each of the eight rules gets the one-owner form D7 s1 prototyped
   (`D7/s1/m7_prototypes.py`, arms note, avail, step, day, reader, fdjac,
   entry, notice), in the module that already owns the concept, **built by
   the group of that module's seam**:

   | arm | owner | seam | carried by | copies |
   |---|---|---|---|---|
   | note | `drift.py`, the evidence notes | kernel | `R11-SEAM-kernel-step` | 1 |
   | step | `plan_step.py`, the covering step | kernel | `R11-SEAM-kernel-step` | 1 |
   | avail | `entity.py`, the payload-flag availability | entity surface | `R11-SEAM-entity-service` | 2 |
   | day | `price_model.py`, the usable day | money | `R11-SEAM-money` | 1 |
   | entry | `ledger.py`, the month's entry | money | `R11-SEAM-money` | 1 |
   | fdjac | `sysid.py`, the forward-difference Jacobian | learners | `R11-SEAM-learners` | 1 |
   | notice | `legionella.py`, the interval notice | actuation | `R11-SEAM-actuation-release` | 1 |
   | reader | `inputs.py`, the entry's reader | input boundary | `R11-SEAM-inputs-freshness` | 1 |

   D7-s1-05 is triaged once, into `R11-SEAM-kernel-step`. It closes when the
   last arm has merged; the clone census is the class sweep at each of the
   six merges.
2. `plan_step.py` owns "the step covering an instant" with its half-open end
   rule; `coordinator._covering_index`, `pump_arbiter._step_index`, both
   `_planned_room` copies and every actuator in `R11-SEAM-actuation-writes`
   read it. This is `R11-SEAM-kernel-step`'s part and the reason for its two
   out-edges.
3. Water's heat capacity, a naive instant's zone and the finite test get one
   definition each in the kernel (`const.py`, `drift.py`, `const.finite_float`);
   the copies in other modules are replaced by a read of it, in
   `R11-SEAM-kernel-step`.
4. D7-s3-05's dead state is removed only where no production code and no
   stored document reads it; a parameter a caller still computes is removed at
   the caller too. `R11-SEAM-dead-state` does this and deletes the fourteen
   import bindings D7-s1-03 lists, in `config_flow.py`, `coordinator.py`,
   `modbus_prefill.py`, `optimizer.py`, `pump_arbiter.py` and
   `thermal_model.py`, and moves `tests/guard_pins.py`'s import of
   `channel_heating_steps` to its owner; `R11-SEAM-ratchets` then records the
   row at zero (ADR-009 part 1).

## Alternatives

- One group for the class (this plan's revision 1, `R11-SEAM-kernel`): 34
  files in at least six seams, five low findings first on about twenty
  hot-file rows, and three out-edges each satisfied by a different part.
  `architect-planner.md` step 4 cuts a class spanning seams into one group
  per seam. Refused.
- A module function handed the detector's list (the `note_helper` arm): the
  score reads its writes as six more in-place writes into a shared object and
  the change is inadmissible. Refused; it is this move's control.
- Folding two bodies under one function with nothing shared (the `fold` arm):
  D7-s1-02 shows the census pays it. Refused as `metric-gamed`; the reviewer's
  check is `m7_prototypes.py --only fold --fold-owner`, which reads NULL.
- The dead state cut per seam like the arms: its deletions create or move no
  owner, so no seam's design is touched; six groups would each carry a few
  one-line deletions and `R11-SEAM-ratchets` would wait on all six. Kept as
  one group and stated as a deviation (`COMPONENTS.md`, "Cut by kind of
  edit"; `PLAN.md`, open point 7).

## Consequences

- No group is first on most hot-file rows (`PLAN.md`, "Hot-file order").
  Each arm is a few lines in a file its carrying group already edits.
- One finding is carried by six groups, so an arm can be dropped unnoticed.
  Each carrying group's roster entry names its arm, and `PLAN.md`'s cases
  state what one arm unrealised costs: from the floor it reads 0.90 short of
  the target.
- A shared helper adds an import edge (tradeoff T12): `layer_violations`,
  `import_cycle_modules` and `private_cross_module` are acceptance checks.
- The six classes left (the solver's and the plant model's scalar and batch
  twins, `inputs.read`) are not planned here; ADR-006 takes one.

## Scenarios served

Maintainability, first scenario (S12, T12); actuator safety, second scenario
(S10).

## Move and fitness functions

`duplication_copies` falls by nine copies over six groups, each arm read
alone at the fork by `prototypes.py --only kstep,avail,owners,fdjac,notice,reader`:
two, two, two, one, one and one. D7 s1's combined prototype reads the nine in
one tree, every reverted arm NULL. Acceptance, for each carrying group:
`shape_copies` and `duplication_copies` in `tests/structure.py` do not rise;
`shared_inplace_writes` flat (the `note_helper` control); `m8_agree.py` reads
no disagreeing probe; D7 s1's `--suite` comparison loses no check line;
mutation kill rate on the touched modules not below the fork's. The import
deletions read NULL (`prototypes.py --only imports`); `m1_ratchet_census.py`
reads `unused_package_imports` 0 after `R11-SEAM-dead-state` merges.
