Fix review: merge 860ca72cb48e90e56f8f50663be7bf63a135daaa

bus-nonce: 4e2e14eac8d019fe783ec6f69eab443d

Round 2 of fix review (round 1 at 6ffc3708d was blocked on a conflict and on governance/hassfest/validate having no stated reason). Measured head: 860ca72cb48e90e56f8f50663be7bf63a135daaa, re-read before posting and still the head. Merge base 5a41a5669. origin/main is now c8cc75ea9, and `git merge-tree --write-tree origin/main 860ca72cb48e90e56f8f50663be7bf63a135daaa` exits 0.

Round-1 blockers, checked against the merged artifact rather than the diff:
1. Conflict resolved. `git diff origin/main(5a41a5669) 860ca72cb48e90e56f8f50663be7bf63a135daaa` contains only additions, apart from this PR's own 8 round-1 lines in tests/entities.py and tests/closures.json. No line of #2405 is lost. .github/CODEOWNERS:77-78 has both `/tools/pr/cancel_superseded.py` and `/tools/pr/codeql_scope.py`. codeql.yml jobs: cancel-superseded (contents read, pull-requests read, actions write), scope (contents read), and analyze (needs scope, per-leg skip intact).
2. Class disposition. The 0/42/19 counts are re-derived. I fetched my own cache (`superseded_runs.py --fetch`, read-only) and ran the same command over the body's window (--since 2026-10-14T22:55:00Z --until 2026-10-18T15:27:04Z):
RESULT validate   nonmain_runs=483 completed_not_cancelled=424 superseded=0
RESULT hassfest   nonmain_runs=483 completed_not_cancelled=428 superseded=0
RESULT governance nonmain_runs=462 completed_not_cancelled=390 superseded=0
RESULT codeql     nonmain_runs=483 completed_not_cancelled=348 superseded=19
RESULT tests      nonmain_runs=483 completed_not_cancelled=351 superseded=44 (body: 42)
RESULT NULLCONTROL all five workflows all_cancelled_superseded=0 same_sha_superseded=0 unique_sha_dup_heads=0
The tests 44 vs 42 gap: my own count (my definition, disclosed: the harness rule with the newer run also required to start inside the window) gives tests=42, validate=0, hassfest=0, governance=0, codeql=19 on the same cache. So the 2 extra tests runs are superseded by runs that started after the body's fetch. That is run history accruing, not a fault in the fix. The harness ships with this PR (no finder-committed harness existed; the pre-study built it). Its --selftest passes.

Re-checked at this head:
RESULT selftest cancel_superseded 19 checks, 0 failed
RESULT mutants 11/11 killed (round 1; tools/pr/cancel_superseded.py is byte-identical since 6ffc3708d)
RESULT inert is_inert(cancel_superseded.py)=False, orphan_files()=[], and `closure.py select --files tools/pr/cancel_superseded.py` runs [tests/entities.py]
RESULT version VERSION, manifest and notes heading are untouched
RESULT head-in-body the body names 860ca72cb48e90e56f8f50663be7bf63a135daaa and its merges of fb3bcf11a and 5a41a5669
RESULT ci check-runs at 860ca72cb48e90e56f8f50663be7bf63a135daaa: 48 in total, 33 success, 15 skipped, 0 failure. That includes closures, fast (3.14), coverage, Analyze (python), mutation, pr-contract x2, instrument-self-tests and cancel-superseded x2. I did not read the mutation lane's log: the production predicates are covered by my own 11 mutants.
RESULT red-history the reds at 72a3f1bbd (closures, closures-autofix, pr-contract) are named and answered in the body. I checked 0a596b410's 47 runs: 32 success, 15 skipped, as the body says.
RESULT forward-carry both are carried. The stale "GITHUB_TOKEN push creates no pull_request run" sentence is folded into orchestrator O2. The same-SHA duplicate is in the orchestrator brief O7-same-sha-dup-runs.md, which carries the #1276 shadowing risk. Both are in the orchestrator's SEATS.md.
Not re-derived: billed-minute figures (I did not fetch the jobs API) and the AFTER prediction.
Owed at merge: tvofi's review (.github/workflows/**, CODEOWNERS).

Evidence: ~/hpo-seats/r10s3/review-2396/evidence2
