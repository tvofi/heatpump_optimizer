Fix review: blocked 6b5d99b5c48036517be86310c773e8e8a66cbe14 merge-conflict: tools/audit/carry_audit.py conflicts with origin/main 17e621f08 (#3318)

bus-nonce: 1c57d1691e7facd69e3bbc2a05035edf

## Block

- Real content conflict with main in tools/audit/carry_audit.py, not a claim file (fix-review.md step 13; owner ruling 2026-11-07 blocks on main only for a real merge-tree conflict, which this is). `git merge-tree --write-tree origin/main 6b5d99b5c48036517be86310c773e8e8a66cbe14` prints `CONFLICT (content): Merge conflict in tools/audit/carry_audit.py` with stages 1 d0bd566, 2 9d54406 (main), 3 6c93f4b (head); no MERGE-CLAIM marker, since no claim file is involved. Main's side is #3318 (merge 17e621f08), commits d4a05c81f (own-group carry index as a status line) and c77a4c037 (self-test pin), and it rewrites the same `landed()` loop body that this PR changes to land a source only through a carry (`group_text(..., brief=False)`). A reviewer cannot know what the merged `landed()` should be, so the fixer resolves it by merging origin/main and re-running steps 2-8 (fixer.md); the round after that reviews the resolution. Carry: R10-CARRY-RESIDUE-2

## Findings

## Evidence

- Head reviewed: 6b5d99b5c48036517be86310c773e8e8a66cbe14; `git ls-remote` shows refs/pull/3325/head and refs/heads/fix/r10-carry-residue-2 both at it (ev/ls-remote.txt). origin/main at review time: 17e621f08c4feec724478573741fbd8b596ceaba (ev/HEAD.txt).
- Merge base: 4fe7d5934b0a4bc092c9398f29b579fbd2df8b50. The three-dot diff touches 9 files, +144/-30. The head-side carry_audit.py change is in ev/head-carry_audit.diff and main's in ev/main-carry_audit.diff.
- merge-tree output in ev/merge-tree.txt. review_packet.py render refused with signal `structure` ("head does not merge cleanly with origin/main", naming carry_audit.py) and still wrote the packet (ev/review-packet.md).
- Round: first round.
- Not done, because the conflict blocks it: mutation proof, finder-harness RESULT lines, the merge_train classify wait for CI, the check-run red audit, and tests/entities.py. A DIRTY PR does not run CI for its merged result (claim-files.md), and measuring a tree that cannot merge would not cover what lands. The next round re-takes all of these at the resolved head.
