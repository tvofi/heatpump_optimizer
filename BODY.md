A stopped pusher must not leave its work running, and no pusher may join the tree without the same guarantee.

A shell does not forward TERM, INT or HUP to a foreground child. So a stopped pusher exited, its subtree was reparented, and the subtree kept burning CPU. On 2026-10-20 six survivors were swept up, aged 26 to 62 minutes, on a box at load 77 on eight cores. The review of `c071fa5f` blocked on `class-rule-missing`: it found a fourth pusher (`handoff_push.sh`) that no rule had enumerated. This branch closes the class with a rule that enumerates every pusher, and it treats every seam that rule returns.

**The rule (the census).** `tools/audit/seat/pr_args.sh --pushers [<rev>]` defines a pusher as any tracked `tools/` script (`*.sh`, `*.py`, `*.mjs`, `*.js`) that names `app_push.sh` or `push.sh`. The test is the census's `git grep -lE '(^|[^A-Za-z0-9_])(app_)?push\.sh'`. Every path the grep returns needs exactly one disposition in `PR_PUSHERS`:
- `runner`: the script installs `pr_exit_trap`, and every line running `"$_push"` or `"$prepr"` runs it asynchronously.
- `runner-py`: the script TERMs its tool rather than SIGKILLing it, and its entry calls `stop_on_signal()`.
- `retired`: `push.sh`.
- `mention`: the script names a pusher but runs none, and the entry gives the reason.

The census prints `OPEN` and exits 1 in three cases: a returned path with no entry, an entry the grep no longer returns, and a runner that lacks either property. `pr_args.sh --self-test` runs the census on the tree. CI runs that self-test (the `open_pr.sh` and `update_pr.sh --self-test` steps), so a new pusher cannot land without a disposition.

**The mechanism is one EXIT trap.** `pr_exit_trap [<command>]` sets an EXIT trap that runs `<command>`, then `pr_reap`, then `$PR_AFTER_REAP`. bash runs the EXIT trap when TERM, INT or HUP ends the shell, as well as on every other exit. Each push runs asynchronously, and the shell `wait`s on it, because an untrapped INT waits for a foreground child while all three signals interrupt `wait`. `pr_reap` walks `pgrep -P` from `$$` and TERMs each pid. It KILLs whatever outlives a 2 s grace (`# mut:grace`), and it ignores further stop signals while it runs (`# mut:sigign`). Every signal goes to a numeric pid the walk returned, never to a pattern or a group.

**The branch lock (from main, kept).** Main's `pr_branch_lock` is the one per-branch lock, shared by `open_pr.sh` and `update_pr.sh`. It now hands its unlock to the reap instead of installing its own traps. `PR_REAP_SPARE` keeps the lock's holder out of the walk, and `PR_AFTER_REAP` ends the holder after the reap. So a stopped run frees the branch only once its push has ended. That keeps main's guarantee and adds this PR's reap.

