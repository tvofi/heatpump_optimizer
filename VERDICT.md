Fix review: merge 4e1c57d5af1326cd61578d3bbf8751f7865a4ffb

bus-nonce: 9329e3e04f3dab9017782b1f82a8fc34

Round 2 (delta review over round 1 merge at 328e222f). Head measured: 4e1c57d5af1326cd61578d3bbf8751f7865a4ffb (PR head ref re-read at post time, unchanged). Role file current vs merge base (empty roles diff).

RESULT delta: tree(4e1c57d5) == tree of mechanical 3-way merge(328e222f, a7cf60cf; base b24cfe51) = 1e43a51c. Every file in main's diff b24cfe51..a7cf60cf has an identical +/- line set in 328e222f..4e1c57d5 (0 dropped, 0 extra); the delta's file list equals main's. The PR's own change (15 files, 294+/22-) is line-identical at old base and new base for every file, including the overlapping policy_lint.mjs, field_coverage.mjs, tools/pr/*, .claude/settings.json, tests/entities.py. (ev/delta.txt)
RESULT merge-tree origin/main 4e1c57d5: rc=0, no conflicts (ev/mt.err empty); origin/main is a7cf60cf, the PR's base.
RESULT policy_lint --self-test / --fixtures: 0 errors, FIXTURE ok 93 errors hold 254 pins; field_coverage: FIELD COVERAGE ok (blind=0 dead=0 refused=0); ref_privacy --self-test 84 checks 0 failed; cloud_dispatch --self-test 68 checks 0 failed.
RESULT prepr fixtures: attribution.md refused (rc=1, "carries a tool's attribution (session-link, generated-footer)"); good-claude-ai.md accepted (rc=0). Full prepr.sh --self-test: 331 passed, 9 failed -- all 9 are 6b gate-recording/orphan-watchdog arms failing on "no interpreter that parses the tree was found (seat venv)", i.e. this cloud environment's missing seat venv; none touches the attribution arms (they pass). I did not run these on main for comparison, so the environmental attribution is by the failure text, stated as such. (ev/prepr-full.txt)
RESULT CI at head (check-runs API, one bulk read): 32 success, 9 skipped, 1 failure = nightly-status; policy-docs success. nightly-status grades main and the diff does not touch tests/nightly_status.py or its inputs (that file arrives from main's side of the delta), so it is not this PR's. (ev/checks.tsv)

Not re-done (delta review, round 1 merge stands): mutation proof, finder-harness baseline/head measurement, claim files, version untouched -- the PR's own hunks are line-identical to round 1, so those carry. Round 1 count: this is round 2.
