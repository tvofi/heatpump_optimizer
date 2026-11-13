Fix review: merge 64d7082b849351fa9923f7c655a36de72520374f

bus-nonce: a70272e24536b8a97cc495270c7da3e5

Round 1, at the handoff. Measured head 64d7082b849351fa9923f7c655a36de72520374f (one commit on origin/main e23124ff6e, one file, `tools/policy/check-wave-script.mjs`).

## Findings

- The switch is a way out in the direction the body does not test. On p2's tree (6f760d9fff), dropping `"enumerator"` from the coverage rows' `required` in `dev/audit/config/finding.schema.json` and in the driver's inlined copy (one token each) prints the `skip` line, 227 passed, 0 failed, rc 0; with `denominatorGaps` then returning `[]` first it still prints 227 passed, 0 failed (ev/mut-p-dual-drop-enumerator.txt, ev/mut-p-dual-drop-enumerator-and-gaps-empty.txt). The schema edit alone is caught, by `the finder's return schema is finding.schema.json itself` only (ev/mut-p-schema-drop-enumerator.txt). The body's "so the skip cannot become a way out" holds for a driver that drops the functions (ev/mut-p-gaps-renamed.txt, killed) and not for a pull request that moves the schema and its inlined copy together. No tree-read switch closes this; the control is that p2, graded by this copy, makes the block unconditional in its own copy of the grader: `DENOM` asserted true, the `skip` arm deleted, and this dual mutant re-run killed. Precondition for p2's handoff, not for this merge: before p2 the block's tests do not exist at all. Carry: R10-DIMENSIONS-FULL-COVERAGE
- Body figure not re-derived: "the 22 tests of the block". The block prints 26 `ok` lines at 6f760d9fff (253 - 227; listed by `diff` of ev/head-on-head.txt and ev/head-on-p2.txt). The orchestrator corrects the body before it opens the pull request; the head does not move. Carry: R10-DIMENSIONS-FULL-COVERAGE
- Body figure not re-derived: "main's copy over p2's tree prints 25 failed" and the `## Figures` line for 5aa113f091. origin/main's copy (e23124ff6e) prints 203 passed, 23 failed over 6f760d9fff, the same with `tools/audit/*.sh` restored from main, and the same over 5aa113f091 with them restored (ev/base-on-p2.txt, ev/base-on-p2-sh-restored.txt, ev/base-on-5aa113f091.txt). The claim it sizes (the base's copy refuses p2's tree, this copy passes it) holds. Corrected with the line above. Carry: R10-DIMENSIONS-FULL-COVERAGE
- Three pins are loosened on main's tree between this merge and p2's, beyond the one the body discloses (`D11: 3` to `2`, which the base does not catch either): `D11: 3` to `1` survives this copy and the base's kills it by construction; `D13: 3` to `2` survives (unpinned at the base too); admitting `D16-s1` in the schema and its inlined copy together survives this copy where the base's fails two tests (ev/mut-head-dual-admit-D16.txt, ev/mut-base-dual-admit-D16.txt). Each is what p2 changes, and each is pinned again on p2's tree: `D11: 1` to `3`, `D13: 1` to `3` and refusing `D17` are all killed there (ev/mutants.txt). Carry: dismissed: the bootstrap's cost, bounded by p2's merge and re-pinned on p2's tree as measured

## Evidence

No review packet and no pull request exist at this handoff, and no CI to wait on or cite: no check run was read, no `## Red checks` answer is owed, and `pr-contract` has not read the body. All figures below are this seat's own runs, in ev/.

RESULT head-on-head (64d7082b849351fa9923f7c655a36de72520374f): 227 passed, 0 failed, one `skip` line, rc 0 (body: 227, verified).
RESULT base-on-base (e23124ff6e): 226 passed, 0 failed (body: 226, verified).
RESULT ok-name diff base to head on main's tree: one added (`a schema that requires a denominator has a driver that enforces one`), one re-titled (the cadence test); nothing dropped (body's null control, verified).
RESULT head-on-p2 (6f760d9fff, whose copy of the file is byte-identical to this head's): 253 passed, 0 failed, no `skip` line (body: 253, verified).
RESULT base-on-p2: 203 passed, 23 failed (body: 25, not verified; see Findings).

Mutation proof, re-run (ev/mutants.txt, one file per mutant):

- head tree, `D5: 2` to `D5: 1`: 1 failed, the cadence test the body names. Killed.
- head tree, `D11: 3` to `2`: survives, and survives the base's copy on the base's tree, as the body says.
- p2 tree, `denominatorGaps` returning `[]`: 11 failed, the ten `denominatorGaps refuses` tests and the dispatched-twice test. Killed, as stated.
- p2 tree, `carryOf` returning `[]`: the two `carryOf` tests, `seatCarry numbers C1..` and a throw in the block. Killed.
- p2 tree, `denominatorGaps` renamed throughout: the driver-enforces test fails and the block throws. Killed.
- p2 tree, `overdue:` forced false: the `seatCarry marks the age-2 item overdue` test. Killed.
- p2 tree, the carried item dropped from the ledger's `not_reached`: the `stays in the ledger under its original words` test. Killed.

Not vacuous: every mutant the body names as killed is killed by the named test.

Steps with nothing to measure: the diff is one instrument file, so no claim file, golden, budget, closure, `VERSION`, manifest or notes heading moves (`git diff origin/main...64d7082b849351fa9923f7c655a36de72520374f --stat`: one file). The change has no finder's harness and no issue seam list; the grader is its own instrument and the mutants above are this seat's. The split is `fixer.md`'s BOOTSTRAP remedy; the body's reason the unpinned-data remedy does not apply (the base asserts the literal `!scopeRe.test('D16-s1')`) is confirmed by ev/mut-base-dual-admit-D16.txt.

Merge with main: `git merge-tree --write-tree origin/main 64d7082b849351fa9923f7c655a36de72520374f` exits 0 (tree 6d7cf3933f); the head is not behind main.

Forward-carry: both body carries name the fixer's own group as p2, the split part; the group is live in `dev/programme/rosters/wave-r10-groups.json` at `handoff/audit-r10-roster` b4ba0493a9. Their content binds p2's artifact and was not reviewed here.

Head re-read before the push: `refs/heads/handoff/r10-dimensions-full-coverage` is 64d7082b849351fa9923f7c655a36de72520374f.