Seams treated in this diff: `handoff_push.sh`, `remerge_main.sh`, `merge_train.py` (`Train._run` TERMs its tool and waits for that tool's trap; `stop_on_signal()` turns TERM and HUP into `SystemExit`), and `cloud_relay.sh` (it runs `update_pr.sh`). The three pushers named before, `open_pr.sh`, `update_pr.sh` and `app_push.sh`, use the same mechanism. In `app_push.sh` that mechanism is `pr_exit_trap cleanup`, and `cleanup` is a no-op until `$PRIV` exists.

SIGKILL is out of scope, because no trap runs on it. The KILL arm asserts only that the lock does not go stale.

## Head

`6978fe22756523dbbd803f0db2d5f3966e2cb5e0` is the code head, and everything below was measured there unless a line names another commit. origin/main was `93e6a63d2855651448a2b8f677b392feddc03c99`, read 2026-10-22T01:17:35Z, and it is this head's merge base.

This head is `e856439273f4ac037b1d0390b0147b3385e201b7` (the previous handoff) plus five commits:
- `be401d6d1` merges origin/main `5a755f53`. It conflicted in three files (`## Conflict resolution`).
- `f58280b8c` adds one self-test arm (`heldrun`, below).
- `e22d385e5` merges origin/main `214350c4`. It conflicted in two files (`## Conflict resolution`).
- `686cc4e50` merges origin/main `46e36812`. The merge was clean, and it changed none of this PR's nine files. Check: `git diff --quiet e22d385e5 686cc4e50 -- <the nine>` exited 0.
- `6978fe22` merges origin/main `93e6a63d`. The merge was clean. It changed none of this PR's scripts and none of the files their self-test fixtures source (`prepr.sh`, `head_note.py`, `delivery_row.sh`, `pr_cap.py`, `tests/throwaway_git.sh`). Check: `git diff --quiet 686cc4e50 6978fe22 -- <those thirteen>` exited 0. Its new `tools/audit/seat/pulse.py` names no pusher: the census still returns 16 paths, 0 of them OPEN.

`prepr` runs with `PREPR_SKIP_CLOSURES=1` (the owner's ruling), so the scoped gate was derived separately and is in `## Figures`.

## Conflict resolution

Each conflicting hunk, the choice made, and why both sides' behaviour survives.

**Merge `be401d6d1` (origin/main `5a755f53`):**

- **`tools/audit/seat/update_pr.sh`, header comment.** Kept main's sentence (one run per branch, `open_pr.sh` included, through `pr_branch_lock`). Replaced its last clause with this PR's: a stopped run reaps its push's tree, then frees the lock only once that push has ended.
- **`tools/audit/seat/update_pr.sh`, the inline lock block.** Took main's `pr_branch_lock "$WT.lock" "$BR" "$WT"`, the lock shared with `open_pr.sh`, together with main's `pr_lock_busy` BUSY text. Put this PR's `pr_exit_trap` on the line before it. This PR's inline flock copy and `upd_unlocked` are gone; main's helper replaces them.
- **`tools/audit/seat/pr_args.sh`, `pr_branch_lock` itself.** This is the semantic conflict. git auto-merged the function without a marker, and the result was broken. Main's version ends with `trap '…' EXIT` and `trap 'exit 143' TERM INT HUP`. Those lines overwrite the EXIT trap that `open_pr.sh` installs first, so `open_pr.sh` would silently stop reaping.
  - Choice: the holder's unlock moves into `PR_AFTER_REAP` (still tagged `# mut:unlock`), and `PR_REAP_SPARE=$LKP` keeps the holder out of the walk. `pr_exit_trap` runs the reap first and the unlock after it. Main's `trap 'exit 143' …  # mut:stop` line is dropped, because the EXIT trap already runs on those signals.
  - Main's property is "a TERMed run keeps the lock until its push has ended". It holds because the push has ended once the reap returns. The new `heldrun` arm pins it with a TERM-proof child (`## Mutation proof`).
  - Demonstrated: the MAINLOCK mutant restores main's version verbatim and fails 5 arms.
- **`tools/audit/seat/pr_args.sh`, the self-test after `took_lock`.** Kept this PR's stoprun arms: reap, lock held during the push, lock free after the stop, the KILL arm, `mut:watch`, and the null control.
  - Main's TERM arm asserted that the lock is still BUSY while the push runs on. That arm is replaced, because the reap now ends the push. Its property is now `heldrun`.
  - Main's `mut:stop` arm ("the lock is freed while the push still runs") is kept as a second assertion on this PR's `mut:stop` (`pr_kill`'s kill), where it holds: the tree survives and the next run is not BUSY.
  - Main's `racerun` (`mut:oplock`, `mut:unpushed`) and `unpushed` arms are kept verbatim.
- **`tools/audit/seat/handoff_push.sh`, the self-test and source hunk.** Took main's `handoff_push_self_test` and its `--self-test` dispatch. Placed this PR's `. pr_args.sh; pr_exit_trap` after the dispatch. Main's fixture copies the script into a scratch clone, so it now copies `pr_args.sh` too (two `cp` lines).
- **`tools/audit/seat/handoff_push.sh`, the three push hunks (update, open, row).** Took main's `push_app` seam and its anchors `# mut:push-update`, `# mut:push-open` and `# mut:push-row`. These lines are the anchors `dev/audit/harnesses/r10_seat_selftests_mutants.py` S35–S37 plant.
  - Inside `push_app`, the push is this PR's: asynchronous into `$B.push.log`, then `wait`, then main's `REFUSE|PUSHED` filter over the log.
  - The push sits on one line ending in ` &`, so the census and its foreground-mutant arm can read it.

**Merge `e22d385e5` (origin/main `214350c4`, R10-ROW-ONLY-UPDATE):**

- **`tools/audit/seat/update_pr.sh`, header comment.** Kept this PR's stop sentence and appended main's `--row-only` paragraph.
- **`tools/audit/seat/update_pr.sh`, the push.** Main's `RO` line is kept (`# mut:rowonly`). Main passes `$RO` to the push, and that push keeps this PR's asynchronous form with `pr_wait`. Main's `grep -h '^app_push: ROW-ONLY:'` line follows the push. Main's `rowrun` arms pass: `pr_args self-test: 86 checks, 0 failed`.
- **`tools/pr/app_push.sh`, the prepr gate in `push_and_open`.** This PR's prepr is kept asynchronous, under `wait`. Main's `row_only_checks` gate is added after it, unchanged. `app_push self-test: 186 checks, 0 failed` includes main's row-only arms. `row_only_checks` runs its two checks in the foreground (`policy_lint.mjs`, `carry_audit.py`). These are not `"$_push"` or `"$prepr"` lines, so the census does not read them. On TERM the EXIT trap reaps them like any descendant. An INT waits up to their runtime: seconds, the cost main's own design states.

## Mutation proof

Each mutant was applied to the committed head `686cc4e50aa92d7cc7086bcb7fea7b60f877bf9e` in a scratch `mut.py`, which asserts that each anchor occurs exactly once. The named self-test was then run under `timeout 600`. Each mutant was restored with `git checkout -- <file>`, and `git status --short` was empty afterwards. These runs, and the harness run below, were measured at `686cc4e50`, not at the head. From there to `6978fe22`, the delta touches none of the files a mutant edits or a fixture sources (`## Head`). The census those arms read returns the same 16 paths with 0 OPEN at the head. Main's new governance step (`pulse.py --self-test`) is the one harness input that changed, and it is not re-run here. M0 at the head is the self-test table in `## Figures`.

- **M0, the null run:** no change to any line. `pr_args self-test: 86 checks, 0 failed`.
- **STOP, `pr_kill`'s kill line (`# mut:stop`) emptied:** 6 failed. They are the named survivor arms: the open_pr TERM and INT arms, the handoff_push, remerge_main and update_pr TERM arms, and `the reap KILLs a child that ignores TERM once the grace is spent…`.
- **RECURSE, `pr_descendants "$k"` emptied (no recursive walk):** the same 6 failed.
- **GRACE, the KILL loop (`# mut:grace`) emptied:** 1 failed, `the reap KILLs a child that ignores TERM once the grace is spent, through a second TERM; the host exits 143`.
- **SIGIGN, `trap '' TERM INT HUP` (`# mut:sigign`) emptied:** 1 failed, the same arm.
- **EXITREAP, `pr_exit_trap`'s trap line emptied:** 11 failed. They are every TERM/INT reap arm, the update_pr lock arms (detached child, holder exited, lock free after stop, the KILL arm), and the `afterreap` arm.
- **SPARE, `PR_REAP_SPARE=$LKP` emptied:** 2 failed: `mutant mut:unlock … the holder is still alive when the run returns` and `update_pr: a TERMed run whose push outlives the TERM keeps the lock until the reap has ended it`.
- **ORDER, `pr_exit_trap`'s order reversed (unlock, then reap):** 1 failed, `update_pr: a TERMed run whose push outlives the TERM keeps the lock until the reap has ended it`.
- **MAINLOCK, main's `pr_branch_lock` restored verbatim (its own `trap … EXIT  # mut:unlock` and `trap 'exit 143' TERM INT HUP`):** 5 failed: the open_pr TERM and INT arms, the update_pr TERM arm, the `mut:unlock` arm, and the `afterreap` arm. This is the auto-merged state that `## Conflict resolution` repairs.
- **OPENFG, `open_pr.sh`'s first push back in the foreground (its ` &` dropped):** killed. The run hit `timeout 600` (rc 124) with 9 arms already failed, among them `open_pr: INT reaps the tree too -- the push runs asynchronously, so the INT does not wait behind it` and both census arms. The other six are open_pr arms that no longer see their open-count fixture.
- **UPDFG, `update_pr.sh`'s push back in the foreground:** killed. The run hit `timeout 600` (rc 124) with 6 arms already failed: both census arms, `update_pr: after the stop the lock is free, so the next run takes it`, the KILL arm, the dead-lock null control, and the detached-child arm.
- **M1, `handoff_push.sh`'s `pr_exit_trap` dropped from its source line:** 4 failed: `handoff_push: TERM reaps the whole descendant tree, and the pusher is gone`, both census arms, and `a runner whose push runs in the foreground is refused` (the no-trap OPEN fires first).
- **M2, `handoff_push.sh`'s `push_app` push back in the foreground (` &` dropped):** 2 failed, both census arms (`a push runs in the foreground`).
- **M3, `remerge_main.sh`'s `pr_exit_trap` dropped:** 3 failed: `remerge_main: TERM reaps the whole descendant tree, and the pusher is gone` and both census arms.
- **M5, `cloud_relay.sh`'s `pr_exit_trap` dropped:** `cloud_relay self-test: 82 checks, 1 failed`, `a relay TERMed mid-update leaves none of the update's tree alive (R10-PUSHER-REAP)`.
- **M6, `app_push.sh`'s `pr_exit_trap cleanup` dropped:** `app_push self-test: 186 checks, 11 failed`. They are `and leaves none of prepr's tree alive (R10-PUSHER-REAP) (got '3', want '0')` and ten token-revoke and private-directory arms.
- **M6B, the same line replaced by `trap cleanup EXIT` (cleanup kept, reap removed):** 1 failed, `and leaves none of prepr's tree alive (R10-PUSHER-REAP) (got '3', want '0')`. So app_push's own reap is pinned apart from its cleanup.
- **M7, `merge_train.py` `Train._run`'s `p.terminate()` turned into `p.kill()`:** `merge_train self-test: 200 checks, 1 failed`, `a TERMed train exits 143 and leaves none of its tool's tree alive (R10-PUSHER-REAP)`.
- **M8, `merge_train.py` `main`'s `stop_on_signal()` call deleted:** `pr_args self-test: 86 checks, 2 failed`, both census arms.
- **M9, the handler's `raise SystemExit(128 + signum)` turned into `return None`:** 1 failed, the same arm as M7.

**Built-in mutants.** `pr_args.sh`'s self-test runs each of these on copies of the scripts, and each arm passes only when its mutant shows the defect: `mut:exitreap`, `mut:grace`, `mut:sigign`, `mut:stop`, `mut:unlock`, `mut:watch`, `mut:lock`, `mut:oplock`, `mut:unpushed` and `mut:rowonly`. The new sed mutant `afterreap` reverses `pr_exit_trap`'s order. All of them pass in M0.

**Review survivors at `c071fa5f`, and where each stands now:**
- The `pr_signal_traps` call is gone, along with the signal traps themselves.
- app_push's EXIT reap is killed by M6 and M6B.
- The KILL escalation is killed by GRACE.
- Both EXIT backstops are killed by EXITREAP, M1 and M3.

**Failing test first.**
- The `heldrun` arm is new in `f58280b8c`. Against production with the reap order reversed (ORDER), it fails, and that is the only arm that fails. At `be401d6d1`, before the arm existed, ORDER passed all 81 checks. The survivor is what the arm was written for.
- The arms from round 2 were shown failing against `c071fa5f`'s `handoff_push.sh` and `remerge_main.sh` in the previous body. Their production lines are unchanged, and M1 and M3 kill them at this head.

**The seat-selftest harness from main.** `python3 dev/audit/harnesses/r10_seat_selftests_mutants.py` (every seat step under `bash -e`, then S01–S38 and W1–W3) printed `== M0: 0 seat step(s) red` and `RESULT survivors=0`, with 42 mutants `KILLED`. That includes S08, S12, S14, S27 and S35–S37, which plant mutants in files this PR changes.

## Null control

- **The bystander.** An unrelated sleeper, started outside any pusher's tree, survives every TERM arm and the successful-run arm. The reap goes by pid only.
- **The merge_train arm** runs its own control: the same driver without `stop_on_signal()`. There the train dies and all 3 pids of its tool's tree survive, so the arm can see the defect it pins.
- **`heldrun`.** Without the TERM-proof child, the reap ends the push in milliseconds, and an early unlock would be invisible. With the child, the grace is 2 s. The arm's `afterreap` mutant must report `early`, which shows the probe can see an early unlock.
- **The census.**
  - On a scratch tree, the census refuses three plants: an undispositioned `new_pusher.sh`, a deleted `pr_exit_trap`, and a dropped `&`. These are self-test arms.
  - Run from outside the repository, the grep returns nothing. `bash <(git show HEAD:tools/audit/seat/pr_args.sh) --pushers` from `/tmp` printed 16 `stale` OPEN lines and exited 1, so an empty enumeration cannot pass.
- **No vacuous reap arm.** Every reap verdict first requires that the push's tree started (4 recorded pids, `treen`).

## Figures

All measured at `6978fe22756523dbbd803f0db2d5f3966e2cb5e0`, with origin/main at `93e6a63d2855651448a2b8f677b392feddc03c99` (read 2026-10-22T01:17:35Z).

- **The class's seams.** Rule: `bash tools/audit/seat/pr_args.sh --pushers <rev>`, the git grep above with the dispositions in `PR_PUSHERS`. It returns 16 paths at each column's revision (`--pushers <rev> | wc -l`).

  | seam | disposition | merge base `93e6a63d` | `c071fa5f` | this head |
  |---|---|---|---|---|
  | `tools/audit/seat/handoff_push.sh` | runner, closed in this diff | OPEN | OPEN | ok |
  | `tools/audit/seat/remerge_main.sh` | runner, closed in this diff | OPEN | OPEN | ok |
  | `tools/audit/seat/merge_train.py` | runner-py, closed in this diff | OPEN | OPEN | ok |
  | `tools/audit/seat/open_pr.sh` | runner, closed in this diff | OPEN | OPEN* | ok |
  | `tools/audit/seat/update_pr.sh` | runner, closed in this diff | OPEN | OPEN* | ok |
  | `tools/pr/app_push.sh` | runner, closed in this diff | OPEN | OPEN* | ok |
  | `tools/pr/push.sh` | retired: decision 0011's retired author path; the level-2 rule below returns no runner of it | ok | ok | ok |
  | 9 `mention` paths, each with its reason in `PR_PUSHERS` | mention | ok | ok | ok |

  The 9 mention paths are `pr_args.sh`, `handover_prompt.py`, `ref_privacy.py`, `app_approve.sh`, `approve_held_runs.sh`, `head_note.py`, `check-wave-script.mjs`, `friction_issues.mjs` and `policy_lint.mjs`.

  Census exit status: 1 at the merge base (6 OPEN), 1 at `c071fa5f` (6 OPEN), 0 at this head (0 OPEN).

  \* At `c071fa5f` these three did reap, through `pr_signal_traps`. The census keys on `pr_exit_trap`, so its reading of that commit is name-keyed.
- **Level 2: who executes a runner.** Rule: `git grep -nE '(bash|exec)[^#|;]*(handoff_push|open_pr|update_pr|remerge_main)\.sh|tool\("(remerge_main|app_push)"\)' HEAD -- 'tools/*.sh' 'tools/*.py'`. It returns 15 lines in 6 files. Each file's disposition:
  - `cloud_relay.sh`, 1 line, runs update_pr: closed in this diff, with its own arm.
  - `merge_train.py`, 2 lines, runs remerge_main and app_push `--branch-only`: closed in this diff (runner-py).
  - `pr_args.sh`, 9 lines: its self-test fixtures.
  - `handoff_push.sh`, 1 line: main's self-test fixture, which runs the script's copy in a scratch clone.
  - `r9_rc_bus_fetchhead.sh`, 1 line: a round-9 measurement harness that runs `handoff_push.sh` in a scratch fixture.
  - `tmp_paths.py`, 1 line: a self-test string.

  Callers above level 2 stop a child that now reaps its own tree: `train.sh` runs `merge_train.py`, and `tick_loop.sh` runs `cloud_relay.sh`.
- **Self-tests:**

  | command | result |
  |---|---|
  | `bash tools/audit/seat/open_pr.sh --self-test` | `delivery_row self-test: 5 checks, 0 failed`; `pr_args self-test: 86 checks, 0 failed` |
  | `bash tools/audit/seat/update_pr.sh --self-test` | the same two lines |
  | `bash tools/audit/seat/handoff_push.sh --self-test` | `delivery_row self-test: 5 checks, 0 failed`; `handoff_push self-test: 2 checks, 0 failed` |
  | `bash tools/pr/app_push.sh --self-test` | `app_push self-test: 186 checks, 0 failed` |
  | `bash tools/audit/seat/cloud_relay.sh --self-test` | `cloud_relay self-test: 82 checks, 0 failed` |
  | `python3 tools/audit/seat/merge_train.py --self-test` | `merge_train self-test: 200 checks, 0 failed` |
- **The scoped gate.**
  - `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` printed `MODE: SCOPED -- 1 script(s) run, 32 scoped out`, and `scope.run` names `tests/entities.py`.
  - `PYTHONPATH=tests/hastub python tests/entities.py` (python 3.13 with `tests/requirements-ci.txt`) printed `ALL 2382 ENTITY CHECKS PASSED`.
- **Checks before push:**
  - `python3 tests/structure.py` printed `STRUCTURE RATCHET PASSED`.
  - `python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD) HEAD` printed `Architecture score: dS +0.0000 NULL`.
  - `python3 -I tools/audit/seat/tmp_paths.py --check` printed `tmp_paths: 0 refused, 0 stale allow entries at HEAD`.
  - `python3 -I tests/throwaway_git.py --check` printed `throwaway_git: 0 raw git init or clone site(s) refused, 0 stale allow entries at HEAD`.
  - `git diff $(git merge-base origin/main HEAD)...HEAD | grep -nE '^\+.*\bgit\b.*\b(init|clone)\b'` printed nothing (exit 1).
- **Rule 3 / rule 4.** `git diff --name-only $(git merge-base origin/main HEAD)...HEAD | grep -E 'VERSION|manifest|RELEASE_NOTES|claimed_drift'` printed nothing (exit 1). The diff is 9 files (`git diff --stat`).
- **Carry.** `python3 tools/audit/carry_audit.py --roster-ref origin/handoff/audit-r10-roster check --body <this body>` printed `CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)`.

## Red checks

- **`pr-contract` at `c071fa5f`.** `carry_audit.py` refused 3 unrouted body items. The body caused it, not the code, and this body passes that check (`## Figures`, Carry). A cheaper detector already exists, `carry_audit.py`'s own check, run here before the push. I am naming the trigger here; its analysis belongs to `root-cause.md`'s seat.
- **`governance` at the round-1 head, the throwaway-git step.** Its cheaper detector is `python3 -I tests/throwaway_git.py --check`, a one-second local run. It passes at this head (`## Figures`). I am naming the trigger here; its analysis belongs to `root-cause.md`'s seat.
- **`nightly-status`** grades `main`. This diff (eight `tools/` scripts and one delivery row) does not reach anything it reads.
- **`ci-ratchet` on main** is red from runner-speed variance, which R10-CI-LAYOUT owns. This diff does not touch it.

## Forward-carry

none

## Friction

none
