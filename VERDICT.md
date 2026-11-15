Fix review: merge 161689a939ce46063175f0e8eebd45e588f2367d

bus-nonce: d150b2cbd1e46df5a90b3d6f2efd6028

## Summary

Round 1 (first review, full scope). The diff is `tools/pr/ci_predict.py` (a step replay that times out at the head is reported `UNMEASURED` instead of being predicted red; the bound comes from `HPO_STEP_REPLAY_TIMEOUT_S`) plus the delivery row `dev/programme/delivery/3624.md`. No `custom_components/` code, no budgets, claim files, VERSION, manifest or release notes are touched.

## Findings

- The body's claim that a non-positive `HPO_STEP_REPLAY_TIMEOUT_S` falls back to 180 s is not pinned: replacing `return v if v > 0 else SELF_TEST_TIMEOUT` with `return v` survives the self-test (`ci_predict self-test: 0 failed`, ev/mutants.txt M5). Under that mutant, a value of `0` gives a zero timeout, so every touched step reads `UNMEASURED` and the step replay predicts nothing. The guard is correct at this head. Only its test is missing, and the instrument is advisory: CI remains the authority on these steps. Carry: dismissed: advisory pre-PR instrument, guard correct at the head, only reachable by an operator setting the variable to 0 or less; a one-line self-test arm is a cheap follow-up, not a defect.

## Evidence

- Head: `161689a939ce46063175f0e8eebd45e588f2367d` (ev/HEAD.txt). The live PR head read back as this SHA at verdict time. The body's `## Head` names it. The second SHA in that section, `d77e2f91896e`, is the code commit and an ancestor of the head.
- Merge with main: `git merge-tree --write-tree origin/main 161689a9` exits 0 with no conflicts (ev/merge-tree.txt).
- Roles drift: `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty.
- CI: `merge_train.py classify 161689a9 --pr 3624` prints `GREEN 161689a939ce46063175f0e8eebd45e588f2367d pending: none red: none`, rc 0 (ev/classify.txt). No reds, so none is owed a `## Red checks` answer.
- Self-test at head: `python3 tools/pr/ci_predict.py --self-test` prints `ci_predict self-test: 0 failed` (ev/selftest-head.txt).
- Mutation proof, my own mutants on the self-test (ev/mutants.txt):
  - RESULT M1 predicate `if rc and rc != TIMED_OUT` -> `if rc` (the body's named mutant): killed, 1 failed.
  - RESULT M2 `return TIMED_OUT` -> `return 124`: killed.
  - RESULT M3 env bound ignored (always `SELF_TEST_TIMEOUT`): killed.
  - RESULT M4 note no longer starts `UNMEASURED`: killed.
  - RESULT M5 non-positive guard removed: SURVIVED (see Findings).
  - RESULT M6 ValueError fallback -> 0.001 s: killed, because unrelated arms time out.
- Null control: the in-tree arm `rc 1 at the head and 0 at the base is still predicted` passes at the head under the 0.5 s bound. The base half (rc 124 is truthy at the merge base, so it was predicted red) is re-derived by reading the base `replay_step`/`step_replay_preds`, not by running it, because the base has no environment bound to shrink.
- Figures: the body's one figure (0 failed at the head, 1 failed under the mutant) re-derives exactly.
- Harness: this finding has no committed finder's harness (the review packet names none). The self-test arms are the fixer's, so I disclose them as such. Their perturbation (M1) moves them.
- Class: one seam. `replay_step` is the only place that maps a replay timeout to an rc, and it has one caller, `step_replay_preds`.
- Step 15: the added lines stay inside the instrument's existing seam, with no architecture breach.

## Notes

- Note: body: `## Mutation proof` names one mutant only; the survivor above is the gap.
