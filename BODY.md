R10-DIMENSIONS-FULL-COVERAGE, p1 of 2: the wave-script grader alone. One file, `tools/policy/check-wave-script.mjs`; no policy, no artifact.

Why it is split. The group's change (p2: the finder's denominator, D16 and D17, D11 and D13 every round) alters the shape `check-wave-script.mjs` grades: the schema's dimension regex, the finder report's `coverage` rows, the cadence table. CI's `wave-script` job restores the base's copy of this file before it runs (decision 0013), and `tools/pr/ci_predict.py` printed `GRADER check-wave-script.mjs REFUSED by the base's copy … BOOTSTRAP` for the whole change. The base's copy, run over p2's tree, fails 25 tests. So the grader lands first, and p2 is a WIP handoff until it is on main (`fixer.md` step 5).

What the file now does, on any tree:

- The seat id it requires the schema to refuse is `D18-s1`, not `D16-s1`.
- The cadence test asserts D5 off on an odd round and on at a multiple of six, D0 on every round, and D11 and D13 as their `CADENCE` entry says.
- The finder stubs return a closed denominator row per step beside the depth word, so the driver on main and the driver p2 brings both read them.
- A switch read from unpinned data, `finding.schema.json`: where a coverage row requires `enumerator`, the driver must export `carryOf`, `seatCarry` and `denominatorGaps`, and the 22 tests of the block "the denominator" run. Where it does not, the block prints one `skip` line, counted as nothing. Keying the switch on the schema and not on the driver's text is the design choice: a driver that drops the functions while the schema still demands a denominator is refused, so the skip cannot become a way out.

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
- This copy over p2's tree prints 0 failed with the denominator block run; main's copy over p2's tree prints 25 failed.

## Figures

- `node tools/policy/check-wave-script.mjs` at this head: 227 passed, 0 failed, one `skip` line. Main's copy at the merge base `e23124ff6e`: 226 passed.
- `node tools/policy/check-wave-script.mjs` at 6f760d9fff (p2's tree, the same file): 253 passed, 0 failed.
- `git show origin/main:tools/policy/check-wave-script.mjs` run over 5aa113f091's tree with its `tools/audit/*.sh` restored from main, as the job does: 25 failed, measured at 270a772353 before the isolation change was withdrawn.

## Red checks

none

## Forward-carry

none

## Friction

- fixer: cost: the BOOTSTRAP arm of `ci_predict.py` prints the first failing line of the base's grader only; the count that sizes the split, 25, needed the base's copy run by hand over the head's tree. Carry: dismissed: one command, and the arm's text already names the remedy
