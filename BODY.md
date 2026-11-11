R10-HOTFIX-SELFTEST-SCOPE-UNION part 2. Main 6cc15e9b is red: `governance / instrument-self-tests` step "Refuse a self-test read set the committed table misses" printed `selftest_scope check: 111 gated step(s), 7 refusal(s)`. **This lands after #3446** (part 1: fix-review.md, prepr and `-c` entries); this branch is origin/main with #3446's head 745a936201ac merged in first, so the two edits of `tools/ci/selftest_closures.json` stack. Part 2 owes the remaining refusal: `selftest-wiring` missing `tools/audit/seat/remerge_main_selftest.py`. Rule: gate-scoping.md and #201 comment 6707834331 (the table is measured, never hand-written).

## Head

2688f4c854350142cca0af33207717064eb8e5df

## Mutation proof

n/a: no production code; the change is one table entry written by the instrument's own `selftest_scope.py record --step selftest-wiring`. The perturbation is the null control below.

## Null control

The same comparison against `git show origin/main:tools/ci/selftest_closures.json` (61afd4f2d) refuses: review-packet and verdict-bus miss dev/governance/roles/fix-review.md, selftest-wiring misses tools/audit/seat/remerge_main_selftest.py. At this head it prints nothing.

## Figures

- Instrument: `python3 -I tools/ci/selftest_scope.py record --out <scratch>` (full re-record, Linux, strace, all gated steps), then a per-step subset comparison of its files/probes/dirs/index/objects against the committed table: zero misses at this head; the three misses above at origin/main. Cloud-unmeasurable CI reads (prepr's .gitattributes, tests/env_drift.py, tools/merge/ledger_merge.py; probe `-c`) are part 1's. A single-step cloud re-record of prepr drops those three, so it was discarded and not committed (over-scope is reported, not refused).
- The two over-scoped notes (cloud-dispatcher, prepr) are not refusals; no entry narrowed.
- Measured against origin/main 61afd4f2db10 on 2026-11-11 (date -u).

## Red checks

- `governance / instrument-self-tests` on main run 6cc15e9b, job 130741855641: not in `merge_train.py owed-reds`, so no answer owed; this fix re-records what its `check` refuses.
- `tests / fast (3.14)`, `gate`, `pr-contract / pr-contract` on 8d8155a39, a commit of #3446 (part 1) carried in by the merge: not this diff's red (this diff is one table entry); #3446's head 745a93620 is green on `tests / fast (3.14)`. Cheaper detector: none beyond the check itself, which already runs at the pull request; standing cost is nil, so nothing is built.

## Forward-carry

none

## Friction

none
