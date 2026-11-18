# ADR-003: an operation value is published whole or read at the decision, never copied in place

Groups: `R11-SEAM-cycle-reporting` (D7-s2-03), `R11-SEAM-learners` (the
identification switch, beside D7-s2-02).

## Context

`CoordinatorContext` is a frozen dataclass whose docstring promises that a
change is published by rebinding `_ctx`. Two writers edit the shared
`OptimizationConfig` in place (`coordinator.py:4258`, `:10941`), so every
context published since setup sees the edit (D7-s2-03); the second is the
score's one `hub_solve_writes` site. `sysid.arm_from_config` copies the
entry's switch onto the collaborator's config on every arm: one of the three
`shared_inplace_writes` sites, and a second copy of a setting the entry owns.

## Decision

1. Both `_opt_config` writers publish a replaced context
   (`replace(ctx, _opt_config=replace(...))`), as D7-s2-03's perturbation does.
2. `SystemIdentification.arm` receives the switch as an argument from
   `arm_from_config`; nothing stores it on the collaborator after
   construction.

## Alternatives

- Moving the comfort-weight write into a pre-solve step or an event callback:
  counters C13 and C16 read it as the same hub write; refused.
- Rebinding `ident.config` to a replaced config each cycle: still a write into
  a long-lived shared object, and still two copies of the switch.
- A setter method on the collaborator: the same store behind a call (C15).

## Consequences

- A holder of an old context keeps the target temperature and comfort weight
  it was handed; code that relied on seeing a later edit through an old
  context must re-read `_ctx` (D7 s2's `enum_m4.py` lists eight holders, all
  readers today).
- One more dataclass copy per comfort-weight change; none per cycle.

## Scenarios served

Maintainability, first scenario (S12); physical sanity, third scenario (S8:
which interval a learner runs on is decided from the entry at the decision).

## Move and fitness functions

`hub_solve_writes` 1 to 0 (`prototypes.py --only hub`); `shared_inplace_writes`
down one (`--only sysid`). Acceptance: `m4_order_context.py` reads no torn
field; `reflective_writes` and `computed_attr_access` flat (C2, C2b);
`coordinator_multiassigned_attrs` not above its budget; the identification
arming checks of `tests/features.py` unchanged.

**Stale-holder check** (decided 2026-11-18, orchestrator under mandate, pending owner confirmation). `early_cutoff.arm` stores the
handed `OptimizationConfig` in `held.wiring = CutoffInputs(inputs, boosts,
opt_config)` (`early_cutoff.py:168`), a holder that outlives the call. The
fixer's acceptance includes a test that changes the comfort weight or the
target temperature after arming and reads, before the next cycle re-arms,
that the held cutoff decides on the replaced context's values, not the ones
it was handed. The other seven holders `enum_m4.py` lists are readers today
and are re-read by the reviewer.
