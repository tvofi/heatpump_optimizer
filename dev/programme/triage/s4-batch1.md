# Proposal triage, session s4, batch 1 (P1-P4)

Re-recorded in `dev/governance/roles/proposal-triage.md`'s format from the
rulings session s4 made out of the tree on 2026-10-22. Each ruling's evidence is
the carry its ACCEPT routed, quoted from the round-10 roster branch at
`0a326689b87058b56450a5966acfda910b002412`; read one with
`git show 0a326689b:dev/programme/rosters/wave-r10-groups.json | jq -r '.groups[] | select(.group=="<group>") | .carry[]'`.
The s4 session's own cost estimates are not in the tree, so `Cost:` states
the scope the carry fixes and no figure the record cannot reproduce.

## P1: discharge a merge-commit handoff tip in `bus.sh orphans`
Verdict: ACCEPT -> R10-FLY-ORPHANS-REWRITTEN (carry)
Source: the orchestrator's sweep, 2026-10-22.
Instances: 1 -- `handoff/r10-fly-gh-read-retry` at `a457acaf4` listed ORPHAN
for 4.5 h (`repair=review`, `uncovered=1`) while fix head `a6e90cbcc` held
both its parents; `bus.sh orphans` output as quoted in the carry.
Cost: one discharge arm in `bus.sh` (a `git rev-list --no-merges --count`
call), its fixture, null control and one mutant.
Binding: a false ORPHAN sends the sweep to repair a ref that needs nothing;
the arm costs one git call per tip.

## P2: `body_patch.sh` works while another worktree holds the branch
Verdict: ACCEPT -> R10-FLOW-BODY-PATCH (carry)
Source: a seat's result, 2026-10-22.
Instances: 1 -- #2589 at 11:40Z, `update_pr.sh` refused ("branch
fix/r10-fly-gh-read-retry checked out elsewhere") because merge train 21 held
the worktree; the re-body went to the merge seat by hand.
Cost: a detached checkout of the expected head in place of `-B <branch>`, one
fixture, a null control and one mutant, inside a group already in flight.
Binding: a body repair blocked by a train's worktree is serialised behind the
train; the fix adds no new file.

## P3: a base-pinned replay in `prepr.sh`
Verdict: ACCEPT -> R10-FLOW-JIDOKA (carry)
Source: a seat's result, 2026-10-22.
Instances: 2 -- #2609 round 2 (about 1 h) and #2529 (`policy-docs`: "pinned
tools/policy/agreement_restore.py is unregistered"), each a pull request green
under the head's graders and red under the base's in CI (`governance.yml`,
"Restore the check source from the base commit").
Cost: one prepr step, gated on `PIN_TOUCHED=0`, a detached worktree and three
lanes; skipped with its reason on a diff touching no pinned path.
Binding: each instance cost a CI round on the critical path; the step runs
only on the diffs that can redden that way.

## P4: the train's hand re-points
Verdict: ACCEPT -> R10-TRAIN-OVERLAP-GRADE (carry)
Source: the orchestrator's sweep, 2026-10-22.
Instances: 1 pull request, 8 refusals -- #2580 in train 27 refused 8 times
("base branch policy prohibits") after `approved (app)`, re-pointed by hand 6
times in 4 h.
Cost: step 1 is the existing #2577 diagnosis (park with the reason instead of
retrying); step 2, widening `_carry_owner_approval`, only if step 1 shows the
missing requirement is an approval at a clean recarried head.
Binding: hand re-points are orchestrator time on the merge path; step 2 is
deferred inside the ruling to the measurement step 1 produces.
