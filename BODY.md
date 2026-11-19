Adds `dev/audit/rca/R11-RCA-CLASS-OPEN.md`, a root-cause analysis of the fix-review blocks classed `class-open`. The beat's bottleneck line `block-class class-open 33% (4/12 blocks) vs 30%` (`tools/audit/seat/bottleneck_check.py`, threshold 0.30 at 5 or more blocks) triggered it. The file is the only change: no tracked tooling or policy is edited.

What the file records:

- Four instances in the 24 h window: #3729 (two rounds), #3734, #3728.
- Measured frequency from 2026-11-15 to 2026-11-19 10:00Z: 196 fix-review heads with a verdict, 131 merge and 65 blocked over 116 PRs; 15 distinct blocks are `class-open` (23% of blocks, 7.7% of reviewed heads). Median block-to-next-verdict is 6.2 h for the 21 class-open blocks since 2026-11-10, against 4.5 h for the other 64.
- Cause: the class-closure step in `fixer.md` step 8 checks that an enumeration rule was run, not that the rule's universe contains the class. Process state (c), with two instances differing ((b) for #3625 round 2, (d) for #3734).
- Cost test for three countermeasures. A (narrow step 8 with recall at the merge base, read every cited finding file) passes by a margin smaller than the estimate's error. B (generic probe instrument) and C (sibling-shape probe per guard) are refused with figures.
- A is stated as a proposal for round-end triage with a shadow measurement; it is not applied here.

## Head

42bb6930ad6593e131b9040de7806437ec723d5b

## Mutation proof

n/a: documentation-only change, one markdown file, no code or check to break.

## Null control

n/a: the unmodified tree has no `dev/audit/rca/R11-RCA-CLASS-OPEN.md`; nothing else changes.

## Figures

none

## Red checks

Inherited from main, not caused by this change (the diff is one markdown file):

- `tests/features.py` lift-peak BLAS failure, inherited; hotfix #3815 is in flight.
- code-scanning alerts 57-67, inherited from main.

## Forward-carry

none

## Friction

none
