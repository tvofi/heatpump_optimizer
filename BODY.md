R11-PRE-RELAY-REBUILD part 2 of 3 (owner card P12, 2026-11-13): roster carries 5-9. Carries 0-4 landed in part 1 (#3648). Carries 10-12 are part 3, dispatched at this handoff, and none is answered here.

- **Carry 5 (RELAY-NOBODY-OWED, P611 arm 2).** `noreturn_arm` counted any moved code ref as a return. It now owes a fire whose `handoff/` or `handoff-wip/<topic>` moved after the dispatch tip, with no `handoff-body/<topic>` commit newer than that tip, once the newest such code commit is older than `HPO_RELAY_NOBODY_SECS` (new knob, default 3600, above the healthy p90 of 48 min that P611 measured). It prints `cloud_relay: SEAT NO BODY <topic> (<code ref> <tip12>, <age>min old, no handoff-body/<topic> since dispatch <sha12>): <owed>` and writes `OWED <utc> seat-no-body <dispatch ref> <sha> NO BODY <topic> <code ref> <tip12> <age>min: <owed>` to `<log>.level`, rewritten every pass. `<owed>` is `continuation owed (fire <sha12>)`, or `carry fold pending` when the wip's BLOCKED.md names CARRY-LANDED alone. That predicate is now one helper, `blocked_kinds`, which `carry_fold_arm` reads too. A fire is read once it is older than either bound, so a fire under the 7200 s no-return bound still owes its body. `seat-no-body` is a ledger kind. The RCA lands as `dev/audit/rca/R10-RCA-FIXER-NOBODY-STALL.md`. Its source, the root-cause seat's queue line 295, is out of tree and unreadable from a cloud seat, so the file assembles the analysis the tree records (triage P611, P617, batch 209) and says so. Host paths and session ids are dropped (`ref_privacy.py body-lines` rc 0).
- **Carries 6 and 7 (R10-UPDATE-PR-SEAT-WORKTREE).** `update_pr.sh`'s own-worktree loop now takes every worktree on `$BR` under the state dir (`$PR_STATE/`), not only `$P/` (`$PR_STATE/pr`). Both guards stay: the worktree is clean, and its HEAD is an ancestor of `origin/$BR`. A worktree outside `$P/` gets a third guard, `pr_cwd_free` (pr_args.sh): no live process has its cwd inside it, read with `lsof -a -d cwd -Fn` as worktree_gc.sh's cwd-inside read does. A live process prints `BUSY: ... a live process stands in it`, and an unreadable or empty lsof prints `BUSY: ... lsof could not be read`, each exit 75. The instruments page is updated. Carry 6's precondition, the two holders' paths taken from the orchestrator, was not met: a cloud seat cannot reach the orchestrator's host, and neither PROMPT.md nor the comms inbox carried them. Carry 7 names the seat worktrees' shape, `$HPO_STATE_DIR/<session>/seat/...`, which the widened loop covers. `remerge_main.sh` takes its worktree from its caller, so the tree does not say where the merge seat's scratch worktree lies. A holder outside the state dir stays BUSY, as today. Widening past the state dir without a measured holder would detach worktrees of unknown owners, so it is not done.
- **Carry 8 (verdicts during an update; owner card P12).** `handoff_arm` now waits on `update_pr.sh` through `update_wait`. While the update runs, every `HPO_RELAY_INFLIGHT_SECS` (default 60, digits only, else 60 with a line saying so) it runs `probe_arm` again, and `confirm_arm` too under `--confirm`, printing `cloud_relay: IN-FLIGHT #<pr> ...`. A verdict that returns during an update is therefore relayed and posted without waiting for the rest of it. That was R10-RELAY-ARM-ORDER's deferred residual. The update's exit status is still `wait`'s. The bound line and the merge-conflict no-retry are carry 10, in part 3.
- **Carry 9 (tick_loop self-test moving its checkout's HEAD).** This was fixed on main before this part's base: `1fba05ec35` and `2057964baa` merged as #3520 (R10-HOTFIX-TICK-SELFTEST-CHECKOUT, merge `ad95665ea3`). The cause, in `1fba05ec35`'s message: the TICK-GH rows ran `bash "$0" --once` before `HPO_TICK_CODE_DIR` pointed at a scratch dir. `fresh_check` therefore read the caller's checkout. A detached checkout behind origin/main was moved by the restart arm, and a branch printed an extra TICK-STALE. Re-measured at both ends (`## Figures`). The self-test pins it (`nest` rows: branch, detached, GIT_DIR), so nothing is built here.

Alternatives not taken, and why each lost:
- Carry 8: run the update detached and return from the pass. That needs a second lock owner for `relay-tools.lock` and for the reap lead, and it moves part 3's bound line into a process the pass no longer waits on. The in-wait arms keep one process and one reap tree.
- Carry 8: run updates concurrently, one per branch. The branch locks exist, but the shared levelled tools tree (`relay-tools.lock`) is single. That is a larger change than this carry, and part 3's own brief owns it.
- Carry 5: key the no-body line on the ledger's `no body ref` with a shorter `AGING_DEFAULT`. That ages every kind the ledger holds, not only fires.

## Head

`ea72dbb682f24d253c028199636a0cae6ef0a3bb`. All figures were measured 2026-11-16 18:00Z to 19:20Z at the commits named beside them, against `origin/main` `30f9caac90735c402c8e3ae60fbaa80c45dc6d26` (the merge base). `git merge-tree --write-tree origin/main HEAD` reports no conflict.

prepr: passed rc=0 at ea72dbb682f24d253c028199636a0cae6ef0a3bb

## Mutation proof

Each `cloud_relay.sh` mutant is applied by `perl -0pi` in its own worktree at `a066d3a480`, and the file's self-test is run there. Failing rows:

- `mut:nobodyowed` (the no-body predicate made `false`): 6 FAIL. `code without a body at 61 min owes: SEAT NO BODY names the topic, the code tip, its age and the owed fire`; `and it is seat-no-body on the level, where the tick reads it`; `a body older than the fire is not a return: handoff-wip code with no body since the fire owes`; `a CARRY-LANDED-alone BLOCKED.md on handoff-wip names the pending fold, not a continuation`; `null control: a BLOCKED.md naming no CARRY-LANDED refusal owes a continuation`; `a fire 4000 s old (under the no-return bound) whose code is 61 min old owes its body`.
- `mut:nobodyfold` (the CARRY-LANDED comparison never matching): FAIL `a CARRY-LANDED-alone BLOCKED.md on handoff-wip names the pending fold, not a continuation`.
- `mut:noreturnage` (the age gate back to the no-return bound alone, the base's): FAIL `a fire 4000 s old (under the no-return bound) whose code is 61 min old owes its body`.
- `mut:inflight` (the in-flight arms line deleted): 3 FAIL. `a verdict returned during an update is not held behind it: the probe arm runs while update_pr is still running (P12)`; `and the pass says so: IN-FLIGHT #41`; `under --confirm the confirm arm runs in flight too, so a relayed verdict is posted during the update`.

`update_pr.sh`'s mutants run inside its own self-test (`pr_args.sh`'s `seatwt` rows), each a passing row at the head:

- `mut:seatwt` (the scan back at `$P/` alone, the base's): `that worktree keeps the branch and the run is BUSY (the defect)`. This is carry 7's demonstration: BUSY on the base, the push reached on the fix.
- `mut:seatcwd` (the cwd guard made `true`): `the worktree is detached under the live process`.

## Unpinned sites

The diff adds one `.py` production line outside `tests/` and `dev/`: the `seat-no-body` key in `ledger.py`'s `KINDS`. Its deletion is killed by `ledger.py --self-test`'s census `every kind cloud_relay.sh writes is a ledger kind`, which prepr step 6d runs as `MUTANT_CMD`.

## Null control

- Carry 5: code 59 min old with no body is silent (`null control: code 59 min old with no body is silent`). A body 30 min after the code is silent. `HPO_RELAY_NOBODY_SECS=7300` silences the 2 h-old rows and empties the level. On live refs the base copy prints `no_body=0` (`## Figures`).
- Carry 8: an update shorter than `HPO_RELAY_INFLIGHT_SECS` runs no in-flight arm. Without `--confirm` the confirm arm does not run in flight. A failed update is still owed `handoff-update`.
- Carry 7: a live process's cwd in the seat worktree keeps it BUSY and on its branch. So does a commit origin lacks, and so does an unreadable lsof (each a self-test row).
- Carry 9: the head end of its measurement is the null control (`moved=0`).

## Figures

- `bash tools/audit/seat/cloud_relay.sh --self-test` at `a066d3a480` (cloud_relay.sh is unchanged after it): `cloud_relay self-test: 535 checks, 0 failed`.
- `bash tools/audit/seat/update_pr.sh --self-test` at `ea72dbb682`: `delivery_row self-test: 6 checks, 0 failed` and `pr_args self-test: 275 checks, 0 failed`, rc 0. At `e40cd48f81` the same run printed `pr_args self-test: 275 checks, 2 failed`, on the cwd and unreadable-lsof rows: `update_pr: STOPPED: line 76 exited 1`. The cwd guard's non-zero return tripped update_pr's STOPPED trap. `ea72dbb682` reads it in an `||` context.
- `python3 -I tools/audit/seat/ledger.py --self-test`: `ledger self-test: 108 checks, 0 failed`.
- `bash dev/audit/harnesses/r11_relay_nobody_replay.sh` (this tree's `noreturn_arm` against the live refs) at 2026-11-16T18:37Z: `RESULT no_body=10 no_return_fixer=0`. With a worktree of the base `30f9caac90` as the argument (`<base worktree>/tools/audit/seat/cloud_relay.sh`), at the same minute: `RESULT no_body=0 no_return_fixer=0`. The refs move, so the counts are a reading. The rule is the harness's own: a `SEAT NO BODY` line per fixer dispatch whose code is past the bound with no body since it. The 10 at the head include a CARRY-LANDED stop read as `carry fold pending` (r11-pre-no-read-builders).
- Added reads per pass, rule: `git for-each-ref` over the fetched `dispatch/fixer-*` tips, those aged 3600-172800 s against those aged 7200-172800 s. At 2026-11-16T18:29Z: 47 against 43, so 4 more `git ls-remote` calls a pass, and no GitHub API call.
- Carry 9: a detached worktree of the repository at `fc2a7edcf2` (`1fba05ec35`'s parent, 39 commits behind origin/main on `SELF_PATHS`), running `bash tools/audit/seat/tick_loop.sh --self-test` in it: `rc=1 moved=1` (HEAD went from `fc2a7edcf2` to origin/main `30f9caac90`), `tick_loop self-test: 30 checks, 4 failed`. The same at `1325b217e0` (holds the fix, 1 commit behind on `SELF_PATHS`): `rc=0 moved=0`, `tick_loop self-test: 48 checks, 0 failed`. The recipe: record `git rev-parse HEAD`, run the self-test from the worktree, then compare HEAD.
- The scoped gate: `python3 tests/closure.py select --diff 30f9caac90` prints `MODE: SCOPED -- 2 script(s) run, 31 scoped out` (`tests/doc_claims.py`, `tests/entities.py`), both rc 0 (`ALL 2723 ENTITY CHECKS PASSED`). The run_always lines are rc 0: `tests/env_drift.py --claims-only`, `tests/closure.py selftest`, `tests/layout.py`, and `tests/harness_headers.py` (`ALL 115 HARNESS HEADER CHECKS PASSED`). `python3 tests/structure.py` rc 0.
- `python3 tools/pr/ci_predict.py --apply-inert` applied `inert_reads tests/harness_headers.py: dev/audit/harnesses/r11_relay_nobody_replay.sh`, then printed `CI PREDICT: no closures, fast, governance or instrument red predicted`.
- Carry 8's class seams. The rule: every synchronous subprocess a pass runs after the probe and confirm arms, enumerated by `awk '/^self_test\(\) \{/{exit} {print NR": "$0}' tools/audit/seat/cloud_relay.sh | grep -nE 'wait "|update_pr.sh|body_push.sh|carry_fold.py|approve_held_runs|bus.sh" dispatch|failure_logs'` and read past its comment lines. Each one returned, with its disposition:
  - `update_pr.sh` (handoff arm): closed in this diff (`update_wait`).
  - `approve_held_runs.sh` and `bus.sh dispatch` (handoff arm, after an update): single `gh` calls. They hold a pass for seconds, not the measured stalls (36-94 min). Left as they are.
  - `failure_logs.sh` (owed red text, carry-fold arm): one `gh` read per newly judged (wip, body) pair, memoed. Left as it is.
  - `carry_fold.py` and `body_push.sh` (carry-fold arm): a body check per fold, run after the handoff arm, not an update. A verdict returning during it waits at most until the next pass's probe arm, which runs before any update. Bounded by one pass, and left as it is.

## Red checks

none

## Brief carries

Roster carries of R11-PRE-RELAY-REBUILD, by position. Carries 0-4 landed in part 1 (#3648), and carries 5-9 are built or answered here, as above.

- Carry 5: built (`noreturn_arm`, `seat-no-body`), and the RCA landed.
- Carry 6: built as carry 7's loop. The holders' paths were not available, and the body says why the scope stays at the state dir.
- Carry 7: built, demonstrated BUSY on the base by `mut:seatwt`.
- Carry 8: built (`update_wait`).
- Carry 9: closed before this base by #3520, and re-measured at both ends here. Nothing built.
- Carries 10-12: part 3 of this group, dispatched at this handoff.

## Forward-carry

none

## Friction

none
