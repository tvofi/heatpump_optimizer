
## N. tick_loop's built-in cloud_relay pass races the dispatch seat's update_pr
Measured s5: three #2675 update refusals (23:15Z, 00:30Z, 00:51Z), from `tick_loop.sh` running `cloud_relay.sh pass --confirm` each 300 s with a body built before the fixer's re-body. Each held the branch lock and BUSY'd dispatch's correct run. Proposal: the relay skips any handoff whose branch has a live update_pr lock or a newer handoff-body ref, and `tick_loop` takes a --no-relay flag (or reads the session's cloud-seat count) instead of the env-var override HPO_TICK_RELAY=/usr/bin/true used here.

## O. queue_pre_flight's findings arm refuses a PR that adds its own carry file
Measured s5: #2675 parked in run16 (02:06:48Z), `#2674 has no owner ... no dev/programme/carries/carry-2674.json`, though the PR head 2845e545 adds that file and CI `pr-contract` (carry_audit at the merge ref) is green there. Cause: `queue_pre_flight.py` line 196, `ca.load_dests(self.checkout, "origin/main")`, globs `dev/programme/carries/` in the train's checkout (main), not the PR's merge tree. finding-propagation.md routes a carry to a stage with no live group INTO this file, so every such PR is refused. Proposal: load_dests unions carry files from `git ls-tree <head> dev/programme/carries/`; control: #2675's head refuses before and passes after, and a body citing a carry file in neither main nor the head still refuses. Workaround used: a `direct` merge_pr.sh line under the mandate.

## P. brief_lint does not lint a roster group's `carry` strings
Measured s5 by the #2683 fixer: a carry string with a planted nonexistent symbol, in a scratch roster copy, gave `brief_lint.mjs` 0 errors. brief-citations.md says the linter lints each group's brief and each carry FILE; carries appended to a group's `carry[]` array (the main route for live groups) are unchecked, so the roster seat's lint gate passes stale or wrong citations. Proposal: lint `carry[]` entries with the brief rules (tag citations resolve at the tag). Control: the planted symbol refuses, and the current roster passes or lists its real errors.

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

