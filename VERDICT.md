Fix review: merge 7786d6e6b40b5694000c8f6222a9be56b4a3a075

bus-nonce: 148ec9344d8705f503d34a7b42eb0c6d

Round 2 of #3143, a delta re-review of the round-1 block (unpinned-site, cite_why's ancestry clause). Head measured: 7786d6e6b40b5694000c8f6222a9be56b4a3a075 (detached worktree). Not the fourth round.

## Findings

none

## Evidence

- Round-1 mutant R11, run with the round-1 reviewer's harness (verdict/3143 ev/rev_mutants.py): at e323d7550 `RESULT mutant=R11 rc=0 fails=0` (survives, reproduced); at the head `RESULT mutant=R11 rc=1 fails=5` (ev/R11_newhead.txt). The killing arms are "set-size refuses a cite whose sha exists but main does not hold it" and the set-files twin, among others.
- My own mutants on the new arm, ev/own_mutants.txt: O1 (is-ancestor arguments reversed) `rc=1 fails=5`; O2 (ancestry replaced by a bare cat-file existence check) `rc=1 fails=5`. Both killed.
- Null control: the accepting paths still pass, namely the existing `main@<main tip>` set-size arm and `set-files --add ... --cite cited@<sha>`, where `cited` holds the sha. The self-test is 0 failed at the head.
- Scope: `git log e323d755..HEAD` (ev/log.txt) shows c3a46a1c2 as the only branch-authored commit; the rest are merges of origin/main. `git diff e323d755 HEAD -- roster_edit.py r10_roster_ops_mutants.py` is byte-identical to c3a46a1c2's diff for those two files (+8 and +5 lines), so the merges brought nothing into either. Files this PR touches that the merges also touched: exactly those two, and both are c3a46a1c2's alone. PR files three-dot against main: delivery/3143.md, instruments/roster_edit.py.md, r10_roster_ops_mutants.py, roster_edit.py (ev/pr_files.txt).
- `roster_edit.py --self-test`: 169 checks, 0 failed (ev/selftest.txt). `r10_roster_ops_mutants.py --self-test`: 144 checks, 0 failed. Both match the body's figures.
- Full mutants table at the head (ev/mutants_table.txt): `plants: 46, without a FAIL line: ['C6']`. C6 sits in the pre-existing block and fails identically on origin/main (`rc=1 fails=0` with a KeyError crash, ev/C6_on_main.txt); it is a crash-kill, not a survivor, and not this PR's. Null is rc=0 fails=0; every Z and R11 plant is rc=1 with FAIL lines. The body's count of 13 new-block plants re-derives (grep prints 13).
- Merge: `git merge-tree --write-tree origin/main 7786d6e6b40b5694000c8f6222a9be56b4a3a075` rc 0 (ev/merge_tree.txt). Claim files byte-identical to origin/main. `tests/structure.py`: STRUCTURE RATCHET PASSED. Delivery row present in the three-dot diff (dev/programme/delivery/3143.md). No host path added.
- CI: `merge_train.py classify 7786d6e6b40b5694000c8f6222a9be56b4a3a075 --pr 3143` exits 0: `GREEN 7786d6e6b40b5694000c8f6222a9be56b4a3a075 pending: none red: none`. The packet's check digest at render had a few runs in progress; all concluded green or skipped by the classify run.
- The body's `## Head` names 7786d6e6b40b5694000c8f6222a9be56b4a3a075 and `## Red checks` says none; its whole-check-set read was taken at e323d7550, and the classify GREEN above covers this head with no red.
- Packet: Refusals none, carry_audit 1 routed, 0 unrouted, figures 3 resolved and 1 not verified (the merge-tree command line).
