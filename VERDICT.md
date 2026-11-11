Fix review: merge 8af19472a77eb2c51517f57bc2bf5597a0638927

bus-nonce: f9adc023a7e8872e6f5d0a41ed1e6ec3
pending-ci: gate

## Scope

Round 4, a delta review against b64fbe44a49f1f4c8aa9aa53f8da6bea64ae6c43, dispatched past three rounds under the orchestrator's ruling that only the harness anchor needed repair. `review_carry.py b64fbe44 8af19472` prints FRESH-REVIEW because the branch's own commits dd61c43d4 and d95a3490e change its content. So the review covers the delta: 8af19472's parents are b64fbe44 and d95a3490, there is no main merge to resolve, and the delta touches only `dev/audit/harnesses/r10_flow_dispatch_mutants.py` and the self-test half of `tools/audit/seat/cloud_dispatch.py`. Nothing under `custom_components/` changed and no production line of `cloud_dispatch.py` moved, so the scope stays narrow (fix-review.md step 12). The single prior block, that `part-topic-dropped`'s pattern occurred 0 times and aborted the drive, is resolved.

## Evidence

- RESULT base-end: at b64fbe44 the finder's harness `dev/audit/harnesses/r10_flow_dispatch_mutants.py part-topic-dropped ...` prints `abort: part-topic-dropped's pattern occurs 0 times`, rc=2. This reproduces the round-3 block (ev/base-end.txt).
- RESULT failing-first: head's harness run against b64fbe44's `cloud_dispatch.py` prints `part-coll-topic-off verdict=SURVIVED` and `part-coll-self-off verdict=SURVIVED`, plus `part-topic-dropped killed`, `part-coll-id-off killed` and `M0 null-ok`. The new R10-ALIAS and R10-SELF-P2 arms are what kill the two survivors (ev/base-end.txt).
- RESULT head: the full drive in a detached worktree at 8af19472 prints `RESULT mutants=63 survived=0`, rc=0, wall 11m21s, and `RESULT mutant=M0 failed=0 verdict=null-ok`. 58 mutants are `verdict=killed` and 5 are `verdict=CRASHED`: parent-drop, topic-to-id, head-ignored, roster-repo-ignored and pointer-off, the same five the body names, all pre-existing and none of this part's. All of this part's mutants are killed with the counts the body quotes, among them part-topic-dropped failed=3, part-coll-topic-off/-id-off/-self-off failed=1, part-split-one failed=1, part-runs-skip failed=1 and part-cli-nogroup-open failed=1 (ev/harness-head.txt).
- The body's figures re-derive at this head: `RESULT mutants=63 survived=0`, the five CRASHED names, `tests/structure.py` printing `STRUCTURE RATCHET PASSED`, and `tests/closure.py select --diff <merge-base>` printing `MODE: SCOPED -- 0 script(s) run, 33 scoped out.` (under PREPR_SKIP_CLOSURES=1, as ruled; the interpreter lacks homeassistant).
- Null control: M0 null-ok at both ends. The collision arm's own null (R10-CLASH part 1, R10-SPLIT part 2 and R10-SELF-P2 part 2 publish) passes at the head, and `part-coll-self-off` kills it.
- Merge: `git merge-tree --write-tree origin/main 8af19472` gives rc=0 with tree 5ba5af3597e0152406658bc65c92374987c848c5 (ev/merge-and-delta.txt).
- The merge-base diff touches none of VERSION, the manifest, RELEASE_NOTES.md, either claim file, `*budgets.json` or `tests/closures.json`. No golden fixture moved, so step 4 has nothing to compare.
- The governance roles show no diff from merge base to origin/main.
- The body's `## Head` names 8af19472a77eb2c51517f57bc2bf5597a0638927, which is the head measured.
- Red checks: the only red on the head is `tests / nightly-status`, which is not in `merge_train.py owed-reds` (ev/owed-reds.txt). It is not this PR's, the body's `## Red checks: none` stands, and it blocks nothing.
- CI: `merge_train.py classify 8af19472 --pr 3450` was polled every ~77 s from 13:20 to 13:50 UTC and printed rc=3 `WAIT 8af19472a77eb2c51517f57bc2bf5597a0638927 pending: gate red: none` throughout, so the verdict returns with `pending-ci: gate`. No owed red was seen (ev/classify.log).
- Forward-carry: the body says none. Its one Friction item carries to R10-REVIEW-DISPATCH-RESIDUE, a later split part of the group, and carry_audit at the head reads it as routed on origin/handoff/audit-r10-roster.
