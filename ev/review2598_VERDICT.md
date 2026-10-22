Fix review: merge 35dd3965082c7deac9b3cf101df992d88081e944

bus-nonce: e34be4d234da099b53edcf39b44a579d

## Round

Re-review of the R10-ROSTER sync PR #2598. At least round 2: the previous verdict, at 0c563c12, was blocked ci-unconcluded by the external installation rate limit. This is not a re-cut. Measured from a detached worktree at 35dd3965082c7deac9b3cf101df992d88081e944 with PREPR_SKIP_CLOSURES=1. The role contract is current: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty.

## Findings

- Non-blocking: R10-RCA-FRICTION goes to stage done at 3976515a, still holding its two `carry` entries: the #2452 card.mjs/deep-link census cost friction, and the #2479 "red-check answer is written per PR, with no cross-run count" disposition item. Neither is dispositioned in dev/audit/rca/R10-RCA-HARNESS-FRICTION.md at origin/main (no #2479, no census cost, no cross-run count). Neither is moved to R10-RCA-FRICTION-RESIDUE either: each text appears once in the head roster, on the done group only. The second item is in the same class as RESIDUE's root-cause-unanswered key #2437. The RESIDUE seat should take both and give each a disposition or a recorded refusal. Precondition: re-scrape the bodies' `## Red checks` answers at its own merge base before it counts anything. Carry: R10-RCA-FRICTION-RESIDUE
- Non-blocking: R10-RCA-FRICTION-RESIDUE's `issues` holds seven numbers (2428, 2429, 2436, 2437, 2438, 2593, 2597), but its brief scopes "the five recurring-friction keys" and names neither #2593 (key body-stale) nor #2597 (key harness). #2597 is a recurrence of the key #2331 that R10-RCA-FRICTION closed, so it tests whether #2561's countermeasure held. A seat reading the brief alone would leave both unmeasured. The RESIDUE seat owes both keys a cause, a process state, a cost test and a countermeasure or a refusal. For #2597 it measures whether the post-#2561 harness blocks are the class-open spelling #2561 taught or a new cause. Control: #2561's `rounds.py --stats` re-run at RESIDUE's merge base. Carry: R10-RCA-FRICTION-RESIDUE

## Evidence

