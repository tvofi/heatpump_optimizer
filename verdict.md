Fix review: merge 2996954eb5d19b0733b6c95fbcf75c03a7098b59

bus-nonce: a5766989ebfb2c5130acfaec387ce7d2

## Evidence

- Round 1 (first review of this PR). Head reviewed: 2996954eb5d19b0733b6c95fbcf75c03a7098b59; the PR's live head and the body's `## Head` both name it.
- The diff is record-only: six `dev/programme/delivery/<N>.md` row files (five open-to-merged rows, one self-row). No `custom_components/`, test, check, `VERSION`, manifest or `RELEASE_NOTES.md` change (ev/diffstat.txt).
- Every row SHA re-derived from git: 4ebd430, f269ecc, 35402f7, e4c929b and 6f6a85c are each the "Merge pull request #N" commit of the PR their row names, and each is an ancestor of origin/main (ev/row-shas.txt).
- Titles and group suffixes match the open rows they replace. The self-row #3844 is the open form.
- `python3 tests/delivery_status.py` at the head: DELIVERY STATUS OK, 6 rowed, 1 pending (#3839, merged after the base), 0 overdue (ev/delivery_status-head.txt). This re-derives the body's one figure.
- Mutation: the body's n/a holds, because no production line exists to delete. The targeted row mutants are in ev/mutants.txt. The ledger moves on a merged-to-open mutant. It does not move on a wrong SHA, which is checked by record_row.py's byte-equality with REST facts and here by git (ev/row-shas.txt). Carry: dismissed: evidence, not a finding
- Merge with origin/main 505ed38: `git merge-tree --write-tree` rc=0, with no conflict and no claim file touched (ev/merge-tree.txt).
- CI at this head: `merge_train.py classify` prints GREEN, pending none, red none, rc=0 (ev/classify.txt). No red at the head, so no `## Red checks` answer is owed (ev/owed-reds.txt).
- Role contracts: `git diff merge-base...origin/main -- dev/governance/roles/` is empty, so this contract is current.
- Finder's harness: none. This is a record beat, not a finding fix, so steps 2, 3, 6 and 9 have no subject.
- No golden or claim file is in the diff, so step 4 has nothing to compare.

## Findings

- Note: stale-body: the `## Head` section says the head was computed against main at `e4c929b`. The base and the row commits' parent is f269ecc, which postdates it and whose own row is in this diff. This is paperwork, not code, and the rows are correct at the actual base. Carry: dismissed: record-beat body wording, no stage depends on it
