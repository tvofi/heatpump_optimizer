# ADR-004: every entity the optimizer writes has one owner of the write, its record and its restore

Group: `R11-SEAM-actuation-release` (D16-s3-02, D16-s3-01, D16-s1-04,
D16-s3-03, D16-s3-04, D1-s2-04). This ADR is the group's approved design.

## Context

`off_restore.py` restores the consumers registered at import: the space
set-point, the heat curve and its MQTT twin. The supply switch, the frequency
number, the valve target and the circulation pumps stop being written in Off
and on unload, and nothing writes their baseline back (D16-s3-02). The
circulation pumps' record is a dict on the coordinator written in an async
method (`coordinator.py:4570`), one of the three `shared_inplace_writes`
sites. `tests/features.py` pins "Off writes the space set-point's baseline
back and nothing else", against the D16 owner ruling of 2026-11-15
(D16-s3-01).

## Decision

1. `off_restore.py`'s registry is the one restore owner. Every writer arms it
   before its first write and is restored on Off, stale plan, unload and
   remove, with a retried restore.
2. Each written entity has one owner object holding the write and the record
   of the write. The circulation pumps get theirs: the coordinator's dict and
   `_async_set_pump`'s body move into it, and the pump decision in
   `_async_drive_pumps` is handed values, not the coordinator.
3. The baseline row written on Off and on unload is built with the cycle
   flags cleared (D16-s3-03).
4. The pinned "nothing else" check is re-pinned to the ruling in the same PR.

## Alternatives

- A restore beside each writer: four more copies of the Off, unload and
  remove rules; D16-s3-02 is that state.
- Keeping the dict on the coordinator and rebinding a new dict per write: a
  spelling that moves the count and leaves the record without a restore
  owner; refused.
- Moving the record into `pump_arbiter.py`'s held record: the arbiter owns
  the pump's own entities, not the circulation pumps.

## Consequences

- Sensitivity S9, S11 and tradeoff T9: a stale plan hands the pump back
  sooner than a short forecast outage needs.
- `R11-SEAM-actuation-writes` reads the held record after this group defines
  what a release leaves in it: a prerequisite, not a file order.
- A new module is a new tracked file: it is classified in a measured closure
  in the same PR (`tests/closure.py`).

## Scenarios served

Actuator safety, first scenario (S9, T9) and third (S11).

## Move and fitness functions

`shared_inplace_writes` down one and `coord_footprint` down six statements
(`prototypes.py --only circ`).

**Banked only with the release cells.** The count falls because the same
post-await store into the record moves out of an async coordinator method
into the owner's own method. The metric's definition reads that as
encapsulation, and it would read a class that only holds the dict the same
way. What makes the move more than a relocation is decision 1: the owner is
registered with `off_restore.py` and restores the pumps on Off, stale plan,
unload and remove. The reviewer runs D16's release cells on the PR; an owner
that does not restore is `metric-gamed` (`fix-review.md` step 14) and the
fall is not banked. The term is banked only when the PR registers the real
restoring owner (decided 2026-11-18, orchestrator under mandate, pending owner confirmation); without it the
round reads `prototypes.py --case no-circ`, +21.1938 end to end, short of
the target (`PLAN.md`, "The cases").

Acceptance: the D16 enumerator's release cells
all restore; `coord_footprint` does not rise in this PR; the behaviour
inventory's entities and services unchanged; mutation kill rate on
`off_restore.py` and the new owner not below the fork's package rate.
