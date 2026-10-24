FIXER SEAT O14 (round 10, part of #201, mandate 6175172275). Topic r10-tick-drivers-2. ORDER: after #2390 (R10-TICK-DRIVERS) merges; cut from main after it.
Items (each with failing test first, mutation proof, re-measured at your merge base): the full list with tests is /Users/timmalmstrom/hpo-seats/r10s3/finding-sweep/fold-R10-TICK-DRIVERS.txt — L03, P55, P57 (prepr.sh), L04, L05, L-T1 (orchestrator_tick.py), P02 (plan_table/resume_doc/handover_prompt RosterNotFound), L12 b/c (ci_predict.py). Split into two PRs if >5 findings or >400 lines: (A) prepr.sh + ci_predict.py, (B) orchestrator_tick.py + roster readers.
Heavy lanes to CI (orch/heavy-to-ci.txt). Push refs only (handoff_push.sh / body_push.sh); no GitHub writes; worktree under /Users/timmalmstrom/hpo-seats/r10s3/O14/; stop only PIDs you started. Each body names `Carry:` destinations for anything it leaves.

From O11 (carry_audit):
FOLD for tools/audit/seat/orchestrator_tick.py (O11, carry-forward enforcement). Not edited by O11:
handoff/r10-tick-drivers is in flight on this file. Fold into that branch, or into the first tick
change after it merges. Source: O11 branch seat/r10-carry-enforce, tools/audit/carry_audit.py.

WHAT: a carry sweep the tick runs once a week and at round closure (not every tick: it costs one
`gh api` call per PR plus one per open issue).

1. A flag `--carry-sweep N` on main()'s parser (beside --roster-ref, about line 2707): when it is
   given, the tick runs, in this order:
     python3 -I tools/audit/carry_audit.py --roster-ref <roster-ref> [--roster-ref <second ref>] \
         --briefs-dir "$HPO_BRIEFS_DIR" sweep --last N --issues
   <roster-ref> is the tick's own --roster-ref (default origin/main). When the tick knows a roster
   branch (handoff/audit-r<N>-roster, roster_lib.round_branch), pass origin/main FIRST and that
   branch SECOND: the drift lines then name every carry or brief text main holds that the branch
   lacks, which a roster PR cut from the branch would revert with no conflict (sweep row L18).
2. Report: the sweep prints `UNROUTED`, `BAD-DEST`, `ISSUE-UNOWNED` and `ROSTER-DRIFT` lines and
   two summary lines, `CARRY-AUDIT: ...` and `CARRY-SWEEP: ...`. The tick puts both summary lines in
   its report and, when the sweep exits 1, a dispatch line "carry sweep: <k> unowned finding(s);
   route each (Carry: line, roster carry, or O-brief)" -- the orchestrator owns the routing.
3. Self-test arm: a fake runner returning one `ISSUE-UNOWNED` line with rc 1 yields that dispatch
   line; the same with rc 0 and no lines yields none (null control).
4. Cadence: the orchestrator's weekly sweep and the round-closure checklist call
   `orchestrator_tick.py --carry-sweep 40`. Forty covers about a week of round-10 merges (#2345 to
   #2388 merged in about two days, record PRs included); re-measure from the merge rate, do not
   carry the figure.

Measured on the O11 branch (2026-10-18): `sweep --issues` printed 6 ISSUE-UNOWNED (#2389 #2381
#2378 #2353 #2331 #2253; with $HPO_BRIEFS_DIR set, #2331/#2353 are owned by
O10-rca-friction-2331-2353.md); `--roster-ref 64b1f82a3 --roster-ref b29cd8d23` printed the six
drift lines of L18, the same ref twice printed none.
- 14:22Z FOLD O14: open_pr.sh refuse missing ## Head with named error, not traceback.
- 15:05Z FOLD: tick reports 'plan republish owed' when handoff/audit-r10-roster moves; plan generator scratch gen.py -> fold into tools/audit/seat/plan_table.py (ETA + live roster ref).
- 17:15Z FOLD O14 (recurring, 3x today: p5, O11, roster-unwire): open_pr.sh leaves ~/.local/state/hpo/pr/<topic>/wt behind; a re-open dies 'already exists'. Fix: open_pr removes or reuses its own clean worktree; refuses only if dirty. Recurring -> RCA trigger reached (3rd instance).
- roster_edit refuses host paths at write time (found 2026-10-18 when #2384 went red on ref_privacy). Run ref_privacy.refusal on the incoming value (edit-brief/append-carry/set-resume/append-group, after @file expansion), or on the dumped roster text before write_text, which covers every op. Add a self-test arm.
- roster_edit trap: a second edit-brief before the first is pushed starts from the remote ref and silently drops the first edit. Refuse when the local roster worktree is ahead of the remote, or edit from local.
- The tick reports POST-MERGE OWED for any merged PR that has no #201 comment (the #2365 beat was missed when its train finished unattended).
