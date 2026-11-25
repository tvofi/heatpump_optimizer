Refs #3885

This PR leaves #3885 open. It removes the main source of the duplicate verified dispatches the light-grading PR measured. The other sources and the remaining duplicates are carried below.

**Why a head was graded twice.** This is the brief's first question: which dispatcher fired at heads a pull_request run had already graded? On 2026-11-22, 23 and 25 the answer is `tools/ci/sweep.py`'s STALE-PIN arm for 20 of the 27 duplicates `ci3885_light.py dup` counts. The other 7, all on 11-22, print no dispatch line in any sweep log read, so their dispatcher is not identified here (`## Forward-carry`).

STALE-PIN works like this. A pull_request run's gate restores `tools/ci/*.py` from the event's `base.sha`. When main has since changed those programs, the sweep does not re-run that gate. It dispatches one complete `ci.yml` run at the head to re-judge it with fresh programs (#3261, #3400, #3544).

The re-judge is needed when the red is the gate's own verdict (a deferral, a busy() read). It is not needed when a code unit has already failed at the head. The code under test is the PR head's own, which no pin restores, so the fresh run grades the same code again. None of the 20 STALE-PIN dispatches ended green: 8 failed and 12 were cancelled by a later push.

**The change.** `Sweep.fresh` now calls a new `Sweep.code_red(runs)` before it dispatches:
- `code_red(runs)` lists the code units (`gate.REQUIRED["no-pr"]`, the gate's own list, imported rather than restated) whose newest-started completed job at the head failed, across every run's latest attempt.
- If that list is non-empty, the sweep dispatches nothing and re-runs nothing, prints `STALE-PIN <pin>: run <id> left: <units> failed at this head ...`, and leaves the head to its next push.
- A body unit's red (`pr-contract`, `budget-raise-gate`, `arch-score`) still dispatches, because the fresh run re-reads the PR.
- A pin-graded unit's red still dispatches. `pinned_graders()` reads `.github/workflows/` for jobs whose block holds a `PINNED:` env naming `github.event.pull_request.base.sha`. At this head those are `tests / briefs`, `governance / policy-docs`, `env-matrix`, `wave-script` and `codeql / Analyze (...)`. A pull_request run grades them with the pin's copy and the fresh dispatch with origin/<base>'s, so the dispatch can turn them green: run 45005979443 on 11-22 turned 3 of 4 such reds green (#3895 review). The set is derived, never listed. An unreadable workflows directory pins nothing, and `code_red` then reads no red, so the dispatch stands (fail closed).
- So does a unit red in one run and green in a later one, and a cancelled unit.
- Every other STALE-PIN path is unchanged: the fresh judge already listed, one dispatch per sweep, the covered deferral, and the #3400 re-run from inside the fresh judge.

`dev/audit/harnesses/ci3885_light.py` gains a `stalepin DAY` arm, the attribution and replay instrument behind the figures:
- It takes `dup`'s duplicates and attributes each to STALE-PIN when a sweep job log prints the dispatch on its branch.
- It then replays the tree's own `Sweep.code_red` over the head's runs as they stood when the dispatch was created.

No CI trust-model change: no run accepts another run's job conclusions. The verdict-reuse lever the carry names stays unbuilt and still needs a design under decision 0014 (`## Forward-carry`). `tools/ci/prelude.py` and `.github/workflows/tests.yml` are not touched. This branch is cut from origin/main `6a58ba5cb3`, which carries #3888.

## Head

`eef6a631a774efa68074b2abb119f74a776f7af7` repairs fix review `blocked d339e843 class-open` (#3895, verdict comment 7163105542) in two commits on `d339e84355`. Delta for review: `git diff d339e84355 eef6a631a7` (`tools/ci/sweep.py`, `tools/ci/sweep_selftest.py`).
- `55ebd5fe32`:
  - `pinned_graders()` derives the pin-graded units from the workflows, and `code_red` leaves their reds to the dispatch.
  - Self-test cases: one per pinned kind (briefs, policy-docs, env-matrix, wave-script, codeql python). A fixture workflow pins the expression-cut name, the key-named job and nothing for a `github.sha`-only `PINNED`. The tree's own set is checked against the five. M6 gets a newer attempt still running beside an older red. M7 gets a lower run's newer green after a higher run's red.
  - The module doc and docstring count 16 dispatches, not 17.
- `eef6a631a7`: an `arch-score` red null case, and the fail-closed case run beside a real `fast (3.14)` red (null: the tree's workflows read it).
- Failing first: the reviewer's two null cases (`tests / briefs` red and `governance / policy-docs` red, each expecting one dispatch) failed at `d339e84355` (the review's `reviewer-null-cases.out`), and pass here. At `d339e84355` the new self-test stops at `AttributeError: module 'sweep' has no attribute 'pinned_graders'`.

`d339e84355ce1be351fd42c77ccafd2694b08dbf` adds one commit to the previous head, containing only this PR's own row, `dev/programme/delivery/3895.md`. The authored code head is `64220be0555fd8569c36702861eb65ba6c725c04`.

`136ac165472bba3ecb354cdabc97a746a73c155a` merges origin/main `bb6377b4da` into the authored code head `64220be0555fd8569c36702861eb65ba6c725c04` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below).

`64220be0555fd8569c36702861eb65ba6c725c04`, four commits on origin/main `6a58ba5cb30bf231dd7c6f60c42dc0d7583cb699`:
- `fd650c767d`: `Sweep.code_red` and its use in `Sweep.fresh` (`tools/ci/sweep.py`), with four self-test cases written first (`tools/ci/sweep_selftest.py`).
- `f4f4113035`: sweep.py's module doc states the exception.
- `87d2068c44` and `64220be055`: the harness arm.

`git merge-tree --write-tree origin/main HEAD` against `bb6377b4da` reports no conflict, so main is not merged (fixer.md step 6).

## Mutation proof

Repair round, each mutant applied to `tools/ci/sweep.py` at `eef6a631a7` and run with `python3 tools/ci/sweep.py --self-test` (base `123 checks, 0 failed`):
- R1 `if red:` -> `if False:`: 2 failed. R2 `c == "failure"` -> `c != "success"`: 1 failed. R3 first job wins: 1 failed.
- R4 `REQUIRED["no-pr"]` -> `REQUIRED["pr-cc"]`: 1 failed (`arch-score's red ... still takes one dispatch`). R5 the left branch's `return True` -> `False`: 2 failed.
- R6 (the review's M6) `status == "completed"` -> `True`: 1 failed, `a code unit red beside a newer attempt still running is left`. R7 (M7) key `(run_id, started_at)`: 1 failed, `the newest-started job decides, not the highest run id`.
- R8 the pinned exemption dropped: 5 failed (one per pinned kind). R9 any `PINNED:` counts: 1 failed (the fixture's `github.sha` null). R10 unreadable workflows fail open: 1 failed. R11 the name kept whole and R12 the key in place of the name: 3 failed each (codeql's `Analyze (` prefix).
- NULL, a comment on the guard line: `123 checks, 0 failed`.

The failing test came first. The new case `stale pin, #3885: a code unit red at the head is no stale verdict` failed on the unmodified sweep.py (`sweep self-test: 112 checks, 1 failed`), and the three null cases passed there.

Each mutant was applied to `tools/ci/sweep.py` at `fd650c767d` and run with `python3 tools/ci/sweep.py --self-test`:
- M1, `if red:` -> `if False:`: rc 1, `FAIL stale pin, #3885: a code unit red at the head is no stale verdict ...`
- M2, `c == "failure"` -> `c != "success"`: rc 1, `FAIL stale pin, #3885 null: a code unit cancelled, not failed still takes one dispatch`
- M3, newest-started ordering dropped (the first listed job wins): rc 1, `FAIL stale pin, #3885 null: a code unit red then green in a later run at the head still takes one dispatch`
- M4, `REQUIRED["no-pr"]` -> `REQUIRED["pr"]` (body units counted): rc 1, `FAIL stale pin, #3885 null: a body unit's red (the fresh run re-reads the body) still takes one dispatch`
- M5, the left branch's `return True` -> `return False` (falls through to a re-run in place): rc 1, `FAIL stale pin, #3885: a code unit red at the head ...`
- NULL, a comment added on the guard line: rc 0, `sweep self-test: 112 checks, 0 failed`

## Null control

- The harness arm, run unchanged from a detached worktree at origin/main `d3d66c4040` (main's sweep.py, which has no `code_red`), leaves 0 of the 20 STALE-PIN duplicates on each day. So the `left` count comes from the fix, not from the arm.
- Within the fixed tree, the predicate does not read every head as red: 7 of the 20 heads still dispatch. That is 6 with no unpinned code unit red, plus 45005979443, whose reds were all pin-graded.
- In the self-test, the three nulls (a body unit's red, a unit red then green, a cancelled unit) each take exactly one dispatch.

## Figures

- `python3 dev/audit/harnesses/ci3885_light.py stalepin 2026-11-22`: `STALE-PIN duplicates 14, of which this tree leaves 8 (2498 runner-min) and still dispatches 6 (3725); unattributed 7 (6412); job listings unread 0`. At origin/main the same arm prints `leaves 0 (0 runner-min) and still dispatches 14 (6222)`. Before the #3895 repair it left 9 (2865); 45005979443 (367 runner-min) now dispatches.
- `python3 dev/audit/harnesses/ci3885_light.py stalepin 2026-11-23`: `STALE-PIN duplicates 2, of which this tree leaves 2 (304 runner-min) and still dispatches 0 (0)`. At origin/main: `leaves 0 (0 runner-min) and still dispatches 2 (304)`.
- `python3 dev/audit/harnesses/ci3885_light.py stalepin 2026-11-25` (the day up to about 15:30Z, all four dispatches concluded): `STALE-PIN duplicates 4, of which this tree leaves 3 (1038 runner-min) and still dispatches 1 (421)`. At origin/main: `leaves 0 (0 runner-min) and still dispatches 4 (1460)`.
- Across the three days, each figure summed from the three `stalepin` lines above (`python3 dev/audit/harnesses/ci3885_light.py stalepin 2026-11-22`, `... stalepin 2026-11-23`, `... stalepin 2026-11-25`): 20 of the 27 duplicates are STALE-PIN dispatches (14+2+4 of 21+2+4). This tree leaves 13 of them (8+2+3) undispatched, 3,840 runner-min (2498+304+1038). Before the #3895 repair, and with 11-25's runs still in progress, the figure was 14 and 3,491.
- `python3 dev/audit/harnesses/ci3885_light.py dup 2026-11-22`, the finder's arm, before the change: `duplicate ... 21 runs, 12635 runner-min; sole grader: 14 runs, 4666`. 2026-11-23: 2 runs, 304 runner-min. The after end of `dup` is a day after this merges, because it reads which dispatches were actually fired (`## Forward-carry`).

The runner-minutes the fix saves are each left dispatch's whole cost, because a dispatch the sweep does not fire runs no job. That is not an upper bound, unlike `dup`'s figure, so the carry's unit-set comparison is not needed for these runs.

## Red checks

none

Scoped prepr only (`PREPR_SKIP_CODE=1 PREPR_SKIP_CLOSURES=1`). This PR's own CI is waived by #3394 comments 7157667401 and 7158048736. `python3 tools/ci/sweep.py --self-test`: 123 checks, 0 failed. `PYTHONPATH=tests/hastub python3 tests/harness_headers.py`: `ALL 115 HARNESS HEADER CHECKS PASSED`.

## Forward-carry

- The 7 unattributed duplicates of 2026-11-22 (6,412 runner-min) print no dispatch line in any gate-sweep.yml or `sweep-self` log the arm reads. The other dispatchers are merge-main.yml's token-push dispatch, tests.yml's three autofix dispatches and `tools/audit/seat/` instruments. Those fire on a newly pushed head rather than a graded one, so a by-hand run or a seat instrument is the next suspect. The next #3885 group attributes these from those logs and from the triggering actor. Carry: #3885
- The 7 STALE-PIN dispatches that the fix still fires (heads with only a body or pin-graded unit red, or the gate's own red) are the re-judges the arm exists for. Whether a fresh judge needs every code unit re-run there, or a gate-only re-judge would do, is the verdict-reuse question the carry names: a trust-model change that needs a design under decision 0014 before a fixer. Carry: #3885
- `dup`'s after end: re-run `python3 dev/audit/harnesses/ci3885_light.py dup DAY` and `stalepin DAY` for a busy day after this merges. STALE-PIN duplicates with a code unit red should read 0. Carry: #3885
- The harness's log read passes `--allow-escape-sequences` to `gh api` (`_log`), because the job logs carry escape sequences and gh refuses to print them otherwise. A gh too old to know the flag fails that call, and the arm then reads every dispatch as unattributed, with nothing saying why. The review reproduced this (`harness-local-patch.diff`). The next #3885 group makes the read fail loudly, or reads the log over REST without gh's terminal filter. Carry: #3885

## Friction

none

