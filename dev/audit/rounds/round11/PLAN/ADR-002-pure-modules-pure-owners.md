# ADR-002: a pure module takes its clock and its constants from a pure owner

Group: `R11-SEAM-kernel` (D7-s1-06).

## Context

`metrics/layering.py` counts 13 modules reaching a layer above their own.
`m7_layer_edges.py` names the carrier of each: `accuracy.py` five, `inputs.py`
four, `tariff.py` two, `currency.py`, `issues.py` and `store.py` one each.
D7-s1-06 prototyped seven and left six as needing a design. Four of the six
ride on `inputs.py`, whose only Home Assistant import is the function-scope
one in `InputReader._utcnow`.

## Decision

1. D7-s1-06's seven: `utc_elapsed_seconds` is imported from `drift.py`, its
   owner; `HISTORY_LENGTH` moves to `const.py`; `currency.py` imports
   `HomeAssistant` for its annotation only.
2. The design for four of the six: `InputReader` takes its clock from its
   caller, and its fallback is the standard library's UTC now. The entry's
   reader (ADR-001's reader arm) is where the coordinator hands the clock in.
   `inputs.py` then imports nothing above the pure layer.
3. `setpoint_check.py` and `snapshots.py` stay. `setpoint_check.py` raises
   repair issues and reads entity state: it is glue ranked pure only because
   it imports no boundary itself. `snapshots.py` reads `store.admitted`;
   separating the store's schema from its persistence is a split of
   `store.py` this round does not need.

## Alternatives

- An unread `import homeassistant` in each violator: C19's game
  (`unused_boundary_imports`), refused.
- Making the imports lazy or moving them under `TYPE_CHECKING`'s `else`: C17
  counts them; refused.
- Keeping `dt_util.utcnow` as the fallback through an injected module-level
  hook: a second clock owner; refused.

## Consequences

- Tests that freeze time through Home Assistant's `dt_util` must hand the
  reader that clock; the reader arm makes the coordinator do so in production.
- `accuracy.py` stays glue; its five importers stop depending on it for a
  function and a constant it does not own.

## Scenarios served

Maintainability, first scenario (S12, T12): a pure module stays testable with
no Home Assistant stub.

## Move and fitness functions

`layer_violations` 13 to 2, read in one tree by `prototypes.py --case full`
(the kernel arm with the clock arm): D7 s1's `layer` and `curr` arms read 13 to 6;
`prototypes.py --only clock` reads 13 to 10 alone, removing `disinfection`,
`price_model` and `quiet_windows`; `sysid`'s two carriers are `accuracy` and
`quiet_windows`, both cleared by the combination. Acceptance:
`unused_boundary_imports` stays at its fork value; `import_cycle_modules`
flat; `m7_layer_edges.py` lists `setpoint_check` and `snapshots` only; the
suites that freeze time (`tests/features.py`, `tests/stress.py`) lose no check.
