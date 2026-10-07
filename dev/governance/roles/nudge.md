# The orchestrator nudge

This file binds a Cursor orchestrator on grok and a Cursor orchestrator on qwen. Any other agent uses it as the reference for a timer, a heartbeat, and one turn's scan. The role contract is `tools/audit/briefs/orchestrator.md`. This file is the turn that contract names.

Run the numbered steps every turn, in order. Do not stop the turn on a log line, a pending check, or a sentence that names work nobody is doing.

A live timer may add three things, and only for that session: a dated owner mandate, seat identifiers that must not be resumed, and one pull request held open. Re-measure those. They are not copied here, because a date and a seat id in this file outlive the session that measured them.

This programme keeps seat worktrees under `/Users/timmalmstrom/hpo-seats`. A reader on another machine substitutes the root its own dispatch names. The same substitution applies to the state mirror and the sync scratch named below.

## Who writes, and what stays shut

You dispatch fixers, reviewers, and root-cause seats. You post verdicts, approve, merge, stamp, and update the roster, the state docs, and issue #201. Do not hand the orchestrator role to a seat.

Opus seats that die are replaced by a new Task on grok-4.7-high. Do not resume a dead Opus agent. Sonnet seats use cursor-grok-4.6-high. Haiku seats use composer-2.5.

Pull requests are authored by the hpo-author App through `tools/audit/app_push.sh`. The login that reads GitHub is tvofi. The hpo-approver App posts verdicts. A code-owned path needs a tvofi review citing the session mandate. `tools/audit/app_approve.sh` refuses those paths. A merge verdict on a path that is not code-owned is approved with that script. A record pull request that only touches `docs/delivery` is not code-owned. The ruleset still requires one approving review, so that record pull request is approved as tvofi and then merged.

Do not push `main` with the deploy key. Do not merge with the admin flag. Do not edit `VERSION`, the manifest version, or the `RELEASE_NOTES.md` heading except through `tools/release/stamp.py`. A merge message must not close #201. Write `Leaves #201 open`. Never the negated form. Do not run a full `tests/derive_closures.sh` off Darwin. Use that script's single-script mode. Touch a claim file only when the branch is claiming drift. Compare a branch with three dots, never two. Run the train under `python3 -u` so its log is not block-buffered.

A timer subscription dedupes by name and answers created false without replacing the prompt. Unsubscribe first, then subscribe. Do not call the two together.

`--ignore-red` replaces the train's default ignore list, so name both `nightly-status` and `delivery-status`.

## 1. Verdict and handoff

Each turn, run `tools/audit/seat/bus.sh` watch once, and also fetch every open pull request head and every live `handoff/<topic>` ref. Watch-once prints only a ref that moved. A handoff already printed is still owed.

For each open pull request, test whether the head contains the handoff tip. If it does not, run `tools/audit/seat/update_pr.sh` this turn when a prepr slot is free and that group's fixer worktree was not written in the last 15 minutes. Run `tools/audit/seat/open_pr.sh` when no pull request exists. If the push or the open refuses and no fixer is working, dispatch the fixer in this same turn. A fixer worktree with unpushed commits and no process is that handoff, not a new fixer.

When the update exits 0, the printed HEAD contains the handoff. Dispatch the reviewer for that HEAD in the same turn. Do not end on a reviewer who waits. If required checks are still pending, leave the merge. The reviewer is still owed.

When a review ref moves, confirm and post that verdict this turn when it names the contained head and carries its nonce. A verdict on an ancestor is not a verdict on this head. A blocked fix review returns to the original fixer in that same turn. Do not repair the body yourself. Do not spawn a new seat for that repair. The same reviewer takes the next round. Do not update a head whose reviewer worktree under the seat root was written in the last 15 minutes.

## 2. Reviewer owed

This check uses the live head, not the bus line. For each open pull request whose head contains the fixer handoff, if the newest posted fix review does not name that 40-hex head, dispatch a reviewer this turn. A fix review of an ancestor is not a review of this head. Do not wait for required checks. Do not dispatch a reviewer for a pull request whose title starts with `record:`, or for a head a fixer is still changing, or when a reviewer worktree for that pull request was written in the last 15 minutes. Do not start a second reviewer for a group that already has one. Before calling a seat stalled, read `tests/gate_lock.py`. A seat that holds the lease is not stalled.

## 3. Train status, before any merge

Find a live `tools/audit/seat/merge_train.py` and read its log. A live process holds every other merge. Do not merge by hand, do not arm auto-merge, and do not load a second train. An empty log, or a last line still on the ci step, is that one pull request's CI wait. Write the line and continue the scan. Do not end the turn on the train log.

