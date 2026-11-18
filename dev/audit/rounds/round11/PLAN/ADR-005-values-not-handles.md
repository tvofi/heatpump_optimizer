# ADR-005: a collaborator receives a value or a published view; a tracked set has one remover

Group: `R11-ARCH-cycle-surface`, a refactor group with no finding.

## Context

Two readers outside the coordinator reach its mode through `getattr(coord,
"mode", ...)`: `boost._mode_live` and `diagnostics._coordinator_snapshot`.
Counter C5 reads a passthrough property as its private, so these are the two
`coordinator_private_reach` sites. #1739 already decided that diagnostics
reads one view (`CoordinatorDiagnostics`) and collaborators receive what they
read; `BoostState.note_mode` is already told every mode change.
`async_shutdown` clears `_background_tasks` after a capped wait, while each
task's done-callback already removes it: the third `shared_inplace_writes`
site, and a second remover that drops a still-running task from tracking.

## Decision

1. `diagnostics.py` reads the mode from `CoordinatorDiagnostics`.
2. `boost.py` answers "is the global boost mode live" from the boost state it
   owns, or is handed the mode as an argument; it does not read the
   coordinator for it.
3. The done-callback is the task set's one remover. `async_shutdown` stops
   clearing it only if the fixer shows the clear is redundant: no test and no
   later reader needs the set empty while a task still runs. If it is
   load-bearing, part 3 is dropped and recorded; rebinding the slot to a new
   set instead is refused.

## Alternatives

- A public accessor under another name: C5's game, refused.
- Reading the mode from `coordinator.data`: the payload lags a mode change by
  one publish; the boost freeze must not.
- Leaving the mode read in `boost.py` and handing the coordinator a wrapper:
  C15 reads the wrapper as the coordinator.

## Consequences

- `boost.mode_since` becomes the source for a decision; the boost session
  restore must set it when a session restores into boost mode. The fixer's
  failing test is a restart in boost mode.
- Tradeoff: one more field on the diagnostics view.

## Evidence and scenario

`prototypes.py --only reach` reads `coordinator_private_reach` 2 to 0;
`--only tasks` reads `shared_inplace_writes` down one; both admissible alone
and combined. Scenario served: maintainability, third scenario (S25, added in
`SCENARIOS.md`), and robustness, third scenario (S5: unload completes in
bounded time and orphans no store write).

## Fitness functions

`computed_attr_access` and `reflective_writes` flat; `tests/features.py`'s
shutdown checks (the saves-done and still-tracked lines) unchanged;
diagnostics output key set unchanged; `coord_footprint` does not rise.