- RESULT head: 35dd3965082c7deac9b3cf101df992d88081e944. It is still the PR head at verdict time (pulls API re-read after CI concluded). ev/HEAD.txt holds it.
- RESULT merge-tree: `git merge-tree --write-tree origin/main 35dd3965…` gives rc 0, tree d0f3b111be5a, which is identical to the head's own tree. origin/main b787c7d45 is an ancestor of the head. No MERGE-CLAIM lines; neither claim file is touched (ev/merge_tree.txt).
- RESULT diff: origin/main...head touches two files, `dev/programme/rosters/wave-r10-groups.json` (+153 −16) and `dev/programme/delivery/2598.md` (+1, this PR's row). VERSION, the manifest and RELEASE_NOTES.md are untouched. The roster at the head is byte-identical to the roster tip 4da10dbae84c7915488ce9fcd29240fc14750eb0, which is still the tip of handoff/audit-r10-roster (ls-remote). So merge 332981305 and merge 35dd39650 resolved nothing inside the roster.
- RESULT ops, the body's jq program at origin/main→head and at 306a96d→4da10dba (both identical): groups 144→147. New: R10-NIGHTLY-PYSPY-RETRY, R10-RCA-FRICTION-RESIDUE, R10-TRAIN-OVERLAP-GRADE, each `resume.stage` queued. Removed: none. Changed (7): R10-FLOW-BOARD, R10-FLOW-BODY-ONLY, R10-FLOW-DESIGN-POLICY, R10-FLY-GH-READ-RETRY, R10-ORCH-MACHINERY, R10-RCA-FRICTION, R10-SCORES. Top-level keys outside `groups` are unchanged, and the existing groups' order is preserved.
- Per-group field diffs, each matching the brief's burst lists, with nothing else changed:
  - R10-FLOW-BOARD: +1 carry (orchestrator_tick owner-gate count under a mandate).
  - R10-FLY-GH-READ-RETRY: +1 carry (#2589 PR 1 proof owed by PR 2/3).
  - R10-TRAIN-OVERLAP-GRADE: two carries (#2595 RCA item; merge_train approval-at-live-head park, #2577).
  - R10-ORCH-MACHINERY: the #2584 carry is dropped and re-appended with its control (ac7935610/e5d5c5084), +1 #2578 body_patch.sh hosted one-shot carry.
  - R10-FLOW-BODY-ONLY: +1 #2578 `--roster-ref` carry.
  - R10-RCA-FRICTION: issues 2428/2429/2436/2437/2438 unwired, resume stage done, commit 3976515a08228598ea3863f4f36dc4c7c4846865.
  - R10-RCA-FRICTION-RESIDUE: issues are those five plus 2593 and 2597.
  - R10-FLOW-DESIGN-POLICY: resume stage done, commit 6077bf70e.
  - R10-SCORES: brief `coordinator.py:10293` becomes `coordinator.py:10309`, and that is its only change.
- RESULT figures against merge base 306a96d: `git rev-list --count 306a96d5f..4da10dbae` gives 21, and the shortstat gives 1 file, +153 −16, as the body says. Against the current merge base: the code head's merge base with origin/main is still 306a96d5f21f7876070d48c194fd4be99b64022c, so 21 / +153 −16 stand. The PR's own merge base is now b787c7d45, and the roster diff against it is the same +153 −16. Null control: `git diff --exit-code origin/main 306a96d5f -- <roster>` gives rc 0, as claimed.
- RESULT done stages: 3976515a (#2561) and 6077bf70e (#2586) are both ancestors of origin/main.
  - R10-FLOW-DESIGN-POLICY checklist: met at origin/main. designer.md and design-review.md exist. orchestrator.md:131 dispatches the fixer after `Design review: approve`. fixer.md:245 says "a departure is raised, not made". fix-review.md:134 judges "the architect or approved design note". CLAUDE.md:118-119 name both contracts. Decision 0014 exists and 0012 reads "Revoked by decision 0014…".
  - R10-RCA-FRICTION checklist: met. The record and the detector landed. The #2561 body carries `Closes #2331` and `## Approval`. #2331 and #2353 are closed. Its undischarged carries are under Findings.
- RESULT citation: at origin/main, coordinator.py:10309 is `ctx._thermal_params.heat_loss_coefficient` inside `_scores_view` (def at 10299). Line 1083 is `return params.heat_loss_coefficient, …` in another function, as the body says.
- Adversarial: re-planting `coordinator.py:10293` makes brief_lint print exactly 1 error ("found at line 1083 instead"), so the repair is what clears the lint. ev/brief_lint_mutant_10293.txt.
- Adversarial: brief_lint does not separate 1083 from 10309. Planting `:1083` lints clean because the token matches. The body's choice of 10309 rests on the enclosing function, which I confirmed by hand. The linter did not establish it.
- RESULT brief_lint: `node tools/policy/brief_lint.mjs <head roster>` gives `TOTAL: 0 error(s)` both from the head worktree and from an origin/main worktree, the roster_edit lint gate's shape. ev/brief_lint_head.txt, ev/brief_lint_from_main.txt.
- RESULT carry_audit: `carry_audit.py --roster-ref origin/handoff/audit-r10-roster check --body <PR body>` prints `0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)`. ev/carry_audit_body.txt. Both Carry destinations in this verdict are R10-RCA-FRICTION-RESIDUE, a live group (resume stage queued) in the head roster.
- RESULT mutation: n/a. The diff writes no production or test code line, so there is no mutant to draw. CI's `mutation` is success.
- RESULT CI at this head, check-runs API, 49 runs, all concluded: 28 success, 20 skipped, 1 neutral (CodeQL), 0 failure, 0 cancelled. `instrument-self-tests` concluded success after I waited for it. pr-contract (twice), briefs, nightly-status, delivery-status, closures, closure-scope and fast (3.14) are all success. No red check, so the step 11 root-cause trigger is not engaged. The previous round's rate-limit stop did not recur on this head. ev/check_runs.tsv.
- The body's Red checks section reads main's tip 16a8240f, not this head. It is moot now that every run at this head is green.
- Forward-carry: the body says none, and its carries are the roster ops themselves, all present at the roster tip 4da10dba.
- RESULT carry_audit over this verdict as a comment beside the body: `2 finding item(s): 2 routed, 0 unrouted, 0 bad destination(s)` (ev/carry_audit_verdict.txt).
