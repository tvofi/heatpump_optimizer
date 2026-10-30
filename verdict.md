Fix review: merge 95342761df4fe8a78dca8da71cd7aaa9b3618ce7

bus-nonce: 210b1901345959c2212966a2438c4ef6

## Round

Round four (the body's `## Re-cut`). The diff at this head, three-dot against origin/main `039eee1dc`, is one added check in `tests/features.py` (+27) and the PR's own row `dev/programme/delivery/2975.md` (+1). It adds no production line. The production change of R10-COP-GATE part 1 (`c9bf05dfe`) is already an ancestor of origin/main.

## Findings

- The body's `## Friction` says the group's carry list "holds 16 entries", and `## Forward-carry` gives a disposition for carries 1–16 only. At this head the roster entry `R10-COP-GATE` in `dev/programme/rosters/wave-r10-groups.json` holds 18. Carry 17 (driver-interface mirror, restating carry 14) and carry 18 (from the R10-UX-HEALTH design review, written "For COP-GATE part 2") were added by `roster_sync`/`roster_edit append-carry` on 2026-10-28. Both already sit in the destination that part 2 reads, so nothing is lost, but part 2 must count 18, not 16. Carry: R10-COP-GATE

## Evidence

- RESULT head-reviewed: 95342761df4fe8a78dca8da71cd7aaa9b3618ce7. Re-read at the end of the review, the PR branch `fix/r10-cop-gate-r4` still resolves to this SHA, and origin/main is still `039eee1dc`.
- RESULT role-file: `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty (the merge base is origin/main).
- RESULT null control: a detached worktree at the head runs `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python tests/features.py` and prints `ALL 4586 FEATURE CHECKS PASSED`, rc=0, with the new check `ok` (ev/features-base.txt). The body's 4583 was taken at `c9bf05dfe`; main has added checks since.
- RESULT mutation m10: `coordinator.py` `if pairs_interval(elapsed):` -> `if True:` prints `1 of 4586 FEATURE CHECKS FAILED`, the new check `[{'1 min': (1, 0), '30 min': (1, 1), '3 h': (1, 0)}]`. This matches the body (ev/features-m10.txt).
- RESULT mutation drawguard: removing the draw reader's `and pairs_interval(...)` term prints `1 of 4586 FAILED`, `[{'1 min': (0, 1), '30 min': (1, 1), '3 h': (0, 1)}]`. This matches the body, so the check reads each of the two readers separately (ev/features-drawguard.txt).
- RESULT mutation m8: `accuracy.py` `0.05 <= elapsed_h` -> `0.0 <= elapsed_h` prints `2 of 4586 FAILED`: the existing bounds check plus the new one, `[{'1 min': (1, 1), '30 min': (1, 1), '3 h': (0, 0)}]`. This matches the body (ev/features-m8.txt).
- RESULT mutation mhi (my own, not in the body): `elapsed_h <= 2.0` -> `elapsed_h <= 5.0` prints `2 of 4586 FAILED`, the new check `[{'1 min': (0, 0), '30 min': (1, 1), '3 h': (1, 1)}]`. The new check also covers the window's high end end-to-end (ev/features-mhi.txt).
- In every mutant run the 30-minute arm stays `(1, 1)`, so a mutant that broke pairing outright would not pass as a window kill. The in-check null control holds.
- Each mutant was one exact single-match replacement in a fresh `git worktree add --detach` at the head. My wrapper ran under `set -e`, so the mutant runs wrote no `rc=` line after the suite's non-zero exit; the `N of 4586 FAILED` summary is the result.
- RESULT merge: `git merge-tree --write-tree origin/main 9534276` exits 0 (tree `ec7eb795d`), with no conflict and no MERGE-CLAIM line (ev/merge-tree.txt). `git diff origin/main 9534276` is exactly the 28 added lines, so the orchestrator's recarry merge brings in nothing beyond main.
- RESULT untouched: the three-dot diff touches none of `VERSION`, `manifest.json`, `RELEASE_NOTES.md` or either claim file. Nothing for `env_drift.py --all` to compare: no fixture or claim moved.
- RESULT CI at head (check-runs API, read after all workflows concluded): every completed check is success or skipped, and none is red. `tests / fast (3.14)`, `tests / closures`, `tests / coverage`, `tests / coverage-ratchet`, `tests / mutation`, `governance / instrument-self-tests`, `governance / env-matrix`, `arch-score` and `budget-raise-gate` are success. `pr-contract / pr-contract` (job 124028398680) started 11:05:09Z, after the last workflow concluded, and concluded success, so it checked the body's `## Red checks` for the range. That run is the evidence for step 11. One `prelude` job (run 41042254198) was still `in_progress` at read; it is not a gate check.
- `tests / mutation` is green, but the diff writes no production line, so it drew no mutant from this diff. The mutation evidence is the hand mutants above.
- Finder's harness: none is named (packet), as in the earlier rounds of this group. The block being answered (verdict/2917) named mutants, not a measured figure, so the mutants above are the instrument.
- Step 6 class: the body names the window's two readers (accuracy sample and draw fold) as the class. `grep pairs_interval custom_components` returns the definition (`accuracy.py:784`) and exactly two call sites (`coordinator.py:9765`, the draw reader, and `:9800`, the accuracy reader). Both are covered.
- Step 14: the diff moves no budget, ledger, closure, claim or score file.
- Not re-derived: the body's ledger-tool figures at `836198dbb` (`PIN RE-VERIFICATION: 2 reproduced`) and its `run_always` and `ci_predict` lines. CI's runs at this head supersede them, and I did not re-run them.
- I built no instrument. The mutant driver is a throwaway wrapper around the suite command the body names.