`TRAIN DONE` means that queue finished. Do not reload it. `TRAIN STOPPED` names the pull request, the step, and the reason. Later entries were not graded. Do not reload that queue. A head that does not contain `origin/main` after the ci step is the one restart the script names: run the train again on the pulls it had not merged. Do not restart a queue whose entries are already merged.

Load a new train only when no train is running, fewer than four preprs are running, and at least two open pull requests are verdicted for the train. Verdicted means the newest posted fix review is merge for this 40-hex head, or `tools/audit/app_approve.sh` carry says the verdict carries. The train waits for CI in its own ci step, so do not wait for required checks to go green before loading. Order the queue by creation time, oldest first. Each entry carries the pull request number, the 40-hex the merge verdict names, the comment id (the comment must cite an absolute evidence path), and the issues the body intends to close.

Leave off the train: a change to a `*_budgets.json` file, a policy path as `policy_lint.mjs --corpus-filter` defines it, and a `record:` pull request. One remaining pull request is not a train. Merge it directly. There is no `tools/audit/merge_train.py`. The instrument is `tools/audit/seat/merge_train.py`. Never pass `--allow-red`.

The command is detached, because a background waiter dies at two hours:

```
python3 -u tools/audit/seat/merge_train.py run <queue.json> --mandate "<the session mandate cite>" --ignore-red nightly-status --ignore-red delivery-status
```

## 4. Required checks

Required checks are the contexts in ruleset `main-protect-checks`. Read that ruleset every turn. The id last used to open it was 23698884. Re-read it. Do not trust a remembered list. `nightly-status` and `delivery-status` are not required. Pending is not a pass. DIRTY is the claim-file merge GitHub cannot run. Absorb `main` locally with the claimnotes driver. Conflicting or DIRTY is not ready.

## 5. Budget files

A `*_budgets.json` change never goes on the train. Merge a budget-file pull request by a mandate approval already on that head, oldest first, only when no train is running. A new head that raises a budget needs a new tvofi review citing the session mandate. A decrease is still a budgets file. Merge it directly, not on the train.

## 6. Record pull requests

A pull request whose title starts with `record:` does not need a fix review. Once required checks are success or skipped and the train is not waiting, approve it as tvofi and merge it. Do not dispatch a reviewer for it. A session overlay may name one record pull request to leave open. That hold is the overlay's, not this file's.

## 7. Direct merge, when no train is running

Before loading a train, direct-merge what step 3 leaves off the train and what is alone: a `record:` pull request the overlay does not hold, a budgets-file pull request whose mandate review is already on that head, and a single verdicted pull request. Ready means required checks are success or skipped, GitHub reports the pull request mergeable, and either the title starts with `record:` or the newest posted fix review is merge for this head or carries. Oldest creation time first. A fix review of an ancestor does not make this head ready. Two or more verdicted pull requests that step 3 allows are the train, not a series of hand merges.

## 8. Prepr slots

This machine runs up to four `prepr.sh` at a time. A seat's own prepr counts. `tools/audit/seat/open_pr.sh`, `tools/audit/seat/update_pr.sh`, and `tools/audit/app_push.sh` each count as one. Do not start a fifth. Do not recarry a branch a seat is writing. Skip a group whose fixer or reviewer worktree was written in the last 15 minutes, or whose own prepr is running. Recarry may run during a train's CI wait. It may not run while the train itself is in recarry. Do not start the train when four preprs are already running.

## 9. Conflicting or DIRTY

Run `git merge-tree --write-tree origin/main <head>` first. Exit 0 and no train running: merge `origin/main` and push with `tools/audit/app_push.sh`, then `tools/audit/approve_held_runs.sh`. A content conflict stops. Name the path and return it to the fixer who owns the branch. Do not resolve it yourself. Use `tools/audit/merge_fastpath.py` only when no train is running.

## 10. A refusal with nobody on it

If a push or an open is refused and no fixer is working on that group, dispatch a fixer this turn. Do not leave the refusal for a later nudge. Do not start a second fixer for a group that already has one working. When you see yourself stating that work needs to be done and no seat is doing it, dispatch or perform that work in this turn.

## 11. Stalled runs, autofix, and a red main

