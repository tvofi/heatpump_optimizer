# BLOCKED: r10-process-slim-p2 (re-authoring of #3245)

## Done

- Steps 1 to 3: c09a9acb was re-authored at main f365ce75 with the addendum's `git filter-branch --env-filter` over origin/main..HEAD. The new head is e24d9e408c6c2f6053faa66a14e305a29f747c37.
  - (a) Both ranges hold 59 commits. Paired by `git rev-list --reverse --topo-order`, every pair has an identical `^{tree}`. Author and committer names and dates, the message, and the parents (mapped through the rewrite) are identical too.
  - (b) `git log --format='%ae%n%ce' origin/main..HEAD | grep -c seat@` prints 0.
  - (c) `ref_privacy.py guard --ref refs/heads/handoff/r10-process-slim-p2 --commits HEAD --over origin/main -C .` exits 0.
  - (d) The final tree is 8e0ef08cc212bdefe8c05fecbb98d6cfbbaae026 at both heads.
- Step 4, first half: e24d9e40 is pushed to handoff/r10-process-slim-p2 (a new branch). BODY.md (this commit) is 9d81a62d's body. Only its `## Head` changed: it names e24d9e40, says it supersedes #3245 with proof 3a to 3d, and demotes the old note to "Previous head note (c09a9acb)". Every Carry marker and closing keyword is byte-identical.
- body_push was NOT run, because prepr.sh refused. handoff/r10-process-slim, fix/r10-process-slim and #3245 are untouched. handoff-wip/r10-process-slim is kept.

## The refusal (step 4, tools/pr/prepr.sh on BODY.md at e24d9e40), verbatim

               PREDICT pr-contract GRADER carry_audit.py check --body /tmp/pr-body.md --branch $HEAD_REF REFUSED by the base's copy, over tools/audit/seat/merge_train.py, tools/pr/app_approve.sh, tools/pr/ci_predict.py: CARRY-AUDIT: 6 finding item(s): 5 routed, 0 unrouted, 1 bad destination(s)
      REFUSE   ci predict             CI PREDICT: 1 predicted red(s) on pr-contract against 806e952cadde -- repair before the handoff; the lines above name each arm's repair
      ok       carry                  CARRY-AUDIT: 6 finding item(s): 6 routed, 0 unrouted, 0 bad destination(s), at origin/handoff/audit-r10-roster 9440f8127
    PRE-PR: e24d9e408c6c2f6053faa66a14e305a29f747c37 00000000000000000000001000000000

## What it means (measured)

- The likely cause, which I inferred and did not trace: the predictor's base-copy arm resolves destinations against main's roster at f365ce75 only. There, R10-CLOSEOUT-INSTRUMENTS appears in no roster: `git grep -l R10-CLOSEOUT-INSTRUMENTS origin/main -- dev` lists only dev/programme/delivery/3324.md. The group is only on origin/handoff/audit-r10-roster (appended at d9393b486, still there at 9440f8127). That would make the one body item marked `Carry: R10-CLOSEOUT-INSTRUMENTS` (ada60feb in the head note; carry_audit's NOTE calls it c65c2636) the bad destination, and pr-contract is predicted red.
- The head's own carry arm, and the base copy of carry_audit.py run by hand in a worktree at 806e952c, both print `CARRY-AUDIT: 6 finding item(s): 6 routed, 0 unrouted, 0 bad destination(s)`. The hand run prints `roster read at origin/main` and then `R10-CLOSEOUT-INSTRUMENTS resolved on origin/handoff/audit-r10-roster`, so it falls back to the roster ref, and the predictor's arm apparently does not. The previous seat's clean prepr at c09a9acb read roster d9393b486.
- The addendum makes me keep every Carry marker exactly, and the roster is not mine to write. The orchestrator decides: land the R10-CLOSEOUT-INSTRUMENTS roster entry on main, or re-route the marker. Then re-run prepr.sh and `bash tools/audit/seat/body_push.sh r10-process-slim-p2 BODY.md` on this body.
