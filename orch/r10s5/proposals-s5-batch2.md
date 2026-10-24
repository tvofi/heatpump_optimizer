# Orchestrator proposals, s5 batch 2 (for proposal triage; number from P34)

Each item: what happened, evidence to read (local first), candidate change. Defect countermeasures that policy already routes are excluded.

## A. Train reads `ci red=[]` while a required context is red
- run3 logged `#2665 b859929d ci red=[]`, then spent merge attempts 1-8 on "base branch policy prohibits the merge"; `pr-contract` was FAILURE at that head (job 120583698954). Evidence: ~/hpo-orch/r10s5/train/run3/train.log lines 30-45; merge-report.txt 18:32:27Z line.
- Candidate: the merge step re-reads required contexts at the head before `gh pr merge` and SKIPs naming the red one, instead of 8 blind retries (~40 min of train time spent).

## B. state_docs.py beat dies on a transient fetch ref-lock race
- beat crashed `cannot lock ref 'refs/remotes/origin/train-hold'` (concurrent fetch in the shared orch-wt) and stayed down ~17:49Z-18:05Z; #2666 went unrecorded meanwhile. Same race refused a roster op at 17:10Z (roster-report.txt). Evidence: ~/hpo-orch/r10s5/state-beat.log traceback; roster-report.txt 17:10Z.
- Candidate: retry the fetch once or twice on `cannot lock ref` in roster_edit.run / state_docs beat_pass; or a beat that survives a failed pass instead of exiting.

## C. `--free-holders` does not free a worktree whose head is an ancestor of the branch tip
- Instance 1: run3 parked #2669, holder ~/.local/state/hpo/pr/r10-policy-lint-family/wt at 48dbc2c8 (ancestor of origin 8734cdd1). Instance 2: run5 skipped #2664, holder train/run4/wt/2664 left by a stopped train. Evidence: run3/skipped.json, run5/skipped.json, merge-report.txt 17:51:06Z.
- Candidate: free a clean holder whose HEAD is reachable from the remote branch (same rule the manual cleanup used), not only one at the exact tip.

## D. replan.py crashes on roster size XS
- `KeyError: 'XS'` at tools/plan/replan.py build_plan; durations.json `sizes_hours` has S/M/L/XL; six live roster groups are XS (R10-FLY-WORKTREE-GC, -DAEMONIZE-ARGV, -CIPREDICT-LAYOUT, -CLOUD-SETUP-TOOLCHAIN, -YIELD-GUARD, -ENVMATRIX-NOREMOTE). roster_edit.py accepted them. Evidence: `python3 tools/plan/replan.py --repo . --seats 7 --out /tmp/p.json` at roster f17570752.
- Candidate: one size vocabulary shared by roster_edit.py's validator and replan.py (refuse XS at edit time, or price it in durations.json).

## E. replan.py ignores merge-verdicted, queued groups
- plan.json schedules R10-FLY-RELAY-REVIEW-FF and R10-POLICY-LINT-FAMILY in the final batch at 2026-10-30, though both hold `Fix review: merge` and sit in the merge queue. Evidence: ~/hpo-orch/r10s5/plan.json batch 55.
- Candidate: replan reads verdict state (bus confirms) or a resume stage for "merge-queued" so the page reflects them. Benefit may be display-only: triage on that.

## F. A body's `## Red checks` misses a red the diff makes its own (delivery-status on a tests.yml diff)
- #2665's body said `none`; `pr-contract` refused it in CI after a full run. The exemption rule (defect-root-cause.md: diff touches what the check reads) is computable from the diff alone. Evidence: #2665 pr-contract job 120583698954; body_patch at 18:40Z.
- Candidate: prepr.sh / body_patch.sh warns when the diff touches a grading check's inputs and the body does not name that check. Check whether `policy_lint.mjs --pr-body` already has the inputs.

## G. Verdict items without `Carry:` markers park a merge-verdicted PR at pre-flight
- run4 parked #2670: review comment 6371729358 has 2 finding items with no valid Carry marker; the reviewer seat returned merge and nothing caught it before the train. Evidence: merge-report.txt 18:34:32Z; `python3 tools/audit/carry_audit.py pr 2670`.
- Candidate: bus.sh push-verdict (or confirm) runs carry_audit over the verdict text and refuses an unrouted item, so the reviewer fixes it in-seat.

