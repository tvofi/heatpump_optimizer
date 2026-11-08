Base-copy bootstrap for R10-BODY-CONTRACT part 3 (handoff/r10-body-contract-p3). CI's governance / policy-docs restores the field-coverage grader from the base, and main's tools/policy/field_coverage.mjs has no DECLARED entry for `pinned tools/pr/figure_block.py`, so part 3 cannot pass until main carries one. This adds that single entry with `pending:` (precedent ee2974270). One line, one file.

## Head

7b4485c4403eb2409c1afaa5c8135142003e0f60

## Mutation proof

n/a: a DECLARED-table entry with `pending:`; the grader's own `node tools/policy/field_coverage.mjs --self-test` covers the pending path (a pending key the set yields is graded; an empty reason is DEAD).

## Null control

n/a: unmodified main has no entry, which is the failure part 3 hits; the full field_coverage run on this head reports refused=0.

## Figures

none

## Red checks

none

## Forward-carry

Part 3 drops `pending:` from this entry once this lands; the drop is part 3's own scope in dev/programme/rosters/wave-r10-groups.json (R10-BODY-CONTRACT). Carry: dismissed: part 3's own scope; no later stage's brief changes

## Friction

none
