R10-MACHINERY-RATCHETS part 1b (unblocking; the orchestrator opens this under group R10-MACHINERY-RATCHETS, and part 2 merges after it). CI grades part 2's `policy-docs` with the base's `field_coverage.mjs`. Main's copy refuses part 2: `pinned tools/audit/machinery_ratchet.py` is unregistered. Adding the plain DECLARED entry to main refuses main instead: the entry reads as DEAD, because nothing pins that file until part 2's governance.yml does. Part 1's body recorded that trade-off.

This part lands the registration in a form both trees accept. A DECLARED entry may now carry `pending: <reason>`, which mirrors the existing IGNORE `PENDING` in `jsonRun`. When the derived set does not yield the entry, `registryRun` prints it as `pending` instead of DEAD. When the set yields it, the entry is graded like any other. An empty reason grants no tolerance. Part 2 drops the key, so the entry is strict (DEAD if absent) from then on. The machinery_ratchet entry rides here with `pending` set.

## Head

5ac16c1052365d609f26fff7e54e50052ed3deec

## Mutation proof

Mutant: the pending predicate in `registryRun` was replaced with `false`, a one-line `sed`, and the file was restored by copy afterwards.
- `node tools/policy/field_coverage.mjs --self-test`: `FAIL a pending DECLARED key the set does not yield is printed, not DEAD`, `FIELD COVERAGE SELF-TEST: 1 FAILED`.
- `node tools/policy/field_coverage.mjs --only registry`: `DEAD registry: DECLARED \`pinned tools/audit/machinery_ratchet.py\` is no longer in the derived set`, rc=1.
Restored: the self-test is ok and the registry arm is ok.

## Null control

- origin/main's own `field_coverage.mjs` on part 2's tree (handoff-wip/r10-machinery-ratchets-p2 3ffd1c43): `REFUSED registry: \`pinned tools/audit/machinery_ratchet.py\` is unregistered`, refused=1. This is the red the part answers.
- This head's `field_coverage.mjs` copied onto that same tree: the machinery_ratchet entry is graded `none`, dead=0, refused=0, `FIELD COVERAGE ok`.
- This head, on its own tree: the entry prints `pending`, dead=0, refused=0, `FIELD COVERAGE ok`.
- Non-widening: the self-test's existing pin `a DECLARED key the set does not yield is DEAD` still holds beside a pending key, and so does the new empty-reason pin.

## Figures

- `node tools/policy/field_coverage.mjs --self-test`: FIELD COVERAGE SELF-TEST ok (three new pins).
- `node tools/policy/field_coverage.mjs --only registry`: FIELD COVERAGE ok, dead=0 refused=0.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir $D`: MODE: SCOPED, runs tests/entities.py.
- `PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh <body>`: PRE-PR rc=0 at this head (re-run after merging origin/main at 616868bd).

## Red checks

none

## Forward-carry

none

## Friction

none
