# ADR-005: a collaborator receives a value or a published view

Group: `R11-ARCH-cycle-surface`, a refactor group with no finding.

## Context

Two readers outside the coordinator reach its mode through `getattr(coord,
"mode", ...)`: `boost._mode_live` and `diagnostics._coordinator_snapshot`.
Counter C5 reads a passthrough property as its private, so these are the two
`coordinator_private_reach` sites. #1739 already decided that diagnostics
reads one view (`CoordinatorDiagnostics`) and collaborators receive what they
read; `BoostState.note_mode` is already told every mode change.

The third `shared_inplace_writes` site is in the same class:
`async_shutdown` ends with `self._background_tasks.clear()`
(`coordinator.py:6626` at the fork), after a capped 5 s wait on the tasks
still pending. Revision 1 of this plan made its removal part 3 of this ADR.
The plan review showed the part moves the count and not the property, and it
is withdrawn (below).

## Decision

1. `diagnostics.py` reads the mode from `CoordinatorDiagnostics`.
2. `boost.py` answers "is the global boost mode live" from the boost state it
   owns, or is handed the mode as an argument; it does not read the
   coordinator for it.
3. **Withdrawn: the shutdown's clear of the task set stays.** The metric
   prices an in-place write in an async coordinator method because the body
   may suspend with the object half-written. No `await` follows this clear,
   so it cannot. The same set is written in place by `_spawn`'s `.add`
   (`coordinator.py:3626`) and by each task's `.discard` done-callback
   (`:3627`), which the metric does not count only because they run in sync
   code. Deleting the one counted statement leaves every writer of the set
   where it was and removes the write that makes the set empty at shutdown:
   a task that outlives the 5 s wait would stay tracked. The count would fall
   by one (+5.4429) and the hazard would not change. `R11-ARCH-cycle-surface`
   names `shared_inplace_writes` at 0.0 and does not edit `async_shutdown`.

## Alternatives

- A public accessor under another name: C5's game, refused.
- Reading the mode from `coordinator.data`: the payload lags a mode change by
  one publish; the boost freeze must not.
- Leaving the mode read in `boost.py` and handing the coordinator a wrapper:
  C15 reads the wrapper as the coordinator.
- Dropping the clear (revision 1's part 3): above.
- Rebinding the slot to a new set at shutdown instead of clearing it: the
  same statement under a spelling the metric does not count. Refused.
- A task tracker object that owns the set, as ADR-004 gives the circulation
  pumps an owner: there the owner takes on a duty the code lacks (restore).
  Here there is no missing duty for an owner to take; it would be a wrapper
  that moves three writes. Not planned.

## Consequences

- `boost.mode_since` becomes the source for a decision; the boost session
  restore must set it when a session restores into boost mode. The fixer's
  failing test is a restart in boost mode.
- Tradeoff: one more field on the diagnostics view.
- `shared_inplace_writes` ends the round at 1, not 0, and the projected dS is
  5.4429 lower than revision 1 stated.

## Evidence and scenario

`prototypes.py --only reach` reads `coordinator_private_reach` 2 to 0,
admissible. `prototypes.py --only tasks` and `--case with-tasks` are kept as
the control for part 3: they read `shared_inplace_writes` down one for the
deleted statement, which is the reading this ADR declines to bank.

Scenario served: S25 (`SCENARIOS.md`, added at step 6): a collaborator is
handed the value. S36, the shutdown scenario written beside it, is no longer
served by a move; it is the behaviour this group must leave as it is, and
its text now states what the fork's code does (a capped wait, then an empty
set), where revision 1's said each task is cancelled.

## Fitness functions

`computed_attr_access` and `reflective_writes` flat; `tests/features.py`'s
shutdown checks (the saves-done and still-tracked lines) unchanged, and
`async_shutdown` untouched in the PR's diff; diagnostics output key set
unchanged; `coord_footprint` does not rise.
