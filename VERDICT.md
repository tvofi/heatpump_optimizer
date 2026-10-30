Fix review: merge 2f5d5065e5361237ed23ab6f92b7ad2fd20f817e

bus-nonce: 5564db30b2355f19ce431706b7b6a041

Round 1. Head measured: 2f5d5065e5361237ed23ab6f92b7ad2fd20f817e (still the PR head at posting).

## Findings

None.

## Evidence

- Diff scope: 9 files, all `dev/programme/delivery/<N>.md` (8 modified, 1 added: 2990.md); each is exactly one line anchoring its own PR number. No production, test, claim, VERSION, manifest or notes file touched (ev/diff-names.txt).
- Row facts: the eight merge SHAs in the rows (2872 d1c7708, 2976 559134e, 2977 96ac7d6, 2978 89ccf73, 2980 bf8103f, 2985 1cbf563, 2986 fe709cb, 2988 b014193) each match a `Merge pull request #N` commit on origin/main.
- Mutation proof, null control, finder harness, claim drift: n/a, record-only diff; the packet names no finder harness and lists no mutation-ledger diff.
- Merge: `git merge-tree --write-tree origin/main 2f5d5065e5361237ed23ab6f92b7ad2fd20f817e` exit 0, clean tree, no MERGE-CLAIM lines (ev/merge-tree.txt).
- Packet: carry_audit 0 findings, figure_lint 1 resolved / 0 not verified / 0 refused, no refusals or advisories. `tests/delivery_status.py` at the head reports rows pending, which its output says is the ordinary batch state and blocks nothing.
- Red checks: none among the 43 check-runs read live from the check-runs API at this head; no gate check is red, so no root-cause answer is owed (the body answers record/nightly-status/delivery-status anyway).
- CI not yet concluded when read: `governance / instrument-self-tests` in progress, and a second-run `prelude` in progress (run 41056356774). Neither is red. I did not see a `pr-contract` run in the list. This verdict does not claim those concluded green; the merge train should require them before merging.
- `record_row.py --automerge-check` could not run here (404 from the API call in the cloud seat), so I did not re-derive it.