## H. carry_audit `pr` audits superseded verdicts; no tool edits an approver comment
- After #2670's verdict was re-taken (comment 6372641454, 0 unrouted), `carry_audit.py pr 2670` still reported the superseded round-2 comment 6371729358's 2 items unrouted, so the train would park it again. The cure (owner-approved 2026-10-23T19:10Z) was a one-off approver-token PATCH appending the two markers, read back identical (len 4570, sha 65c6ae34). Evidence: ~/hpo-orch/r10s5/patch-6371729358/{orig.md,new.md,patch.sh}.
- Candidate: carry_audit skips a verdict comment superseded by a later verdict at the same head on the same PR; or app_comment.sh gains a `patch` verb with the same refusals.

# Next batch (s5 batch 3)

## I. sweep_template.md step (3) tells the orchestrator to run train.sh itself
- Contradicts orchestrator.md section 5 ("Four standing seats do the routine work, never you inline") and the owner (2026-10-23T19:42Z: merges are the merge seat's). Steps (2), (4) and (6) likewise name inline work the dispatch and roster seats own. Evidence: tools/audit/seat/sweep_template.md steps 2-6; ~/hpo-orch/r10s5/seat-ledger.md "Sweep overrides".
- Candidate: the template routes each step to its standing seat as queue lines.

## J. pulse.py's seat-queue format is tied to one harness's session queues; make it harness-neutral
- `pulse.py --seat-queue` expects `<epoch> <text>` lines that the seat removes when it acts, which is likely the Claude Code desktop session's queue convention. This session runs in Cursor, where the orchestrator-written seat queues have their own per-seat formats: merge-queue.txt's leading PR number was read as an epoch (57 years old), so seat-merge showed STOPPED, and queues with comment lines showed UNREADABLE. Evidence: the first pulse at 19:39Z in this session; the pulse-*.txt workaround recorded in seat-ledger.md.
- Candidate: one harness-neutral, documented seat-queue contract that every standing seat and pulse.py share (for example, each queued item carries its enqueue time and an id, and the seat records completion in its report rather than deleting lines), plus a liveness signal any harness can write (the `<seat>.alive` mtime). Then pulse judges the same files in Claude Code, Cursor, Codex or ZCode, and no session needs a shadow file.

## K. roster_sync marks a multi-PR group done when any one of its PRs merges
- 2026-10-23T20:08Z: R10-CI-LAYOUT-P2 went in-progress -> done "at 5056615a28b8 (PR #2638 MERGED)" while P2b (#2662 / the p2b-v2 re-cut) was unmerged; that unblocked R10-FLOW-MQ-PROBE falsely, and roster_sync then REFUSED a carry to the group as done. Same shape as R10-FLY-RELAY-REVIEW-FF at #2664 (carries open). Evidence: state-beat.log lines 306-308; roster 90543361f.
- Candidate: done only when no open PR or unmerged handoff ref answers for the group, or stage done only by an explicit set-stage for groups that declare several PRs.

## L. roster_edit.py has no op for `files` or `resume.pr`
- 2026-10-23 17:10Z and 21:1xZ: R10-LIVESTATE files widening (accepted at design) refused twice: no op writes `files`. 20:4xZ: `resume.pr` for R10-CI-LAYOUT-P2 refused (only roster_sync derives it). Evidence: roster-report.txt.
- Candidate: `set-files add|remove` op behind the same lint gate; `resume.pr` stays derived (roster_sync), but roster_sync must map a fix/<topic> PR to handoff/<topic>.

## M. record-autofix opens a new record PR after every record merge (chain)
- 2026-10-23: #2653 merged 22:3xZ -> bot opened #2676 (22:31Z); #2676 merged 22:47:53Z -> #2677 opened minutes later. Each carries the previous record PR row plus its own self-row, so the chain never ends and ruleset_cutover.py queue-drained can never pass without closing one.
- Candidate: the record PR row for a record-autofix PR is written in the same PR (self-row with merge resolved at stamp), or record-autofix skips opening a PR whose only rows are record-autofix PRs.
