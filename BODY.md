R10-DIMENSIONS-FULL-COVERAGE, p1 of 2: the wave-script grader alone. One file, `tools/policy/check-wave-script.mjs`; no policy, no artifact.

Why it is split. The group's change (p2: the finder's denominator, D16 and D17, D11 and D13 every round) alters the shape `check-wave-script.mjs` grades: the schema's dimension regex, the finder report's `coverage` rows, the cadence table. CI's `wave-script` job restores the base's copy of this file before it runs (decision 0013), and `tools/pr/ci_predict.py` printed `GRADER check-wave-script.mjs REFUSED by the base's copy … BOOTSTRAP` for the whole change. The base's copy, run over p2's tree, fails 23 tests (203 passed, 23 failed: origin/main's copy of the file placed over 6f760d9fff's tree, then `node tools/policy/check-wave-script.mjs`). So the grader lands first, and p2 is a WIP handoff until it is on main (`fixer.md` step 5).

What the file now does, on any tree:

- The seat id it requires the schema to refuse is `D18-s1`, not `D16-s1`.
- The cadence test asserts D5 off on an odd round and on at a multiple of six, D0 on every round, and D11 and D13 as their `CADENCE` entry says.
- The finder stubs return a closed denominator row per step beside the depth word, so the driver on main and the driver p2 brings both read them.
- A switch read from unpinned data, `finding.schema.json`: where a coverage row requires `enumerator`, the driver must export `carryOf`, `seatCarry` and `denominatorGaps`, and the block "the denominator" runs: 26 more `ok` lines than at this head's own tree (253 at 6f760d9fff against 227 at this head, `node tools/policy/check-wave-script.mjs | grep -c '^  ok '` at each; the `diff` of the two sorted `ok` lists shows 27 added and 1 re-titled, the cadence test). Where it does not, the block prints one `skip` line, counted as nothing. Keying the switch on the schema and not on the driver's text is the design choice: a driver that drops the functions while the schema still demands a denominator is refused, so the skip cannot become a way out.

