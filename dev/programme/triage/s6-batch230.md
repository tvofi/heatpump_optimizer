# Proposal triage, session s14, batch 230

Source: the orchestrator's brief to triage seat s14-39 (2026-11-12), jobs 1-4 plus a critical-path
reorder (R10-STANDING-CONTRACTS-P2 carries 0-4 first), ruled as P697-P699. Line numbers are at
origin/main 2ced371c1a. Roster read at handoff/audit-r10-roster 81e01e37aa. Rulings are the
orchestrator's under mandate 6715477401 (scope all), made by triage s14-39.

## P697: R10-STANDING-CONTRACTS-P2 carries 0-4 are already on main

Verdict: IMPLEMENTED
Evidence: the part-1 fixer's body (ref handoff-wip/r10-standing-contracts-p2-body dea4c2ae8f, BODY.md
lines 20-26) cites one `Carry: dismissed: implemented at <sha>` line per carry. Spot-checked two on
main: tools/pr/ci_predict.py:656 BOOTSTRAP constant and :872 its use (carry 0 (c), e566f7e02);
dev/governance/roles/standing.md:27-30 "## Autofix hold" naming mutation-, closures- and
claims-autofix (carry 3, 1b174e9b3). e566f7e02 is an ancestor of 1b174e9b3.
Ops: mark-carry implemented 1b174e9b3 on carries 0-4. The part-1 fixer has nothing left to cut.

## P698: ci_predict's throwaway clone reads local heads as origin/* (P687 reopened)

Verdict: ACCEPT
Scope: tools/pr/ci_predict.py:666-692 (`ci_tree_run`); tests/throwaway_git.py:151-159.
Evidence: second instance. body_push/open refused because the predictor ran CI's tree against a stale
roster: a local refs/heads/handoff/audit-r10-roster, behind the remote, was what the steps read as
origin/handoff/audit-r10-roster. Cause, read from the code: `throwaway_git_clone` is a plain
`git clone --shared` of the local checkout, so the clone's refs/remotes/origin/* are the checkout's
LOCAL heads (refs/heads/*), not its origin/* refs. `ci_tree_run` overwrites only
refs/remotes/origin/main (with `tip`); every other origin/* a step reads (HPO_LANDED_ROSTER_REF, the
roster and handoff refs) is a local branch of whatever age, or is absent. CI fetches them fresh.
P687's first instance (a four-day-old base) is consistent with that class but was not located.
Destination and severity: carry on R10-PREPR-RESIDUE (in-progress, owns ci_predict.py and
body_push.sh), normal. Figure against 20%: two refused body_push/open runs (the first cost about 12 min; the second was not timed) on
release-path heads; a predictor that predicts falsely makes every red it prints suspect.
Fix shape: after the clone, set every refs/remotes/origin/* in the clone from the checkout's own
refs/remotes/origin/* (or fetch the named refs), never from its refs/heads/*. Control: a self-test with a
local head behind its origin/ twin, where the step reads the origin/ value.

## P699: grep-level pass over the open moved carries

Verdict: IMPLEMENTED
Evidence, all at origin/main 2ced371c1a:
- R10-STANDING-CONTRACTS-P2 idx 5: standing-merge.md:8-13 no longer names merge_pr.sh; a budget-file
  or policy head "takes the train's serial route". Implemented at 1b174e9b3.
- idx 6: standing-merge.md:9-12 "joins the live train (`train.sh add`) as its next batch, never
  waiting". Implemented at d69619360.
- idx 8: orchestrator.md:108-109 "read state only from the plan page and the ledger's digest".
  Implemented at 1b174e9b3.
- idx 19: standing.md:49 names `$HPO_STATE_DIR/alive/`. Implemented at 1b174e9b3.
- idx 20: designer.md:15 reads the verdict at `design-verdict/<group>`; cloud_dispatch.py:351 pins it.
  Implemented at 1b174e9b3.
- R10-COMBI-TANK-PR-B idx 5: tests/features.py:9800 "`unwired_combi` exemption is gone".
  Implemented at c2cb6262d4, inside #3398.
Left open (doubtful at grep level, not ruled): R10-STANDING-CONTRACTS-P2 idx 7 (orchestrator.md:106
says "never you inline", but no line says a seat stays until its replacement job is live), 9-18
(retirement and beat-job items folded to ORCH-LEDGER; owner orders), 21-23 (liveness-hook amendments),
27 (the HANDOVER.md standing-seats bullet names four seats plus triage; the roster seat is retired).
R10-COMBI-TANK-PR-B idx 0-2 (owner rulings that bind the design, spent once PR B merged: they need a
dismissal ruling, not a mark), 3 (the MFS 600 S figures: no 504 l or MFS in custom_components/*.py),
6 and 7 (constraints on later stages: they stay as long as a stage can still break them).
