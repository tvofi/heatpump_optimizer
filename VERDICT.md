Fix review: blocked 957df90af06717cd38127f7edf6623b9ff248989 defect: conflicts() parses the claimnotes driver's MERGE-CLAIM stderr as merge-tree output, so a claim-only DIRTY reads "could not answer" in any clone with the driver installed

Round 1 (first review). Head measured: 957df90af06717cd38127f7edf6623b9ff248989 (re-read on origin at posting: unchanged). Contract current: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` empty.

## Blocking

- K15 (c) misclassifies under the driver every clone is told to install (`claim-files.md`: "Install it once per clone"). `Tick.git` returns `stdout + stderr` (orchestrator_tick.py:288-290), and `mt.conflicts` reads every line of that. `git merge-tree --write-tree --name-only --no-messages` still invokes the `claimnotes` driver, which prints `MERGE-CLAIM: resolved <path>` to stderr (env_drift.py:1797). Reproduced in a clone of 57f0c9c77 with the driver configured, using a runner of the tick's own shape (ev/conflicts_with_driver.txt): a branch whose only conflict with main is a claim note, which is the DIRTY that GitHub reports and the shape the old hint was written for, gives `conflicts() -> None`. The tick then prints "git merge-tree could not answer", and the claimnotes repair is never offered. A content-plus-claim conflict lists `'MERGE-CLAIM: resolved tests/golden/claimed_drift.txt'` as a conflicted file. Without the driver (ev/conflicts_real_git.txt) all four arms classify correctly, so the self-test passes only because its throwaway repository has no driver and the tick arm is stubbed. Repair: read stdout alone (or drop lines that are not paths), then decide what a driver-resolved claim file means for a GitHub DIRTY, which reads `[]` locally. Pin it with a driver-installed arm. Carry: dismissed: blocks this PR, fixer repairs at this head (item 0d1ac6a4)

## RESULT lines (reviewer's own harness, ev/replay_live.txt, tools/replay_live.py in ev)

- RESULT live replay, no rewriting: the PR head's own check runs (ev/head_check_runs.json, read 18:3xZ with Analyze (python), browser and fast (3.14) in flight, closures with no run, nightly-status red) against main-protect-checks read live, less PR_ONLY. The base logs `is not green (Analyze (python), browser, closures, fast (3.14)) ... revert it first`, and the head logs `is still running (...): a wait, not red`, with `classify -> ('wait', [...], [])`. This confirms the body's claim on live in-flight runs. Carry: dismissed: confirmed claim, nothing owed (item 43c7f166)
- RESULT perturbation: with typing set to failure, the head logs `is RED (typing)`. Null control: with every run settled green, base and head both log nothing (ev/replay_perturb.txt). The harness moves under its perturbation. Carry: dismissed: confirmed claim, nothing owed (item 95d1f293)
- RESULT fixer's e7c66485 replay at both ends reproduces the body's quoted lines exactly (ev/replay_fixer_e7c66485.txt). Carry: dismissed: confirmed claim, nothing owed (item 26a423c7)
- RESULT self-tests base 198/168/14 and head 214/178/16, 0 failed, under python 3.11 (ev/selftests.txt), match the body. Carry: dismissed: confirmed claim, nothing owed (item 52adc4d5)
- RESULT mutants: all 15 named mutants were KILLED, each with the failed count the body quotes, `RESULT survivors=0` (ev/mutants_fixer.txt). Carry: dismissed: confirmed claim, nothing owed (item 553f4490)
- RESULT stale path: the stale-check-run arm (re-run once, logged with its run id, null control on an in-progress run, a stop when it stays unconcluded) is exercised by the train self-test and by merge_pr.sh's two new checks, and is killed by merge_train-6/7/8 and merge_pr-1. The tick and merge_pr.sh delegate to merge_train's `latest_runs`/`run_state`/`classify`/`conflicts`/`dirty_repair` (diff read; orchestrator_tick-1/3 and merge_pr-1 kill the delegations). Carry: dismissed: confirmed claim, nothing owed (item 08d3daad)

## Reviewer mutants that survive (ev/mutants_reviewer.txt), for the repair round

- R2: `getattr(self, "_req_pr", None) or required` to `required` survives (178/0). The body's "(PR_ONLY included)" for the tick's NOT REVIEWABLE line is unpinned: a red `pr-contract` at a PR head would go unflagged. Carry: dismissed: blocks this PR, fixer repairs at this head (item a30fdf1c)
- R1: dropping the `(code == 1) != (len(lines) > 1)` guard in `conflicts` survives, and so does R3, re-running a shared workflow run once per check-run name instead of once per run. R4, removing the `runs is None` unreadable arm in the overlap gate, survives too. Carry: dismissed: blocks this PR, fixer repairs at this head (item cfa21c00)

## Other checks

- Merge with origin/main 57f0c9c77: `git merge-tree --write-tree` is clean (tree 9d0d50c06, rc 0, ev/merge_tree.txt). VERSION, the manifest and RELEASE_NOTES are untouched. throwaway_git --check 0 refused, selftest_wiring 38/38, tmp_paths 0 refused, `STRUCTURE RATCHET PASSED` (ev/cheap_checks.txt). Carry: dismissed: confirmed claim, nothing owed (item fb2f4ea5)
- CI at the head (check-runs API, ev/head_check_runs_final.json): coverage, fast (3.14) and Analyze (python) were still in progress when posted. The only red is nightly-status, which grades main and is not this PR's, so `## Red checks: none` stands for now. Carry: dismissed: not this PR's red (item e1854054)
- Forward-carry: both bullets name R10-ORCH-MACHINERY (on the roster, not-started), and the first states its control (the e7c66485 replay). Carry: dismissed: confirmed claim, nothing owed (item 62a7838d)
- Class rule: the body's `git grep` enumeration was not re-run seam by seam. This verdict blocks on (c) before class closure is reached. Carry: dismissed: deferred to next round (item dd9f8410)

bus-nonce: ee2cfa334fe07c8fd0715f8725b0e38d
