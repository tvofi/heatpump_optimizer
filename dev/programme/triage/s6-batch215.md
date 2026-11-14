# Proposal triage, session s14, batch 215

Sources: triage queue lines 331 to 333, three PROPOSAL lines (orchestrator s14,
2026-11-11T20:48:09Z), ruled as P653 to P655. Line numbers are at origin/main 61afd4f2db.
Roster read at handoff/audit-r10-roster 5700990bac. All three accepted parts are carries on
existing groups, so the open-PR cap does not bear on them.

## P653: merge_pr.sh re-posts a verdict the bus already posted

Verdict: ACCEPT part (b) as a carry on R10-GATE-DEFER-BARRIER; REJECT part (a), the host-path claim (refuted: the Evidence line is the sanctioned home-relative form).

Source: triage queue line 331.

Instances:
- $HPO_STATE_DIR/s14/sweep.md:629, `WORKAROUND 20:40Z merge s14-7: #3355 stray verdict comment
  6805392170 (posted by my merge_pr.sh try ...) patched via gh_comment.py patch to the body of
  verdict comment 6783731829 ... so newest verdict matches tip aad4f556`.
- tools/audit/seat/merge_pr.sh:272-273 copies the evidence directory's VERDICT.md, appends
  `Evidence: <path>/` when the text does not name the directory, and posts it through
  app_comment.sh. It runs before the merge, and nothing first reads whether the bus already
  posted a verdict for this head. A try that then fails leaves a newer verdict comment whose text
  differs from verdict/<pr>'s tip, which merge_train.py:3190 refuses ("the newest posted
  verdict (comment N) is not verdict/<pr>'s tip").
- Part (a) is refuted. The path is written by `ref_privacy.py path`, which makes it
  `~/<rest>`, the form the tool documents for posted text (ref_privacy.py:5). body_refusal
  passes it, and its self-test at ref_privacy.py:837 pins exactly that
  (`evidence: ~/.zcode/bus/...`). Publishing `~/...` paths is today's policy, not a leak.
  Changing that would be a ref_privacy policy proposal of its own.

Measure: $HPO_STATE_DIR/merge_pr/v holds 8 verdict files, which is every merge_pr.sh post under
this state dir, and one of them did harm. The owner restricted merge_pr.sh to deadlocks and the
critical path (sweep.md:613, ruling 5), so the harm falls on the pull requests where a stall
costs most.

Basis: severity-exempt defect repair (medium) only. On the 20% bar alone it would be REJECTed:
it is one instance in 8 uses, with a one-call workaround.

Destination: append-carry on R10-GATE-DEFER-BARRIER (medium, not started). It is the open group
that lists tools/audit/seat/merge_pr.sh. The seat is the verdict post, beside that group's
gate-reader arm. Text:

