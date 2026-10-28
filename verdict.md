Fix review: merge ceb41a60bfe094903a2aac8b5f3f07af4cef83a4

bus-nonce: 63c5cfb0b5c3f5efe4282ee6865bf087

## Round

Round 1. Measured head: ceb41a60bfe094903a2aac8b5f3f07af4cef83a4, which was still the PR head when this verdict was written.

## Findings

- `tools/audit/seat/gh_read.py:12` ("stated once in `INSTRUMENTS.md`") and `tools/audit/seat/cloud_dispatch.py:29` ("INSTRUMENTS.md has the measured shape of a cloud seat") now point one hop short: the text they mean is in `instruments/app_push.sh.md` and the cloud-seat entry, which the index links. The PR body dispositions both as resolving through the index, and the pointer still leads there in one link. Carry: dismissed: still resolves through the index, which links every entry and is pinned by the new --check index rule

## Evidence

- Roles current: `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty.
- Mutation proof (ev/mutants.txt), my own mutants at the head:
  - The owner's mutant: deleting the `push.sh` index line makes `--check` print `UNINDEXED tools/audit/seat/instruments/push.sh.md` and `1 index gap(s)`, and it exits with rc=1.
  - Replacing the UNINDEXED append with `pass` gives `26 checks, 3 failed`, the same three names as the body.
  - The same for MISMATCH, DUPLICATE and MISSING-file: `26 checks, 1 failed` each, each failure naming its own arm.
  - Making `report()` ignore the gaps: `1 failed` (the rc arm).
  - A real-tree label mismatch (`push.sh` to `pushx.sh`) gives a MISMATCH gap.
  - Every gap kind is pinned. Restored, the self-test reports `26 checks, 0 failed`.
- Null control: the unmutated head prints `--check`: `99 self-testing, 99 wired, 0 unwired` and `0 index gap(s)`, rc=0.
- Move proof (ev/move_proof.txt), rebuilt with my own script rather than the fixer's:
  - From the first commit 9a3a11edd, I removed the index's added sentence and replaced each linked line with its entry body minus the title. The result is byte-identical to the merge base's `INSTRUMENTS.md` (`cmp` rc=0).
  - The second commit changes entry text only in `instruments/selftest_wiring.py.md` (+5 lines), as the body says.
- Figures, re-derived:
  - 83235 bytes at the base and 12060 at the head.
  - 76 entries at the base and 76 files at the head.
  - The body's "merge base b6f6ceca4" is the pre-merge base. `INSTRUMENTS.md` is identical at b6f6ceca4 and b0b2d7697, so the figure holds at the actual base.
  - corpus `~66398 tokens, cap 66434` at the head. `--corpus-filter` lists 0 `audit/seat` paths, so the guide is outside the corpus and the flat claim follows.
  - `MODE: SCOPED -- 0 script(s) run, 33 scoped out`.
  - `STRUCTURE RATCHET PASSED`, `ALL 2467 ENTITY CHECKS PASSED` and `ALL 112 HARNESS HEADER CHECKS PASSED` (ev/merge_and_checks.txt).
- Harness: the finding names no finder's harness. The packet shows "none named", and the owner's order (R10-FLY-INSTRUMENTS-SPLIT) is a restructure with the owner's mutant as its test. The check that pins it is the extended `selftest_wiring.py --check`, which is the fixer's own and is disclosed as such. I graded it with my own mutants above.
- Class (step 6): one seam, the guide and its entry files. Programmatic readers of the guide (`git grep INSTRUMENTS`) are `tests/entities.py`, which pins the path string and still passes, plus two docstrings (see Findings). There are no `INSTRUMENTS.md#` anchor citations (ev/citations.txt).
- `VERSION`, the manifest and `RELEASE_NOTES.md` are untouched. No golden or claim file is touched, and no budget, closure or ledger moves.
- Merge:
  - `git merge-tree --write-tree origin/main ceb41a60bfe094903a2aac8b5f3f07af4cef83a4` exits 0 against b0b2d7697.
  - It exits 0 again against the moved main 593f57c44 (tree 54f5a981a). No main commit since the base touches the guide or `selftest_wiring.py`.
  - The merged tree's index rule prints `0 index gap(s)` (ev/merge_new_main.txt). That run extracted only `tools/audit/seat`, so its self-testing count of 54 is partial and only the gap line is the evidence.
- CI on this head (ev/check_runs.txt): all 55 check runs completed, none red. Every one is success, skipped or neutral, including `governance / instrument-self-tests`, `gate` and `budget-raise-gate`. There is no red check, so no root-cause answer is owed. The body's "Red checks: none" matches.
- Head named in the body: the body names ceb41a60bfe094903a2aac8b5f3f07af4cef83a4, with authored code head 89078deb1 and a delivery-row-only commit on top. That matches the head measured.
- Forward-carry: none claimed, and none needed. The change alters no later stage's procedure.
