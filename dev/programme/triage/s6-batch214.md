# Proposal triage, session s14, batch 214

Sources: triage queue lines 329 and 330, two OWNER-RULED lines (orchestrator s14,
2026-11-11T20:13:30Z), recorded as P651 and P652. Both are the owner's decisions, ruled by the
owner, not weighed on cost/benefit here; this batch records them and places the work. Line numbers
are at origin/main 61afd4f2db; roster read at handoff/audit-r10-roster 5ab8abe6ea.

Also recorded: the owner ruled on 2026-11-11 (verbatim: "1) A.") that the severity exemption stays
as it is. Rulings P640, P644 and P646 stand, and the question is closed.

## P651: the opener's blockers as one hotfix group

Verdict: ACCEPT, ruled by the owner (tvofi 2026-11-11, "3) make it a hotfix"), as the new hotfix group R10-HOTFIX-OPENER-UNBLOCK (size M, severity high, class hotfix), taking R10-SEAT-IDENTITY-P5 carries 5, 6 and 7.

Source: triage queue line 329. The owner's verbatim words are "3) make it a hotfix". The
orchestrator had described item 3 to the owner as the opener's stale-checkout refusals but labelled
it P603. Its clarification (s14, 2026-11-11) puts both opener blockers in one hotfix:
- BEAT-STALE-CHECKOUT, s6-batch167.md#P581, R10-SEAT-IDENTITY-P5 carry 5;
- OPENER-LIVE-TIP, s6-batch183.md#P603, carries 6 and 7.

Instances (cited, re-measured where local):
- `grep -E '^2026-11-11' open-driver/open-driver.log | grep -cE 'SKIP \S+ \S+ moved'` gives 49
  moved skips. The same day has 70 RESULT lines. Per s6-batch211.md#P643 they fall over 7 topics,
  including a hotfix held 39 min and r10-process-slim-p2 held about 6 h.
- P581 measured STALE CHECKOUT on 8 of 25 opener attempts (32%) from 2026-11-10T09:50Z to
  11T06:12Z. P643 counted 2 of 66 RESULT lines on 11-11. Each was cleared only by a hand rotation
  of the beat's tools checkout; the s14 sweep record shows rotations at 06:12Z, 08:18Z and 11:44Z.

Placement:
- One fixer is sound. The two seams sit in disjoint files: part A in tools/audit/seat/beatd.py,
  with its self-test in `beatd.py --self-test`; part B in tools/audit/seat/open_driver.py and
  open_driver_selftest.py. Both unblock the same actor, the opener.
- Size M, as two S seams. The brief carries the three carry texts verbatim, with their figures and
  controls.
- R10-SEAT-IDENTITY-P5 carries 5, 6 and 7 are marked moved to the new group by `--match`.
- A hotfix is not held by the open-PR cap.

Cost: one M hotfix fixer and review (opus), in three instrument files.

Binding: owner ruling.

## P652: CI queue priority, built in

Verdict: ACCEPT, ruled by the owner (tvofi 2026-11-11, "6. Do it, it is already decided and should be built in"), as a carry on R10-CI-PRIORITY-PAUSE, reopened from refused to not-started, with tools/pr/cancel_superseded.py and tools/audit/seat/beat_jobs.py added to its files.

Source: triage queue line 330. The owner's verbatim words: "6. Do it, it is already decided and
should be built in, no critical path, outside or hotfix PR should wait in CI queue." A local version
has run since 20:20Z: a seat cancels the queued runs of non-priority PRs while a critical-path,
hotfix or outside PR has a run queued, and re-runs them afterwards. It never cancels the PR the
train waits on.

Instances:
- $HPO_STATE_DIR/s14/sweep.md:611 (2026-11-11T20:12:02Z): 77 runs queued and 9 running, and
  #3455's review run queued for 31 min.

Placement, existing groups first:
- R10-FLY-CANCEL-SWEEP owns tools/pr/cancel_superseded.py. It is done (#3004), so it cannot
  receive the carry.
- R10-CI-PRIORITY-PAUSE is this exact seam, from the owner's directive of 2026-10-28: pause the
  lowest-priority PR's CI when the account's job limit binds. #3004 left it as its part 2, and it
  already holds the tier carries (P267/P268).
  - Its stage is `refused` by the keep test (2.7% of main CI wall, s6-batch136.md#P428). The
    owner's ruling now overrides that keep test, so the group reopens to not-started.
  - Both its after-edges are done: R10-TICK-LEVELS and R10-OUTSIDE-FIRST.
  - Its files gain tools/pr/cancel_superseded.py, and tools/audit/seat/beat_jobs.py, which holds
    the beat's cancel-sweep row (:83, :522).
- No new group is needed. The owner directs that the build starts and that priority PRs never
  wait, so the open-PR cap does not hold it; the orchestrator dispatches it as a priority group.

The measure the PR must report: the minutes a priority PR's first job waits in the queue, before
and after. Before is 31 min (#3455's review run, 20:11Z, 77 queued and 9 running).

Cost: one M instrument group, already sized on the roster, plus one carry.

Binding: owner ruling.

The carry, as queued:

> CI-QUEUE-PRIORITY-BUILT-IN, owner ruling (tvofi 2026-11-11T20:13Z, verbatim: "6. Do it, it is already decided and should be built in, no critical path, outside or hotfix PR should wait in CI queue."), reopening this group from its 2026-11-08 keep-test refusal (triage P652). Build into the beat's cancel-sweep row (tools/audit/seat/beat_jobs.py cancel-sweep, :83 and :522) and tools/pr/cancel_superseded.py the rule the session's local seat has run since 2026-11-11T20:20Z: while any critical-path, hotfix or outside pull request (classes read from the roster through roster_lib, this group's tier mapping) has a workflow run queued, cancel the queued runs of non-priority pull requests and re-run them once no priority run is queued; never cancel a run of the pull request the merge train is waiting on, nor a run already in progress, nor a main-branch run. Print one line per cancel and per re-run naming the PR, the run and the priority PR that caused it. Self-test: a queued priority run plus a queued non-priority run cancels the non-priority one and re-runs it after; the train's PR is never cancelled; null control: no priority run queued cancels nothing; mutation proof: dropping the priority check makes the null control cancel. Measure in the body: minutes a priority PR's first job waits queued, before and after, with the before figure re-measured at the merge base (31 min was measured for #3455's review run at 2026-11-11T20:11Z, 77 queued and 9 running); carry no count.
