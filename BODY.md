A stopped pusher must not leave its work running, and no pusher, or launcher of one, may join the tree without the same guarantee.

A shell does not forward TERM, INT or HUP to a foreground child, so a stopped pusher exited and its reparented subtree kept running (2026-10-20: six survivors, aged 26 to 62 minutes, on a box at load 77 on eight cores).

**The fix.** `tools/audit/seat/pr_args.sh`'s `pr_exit_trap [<command>]` sets one EXIT trap: `<command>`, then `pr_reap`, then `$PR_AFTER_REAP`. Each push or child runs asynchronously and the shell `wait`s on it, so TERM, INT and HUP all interrupt the wait and run the trap. `pr_reap` walks `pgrep -P` from `$$`, TERMs each numeric pid it returned (never a pattern or a group), and KILLs what outlives a 2 s grace. A runner whose child is itself a runner names it `PR_REAP_LEAD`; `pr_reap` TERMs the lead alone first and waits up to `PR_REAP_LEAD_TENTHS` for it to stop its own tree.

Seams closed: the runners `open_pr.sh`, `update_pr.sh`, `handoff_push.sh`, `remerge_main.sh` and `tools/pr/app_push.sh` (its prepr and its own `git push`; `MINT_TRAP=caller` keeps `app_mint.sh`'s traps off the reap); `merge_train.py` (`Train._run` TERMs its tool, never a bare SIGKILL, and `stop_on_signal()` makes a TERM or HUP unwind); `train.sh`, with `merge_train.py` as its lead; `cloud_relay.sh`, with `update_pr.sh` as its lead, launched for the stub and the production route from one backgrounded line (`788a882d7`), which clears the `a01627177715` review's mutation-vacuous block.

Part of #2502, which stays open (`## Forward-carry`).

## Head

`a0cb0cdd7f2d3955f06dbb65946257a938d633a3` merges origin/main `50808a755ce300fac4b19b7cfe7f89c795b8387b` (#2580, R10-FLOW-RELAY-HOLD) into the previous PR head `e62be31de2c3d80217d6d855b59f7d27f5392826`, whose parents are `c3bafaf88` and origin/main `a9db47846`; the authored code head `2d5d6be11` is reached through `c3bafaf88`. Everything below was measured at `a0cb0cdd7` unless a line names another commit.

**Conflict resolution, `tools/audit/seat/cloud_relay.sh`.** One hunk, `handoff_arm()`'s `local` line: #2580 adds `held_prs`, this PR adds `upd`. Resolved as the union, `... nonce urc held_prs upd`; no other line conflicted.
- Order in `handoff_arm()`: the contained test (`git merge-base --is-ancestor "$hs" "$head" && continue`), then #2580's hold (`HELD #$pr $hs; continue`), then the failed-update ledger, then the single launch (`"${upd[@]}" ... &`, `PR_REAP_LEAD=$!`). A held PR `continue`s before the launch, so the relay never runs `update_pr.sh` on it.
- That order is pinned: moving the hold line to just after `PR_REAP_LEAD=$!; wait ...` reds 3 of 192 arms (`a held PR whose handoff is ahead is not updated`, `a held PR whose handoff tip moved is still not updated`, `a hold outranks a recorded failed update: still HELD`). #2580's own ordering mutants `cloud_relay-8` and `cloud_relay-9` are killed below.
- No revert of either side: `git diff --stat 50808a755...HEAD` prints `13 files changed, 904 insertions(+), 83 deletions(-)`, the same as at `2d5d6be11`; #2580's hold arms all pass in the merged self-test (192 checks, 84 before #2580).

## Mutation proof

**The review's block, failing test first and fixed.** `dev/audit/harnesses/r10_pusher_reap_launch_mutants.sh` (sha1 `5a4a1925`, unchanged since `db0d88377`) applies each mutant exact-once in a fresh detached worktree and runs the named self-tests:
- At `a01627177715` (the blocked head), `F-CR-ELSEFG` and `F-CR-ELSELEAD` each print `MUTANT F-CR-…: CR rc=0 cloud_relay self-test: 83 checks, 0 failed`, re-run this round (`… a01627177 M0 F-CR-ELSEFG F-CR-ELSELEAD`; M0 there: CR 83/0, TR ok, PA 90/0, AP 186/0, MT 200/0). The block is reproduced.
- At `af7eb2d9a` (the production-route arm, the split launch unchanged), both are killed:
  - `MUTANT F-CR-ELSEFG: CR rc=1 cloud_relay self-test: 84 checks, 1 failed` / `FAIL with no stub, the relay runs update_pr.sh beside it as the lead, asynchronously: a TERM ends it in that order (rc=1, want 0)`
  - `MUTANT F-CR-ELSELEAD: CR rc=1 cloud_relay self-test: 84 checks, 1 failed` / `FAIL with no stub, the relay runs update_pr.sh beside it as the lead, asynchronously: a TERM ends it in that order (rc=1, want 0)`
- At this head, `788a882d7` removed the split line, so `F-CR-ELSEFG` prints `NOT APPLIED at 2d5d6be11` (its anchor occurs 0 times); its successors on the one launch line are killed: `CR-FG` (CR rc=1, `$!: unbound variable` under `set -u`, no summary line) and `CR-FG-BOUND` (`84 checks, 4 failed`, among them the production-route arm). `F-CR-ELSELEAD` still applies and is killed: `cloud_relay self-test: 84 checks, 1 failed` / `FAIL with no stub, the relay runs update_pr.sh beside it as the lead, asynchronously: a TERM ends it in that order (rc=1, want 0)`.

**The sweep at this head**, `bash dev/audit/harnesses/r10_pusher_reap_launch_mutants.sh 2d5d6be11` (every row):

| row | mutant | result at `2d5d6be11` |
|---|---|---|
| M0 | none | CR `84 checks, 0 failed`; TR `ok`; PA `93 checks, 0 failed`; AP `197 checks, 0 failed`; MT `221 checks, 0 failed` |
| CR-FG | relay update launch in the foreground | CR rc=1, no summary line (`$!` unbound under `set -u`) |
| CR-FG-BOUND | the same, `$!` kept bound | CR `84 checks, 4 failed`, including `FAIL with no stub, the relay runs update_pr.sh beside it as the lead, asynchronously: a TERM ends it in that order` |
| CR-LEADNAME | the launch not named `PR_REAP_LEAD` | CR `84 checks, 2 failed`, the stub lead arm and the production-route arm |
| CR-PRODPATH | default command → `update_pr.missing` | CR `84 checks, 1 failed`, the production-route arm alone |
| F-CR-ELSEFG | the review's split-line mutant | `NOT APPLIED at 2d5d6be11` (anchor occurs 0 times); killed at `af7eb2d9a`, above |
| F-CR-ELSELEAD | the production route not named the lead | CR `84 checks, 1 failed`, the production-route arm |
| TR-FG | train.sh launch in the foreground | TR `REFUSE: self-test: the stubbed --ignore-red run did not succeed` |
| TR-LEAD | train.sh lead renamed | TR `REFUSE: … a TERMed train did not stop merge_train.py first (alive 0, marks 'G early ', pidfile removed)` |
| TR-RC | `wait "$PR_REAP_LEAD" \|\| rc=$?` → `\|\| :` | TR `REFUSE: … a child exiting 3 left train.sh rc 0, state/rc '0', log 'TRAIN_RC=0'` |
| OP-FG1 | open_pr's first push in the foreground | PA rc=124 (the 900 s timeout) with 9 arms already failed, among them `open_pr: INT reaps the tree too …` and both census arms |
| OP-FG2 | open_pr's second push in the foreground | PA `93 checks, 3 failed`: both census arms and `mutants mut:oplock and mut:unpushed …` |
| UP-FG | update_pr's push in the foreground | PA rc=124 with 7 arms already failed, among them `update_pr: INT reaps the tree too …`, `update_pr: after the stop the lock is free …` and both census arms |
| HP-FG | handoff_push's push in the foreground | PA `93 checks, 3 failed`: `handoff_push: INT reaps the tree too …` and both census arms |
| RM-FG | remerge_main's push in the foreground | PA `93 checks, 3 failed`: `remerge_main: INT reaps the tree too …` and both census arms |
| AP-FG | app_push's prepr in the foreground | AP `197 checks, 2 failed`: `app_push INTed mid-prepr ends within 4 s, not behind prepr (got 'alive', want 'gone')`, `and leaves none of prepr's tree alive (got '3', want '0')` |
| AP-PUSHFG | app_push's own `git push` in the foreground | AP `197 checks, 16 failed`, led by `app_push INTed mid-push, after the mint, ends within 4 s (got 'alive', want 'gone')` |
| AP-MINTTRAP | `MINT_TRAP=caller` commented out | AP `197 checks, 2 failed`: `and leaves none of the push's tree alive (got '3', want '0')`, TERM and INT arms |
| MT-KILL | `Train._run`'s `p.terminate()` → `p.kill()` | MT `221 checks, 1 failed`: `a TERMed train exits 143 and leaves none of its tool's tree alive (R10-PUSHER-REAP)` |

Every applicable row turns its self-test red, and M0 is green. TR-EXEC (train.sh's `exec ` deleted) stays unpinned: equivalent on bash 5.2 (the previous review measured it), kept for macOS bash 3.2.

## Null control

M0 is green on all five self-tests, so each red above is its mutant's. `CR-PRODPATH` (the default command pointed at a missing file) reds only the production-route arm, so that arm alone runs `bash "$HERE/update_pr.sh"`. merge_train's stop arm has a null control (no `stop_on_signal`, tree survives, `left == 3`) that passes, so the arm can see the defect. An unrelated sleeper survives every TERM arm in pr_args (`open_pr: the null control -- an unrelated sleeper survives`).

## Figures

All at `a0cb0cdd7`, origin/main `50808a755`, `PREPR_SKIP_CLOSURES=1`.

**Self-tests:**

| command | result |
|---|---|
| `bash tools/audit/seat/cloud_relay.sh --self-test` | `cloud_relay self-test: 192 checks, 0 failed` |
| `bash tools/audit/seat/pr_args.sh --self-test` | `pr_args self-test: 93 checks, 0 failed` |
| `bash tools/audit/seat/train.sh --self-test` | `train.sh self-test: ok (5 refusals shown, root and options reach the child, no unasked flag, the child's exit is the train's, a stop reaps the tree, merge_train.py first)` |
| `bash tools/pr/app_push.sh --self-test` | `app_push self-test: 197 checks, 0 failed` |
| `bash tools/audit/seat/handoff_push.sh --self-test` | `delivery_row self-test: 5 checks, 0 failed`; `handoff_push self-test: 2 checks, 0 failed` |
| `python3 tools/audit/seat/merge_train.py --self-test` | `merge_train self-test: 221 checks, 0 failed` |

**Launch-mutant harness, CR rows** (`bash dev/audit/harnesses/r10_pusher_reap_launch_mutants.sh HEAD M0 CR-FG CR-FG-BOUND CR-LEADNAME CR-PRODPATH F-CR-ELSEFG F-CR-ELSELEAD`):
- M0: CR `192 checks, 0 failed`; TR ok; PA 93/0; AP 197/0; MT 221/0.
- CR-FG: rc=1, no summary. CR-FG-BOUND: 192/4. CR-LEADNAME: 192/2. CR-PRODPATH: 192/1, the production-route arm alone. F-CR-ELSEFG: NOT APPLIED (its anchor, the split launch, is gone since `788a882d7`). F-CR-ELSELEAD: 192/1.

**#2580's hold mutants** (`python3 dev/audit/harnesses/r10_seat_selftests_mutants.py cloud_relay-1 … cloud_relay-11`): all 11 KILLED, `RESULT survivors=0` (failed arms 1 via a dead stub, 36, 49, 2, 3, 18, 2, 1, 1, 27, 1).

**Gate and ratchet.**
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`; no `*_budgets.json` in the diff.
- `python3 tests/closure.py select --diff origin/main`: `MODE: SCOPED -- 1 script(s) run, 32 scoped out`.
- `ci_predict.py --base origin/main`: `no closures or fast red predicted against 50808a755ce3`. `pr_args.sh --pushers HEAD`: 18 ok, none other. `git merge-tree --write-tree origin/main HEAD` exited 0.
- Rule 3/4: `git diff --name-only 50808a755...HEAD | grep -E 'VERSION|manifest|RELEASE_NOTES|claimed_drift'` printed nothing, rc 1.
- Not re-run here: the scoped `tests/run.sh` gate, `score.py`, `tmp_paths.py`, `throwaway_git.py`, `policy_lint.mjs`. This container has Python 3.11, on which entities.py fails to parse (a 3.12 f-string), as recorded at `2d5d6be11` where the 3.14 gate passed (`ALL 2397 ENTITY CHECKS PASSED`, `5 TEST SCRIPT(S) PASSED`). The merge adds only #2580's files to this diff's base; CI's run on `a0cb0cdd7` is that gate.

## Red checks

From the check-runs API, as recorded:
- `e62be31de` (41 runs): `nightly-status` failure only; `pr-contract`, `closures`, `fast (3.14)`, `mutation`, `instrument-self-tests`, `coverage` success.
- `f99ac55b4` (41 runs) and `a01627177715` (49 runs): `nightly-status` failure only.
- Earlier: `6fd073c9` `PR contract` failed twice (`CodeQL`, `Governance`, `Tests` cancelled by `cancel-superseded`); `50571afa` and `c071fa5f` `PR contract` failed twice each, and `nightly-status`; `9629ae17` `nightly-status`.
- `a0cb0cdd7` has no CI yet; the orchestrator's push is its first run.

Answers:
- `pr-contract` (`6fd073c9`, `50571afa`, `c071fa5f`): the body, not the code — carry_audit refused unrouted items. The cheaper detector, `carry_audit.py check --body`, runs offline in seconds and is run on every body since. The trigger is named; its analysis is `root-cause.md`'s seat.
- `nightly-status` (every head from `50571afa`): it grades main's last scheduled run, which this diff (`tools/` scripts, one harness, `tests/closures.json`, one delivery row) does not reach. No cheaper detector applies to a red this branch did not cause.

## Forward-carry

- #2502's SIGKILL clause ("a TERM, INT, HUP or SIGKILL of a running update must not free the branch lock while its push still runs"): this PR meets TERM, INT and HUP, not SIGKILL — a SIGKILLed run runs no trap, and its lock holder exits within 2 s of losing its parent (`# mut:watch`) while its push may still run. Owed: the holder keeps the lock until the run's former tree is gone, by a drain that waits on a condition, never a fixed window, and passes in a container whose PID 1 reaps late. #2502 stays open; keep `resume.stage` at `in-progress` past #2524's merge. Carry: R10-UPDATE-PR-SIGNALS
- The roster's Revision-12 self-test isolation ("every self-test runs under a timeout in its own process group, reaped on exit") is not built here: it reaches files outside this group, and a process-group kill is a design question against `pr_kill`'s never-a-group rule. Carry: R10-UPDATE-PR-SIGNALS

## Friction

none
