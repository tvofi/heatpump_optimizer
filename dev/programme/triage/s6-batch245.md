# Proposal triage, session s14, batch 245

Source: orchestrator order of 2026-11-12 to triage seat s14-72 (three proposals). Standing owner
rulings applied: the closure test on every ACCEPT (P718); R10-OUTSIDE-CONTRIBUTOR-CYCLE and outside
work first (P719); owner-approved study decisions built now when they do not move closure (P734).

## P739: open_pr.sh re-renders a body's figure blocks at the head it pushes

Verdict: ACCEPT
Source: seat s14-69's defect note and local patch (s14-69/NOTE.md and
s14-69/open_pr-figure-refresh.diff, uncommitted, against origin/main).
Instances: `tools/audit/seat/open_pr.sh` writes the PR body once from handoff-body/<topic>:BODY.md
and never runs `tools/pr/figure_block.py refresh`. A figure block names the head it was rendered
at, so pr-body lint refuses p1 after a main merge and always refuses p2, whose row commit moves the
head. Seen on R10-OUTSIDE-DISINFECTION-SETPOINT part 2: the opener was refused twice and PR #3495
was opened and auto-closed after its p2 refusal (s14-69/NOTE.md). `open_pr.sh --self-test` runs
only delivery_row.sh's and pr_args.sh's self-tests, so no case covers the p1/p2 body path: it
passed before and after the patch (s14-69/NOTE.md).
Cost: one S fixer part, about 25 changed lines in open_pr.sh (s14-69 diff: 2 hunks, 7 added
lines) plus a self-test case. A body with a figure block then runs the full prepr at p2 instead of
the row-only skip (the refreshed body differs past the `## Head` note); a body without a block
keeps the skip. No capped file named; the fixer reports structure.py and `--budgets` rows.
Binding: an outside product group's PR cannot open while its body carries a figure block; outside
work outranks all else (P719).
Destination: new group R10-HOTFIX-OPENPR-FIGURE-REFRESH, class hotfix, kind instrument, size S,
severity high, sonnet fixer, opus reviewer, files tools/audit/seat/open_pr.sh, after none. Overlap
on open_pr.sh with R10-SEAT-SCRIPT-OUTPUT (in-progress, PR #3490) is admitted by seam: this group
touches only the p1/p2 body-render points. Build: (1) refresh before p1 when the merged head
differs from the code head, refusing with nothing pushed on failure; (2) refresh before p2 at the
row head, always, closing the PR with the reason on failure; (3) a self-test case with a figure
block in the body. Null control (s14-69/NOTE.md): a figure-block body opens with p1, p2 and the row;
the mutant without the p2 refresh is refused at p2 with "figure-block scope-line names another
head"; a body with no block still prints `ROW-ONLY: prepr SKIPPED`. (4) the rerun hazard the same
open hit: a closed-after-p2 open leaves branch fix/<topic>-pr and a detached worktree that make
the next `git worktree add -b` fail; the re-run removes or reuses them. Keeping row-only for a
figure-block-only re-render is optional, not owed.
Closure: needed by an outside group's opener (DISINFECTION-SETPOINT part 2), so it is on the
outside path and enters round 10; size S on a non-binding lane. Not measured by replan; main runs
the replan on dispatch if it wants a number. Machinery bar: severity high skips the 10% keep bar.
Figure against 20%: not applicable (defect repair).

## P740: R10-ROUND-PLAYBOOK-FINAL's brief names the protection census and B1

Verdict: ACCEPT
Source: orchestrator order; analyst s14-68's study reconciliation (s14-68/study-reconciliation.md
lines 79-85, 115).
Instances: B1 (product-only required set: on an all-product `pr-cc` diff, briefs, policy-docs and
wave-script become advisory; blueprints/ joins the product predicate) reaches 12 of 118 product
merges, 23 of 118 widened (study line 81). Chained after the census it is measured at no closure
move (B1 11-14T10:58Z, closure 11-14T18:32Z, study line 105) but is not recommended in round 10 on
risk: line-citation reds move from PRs onto main's push gate, landing about 30 min before the last
product merge (study lines 80, 85).
Cost: one `edit-brief` op; no new carry, no group, no critical-path time.
Binding: the census result (R10-PROTECTION-CENSUS, P737) must reach the round-11 intake, and B1
needs a named home.
Destination: `edit-brief R10-ROUND-PLAYBOOK-FINAL` appending one paragraph: (a) the
R10-PROTECTION-CENSUS result is an input to the README's round-11 list and its intake baseline;
(b) B1 is a round-11 opening item, conditional on the census, unless the owner orders it into
round 10. This narrows P737's sentence "if the census supports it, B1 is ordered for round 10".
Owner visibility: P734 (owner, about 08:20Z) builds now what does not move closure, and B1 was
measured not to; its round-11 placement rests on risk, not date. The orchestrator surfaces that to
tvofi; an owner order puts B1 in round 10 as an S group after the census.
Closure: no move (a brief edit). Severity normal. Figure against 20%: not applicable.

## P741: A1 and A2 are built by parts of their existing groups

Verdict: ACCEPT
Source: orchestrator order; P738 (batch 244) kept both carries in round 10.
Instances (roster at 1af7ce7552): A2, TRAIN-WAIT-CAP-OUTAGE, is R10-TRAIN-RESIDUE-P2 carry 20,
open; the group is carries-open after part 1 (PR #3470, be86e36a56), size S, after
R10-TRAIN-RESIDUE (done). A1, MAIN-CANCEL-BOUNDED, is R10-CI-PRIORITY-PAUSE carry 7, open; the
group is not-started, size M, after R10-TICK-LEVELS and R10-OUTSIDE-FIRST (both done).
Cost: no new group, no new carry, no roster op from this ruling.
Binding: none beyond P738.
Destination: A2 rides R10-TRAIN-RESIDUE-P2's next part with open carries 0-4 and 20; carries 21
and 22 are queued moved to R10-ROUND-PLAYBOOK-FINAL (queue lines pending, see below) and must land
before that part is dispatched, or its fixer receives them as open. A1 rides R10-CI-PRIORITY-PAUSE's
first part with its open carries; carry 8 is queued moved (pending). Both groups are dispatchable
now; dispatch is the orchestrator's act.
Closure: A2 restored to TRAIN-RESIDUE-P2 measured no move (P2 finish 11-13T21:27Z, study line
101). A1 was measured as its own S group, no move (study line 100); as a carry on the M group it
was not measured separately, on a lane that does not bind closure. Severity medium.
Figure against 20%: not applicable (owner ruling P734).

Pending at ruling time: the roster drain refuses with QUEUE-SHRANK (queue lines were pulled by
deletion in batch 244), so queue lines 4741-4761 and everything after are unapplied until the
orchestrator rebaselines the drain state.
