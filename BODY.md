R11-PRE-FINDER-CONTRACT, p1 of 2: the wave-script grader alone. One file, `tools/policy/check-wave-script.mjs`; no policy, no artifact.

Why it is split. p2 (the finder's denominator in `COMMON.md`, `finding.schema.json` and `audit-find.js`; every dimension every round, so the driver's cadence table, `EVERY_DIM_ROUNDS` and `activeIn` are deleted) changes the shape this file grades. CI's `wave-script` job restores the base's copy of this file before it runs (decision 0013). Main's copy, placed over p2's tree and run, prints 163 passed, 1 failed: `the scoped round driver threw: CADENCE is not defined`; and its denominator block asserts D5 off at round 11, which the owner's ruling (tvofi 2026-11-13, "the scope of d5 and d6 to always cover that full scope") reverses. No data file sits between that literal and the tree, so registering in unpinned data cannot carry it; the grader lands first and p2 is a WIP handoff until it is on main (`fixer.md` step 5).

What the file now does. The existing switch, read from unpinned data (`finding.schema.json`'s coverage rows requiring `enumerator`), now also holds the cadence:

- switch off (main's tree): the cadence tests and the subset-box test run as before; the denominator block prints its one `skip` line.
- switch on (p2's tree): the driver must declare no `CADENCE`, `EVERY_DIM_ROUNDS` or `activeIn` and filter no seat by round, and rounds 11 and 13 (the rounds the retired cadence left D5, D6, D11 and D13 out of) are driven and must dispatch every `scopes.json` seat; the test asserting D5 off at round 11 is deleted.
- `CADENCE`, `EVERY_DIM_ROUNDS` and `activeIn` are read from the DISPATCH block with a `typeof` guard, so a tree without them is graded, not thrown on.

Keying the cadence on the same switch is the design choice: a tree with the denominator and a cadence is refused, and the dual edit carry 2 names (dropping `enumerator` from the schema and the driver's inlined copy together) now also fails over p2's tree, because the switch-off arm then needs the cadence p2 deleted.

## Head

9259c5e81bdd4061d661e8979f65ba54379868c5

## Mutation proof

Each mutant applied to p2's tree at `handoff-wip/r11-pre-finder-contract` (cb6600d2f1), graded by this head's copy, then restored:

- the dual edit (`"enumerator"` dropped from the coverage rows' `required` in `dev/audit/config/finding.schema.json`, then `python3 tools/audit/fold_ledger.py sync`): 164 passed, 2 failed: `round 9, and every round in EVERY_DIM_ROUNDS, runs every dimension` and `the scoped round driver threw`.
- a cadence reinstated as a filter (`const SEATS = DIMS.filter((d) => d !== "D5").flatMap(...)`): 182 passed, 28 failed, `the driver declares no cadence: ...` among them.
- a cadence declared but unused (`const CADENCE = { D5: 2 }` and an `activeIn` in the DISPATCH block): 247 passed, 1 failed: `the driver declares no cadence: no CADENCE, EVERY_DIM_ROUNDS or activeIn, and no seat filtered by round`.

Unpinned site, inherited: on main's tree `CADENCE`'s `D5: 2` set to `D5: 1` passes this copy (223 passed) and main's own, because main's cadence test reads every dimension off `CADENCE`. p2 deletes the table.

## Null control

- Main's copy and this copy over main's tree (26dbf7c43e) both print 223 passed, 0 failed; this copy's extra `skip` line is the denominator block's, unchanged.
- This copy over p2's tree prints 248 passed, 0 failed; main's copy over the same tree prints 163 passed, 1 failed.

## Figures

- `node tools/policy/check-wave-script.mjs` at origin/main 26dbf7c43e: 223 passed, 0 failed.
- The same command with this head's copy of the file over main's tree: 223 passed, 0 failed.
- The same command with this head's copy over p2's tree (cb6600d2f1): 248 passed, 0 failed; with main's copy over it: 163 passed, 1 failed.
- `python3 tools/pr/ci_predict.py` at this head: no closures, fast, governance or instrument red predicted against 26dbf7c43ec3.

<!-- figure-block: scope-line mb=26dbf7c43ec3742101398b098dbdcc61bbee8f19 head=9259c5e81bdd4061d661e8979f65ba54379868c5 -->
~~~text
MODE: SCOPED -- 1 script(s) run, 32 scoped out.
~~~
<!-- /figure-block -->

## Red checks

none: this head has no CI run of its own, and no check in the set `python3 tools/audit/seat/merge_train.py owed-reds` prints has gone red on a commit of this branch.

## Forward-carry

- p2, the group's artifact, waits at `refs/heads/handoff-wip/r11-pre-finder-contract` (cb6600d2f1) for this merge: `COMMON.md`'s denominator and the `check_scopes.py --seat` bound, the schema's coverage rows and D16/D17 patterns, the driver's `carryOf`, `seatCarry`, `denominatorGaps` and its cadence deleted, the playbook's round start (P795, intake carry 169), its planted control (a harness driving the driver's check and the evaluation's reader over one bare and one full row), the `COMMON.md` budget rows, and its own unconditional copy of this grader (carry 2). The group's carries 0, 1 and 2 bind p2, not this file. Carry: R11-PRE-FINDER-CONTRACT

- Carry 0 (D5 and D6 cover their full scope every round; the D5 and D6 finders start only after R10-D5-D6-FULL-SCOPE's pull request): that pull request is #3571, merged (5b8f05ba4e on main). The every-round half is p2's: its driver deletes the cadence that left D5 and D6 out of odd rounds, and this file's switch-on arm drives round 11 to dispatch every D5 and D6 seat. Carry: R11-PRE-FINDER-CONTRACT
- Carry 1 (the playbook's Round start step 3 names the paths that land instead of the group citation): built in p2's `dev/audit/README.md`, step 3 naming `COMMON.md`, the schema's `coverage` and `audit-find.js`'s `denominatorGaps`; the two dimension briefs are R11-PRE-NEW-DIMENSIONS', so step 3 names none. Carry: R11-PRE-FINDER-CONTRACT
- Carry 2 (the denominator block made unconditional in p2's own copy of this grader, the dual mutant killed): built in p2 (`DENOM` and its `skip` arm deleted; the dual edit fails 1 test there). This head also kills the dual edit over p2's tree (Mutation proof). Carry: R11-PRE-FINDER-CONTRACT

## Friction

none
