Fix review: merge 8993af01a55631987d4857314b41a342576bd658

bus-nonce: dd79003e82b897e30cc7a52d8374a596

## Scope

Round 1, full scope. Record-only diff: 21 files, all `dev/programme/delivery/<N>.md` row files (20 rewritten or added as merged, plus this PR's own row as open). No production, test or check code; `VERSION`, the manifest version and `RELEASE_NOTES.md` are untouched (0 paths). The role contract matches main (`git diff <merge-base>...origin/main -- dev/governance/roles/` is empty).

## Findings

- Mutant M3 (a merged row's sha changed to `1234567`) survives `tests/delivery_status.py --require-rows` (rc 0). That is how the check is designed: `anchored()` says the merge sha is not part of a row's anchor, because the record PR's own row is written before it merges. No check reads the sha in a row, so this review checked all 20 shas by hand (see Evidence). Carry: dismissed: the instrument is designed this way and documents it in `anchored()`; every sha in this diff was verified by hand

## Evidence

- Head: the PR body's `## Head` is `8993af01a55631987d4857314b41a342576bd658`, the head reviewed here. Base and merge base: `baa9a46`.
- Rows checked against main (ev/rows_verify.txt): for each of the 20 merged rows, the quoted short sha resolves to a commit that is an ancestor of origin/main, and that commit's subject is `Merge pull request #<N>` for the same N as the row file. 20 of 20 match. Row 3844 reads `**open**`, which is correct for an open PR.
- Delivery-status at the head (ev/delivery_status_head.txt): `DELIVERY STATUS OK — 21 rowed, 0 pending, 0 overdue`. That is 20 merged rows plus this PR's own row, the same count the body lists.
- Mutation proof (ev/mutants.txt), using `delivery_status.py --require-rows`: M0 unmutated rc 0; M1 deleting row 3851 gives rc 1 (1 pending); M2 setting row 3728 back to `**open**` gives rc 1 (1 overdue); M3 wrong sha gives rc 0 (by design, see Findings).
- Merge with main (ev/merge_tree.txt): `git merge-tree --write-tree origin/main 8993af01a55631987d4857314b41a342576bd658` exits 0, so there is no conflict.
- CI (ev/classify.txt): `merge_train.py classify 8993af01a55631987d4857314b41a342576bd658 --pr 3844` printed `GREEN 8993af01a55631987d4857314b41a342576bd658 pending: none red: none`, rc 0.
- Red checks: no red at this head. The body's `## Red checks` answers `record`, `nightly-status` and `delivery-status` as reds that may be standing on main. None of them is red at this head. Owed-reds set (ev/owed_reds.txt).
- Finder's harness: none. A record beat has no finder. The figure the body quotes names its instrument (`tests/delivery_status.py`), and this review re-ran it at the head (above).
- Claim files and goldens: not touched by the diff, so step 4 does not apply.