> MERGE-PR-NO-REPOST (triage P653). tools/audit/seat/merge_pr.sh:272-273 always posts the
> evidence VERDICT.md (plus an `Evidence:` line) through app_comment.sh before it merges, even
> when the bus has already posted that verdict for the head. A try that then fails leaves a newer
> verdict comment that is not verdict/<pr>'s tip text, and `merge_train.py add` refuses the PR
> (merge_train.py:3190). Instance: #3355, comment 6805392170, 2026-11-11T19:33Z, cured by hand
> with a gh_comment.py patch.
> Repair: before posting, read the PR's newest posted merge verdict with the same reading the
> train's add check uses. When that verdict is for this head, post nothing and print
> `ALREADY POSTED: comment <id>`. Post only when no verdict for the head is posted. Keep the
> Evidence line's `ref_privacy.py path` form unchanged.
> Self-test (merge_pr.sh's offline flow): with a posted verdict for the head, there is no
> app_comment.sh call and the merge proceeds. Null control: with no posted verdict, it posts as
> today. Mutation proof: dropping the read makes the first arm post.

## P654: zombie workflow runs that refuse cancel

Verdict: ACCEPT parts (1) and (3) as two carries on R10-CI-PRIORITY-PAUSE; DEFER part (2) (the fresh-run step) until a zombie at a live PR head is shown permanent.

Source: triage queue line 332.

Instances:
- $HPO_STATE_DIR/digest/jobs/cancel-sweep (written 21:46Z) has 12 lines. These are six pairs of
  `gh api .../runs/<id>/cancel rc=1: ... not in progress. (HTTP 409)` and `could not cancel
  <id>`, for 42810088662, 42810088912, 42817922694, 42818706376, 42955031956 and 42961218591.
  The ids match the proposal's.
- tools/pr/cancel_superseded.py:222-228 POSTs a cancel for every planned id on every pass and
  keeps no memory of a 409. beat_jobs.py:83 runs it every 600 s, and beat_jobs.py:518-527
  reports each `could not cancel` line as a job failure.
- $HPO_STATE_DIR/s14/seat/ci-priority/FINDINGS.md:3-5: the local shim ran 20:15Z to 20:42Z,
  cancelled 21 queued non-priority runs, and `priority_queued stayed 19 to 20`. GitHub completed
  about 2 runs per hour, so the cancels freed no runner. sweep.md:619 (20:22Z) shows 37 of the
  queued runs were main `Gate sweep` runs, which the shim's rule never touches.
- Part (2) is not established. FINDINGS.md:5-6 list the #3441, #3458, #3451, #3469, #3442 and
  #3428 runs as not completed about 30 minutes after a cancel on a saturated account. It also says
  "queued cancels did not take effect on a saturated account" and (:8) "rerun refused 'already
  running' ... their status turned queued again, so a run existed". A cancel still pending on a
  saturated queue is not shown to be a permanent zombie. Only the ten-day Hassfest run and the
  six sweep ids are long-lived, and the proposal does not show those at a live PR head.

Measure, part (1): one sweep pass costs 1 PR listing, 5 run listings, one commit read per PR
with something to cancel, and one POST per cancel (cancel_superseded.py:39-42). The six refused
POSTs, and their commit reads, are at least 6 of at most 18 calls, about 33% or more of the
pass's REST calls. That is 864 refused POSTs a day at the 600-s cadence. It is over 20% on REST
calls per pass, and it is a medium-plus defect repair as well.

Measure, part (3): 21 cancels drained no priority run (0%), and the reruns turned 10 spooled
verdicted pull requests red (proposal; FINDINGS.md:3 lists the cancelled PRs). Carry 4 of
R10-CI-PRIORITY-PAUSE specifies that cancel rule. A measured defect in an accepted carry's design,
on a high, owner-directed group, is severity-exempt, and the measured result is the reason.

Destination: two append-carries on R10-CI-PRIORITY-PAUSE (high, not started), which lists
tools/pr/cancel_superseded.py and tools/audit/seat/beat_jobs.py. Texts:

> CANCEL-SWEEP-ZOMBIE-MEMORY (triage P654 (1)). tools/pr/cancel_superseded.py:222-228 POSTs a
> cancel for every planned run on every pass. Six runs (42810088662 42810088912 42817922694
> 42818706376 42955031956 42961218591) answer HTTP 409 "Cannot cancel a workflow run that is not
> in progress" on every 600-s beat pass (beat_jobs.py:83). That is 12 failure lines in
> digest/jobs/cancel-sweep and at least a third of the pass's REST calls.
> Repair: record a run that answers 409 while it is listed active in a state file under
> $HPO_STATE_DIR (id, first-seen time). Skip it on later passes without a POST or a commit read.
> Print it once as `cancel_superseded: zombie <id> (409, not retried)`, and count zombies in the
> CANCEL-SWEEP summary line. Do not count a known zombie as a failure in beat_jobs.py's
> cancel_sweep filter (:523-524). A run that is gone from the active listings drops out of the
> file.
> Self-test: a 409 answer is recorded and the next pass makes no POST for it. Null control: a
> non-409 failure (rc 1, HTTP 500) is retried on the next pass. Mutation proof: dropping the
> record makes the second pass POST again.

> CI-PRIORITY-NO-VERDICT-CANCEL (triage P654 (3)), amending carry 4 (CI-QUEUE-PRIORITY-BUILT-IN)
> with the local shim's measured result (s14 ci-priority FINDINGS, 2026-11-11 20:15-20:42Z). 21
> cancels of queued non-priority runs drained no priority run: priority_queued held at 19-20, and
> GitHub completed about 2 runs per hour. The cancels and reruns also turned 10 spooled verdicted
> pull requests red. 37 of the queued runs were main `Gate sweep` runs, which carry 4's rule
> exempts.
> The build must: (i) never cancel a run of a pull request that holds a posted merge verdict at
> its head, or that is in the merge train's queue or spool, as well as the train's current PR;
> (ii) prefer holding to cancelling, which means starting no rerun or dispatch of a non-priority
> PR's CI (the train and merge_pr unstale reruns, rerun helpers) while a priority run is queued,
> and cancelling a queued run only where the body's before/after measure (carry 4) shows that
> cancelling shortens a priority PR's queued wait; (iii) report in the body which share of the
> queue is main-branch runs, because they decided the shim's zero.
> Self-test: a queued run of a verdicted spooled PR is never cancelled while a priority run is
> queued. Null control: a non-verdicted, non-spooled queued run is handled as carry 4 says.
> Mutation proof: dropping the verdict check cancels the verdicted run.

Re-raise trigger for part (2): a run at a PR's live head still not completed 2 hours after its
cancel, while the account has queued runs below its job cap, with rerun refused. Then the
fresh-run step (workflow_dispatch of ci.yml with pr and base, as the autofix jobs do) is
ACCEPTable as a carry on R10-CI-PRIORITY-PAUSE. Until then, moving the head is the workaround.

## P655: the merge train keeps a skipped entry's worktree on its branch

Verdict: ACCEPT form (a) as a carry on R10-TRAIN-RESIDUE-P2 (the train releases a skipped entry's recarry worktree at the skip); REJECT form (b) (update_pr.sh detaching the train's worktree).

Source: triage queue line 333.

Instances:
- $HPO_STATE_DIR/s14/sweep.md:625, `#3464 handoff d9ab65e9 NOT applied: update_pr BUSY (exit 75
  twice; branch checked out in merge_train/wt/3464)`. :628, `WORKAROUND 20:39:18Z detached the
  train's clean worktree wt/3464 ... (train skipped #3464 on conflict)`. :632, applied at
  20:44:25Z.
- $HPO_STATE_DIR/train/current.log: `SKIP #3464 recarry: main does not merge without a
  resolution`. That log has 55 `recarry:` skips in total.
- merge_train.py:2512-2525 adds the recarry worktree on the branch (`worktree add -B`) and
  appends it to made_wts. release_worktrees (:2895-2906) removes made_wts only before the run's
  closing line. skip (:3681) does not touch the worktree, so a skipped entry's branch stays
  checked out until the train ends.
- update_pr.sh:64-67 detaches another instrument's clean worktree only under its own state
  prefix `$P/` (:44, `$HPO_STATE_DIR/pr`). A train worktree is outside it, so :69 exits 75 BUSY.
- Not a duplicate. --free-holders (merge_train.py:1705) frees OTHER holders for the train's own
  recarry, the opposite direction. R10-FLOW-BODY-PATCH carry 0 and the exit-75 carry (P2/P22)
  made the train's hold a retryable BUSY. Neither releases it at a skip.

Measure: one instance, a critical-path repair blocked about 25 minutes (20:15-20:39Z), with two
one-shot seats spent. A worktree is held after every recarry skip (55 in the log), but a block
needs an update to arrive while the train is still running.

Basis: severity-exempt defect repair (medium) only. On the 20% bar alone it would be REJECTed.
It is one measured instance.

Why (a) and not (b): the instrument that made the worktree owns its release (release_worktrees'
own rule). If update_pr.sh detached a worktree a live train may still be using, it would act on
another instrument's working state while that instrument is running. A skip ends the train's use
of that entry, so releasing at the skip is sound and needs no cross-instrument rule.

Destination: append-carry on R10-TRAIN-RESIDUE-P2 (medium, in progress, files merge_train.py).
Text:

> TRAIN-SKIP-RELEASES-WORKTREE (triage P655). merge_train.py's recarry adds a worktree on the
> entry's branch (:2512-2525, made_wts). release_worktrees (:2895) removes it only before the
> run's closing line. So after `SKIP #N recarry` (skip, :3681) the branch stays checked out until
> the train ends, and update_pr.sh for that PR exits 75 BUSY (update_pr.sh:69; its detach rule
> :64-67 covers only $HPO_STATE_DIR/pr). Instance: #3464 (critical path), 2026-11-11 20:15-20:39Z,
> two BUSY exits, cured by a hand detach.
> Repair: when an entry is skipped, release that entry's worktree if this run made it (it is in
> made_wts), with release_worktrees' rule: `git worktree remove`, never forced. Log
> `released <wt>` or `NOT released <wt> (...)`, and drop it from made_wts. A queue entry's own
> `worktree` is never touched.
> Self-test: a recarry skip with a clean made worktree removes it and logs `released`. Null
> control: a skip of an entry whose worktree came from the queue entry leaves it. Mutation proof:
> dropping the release leaves the branch checked out after the skip.