Zero check runs is stalled zero-runs. Run `tools/audit/approve_held_runs.sh` after every App push. CodeQL on a tools-evidence diff is `tools/audit/seat/codeql-triage-poll.sh`, not a new fixer. Read the autofix summary before dispatching a fixer. `changed` means wait for the bot commit. `skip-failed-recording` means fix the script and do not re-derive. `skip-manual-repair-owed` means closures failed and the job was not under-scoped, so no bot commit is coming and the check itself is the repair. `skip-clean` means the check passed and no bot commit is coming. A selectable script with no recording is not under-scoped: add it to a derive lane or record it alone. A red Tests run on `main` outranks the queue. Revert a merge that reddened `main` only when that diff can reach the failure. Never pass `--allow-red`.

## 12. After each merge

Run `tools/audit/worktree_gc.sh` with the owner and repo as its one argument. Post one #201 comment through `.claude/workflows/gh_comment.py` and require a byte-identical read-back. That comment is not a heartbeat. Run `tools/audit/seat/roster_edit.py` set-stage only when the pull request belongs to a roster group. Run `tools/audit/seat/state_docs.py` with its push flag and the mirror at `/Users/timmalmstrom/hpo-orch/state`. The state docs are not the handover. Only a decision-changing merge owes `docs/HANDOVER.md` an updated-for line, in its own pull request. After a roster update, an open issue the plan does not name is scheduled, deferred, or refused. Do not file a new issue. Issues a session has already deferred stay deferred. The overlay names them.

## 13. Stamps

Run `tools/release/stamp.py` only when no train is waiting, the roster's stamp-unblock group is done, and the latest Tests run on the current `origin/main` is green. Not during a CI wait. A push-triggered green Tests run is not a nightly. `nightly-status` reads the last concluded schedule or workflow_dispatch on `main`. Do not rerun a push-triggered Tests run and call it the nightly. A dependabot alert the overlay names stays open. Do not force an override the overlay forbids.

## 14. Handed-off seats

Do not resume a seat the session overlay names as handed off. A later refusal on another group still gets a new seat. Do not start a second fixer or reviewer while that group's worktree was written in the last 15 minutes.

## 15. CI watch

Each turn, read the required contexts from ruleset `main-protect-checks`, as step 4 says. For every open pull request, take the latest check run of each required context on the head oid. A conclusion of failure returns that pull request to its original fixer this turn, with the job URL and the failure line. `tools/audit/seat/ci-watch.sh` alerts only on a new signature and then exits. A red it already printed is still owed, so the signature file is not this check. Do not return a pull request for `nightly-status` or `delivery-status`. Pending is not a return. Zero check runs is stalled zero-runs: `tools/audit/approve_held_runs.sh`, not a fixer. Read the autofix summary before returning a closures or mutation failure, under the same words as step 11. Do not start a second fixer when that group's fixer worktree was written in the last 15 minutes. A pull request the overlay holds is not returned by this step.

## 16. Unblocked groups

Load the roster through `tools/audit/seat/roster_lib.py` at the ref `tools/audit/seat/state_docs.py` defaults. A group whose resume stage is not-started, whose after-edges are all done or absent, and which the roster does not list as deferred or refused, gets a fixer this turn when no fixer is working on it. Brief it that group's own brief from the roster. A deferred group stays deferred. Done stages are the pair `roster_lib.py` names.

## 17. State

When the roster or the open pull-request set changed, run `tools/audit/seat/state_docs.py` with its push flag and the mirror at `/Users/timmalmstrom/hpo-orch/state`. That regenerates the plan table, the resume, and the next-session prompt on the plan ref that script writes. It is not `docs/HANDOVER.md`. Fetch `origin/main` at the start of the turn and measure how many commits `HEAD` lacks. An ancestor checkout is not current.

## 18. After the merge, and the instruments

After each merge, read which issues the merge commit closed. Reopen one the message did not name as intended. A carry is `tools/audit/app_approve.sh` when its carry predicate holds. `tools/audit/merge_fastpath.py` reporting the head eligible is the only bypass of a fresh CI wait after `main` moves. Never clear a live gate lease. `tools/audit/preflight.sh` reads the body on stdin. A filename argument reads nothing and prints clean. Run each instrument from its path in the tree, `tools/audit/seat/` or `tools/audit/`, never from a scratch copy. If no sync loop is running, start one detached with `tools/audit/seat/wt_sync.sh` and the scratch at `/Users/timmalmstrom/hpo-orch`. Do not start a second.

A background update that has exited 0 since the last turn is that notification: dispatch the reviewer for its printed HEAD before ending. A required check that failed since the last turn is the same kind of notification: return that pull request to its fixer before ending.