The alternative that lost: one pull request with the registration moved to unpinned data (`fixer.md`'s first remedy). The base's copy asserts a literal, `!scopeRe.test('D16-s1')`, against the schema's own pattern; no data file sits between them, so nothing could be moved.

## Head

64d7082b849351fa9923f7c655a36de72520374f

## Mutation proof

At this head (main's driver):

- `.claude/workflows/audit-find.js`, `CADENCE`'s `D5: 2` set to `D5: 1`: `node tools/policy/check-wave-script.mjs` fails `...and the cadence is otherwise read from the round number (D5 off at 11, on at 12; D0 on at 11; D11 and D13 follow their CADENCE entry)`.
- `D11: 3` set to `D11: 2`: no test fails. The base's copy does not catch it either (it asserts D11 off at round 11 and on at round 12, which cadence 2 also gives), so this is an unpinned site this change inherits and does not add; p2 sets D11 to 1, which the block's round-11 test pins.

Over p2's tree, at `handoff-wip/r10-dimensions-full-coverage` (6f760d9fff), where the denominator block runs, each driver mutant applied to a copy:

- `denominatorGaps` returning `[]` first: ten `denominatorGaps refuses …` tests and `a seat whose report carries no denominator is dispatched twice, ends missing, and intake does not run` fail.
- `carryOf` returning `[]` first: the `carryOf` and `seatCarry` tests fail.
- `denominatorGaps` renamed at its definition and uses: `a schema that requires a denominator has a driver that enforces one (carryOf, seatCarry, denominatorGaps in the DISPATCH block)` fails.
- `overdue:` forced false: `seatCarry marks the age-2 item overdue at bound 3, not at bound 4, not with no rotate` fails.
- the carried item dropped from the ledger's `not_reached`: `a carried item answered not_reached stays in the ledger under its original words` fails.

## Null control

- Main's own copy on main's tree and this copy on main's tree print the same `ok` names but one, re-titled: the cadence test. This copy adds one test and one `skip` line.
- This copy over p2's tree prints 0 failed with the denominator block run; main's copy over p2's tree prints 203 passed, 23 failed (the same with `tools/audit/*.sh` restored from main).

## Figures

- `node tools/policy/check-wave-script.mjs` at this head: 227 passed, 0 failed, one `skip` line. Main's copy at the merge base `e23124ff6e`: 226 passed.
- `node tools/policy/check-wave-script.mjs` at 6f760d9fff (p2's tree, the same file): 253 passed, 0 failed.
- `git show origin/main:tools/policy/check-wave-script.mjs` run over 5aa113f091's tree with its `tools/audit/*.sh` restored from main, as the job does: 203 passed, 23 failed (the same command, `node tools/policy/check-wave-script.mjs`, with main's copy of the file in place; run at 6f760d9fff and 5aa113f091, with and without `tools/audit/*.sh` restored from `origin/main`: identical).

## Red checks

Read from the Actions jobs of every red main push run in this head's ancestry (CI code runs 43440835978 at ad95665ea3 #3520, 43448248435 at 154dbb4c61 #3555, 43473184186 at 90c6bc3b07 #3511, 43477646097 at 3fd9fab077 #3546, 43477771571 at e23124ff6e #3559, and the cancelled run 43477593296 at d7cd2722c5 #3558); this branch has no CI run of its own at 64d7082b.

- governance / instrument-self-tests: inherited. It is the only job that failed in those runs, at the step "Refuse a self-test read set the committed table misses", on each of the main commits above, none of them this branch's. Repaired on main by #3557 (R10-HOTFIX-SELFTEST-SCOPE-TABLE, merge 50373173d4), which this head predates; this branch touches neither the self-test nor its table.
- tests / closures, tests / fast (3.14), tests / mutation: not red on any ancestry commit. Each job is `success` in the runs above, so there is nothing to answer as introduced or inherited; the lint names them because the head has no run of its own.
- tests / mutation-autofix, tests / nightly-ha (2025.2.0), tests / nightly-ha (stable), tests / nightly-status: not red on any ancestry commit. These jobs are `skipped` on the push runs above, and the Nightly workflow on those commits concluded `success`. A skipped job is not a red.

## Forward-carry

The roster group's two dispatched carries bind the artifact, which is p2, not this file. Their state at p2's WIP head 6f760d9fff:

- Carry 0 (each hotfix and outside group records what caused the defect and what found it; escapes split by owning dimension, built once with the convergence records): partly built in p2. Its convergence instrument reads a defect group's `cause` (dimension, pull request, round, origin) and prints escapes per dimension; `root-cause.md` section 6 and `orchestrator.md` section 13 say who writes it. Not built: the field for what found the defect (a finder dimension, a reviewer, CI on main, the owner, an outside user), and `tools/audit/seat/scorecard.py`'s `E` line reading that one field instead of counting groups. Owed in p2 before its handoff; item 0 of the resume note on `handoff-body/`. Carry: R10-DIMENSIONS-FULL-COVERAGE
- Carry 1 (the playbook stays usable: a pointer at the place in the round's order where the step runs, and a dry read in the body): partly built in p2. `dev/audit/README.md` phase 13 names the convergence instrument and the four counts. Not built: the pointer at the finder phase to `COMMON.md`'s denominator and its enumerator, and the dry read. R10-ROUND-PLAYBOOK-FINAL's roster stage is `carries-open`, which `carry_audit.py` refuses as a destination, so the pointer stays this group's. Owed in p2; item 0 of the resume note. Carry: R10-DIMENSIONS-FULL-COVERAGE
- Carry 2 (from r11-pre-objective-function, body item 27f9ce96: the same, for found-by, cause and the per-step denominator; an off-cadence dimension reads 0; lands in `dev/programme/rosters/wave-r10-groups.json`): not built in this file, which changes no roster and no artifact; it binds p2. Carry: R10-DIMENSIONS-FULL-COVERAGE (items 27f9ce96)

The merge verdict's other findings (the merge reviewer's verdict on the probe branch `probe/revt-r10-dimensions-full-coverage-a70272e2`), each with its destination:

- The switch is a way out in a direction this body does not test: on p2's tree, dropping `"enumerator"` from the coverage rows' `required` in `dev/audit/config/finding.schema.json` and in the driver's inlined copy together prints the `skip` line, 227 passed, 0 failed, rc 0; the schema edit alone is caught, and a driver that drops the functions is caught. "so the skip cannot become a way out" above holds for those two and not for the dual edit. No tree-read switch closes it; the control is that p2, graded by this copy, makes the block unconditional in its own copy of the grader (`DENOM` asserted true, the `skip` arm deleted, the dual mutant re-run killed). A precondition for p2's handoff, not for this merge. Carry: R10-DIMENSIONS-FULL-COVERAGE
- Three pins are loosened on main's tree between this merge and p2's, beyond the `D11: 3` to `2` disclosed above: `D11: 3` to `1` survives this copy (the base's kills it); `D13: 3` to `2` survives (unpinned at the base too); admitting `D16-s1` in the schema and its inlined copy together survives this copy where the base's fails two tests. Each is what p2 changes and each is pinned again on p2's tree (`D11: 1` to `3`, `D13: 1` to `3` and refusing `D17`: all killed there). Carry: dismissed: the bootstrap's cost, bounded by p2's merge and re-pinned on p2's tree as measured

## Friction

- fixer: cost: the BOOTSTRAP arm of `ci_predict.py` prints the first failing line of the base's grader only; the count that sizes the split, 23, needed the base's copy run by hand over the head's tree. Carry: dismissed: one command, and the arm's text already names the remedy
