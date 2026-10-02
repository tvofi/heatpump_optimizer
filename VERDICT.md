Fix review: merge bf707c50b6c9200928220269ae40ebecf65e869f

bus-nonce: 7cd89290dd1063dac6717216910282f4

Round 1. Measured at head bf707c50b6c9200928220269ae40ebecf65e869f, live head re-read before posting and unchanged. Code head a6e9df23, base af7660c7 = origin/main at measurement. Detached worktree, own commands, admin-token live reads (`gh api`).

## RESULT lines
- RESULT live-ruleset 23698884 bypass_actors = [{null, DeployKey, always}, {5094721, Integration, always}], updated_at 2026-10-02T13:12:25Z. 5094721 = ~/.zcode/hpo-ledger.appid. The approver App (4968222) and the run App (5009497) are not on it.
- RESULT live-ruleset 22628467 bypass_actors = [{5094721, Integration, always}], updated 2026-09-27. Unchanged, and not recorded by the fixture (by design, #1300).
- RESULT null-control origin/main af7660c7: policy_lint rc=1, 5 [required-contexts] errors (bypass_actors[0].actor_id/actor_type, [1].actor_id/actor_type/bypass_mode), TOTAL 5 across 40 files. This matches the body.
- RESULT head: policy_lint rc=0, TOTAL 0 across 40 files. The fixture order (Integration first) differs from the live order (DeployKey first), and the compare passes, so the sorted-array claim holds.
- RESULT mutant 1 (the body's: Integration entry dropped): rc=1, the same 5 errors, TOTAL 5. Restored, `cmp` clean.
- RESULT mutant 2 (mine: bypass_mode of the Integration entry set to pull_request): rc=1, 1 error naming that field. So the record pins the mode, and not only whether the entry is present.
- RESULT fixture byte-identical to cb6870bc (R9-F10.5): `cmp` exit 0. `git merge-tree --write-tree cb6870bc HEAD` rc=0, and against origin/main rc=0.
- RESULT field_coverage: blind=0 dead=0 refused=0, FIELD COVERAGE ok.
- RESULT VERSION, manifest, RELEASE_NOTES and both claim files are untouched (three-dot diff is empty).
- RESULT CI cannot see it: in the head's policy-docs job 110864693251 (13:47Z, after the 13:12Z ruleset change), log line 690 is the TOKEN_HIDDEN_SKIP_RE line `skip required-contexts ruleset 23698884 field \`bypass_actors\` is absent from the live read (this token cannot see it); it is UNCHECKED this run, not confirmed`, and its TOTAL is 0. Main's job 110835592950 (12:23Z) prints the same line, but it ran before the change, so it shows the class and not this drift. The head run is the stronger cite.

## Head CI (check-runs API, 35 runs)
There are no failures. 30 runs passed or were skipped by design. CodeQL is neutral. `Analyze (python)` was still in progress at posting; it is not a gate. The cancelled `pr-contract` 110864690248 and `budget-raise-gate` 110864691487 are superseded runs, and each has a later successful run of the same name. No red check owes an answer.

## Assertion sites (re-read adversarially)
- CLAUDE.md:58 "stamps push over the deploy key" is still true: it describes the stamp path, and the App does not stamp. CLAUDE.md does not claim the deploy key is the only bypass.
- 0013:42 "the approver App is not on the ruleset's bypass list" is still true. The added actor is hpo-ledger 5094721, not the approver 4968222.
- 0009:90 "A stamp pushes over the deploy key alone" and :81 "cut bypass_actors to [{DeployKey, always}]" are dated historical notes, and they stay true as history. The stamp statement is still literally true.
- HANDOVER:128 "A stamp pushes to main only over the deploy key" is still true, because it is about stamps.
- orchestrator.md:253 "the queue's one bypass" means merge_fastpath, not a ruleset actor. It is unaffected.
- 0011 is left to R9-F10.5 (cb6870bc rewrites it, +55/-?). I confirmed that F10.5's diff touches 0011.
- HANDOVER edits: lines 106-108 (two `always` bypasses, deploy key plus App 5094721 since 2026-10-02) match the live read. "drops ... the bypasses" (line 118) is correct. The dated line on the 22628467 bullet is accurate, and it hands retirement to F10.5's merge.

## Notes (not blocking)
- HANDOVER:111 still says "seats author as `tvofi-seat-author`", which conflicts with CLAUDE.md's hpo-author/0011. This predates this PR and the PR does not touch it. It is out of scope here and is noted for the record owner.
- I did not wait for `Analyze (python)` to finish. No gate requires it.
