`Payments tried:` as a bare heading over a list (#2633): the gate needs text
after the colon on the same line, so it refuses this body; so must the lint.

## Head

`0000000000000000000000000000000000000000`

## Mutation proof

Reverting the guard turns `tests/structure.py` red on `max_cc`.

## Null control

The unmodified tree passes.

## Raise justification

- Payments tried:
  - moved the helper into its caller; arch_score read it worse.
- Architecture score: dS -0.0310 WORSENS

## Figures

`37 passed`: `node tools/policy/check-wave-script.mjs`

## Red checks

none

## Forward-carry

`dev/governance/dimensions/D7.md`

## Friction

`budgets`: `cost`: a one-sided cap is measured at head only, so two branches can
each be honest and their merge red.
gate-scoping: unenforced: a directory prefix reads as a safe over-approximation.
