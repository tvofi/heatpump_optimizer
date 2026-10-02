Fix review: merge c010925be70e8bf02533b752410d5697cb0d65c1

Resolution-delta judgement for PR #1824 (stage 3): 29c3eef7 + main d536fb4d (with #1823) -> c010925b.
- The only difference from git merge-tree d536fb4d 29c3eef7 is in tests/entities.py, where the 3 conflict
  marker lines were removed. Nothing else was edited by hand.
- The PR's diff against main (d536fb4d..c010925b) is tests.yml, entities.py and docs/delivery/1824.md. Its
  +/- lines in .github and tests are byte-identical to the authored stage-3 diff af2ac763..7a113ee6.
  #1823's concurrency checks (_cc_problems, _CC_NULL) are kept, and the coverage-cache check (_cov_trust)
  follows them.
- tests/entities.py compiles. It has no leftover markers: the 4 "<<<<<<<" strings are fixture strings, and
  main has the same 4.
- codeowners_gap --check: uncovered_files=0.
- The red history (fast on c1ee65df, delivery-status on e67bc382) is now answered in the body, per the
  coordinator; I did not re-read the body.
UNRUN: CI on c010925b (not pushed to the PR branch when I checked: fix/r9-f10-merge-queue-3 was 29c3eef7;
merge on green only), typing, real-HA.
