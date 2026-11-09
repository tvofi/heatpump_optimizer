Fix review: blocked b74fd1ac9b676610966d80aeba0e83a8be0638fe body-stale: PR body figures describe an already-merged state, not this head

bus-nonce: f6e9c4da8562a5d18213daeeb1fe7bdd

## Block
Round 1 of review. The body's figures do not hold at head b74fd1ac9b676610966d80aeba0e83a8be0638fe (fix-review steps 7, 8):
- Body: "1 file ... roster 279 in / 25 out"; at this head `git diff --numstat origin/main...b74fd1ac9b676610966d80aeba0e83a8be0638fe` shows 14 files: the roster 3185/387 plus 12 `triage/s6-batch129..140.md` and the delivery row.
- Body: groups 337 on main to 342 (5 added, 13 changed). Measured: origin/main (2f6d699e50) already has 342 groups; head has 398 (56 added, 0 removed, 54 changed).
- Body's tip `c516cf0f` is an ancestor of origin/main: that content already landed. The head carries later handoff ops and triage files the body never describes (the triage files are not mentioned at all; "No production or test code" stands, but "roster state only: 1 file" is false).
- Body's "Red checks: none yet" was written before any check ran; stale.
Fix: regenerate the body's figures at this head (numstat, group counts, added/changed, base) and re-dispatch.

## Evidence
- brief_lint at head: TOTAL: 0 error(s) across 1 file(s).
- merge-tree origin/main head: clean (tree 62493ffdd439548914744ca44663a10d59a324d5).
- classify at review time: WAIT, gate red: none. CI not waited to completion; block is independent of CI.
- Mutation proof n/a (no code). VERSION/manifest untouched (diff lists none).
- Review packet render did not finish within the session; not used.
- `ev/HEAD.txt` holds the head reviewed.
