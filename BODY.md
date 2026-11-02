Carry 1 (stranded carry 35): built. Closes #3100. Carry 35 (bootstrap deadlock of a shared grammar under a pinned grader) is built: `tools/policy/agreement.mjs` gains a `bootstrap:<reason>` SHARED_GRAMMARS disposition. An entry may span one file when its reason carries a `#N` or ISO date; it is refused once a second file reads the grammar (stale), and DEAD if no file reads it. The entry can therefore land before its reader (no DEAD), and the reader's PR is graded by a base that already holds the entry (no UNREGISTERED). Chosen over letting the base-copy lane accept an entry whose reader is in the same diff: that would loosen the pinned grader for every PR, whereas this changes nothing for steady-state entries and a bootstrap entry expires by itself.

## Head

85b9b7c76b553f4926e22b4b3a1d98a854a7690a (merge base c7aa121650058ec9f1540b5bf60ffd69eea75298 = origin/main at the time; main unmoved since the prepr run, so no second run).

## Mutation proof

Mutant: the DEAD predicate for non-bootstrap entries replaced by `else if (false)` (every one-file entry passes). Self-test: FAIL 'an entry that no longer spans two files is DEAD' and FAIL 'an undeclared one-file entry still reads DEAD' (218 of 220). Restored: 220 of 220. Failing first: the new probes spliced into origin/main's agreement.mjs fail 3 (bootstrap accepted, empty reason refused, reason without #N/date refused).

## Null control

Undeclared one-file entry still reads DEAD; `bootstrap:` with no reason and `bootstrap:soon` are refused; a two-file entry with an identical: disposition is unaffected; a bootstrap entry whose reader landed is refused as stale. All are self-test probes.

## Figures

- node tools/policy/agreement.mjs --self-test: 220 of 220 probes held
- node tools/policy/agreement.mjs --only discovery: AGREEMENT ok, dead=0 unregistered=0
- python3 tests/structure.py: STRUCTURE RATCHET PASSED
- bash tools/pr/prepr.sh: rc=0 at the head (scoped gate: MODE: SCOPED, runs tests/entities.py, passed)

## Red checks

none

## Forward-carry

none

## Friction

none
