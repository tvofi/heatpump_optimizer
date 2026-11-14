R10-RCA-MAIN-SELFTESTS-RED (topic r10-rca-main-selftests-red): the root-cause seat for main's `governance / instrument-self-tests`, which concluded `success` on no push from #3315 (`ba6fd7e8b`) to `57091a694`. It runs beside R10-HOTFIX-MAIN-SELFTESTS and changes no production code; the one file is `dev/audit/rca/R10-RCA-MAIN-SELFTESTS-RED.md`.

- Causes, each reproduced: (2a) table drift in `tools/ci/selftest_closures.json`; (2b) `ref_privacy.added_lines`' `git show REV:path` on an absent side stats the worktree path, so its read set follows each push's diff; (2c) #3361's ungated step, red on #3361's own merged head and merged under a non-required job; (2d, found in the run logs) #3315's push-only arm first ran on `main` and failed there (strace install under no-new-privileges sudo, a skipped launcher, the 60-minute timeout) until #3375.
- Process state: **(c)**. Detection (`drift`), the stated repair ("commit that file") and the trigger (the tick's main-red brief) all ran; the hand repair is outrun by the merge rate, and `ci_predict.py` has no arm for `selftest_scope.py`'s own gating check.
- Cost test: countermeasure A (commit the measured table through the `record/autofix` route on a drifted push) and B (a `ci_predict.py` arm over `selftest_scope.wiring_gaps`) both pass; neither is built here. 2d: none, recorded with its numbers.

## Head

`3f607ba9619a33dca856278d2d5a080161764f23`, on merge base `0362916ac7c1daf994e042c41d79b7e4083414e3` (origin/main at 2026-11-10, after run 42758119155 of `57091a694` concluded).

## Mutation proof

n/a: no production, test or check code changes; the diff is one RCA document. Countermeasure B's detector is demonstrated in the document (section 5) with a scratch probe calling the production `wiring_gaps`: 1 gap at `8652aa65c`, 0 at its parent `5ab6030d7`, 0 at `8652aa65c` with the step gated in scratch (reverted).

## Null control

- 2b: `strace -f -qq -e trace=%file git show HEAD:tools/audit/seat/gh_read_run.py` (path present) touches no worktree path; the same with `HEAD~400:` (path absent) touches `tools/audit/seat/gh_read_run.py`.
- 2c: `python3 -I tools/ci/selftest_scope.py --self-test` at `5ab6030d7` prints `103 checks, 0 failed`; at `8652aa65c`, `103 checks, 1 failed`.

## Figures

- `git log --first-parent --format=%h ba6fd7e8b..0362916ac | wc -l`: 36 commits after #3315 on main.
- Push runs per phase and their summary lines: `list_workflow_runs` of `ci.yml` (`branch=main`, `event=push`) and each run's `governance / instrument-self-tests` job log, tabulated in the document's section 1.
- `selftest_scope check` at `57091a694`: run 42758119155, job 129637321760, its own summary line.
- #3361's PR red: run 42748431595, job 129632432183, step "Show the self-test scope (tools/ci/selftest_scope.py) refusing its own fixtures".
- `git diff --stat 2cf0f129b^1 2cf0f129b -- tools/ci/selftest_closures.json`: #3375 added one entry, 26 insertions, 0 deletions.
- Missed-path add dates: `git log --diff-filter=A --format='%h %ad' --date=short -1 -- <path>`, per path in section 2a.
- Class enumerator 2: `for f in $(git grep -lE '"show", *f"\{' -- tools tests); do grep -qE -- '--name-only|--name-status|diff-tree' "$f" && echo "$f"; done`, 23 files at `0362916ac`.
- Push-only arms: `git grep -c "event_name == 'push'" -- .github/workflows`, 19 lines in 4 files.
- `python3 -I tools/ci/selftest_scope.py --self-test` wall clock at `8652aa65c`: 0.79 s (`date +%s.%N` before and after); `python3 -I tools/pr/ci_predict.py` at the same tree: 3.1 s.
- `python3 tests/closure.py select --diff 0362916ac --workdir "$D"`: `MODE: SCOPED -- 0 script(s) run, 33 scoped out`, over 1 changed file.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.

## Red checks

none

## Forward-carry

- Countermeasure A, the mechanical commit of the `selftest-closures` artifact on a push whose `drift` refuses only `UNDER-SCOPED` or missing-entry lines, through the `record/autofix` route. It changes `.github/workflows/` (code-owned), so it is a proposal for the owner, addressing state (c); its detector demonstration is owed by whoever builds it (section 5). Carry: dismissed: proposal for the owner, no stage brief changes before approval.
- Countermeasure B, a `tools/pr/ci_predict.py` arm predicting an `instrument-self-tests` red per `selftest_scope.wiring_gaps` gap on a diff touching `governance.yml`. Carry: dismissed: proposal for the owner, no stage brief changes before approval.
- Shape 2's instances (`ref_privacy.added_lines`, and beatd's suspected timing-dependent read set) are the live hotfix's own items (its brief's FIX line and step 4); nothing new to carry. Carry: R10-HOTFIX-MAIN-SELFTESTS

## Friction

none
