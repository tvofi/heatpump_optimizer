Fix review: merge 7ef58ef6e19bcac2722a6099dd0fde1e41d282fa

bus-nonce: 6be0f8bbebd9cf674e281981f7e07e10

Round 2 (round 1 blocked only on ci-pending). Head measured and current: 7ef58ef6e19bcac2722a6099dd0fde1e41d282fa. Base 915406ce6.

## Evidence
- RESULT diff: only dev/programme/delivery/3031.md and dev/programme/triage/s6-batch85.md change; no production code, VERSION, manifest or notes heading.
- RESULT citations at base 915406ce6: ledger.py:618 is `def review_owed`; orchestrator_tick.py:701 is the `for text in lg.review_owed(...)` call; record_row.py:619 is `RECORD_BRANCH = "record/autofix"`. The record cites ledger.py:618-634 and `git grep RECORD_BRANCH` on ledger.py/orchestrator_tick.py as empty: no RECORD_BRANCH test in review_owed at base.
- RESULT P241: s6-batch49.md has `## P241: record PRs merge with no review` (line 165) and its carry names R10-RECORD-HOLD-APPROVE, which the record states is done (#2918); the stranded-carry framing holds.
- RESULT destination: R10-FLY-TICK-APPROVAL-OWED is in wave-r10-groups.json on origin/handoff/audit-r10-roster at b87f49371, resume.stage not-started, lane IN, size S (ev/group.json). Round 1's finding that it is absent is wrong.
- RESULT merge: `git merge-tree --write-tree origin/main 7ef58ef6e19bcac2722a6099dd0fde1e41d282fa` exit 0, no conflict (ev/merge-tree.txt).
- RESULT CI: `merge_train.py classify 7ef58ef6e19bcac2722a6099dd0fde1e41d282fa` exit 0, GREEN, pending none, red none (ev/classify.txt). The packet digest shows pr-contract, delivery-status, briefs and policy-docs success.
- Not re-derived: the 3-sweep and `AUTOMERGE OK #3028` at 9e688830 measurement is from the orchestrator's out-of-tree ledger and gh, which this seat cannot read. The held op b85-P322.txt is on the orchestrator's machine and not in the tree or on the roster branch, so I could not read it; the carry text in the record is what I checked. The carry is not yet on the roster group (carry is empty at b87f49371), which is the held op's write.
- The brief_lint and triage gate were not run on the carry text itself, which is in no roster or carry file yet; the head's tests / briefs and pr-contract checks are green.

## Findings
none
