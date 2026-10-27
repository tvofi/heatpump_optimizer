Fix review: merge 0e3b89f23c35a89f605e9611d5d074d800783b5b
bus-nonce: 8c342fa9d63059fd2159f133a6075eb9

Round 1. Measured at head `0e3b89f23c35a89f605e9611d5d074d800783b5b`, re-read live immediately before publishing: `OPEN`, still that head, `MERGEABLE`. Record-only PR; every arm below is a read or a grep. Evidence: `~/hpo-seats/r10s6/review-2885-r1/evidence/` (files named per arm).

## Evidence

- **R1, record-only.** `git diff --name-status origin/main...0e3b89f23c` (`r1-file-list.txt`) lists exactly nine paths, all `dev/programme/delivery/<N>.md`: modified 2745, 2819, 2869, 2871, 2874, 2880, 2881, 2882; added 2885. The complement of that glob is empty — no `custom_components/`, `tools/`, `tests/` or policy path. Diffstat 9 files, +9/−8; every one of the nine files is exactly one line.
  Carry: dismissed: verification arm, not a finding
- **R2, each changed line re-derives.** All eight named SHAs are ancestors of `origin/main` whose subject is `Merge pull request #<n>`, and each equals the live API's `mergeCommit.oid`/title/state MERGED (`r2-row-rederivation.txt`). Four shown: #2745 `34cd75bf1fe506334611ba6c074c223317370e67` "Merge pull request #2745 from tvofi/fix/r10-sav-comfort"; #2819 `4f3c7302046eccd1f869724a6de2cbf6f8183418` (#2819); #2874 `524c1896b6943b3da03d6cad61420ced31e14c9c` (#2874); #2882 `4db1d3e28f0dff50f6916e39d52efed0ce856d0a` (#2882). Re-deriving each rewritten file with the generator's own `record_row.row_line` against the roster at the head prints `MATCH` for all eight, byte for byte.
  Carry: dismissed: verification arm, not a finding
- **R3, the self-row is honest.** `dev/programme/delivery/2885.md` reads `**open**, record: delivery rows (autofix)` (`r3-self-row.txt`); PR 2885's API state is `OPEN` at this head, and the line cites no head SHA, so it cannot be stale about one. It is the generator's `OPEN_ROW_TITLE` pre-merge line, not a `merged` claim before the merge.
  Carry: dismissed: verification arm, not a finding
- **R4, the set matches the window.** `r4-window-reconciliation.txt`: in the record window (`v7.0.4..0e3b89f23c`) there are 215 PR merges — 209 rows tell their merge (the eight rewrites among them), 6 are record-class merges that owe no rewrite (`stamp.merge_is_record_class` true: 2795, 2845, 2847, 2856, 2863, 2868), 0 merges lack a row, 0 non-record rows remain stale. `python3 -I tests/delivery_status.py` at the head prints `215 rowed, 3 pending, 0 overdue`; the three pending are #2877, #2879, #2884, which merged after this PR's base and each already carries a row written by its own branch.
  Carry: dismissed: no gap; pending is the ordinary batch state
- **No red check to answer.** `gh api --paginate .../commits/0e3b89f23c/check-runs` (`checks-head.tsv`, `checks-summary.txt`) returns 58 runs at this head: 36 success, 20 skipped, 2 queued (`refresh`, `prelude`), 0 failing; `gate`, `pr-contract`, `governance / delivery-status` and `tests / mutation` are success. The earlier head `fddc5809b`'s runs are 4 cancelled (superseded), 10 skipped, 0 red. So `defect-root-cause.md`'s second trigger has no moment here.
  Carry: dismissed: no red check at this head
- **Other arms.** `git merge-tree --write-tree origin/main 0e3b89f23c` exits 0 with no conflicting path (`merge-tree.txt`); `record_row.py --automerge-check --pr 2885 --head 0e3b89f23c` prints `AUTOMERGE OK` (`automerge-check.txt`); `VERSION`, the manifest version and the `RELEASE_NOTES.md` heading are untouched, since no such path is in the diff.
  Carry: dismissed: verification arm, not a finding
- NONBLOCK: five rewrites (#2819, #2871, #2874, #2880, #2881) drop the group suffix their `**open**` line carried, because `roster_lib.group_for_branch` matches `resume.branch` or the branch's last segment exactly and those merges rode `...-pr` branches (`fix/r10-arch-shapes-pr` vs group `R10-ARCH-SHAPES`, whose `resume.branch` is `handoff/r10-arch-shapes`). The merge fact is unchanged, and the PR body discloses the neutral phrasing ("a row whose subject no roster group claimed carries the neutral phrasing").
  Carry: dismissed: body discloses neutral phrasing
- NONBLOCK: #2877, #2879 and #2884 still read `**open**` at `origin/main`; `tests/delivery_status.py` classes them pending and not overdue, so their upgrade is the next beat's, outside this PR's base.
  Carry: dismissed: next beat upgrades them
