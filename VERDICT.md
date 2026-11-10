Fix review: merge d705f090031711d1f4b5445299eed2734cf86d9c

bus-nonce: 1fc76c0bb0a407ae5bcfd6290087eff9

## Summary
Hotfix R10-HOTFIX-SELFTEST-SCOPE-HANG, round 1. Measured head d705f090031711d1f4b5445299eed2734cf86d9c; the body's 4f167ab4 measured head carries (review_carry: CARRY, only a main merge moved it). Merge with origin/main is clean (merge-tree exit 0, no conflict). merge_train classify: GREEN, no pending, no red. Roles dir unchanged against main.

## Evidence
- RESULT selftest_scope self-test at head: 103 checks, 0 failed (ev/selftest.txt).
- RESULT mutants: sh tools/ci/selftest_scope_mutants.sh --self-test: all 10 mutants refused, ends "SELFTEST-SCOPE MUTANTS: every mutant refused" (ev/mutants.txt). Mutation proof holds.
- RESULT null control: base wrapper (origin/main selftest_step.sh) under head self-test: 7 of 103 failed, as the body says (ev/null-control.txt).
- RESULT class seams: steps with no if: at head are ['', '', 'scope'] (ev/seams.txt), matching the body; UNTRACED == UNGATED is pinned by the self-test.
- RESULT selftest_wiring: 127 wired, 0 unwired; structure ratchet passed; no budget file touched.
- Figure drift, not a defect: body says "107 gated steps" for selftest_scope static; at this head (main merged in) it prints 108 gated step(s), 0 problem(s). The 107 was measured at the older head; the rule (static, 0 problems) holds.
- Fold timing figures (70504 lines, 0.4/0.6/0.7/4.4 s) not re-derived; I did not rebuild that trace. Not verified. The behavioural claim is proven by the mutants and null control instead.
- Claim files, VERSION, manifest version and notes heading untouched in the PR's three-dot diff (only governance.yml, delivery row, selftest_closures.json, selftest_scope.py, selftest_scope_mutants.sh, selftest_step.sh). No solver code, so no golden drift.
- Red checks: owed-reds set (tests / fast (3.14), tests / mutation, tests / typing, validate / validate-hacs) is all green at the head. The earlier reds are answered in the body regardless.
- Architecture (step 17): added code is an instrument-only change, streamed fold and memoised realpath, no new layering or duplication seen.
- No finder's harness named; the PR's own self-test and mutants script are committed in the tree.
