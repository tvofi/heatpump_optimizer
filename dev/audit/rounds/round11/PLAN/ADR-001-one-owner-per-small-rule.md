# ADR-001: a small rule has one owner, and a copy is removed by sharing it

Groups: `R11-SEAM-kernel` (D7-s1-05, D7-s3-03, D7-s3-04, D7-s3-05), read by
`R11-SEAM-actuation-writes` and `R11-SEAM-inputs-freshness`.

## Context

`counters.gapped_clones` lists 14 clone classes at the fork (D7 s1's
`m7_sites.py`). Eight are a rule of a few statements with no owner. D7-s3-03
and D7-s3-04 show copies that already disagree: the step covering now has two
copies with no end rule, water's heat capacity has three values, a naive
instant has two zones and "finite number" four domains.

## Decision

1. Each of the eight rules gets the one-owner form D7 s1 prototyped
   (`D7/s1/m7_prototypes.py`, arms note, avail, step, day, reader, fdjac,
   entry, notice). The owner is the module that already owns the concept:
   `drift.py` the evidence notes, `entity.py` the payload-flag availability,
   `plan_step.py` the covering step, `price_model.py` the usable day,
   `inputs.py` the entry's reader, `sysid.py` the forward-difference Jacobian,
   `ledger.py` the month's entry, `legionella.py` the interval notice.
2. `plan_step.py` owns "the step covering an instant" with its half-open end
   rule; `coordinator._covering_index`, `pump_arbiter._step_index`, both
   `_planned_room` copies and every actuator in `R11-SEAM-actuation-writes`
   read it.
3. Water's heat capacity, a naive instant's zone and the finite test get one
   definition each in the kernel (`const.py`, `drift.py`, `const.finite_float`).
4. D7-s3-05's dead state is removed only where no production code and no
   stored document reads it; a parameter a caller still computes is removed at
   the caller too.

## Alternatives

- A module function handed the detector's list (the `note_helper` arm): the
  score reads its writes as six more in-place writes into a shared object and
  the change is inadmissible. Refused; it is this move's control.
- Folding two bodies under one function with nothing shared (the `fold` arm):
  D7-s1-02 shows the census pays it. Refused as `metric-gamed`; the reviewer's
  check is `m7_prototypes.py --only fold --fold-owner`, which reads NULL.
- One PR per seam for the eight arms: eight hot-file orders for nine copies;
  the finding is one root (no owner) and stays one group.

## Consequences

- The kernel is first in file order on `pump_arbiter.py`, `price_model.py`,
  `ledger.py`, `legionella.py`, `sysid.py`, `sensor.py` and `coordinator.py`.
- A shared helper adds an import edge (tradeoff T12): `layer_violations`,
  `import_cycle_modules` and `private_cross_module` are acceptance checks.
- The six classes left (the solver's and the plant model's scalar and batch
  twins, `inputs.read`) are not planned here; ADR-006 takes one.

## Scenarios served

Maintainability, first scenario (S12, T12); actuator safety, second scenario
(S10).

## Move and fitness functions

`duplication_copies` falls by nine copies in `R11-SEAM-kernel` (D7 s1's
combined prototype, every reverted arm NULL). Acceptance: `shape_copies` and
`duplication_copies` in `tests/structure.py` do not rise;
`shared_inplace_writes` flat (the `note_helper` control); `m8_agree.py` reads
no disagreeing probe; D7 s1's `--suite` comparison loses no check line;
mutation kill rate on the touched modules not below the fork's.
