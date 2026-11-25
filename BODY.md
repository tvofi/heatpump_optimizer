Refs #3885

This PR leaves #3885 open. It removes the main source of the duplicate verified dispatches the light-grading PR measured. The other sources and the remaining duplicates are carried below.

**Why a head was graded twice.** This is the brief's first question: which dispatcher fired at heads a pull_request run had already graded? On 2026-11-22, 23 and 25 the answer is `tools/ci/sweep.py`'s STALE-PIN arm for 20 of the 27 duplicates `ci3885_light.py dup` counts. The other 7, all on 11-22, print no dispatch line in any sweep log read, so their dispatcher is not identified here (`## Forward-carry`).

STALE-PIN works like this. A pull_request run's gate restores `tools/ci/*.py` from the event's `base.sha`. When main has since changed those programs, the sweep does not re-run that gate. It dispatches one complete `ci.yml` run at the head to re-judge it with fresh programs (#3261, #3400, #3544).

The re-judge is needed when the red is the gate's own verdict (a deferral, a busy() read). It is not needed when a code unit has already failed at the head. The code under test is the PR head's own, which no pin restores, so the fresh run grades the same code again. Of the 16 STALE-PIN dispatches of 11-22 and 11-23, none ended green: 8 failed and 8 were cancelled by a later push. The 4 of 11-25 were still running when this was measured.

**The change.** `Sweep.fresh` now calls a new `Sweep.code_red(runs)` before it dispatches:
- `code_red(runs)` lists the code units (`gate.REQUIRED["no-pr"]`, the gate's own list, imported rather than restated) whose newest-started completed job at the head failed, across every run's latest attempt.
- If that list is non-empty, the sweep dispatches nothing and re-runs nothing, prints `STALE-PIN <pin>: run <id> left: <units> failed at this head ...`, and leaves the head to its next push.
- A body unit's red (`pr-contract`, `budget-raise-gate`, `arch-score`) still dispatches, because the fresh run re-reads the PR.
- So does a unit red in one run and green in a later one, and a cancelled unit.
- Every other STALE-PIN path is unchanged: the fresh judge already listed, one dispatch per sweep, the covered deferral, and the #3400 re-run from inside the fresh judge.

`dev/audit/harnesses/ci3885_light.py` gains a `stalepin DAY` arm, the attribution and replay instrument behind the figures:
- It takes `dup`'s duplicates and attributes each to STALE-PIN when a sweep job log prints the dispatch on its branch.
- It then replays the tree's own `Sweep.code_red` over the head's runs as they stood when the dispatch was created.

No CI trust-model change: no run accepts another run's job conclusions. The verdict-reuse lever the carry names stays unbuilt and still needs a design under decision 0014 (`## Forward-carry`). `tools/ci/prelude.py` and `.github/workflows/tests.yml` are not touched. This branch is cut from origin/main `6a58ba5cb3`, which carries #3888.

## Head

`64220be0555fd8569c36702861eb65ba6c725c04`, four commits on origin/main `6a58ba5cb30bf231dd7c6f60c42dc0d7583cb699`:
- `fd650c767d`: `Sweep.code_red` and its use in `Sweep.fresh` (`tools/ci/sweep.py`), with four self-test cases written first (`tools/ci/sweep_selftest.py`).
- `f4f4113035`: sweep.py's module doc states the exception.
- `87d2068c44` and `64220be055`: the harness arm.

`git merge-tree --write-tree origin/main HEAD` against `bb6377b4da` reports no conflict, so main is not merged (fixer.md step 6).

## Mutation proof

The failing test came first. The new case `stale pin, #3885: a code unit red at the head is no stale verdict` failed on the unmodified sweep.py (`sweep self-test: 112 checks, 1 failed`), and the three null cases passed there.

Each mutant was applied to `tools/ci/sweep.py` at `fd650c767d` and run with `python3 tools/ci/sweep.py --self-test`:
- M1, `if red:` -> `if False:`: rc 1, `FAIL stale pin, #3885: a code unit red at the head is no stale verdict ...`
- M2, `c == "failure"` -> `c != "success"`: rc 1, `FAIL stale pin, #3885 null: a code unit cancelled, not failed still takes one dispatch`
- M3, newest-started ordering dropped (the first listed job wins): rc 1, `FAIL stale pin, #3885 null: a code unit red then green in a later run at the head still takes one dispatch`
- M4, `REQUIRED["no-pr"]` -> `REQUIRED["pr"]` (body units counted): rc 1, `FAIL stale pin, #3885 null: a body unit's red (the fresh run re-reads the body) still takes one dispatch`
- M5, the left branch's `return True` -> `return False` (falls through to a re-run in place): rc 1, `FAIL stale pin, #3885: a code unit red at the head ...`
- NULL, a comment added on the guard line: rc 0, `sweep self-test: 112 checks, 0 failed`

## Null control

- The harness arm, run unchanged from a detached worktree at origin/main `6a58ba5cb3` (main's sweep.py, which has no `code_red`), leaves 0 of the 20 STALE-PIN duplicates on each day. So the `left` count comes from the fix, not from the arm.
- Within the fixed tree, the predicate does not read every head as red: 6 of the 20 heads had no code unit red when the dispatch fired, and they still dispatch.
- In the self-test, the three nulls (a body unit's red, a unit red then green, a cancelled unit) each take exactly one dispatch.

## Figures

- `python3 dev/audit/harnesses/ci3885_light.py stalepin 2026-11-22`: `STALE-PIN duplicates 14, of which this tree leaves 9 (2865 runner-min) and still dispatches 5 (3357); unattributed 7 (6412); job listings unread 0`. At origin/main the same arm prints `leaves 0 (0 runner-min) and still dispatches 14 (6222)`.
- `python3 dev/audit/harnesses/ci3885_light.py stalepin 2026-11-23`: `STALE-PIN duplicates 2, of which this tree leaves 2 (304 runner-min) and still dispatches 0 (0)`. At origin/main: `leaves 0 (0 runner-min) and still dispatches 2 (304)`.
- `python3 dev/audit/harnesses/ci3885_light.py stalepin 2026-11-25` (the day up to about 12:40Z, its four dispatches still running, so their minutes are partial): `STALE-PIN duplicates 4, of which this tree leaves 3 (322 runner-min) and still dispatches 1 (213)`. At origin/main: `leaves 0 (0 runner-min) and still dispatches 4 (535)`.
- Across the three days, each figure summed from the three `stalepin` lines above (`python3 dev/audit/harnesses/ci3885_light.py stalepin 2026-11-22`, `... stalepin 2026-11-23`, `... stalepin 2026-11-25`): 20 of the 27 duplicates are STALE-PIN dispatches (14+2+4 of 21+2+4). This tree leaves 14 of them (9+2+3) undispatched, 3,491 runner-min (2865+304+322).
- `python3 dev/audit/harnesses/ci3885_light.py dup 2026-11-22`, the finder's arm, before the change: `duplicate ... 21 runs, 12635 runner-min; sole grader: 14 runs, 4666`. 2026-11-23: 2 runs, 304 runner-min. The after end of `dup` is a day after this merges, because it reads which dispatches were actually fired (`## Forward-carry`).

The runner-minutes the fix saves are each left dispatch's whole cost, because a dispatch the sweep does not fire runs no job. That is not an upper bound, unlike `dup`'s figure, so the carry's unit-set comparison is not needed for these runs.

## Red checks

none

Scoped prepr only (`PREPR_SKIP_CODE=1 PREPR_SKIP_CLOSURES=1`). This PR's own CI is waived by #3394 comments 7157667401 and 7158048736. `python3 tools/ci/sweep.py --self-test`: 112 checks, 0 failed. `PYTHONPATH=tests/hastub python3 tests/harness_headers.py`: `ALL 115 HARNESS HEADER CHECKS PASSED`.

## Forward-carry

- The 7 unattributed duplicates of 2026-11-22 (6,412 runner-min) print no dispatch line in any gate-sweep.yml or `sweep-self` log the arm reads. The other dispatchers are merge-main.yml's token-push dispatch, tests.yml's three autofix dispatches and `tools/audit/seat/` instruments. Those fire on a newly pushed head rather than a graded one, so a by-hand run or a seat instrument is the next suspect. The next #3885 group attributes these from those logs and from the triggering actor. Carry: #3885
- The 5 STALE-PIN dispatches on 11-22 that the fix still fires (heads with only a body unit red, or the gate's own red) are the re-judges the arm exists for. Whether a fresh judge needs every code unit re-run there, or a gate-only re-judge would do, is the verdict-reuse question the carry names: a trust-model change that needs a design under decision 0014 before a fixer. Carry: #3885
- `dup`'s after end: re-run `python3 dev/audit/harnesses/ci3885_light.py dup DAY` and `stalepin DAY` for a busy day after this merges. STALE-PIN duplicates with a code unit red should read 0. Carry: #3885

## Friction

none