## Q. Cloud seat pools: claim-ref routines instead of one routine per seat
Measured s6 (2026-10-24 07:46-07:56Z): each per-seat RemoteTrigger create+run echoes the full payload three times (~5k orchestrator tokens per seat); a pool routine (persist off) whose short prompt claims the next line of POOL.txt on dispatch/pool-s6 via an atomic `claim/s6/<topic>` ref push fired 8 fixers at ~2.5k tokens each, and a reviewer pool (dispatch/rpool-s6) the same. Cost: blocked verdicts cannot return to the same session (pool runs are not persistent); claim refs need pruning; the pattern lives only in session scratch. Proposal: make it an instrument (cloud_dispatch.py `--pool` publishing POOL.txt + claim protocol, prune_refs rule for claim/*, INSTRUMENTS.md entry). Instances: /Users/timmalmstrom/hpo-orch/r10s6/seat-ledger.md 07:52Z and 07:56Z lines.

## R. Standing seats end their turn after one pass
Measured s6: the haiku tick and dispatch seats and the sonnet merge/roster seats each ended their first turn with a nohup'd or untracked watcher, so nothing woke them; each needed an orchestrator SendMessage to resume (s6 07:49Z-08:00Z, four instances). Proposal: a tracked loop helper in tools/audit/seat/ (e.g. `seat_loop.sh <alive-file> <window-end> -- <pass cmd>`, run_in_background-friendly) named in the standing-seat contracts' Restart lines.

## S6-S (08:55Z, orchestrator) — barrier for the class "P2b assembly: a reader meets a sibling unit's change"
Four instances in one day: bd0d4d603, 69a26d2a2, 168365196, plus ci-ratchet run-name (RCA handoff/r10-rca-ci-ratchet-run-name 776d37392, state (d)). Under the audit-class rule, three or more instances owe a barrier, not a refusal. Each unit's gate passed because the premise changed in a sibling unit.
Candidate: an assembly-time check that re-runs each unit's self-test against the assembled tree, or an "API-shaped stub from the live tree" convention. Triage: cost/benefit; add a bugclasses.json entry either way.

## S6-T (09:35Z, tvofi steer: "the gate lease does not apply to cloud")
open_pr.sh and app_push.sh re-run prepr locally under the 4-slot gate lease, even for a cloud fixer's handoff that already ran prepr in the cloud. At 09:30Z all 4 slots were held by open prepr runs, and the critical-path ratio-anchor open queued behind them.
Candidates:
(a) open_pr accepts the cloud fixer's prepr evidence at the exact code SHA (a prepr-tree stamp on the handoff-body ref) and skips the local prepr, as app_push's RECARRY skip already does for a clean re-merge.
(b) The opener's prepr runs in a cloud routine, not locally.
CI's gate remains the authority either way.
Triage: cost/benefit. Fold into R10-FLY-OPENPR-ATOMIC if accepted.

## S6-U (orchestrator, 2026-10-24 ~12:58Z): tick's owner-gated line over-fires
Source: tick.txt REPLAN: "38 group(s) blocked on owner disposition -- surface them to the owner". orchestrator_tick.py:1804-1823 counts every open group whose `owner_gate` field is non-empty.
Instances: on handoff/audit-r10-roster f596fd3c4, 29 of the 38 cite a mandate (16 cite 6175172275, 6 cite 6319294694, 6 cite 6329234399, plus 1 more), and 5 more are code-owned, policy or budget gates that the mandate in force (6329234399, scope all) covers. Only R10-FLOW-MQ-PROBE ("owner decision after the probe") needs tvofi's own decision. Command: `git show origin/handoff/audit-r10-roster:dev/programme/rosters/wave-r10-groups.json | python3 -c '<count owner_gate over non-done groups>'`.
Proposal: the tick counts a group as owner-blocked only when no mandate in force covers its gate, reusing budget_raise_gate's mandate reader, which the tick already imports. That cuts the line to the real owner items.
Cost: about 15 lines in orchestrator_tick.py plus one self-test arm.
Triage: cost/benefit. If accepted, the destination is an existing tick or flow instrument group.

### Ruling S6-U (triage, 2026-10-24): ACCEPT
Benefit: the REPLAN line fires every tick with 38 groups where about 1 is real, so it trains the orchestrator to ignore it or spuriously surfaces to the owner. Cost: about 15 lines plus one self-test arm in one file, reusing an existing import; no API calls added, no standing CPU. Binding: low cost, measured instance; guard is that a mandate that is revoked or out of scope must still count. Destination: R10-ORCH-BEATD, carry carries/carry-triage-s6u.md.

## S6-V (orchestrator, 2026-10-24 ~13:25Z): recurring slips today, each a proposal to prevent recurrence
Owner directive (tvofi 2026-10-24): every recurring slip is filed here and ruled on cost/benefit, risk and code complexity.
- V1 stale pool claims → POOL EMPTY runs (3 instances: #2692/#2697/sav-comfort). Candidate: the pool prompt treats a claim older than N min with no handoff move as reclaimable; or cloud_dispatch publishes a claim-reset with each pool line.
- V2 hidden push errors (`2>/dev/null` on the POOL push; 1 instance, cost 2 lost runs). Candidate: a tracked pool_push.sh (append, push, read back, refuse on mismatch).
- V3 seat-owned background jobs killed at rotation (roster app_push rc=143; 1 instance, cost one PR cycle). Candidate: briefs/seat contract say long pushes run under daemonize.py, never as a seat's own background task; or app_push self-detaches.
- V4 two writers on one queue/branch across a window rotation (roster w5/w6, #2698 fixer vs update; 2 instances). Candidate: a per-seat lock file (flock) the standing-seat brief takes before applying queue lines.
- V5 carries routed to done groups (3 instances today plus 38 audit candidates). Already being made permanent as R10-ROUTING-INVARIANTS; triage the consumed-vs-pending marker design when the remediation seat lands it.
- V6 fake liveness (a detached toucher; 1 instance). Candidate: liveness read from the seat's own log mtime, not a touch file.

### Rulings S6-V (triage, 2026-10-24)
- V1 ACCEPT (narrowed): 3 instances, each a lost run. Clear a stale claim ref in cloud_dispatch when it appends the pool line (null control: a claim with a moved handoff stays). Reject the "reclaimable after N min" prompt variant: it puts a timing heuristic in a routine prompt and races a live fixer. Cost: ~10 lines in one existing script. Carry carry-triage-s6v1.md -> R10-FLY-CLOUD-SETUP-TOOLCHAIN.
- V2 ACCEPT (folded into V1): same script, ~5 lines (stop discarding stderr, read back). Reject a new pool_push.sh: a new file for one call site. Same carry.
- V3 DEFER: 1 instance. app_push self-detaching adds process-management code to a hot instrument (reject). Would change the answer: a second kill; then one line in the seat contract, owned by R10-FLY-DAEMONIZE-ARGV.
- V4 DEFER: 2 instances, no measured cost beyond one PR cycle. A flock named in a brief binds only a seat that remembers it, and rotated seats do not share a process. Would change the answer: a third instance; then queue lines consumed by atomic rename to a .inflight file (enforced in the roster/merge queue readers, not in prose).
- V5 DEFER per directive: judge the consumed-vs-pending marker design when R10-ROUTING-INVARIANTS lands.
- V6 DEFER: 1 instance, cause was a rogue toucher already killed. A log mtime is as forgeable and an idle polling seat writes no log. Would change the answer: a second fake-liveness instance; then pulse.py reads the seat process's elapsed CPU/children instead of a file.

### Amendment S6-U (triage): ACCEPT OVERTURNED to DEFER
Window 3's P54 shows the null control fails: owner_gate is free prose and R10-FLOW-MQ-PROBE cites a mandate id yet needs tvofi, so "mandate cited = covered" silences the one real item. Carry carry-triage-s6u.md deleted and its queue line removed; sound form is a structured gate field owned by R10-ORCH-ROSTER-SCHEMA.
- V7 (13:33Z) fire-owed-fixer sent with no pool line (r10-ratio-anchor, CP; caught by main before firing). Same class as V1/V2: pool state not verified at fire. Candidate: cloud_dispatch --role fixer appends the pool line itself and prints "pool read back OK" as its fire line.
- V7 ACCEPT (folded into V1/V2, P55): 1 instance, caught by hand on a critical-path fixer. Marginal cost is about 5 lines reusing the V2 read-back in the same script; refuse-to-fire when the pool line is absent. Same carry file.
- V8 (13:50Z) record beat: the tick finds a #201 record by searching the FULL merge sha; my comments cited short shas, so 10 merges read unrecorded although commented. Plus HANDOVER.md updated-for is 2030 commits behind main (writing-for-agents: updated per merge). Candidate: a tracked record_beat.py that posts the #201 comment with full shas via gh_comment.py and refreshes HANDOVER updated-for in the record PR, called by the merge seat after each merge.
- V9 (13:52Z) pr-contract goes RED (tools/ci/codescan_wait.py exit 1) while codeql Analyze is still in_progress on a fresh head, and gate fails "still being judged"; 3 instances today (#2698 3383fb2a, #2704 04860ee0, #2706 ea459c0b), each needing a hand rerun and misread by the tick as "Red checks unanswered -> back to fixer". Candidate: codescan_wait waits/re-queues instead of failing (or reports neutral), and the tick classifies these as WAIT via merge_train classify, not owed.
- Re-rule P50/P55 (triage): REOPEN P50 as ACCEPT. The pool ran all day with no tracked code and caused V1, V2, V7 (5 instances, one on a critical-path fixer); P50's cost estimate (M) was for the full protocol, the instrument needed is S (pool.py: append+readback, stale-claim clear, fire refusal). New group R10-FLY-POOL-INSTRUMENT, brief carries/brief-pool-instrument.md. Old v1 carry removed from the queue.
- V8 ACCEPT narrowed -> new group R10-FLY-RECORD-BEAT (S), brief carries/brief-record-beat.md: record_beat.py posts the #201 comment with the full sha resolved from git. HANDOVER updated-for refresh DEFERRED: no check reads it (2030 commits stale, nothing failed); measure first.
- V9 ACCEPT -> R10-CI-LAYOUT-P2 (owns codescan_wait.py), carry carry-triage-s6v9.md. It IS a red-check root-cause trigger (3 instances, a cheaper detector: the in-progress state was knowable): dispatch root-cause now; process state (b) ordering race, countermeasure is the wait itself.

- V4 recurrence 2026-10-24T14:07:45Z: dispatch w14 reported completion while background work was still running; w15 was started and both were live, so two dispatch writers existed. Stopped w14 with TaskStop. Candidate countermeasure: before starting a replacement seat, require the old seat's task to be killed (seat-rotate helper).
- V4 re-rule (triage): ACCEPT narrowed. Three instances now, so under the audit-class rule a barrier is owed. A seat-rotate helper that kills the old task is REJECTED: killing is an agent-tool action (TaskStop), not scriptable, so the helper would be prose. Accepted form: a generation token (seat_gen.py bump/check) that the tracked queue writers check before writing, binding the old seat without killing it. Cost S, one script plus a check call in each tracked writer. Carry carries/carry-triage-s6v4.md -> R10-ORCH-BEATD (owns seat liveness).

- V10 2026-10-24T14:15:31Z: update_pr.sh refused #2734/#2735 ("branch checked out elsewhere") because the triage seat's worktrees held the branches. Same shape as the train's holder problem, which merge_train --free-holders already cures. Candidate: update_pr.sh gets the same --free-holders (detach a clean, pushed holder).
- V10 ruling (triage): ACCEPT narrowed -> R10-FLY-OPENPR-ATOMIC (owns app_push.sh). app_push detaches the clean, pushed worktree after opening, which removes the class for every opener seat; update_pr.sh --free-holders is REJECTED (it detaches a worktree another seat may be using). Cost XS, about 6 lines plus a self-test arm. Carry carries/carry-triage-s6v10.md; the ruling P64 goes in the next batch file (s6-batch5 is already open as #2735, so it rides a follow-up).
