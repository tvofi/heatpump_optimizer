Fix review: merge 53d38475ef2f31f5baf17bd2c9c171881b8ccf17

bus-nonce: 08a0a72da5be5e217f7e0bc8709e0412
pending-ci: gate

## Scope

Round 3, a later round over the reviewed head 6ee7ba56e48bdeb1b8d1c05cb7a9df3a43c17daa. The packet's `## Review scope` reads `delta`, and the previous verdict at 6ee7ba56e48b had no findings to resolve. The delta is three merge commits: 4e8c918de7df, 948ce9050b71 and 53d38475ef2f. `review_carry.py` prints FRESH-REVIEW because 4e8c918de7df is not the automatic merge of its parents (ev/review_carry.txt). The delta has no `custom_components/` line, so nothing widens the review. What was reviewed is that merge's hand resolution plus the PR's own three-dot diff, compared with the one reviewed before.

## Findings

none

## Evidence

- Resolution, `tests/layout.json` (from `--remerge-diff`, ev/remerge_diffs.txt):
  - The only conflict hunk is the `root` globs. One side has this PR's `"CODE_OF_CONDUCT.md"`, the other has main's `"ROADMAP.md"`, and the resolution keeps both once each.
  - 948ce9050b71 and 53d38475ef2f show an empty remerge-diff, so they are automatic merges.
- Own diff unchanged: `git diff <mb>...6ee7ba56e48b` and `git diff b425502da8...53d38475ef2f` touch the same 11 files with 358 insertions. They differ only in index hashes, hunk offsets and main's neighbouring context lines in `scopes.json` and `layout.json` (ev/own_diff_old_vs_new.txt).
- Community files: `git diff 6ee7ba56e48b 53d38475ef2f -- CODE_OF_CONDUCT.md .github/ISSUE_TEMPLATE/` is empty (ev/body_checks.txt).
- Body read-back figures re-derived (ev/body_checks.txt):
  - The `tests/layout.json` diff against merge base b425502da8 is the single added line `"CODE_OF_CONDUCT.md",`, as the body states.
  - The merged file loads as JSON.
  - The merge base of 4e8c918de7df with origin/main is 92d38ecb640b, as the body states.
- Mutant on the resolution: deleting `"CODE_OF_CONDUCT.md",` from the merged `tests/layout.json` makes `tests/layout.py` exit 1 with `placement: CODE_OF_CONDUCT.md is in 0 categories` (ev/layout_mut_coc.txt). The head exits 0 (ev/layout_head.txt). So the PR's line survived the resolution and still carries its check.
- Cheap checks at the head, all exit 0:
  - `tests/layout.py`
  - `check_scopes.py --repo .`
  - `tests/structure.py` (STRUCTURE RATCHET PASSED)
  - `tests/env_drift.py --claims-only origin/main`
  - `closure.orphan_files()` returns `[]`
  - Files: ev/layout_head.txt, ev/scopes_head.txt, ev/structure_head.txt, ev/env_drift_claims.txt, ev/orphan_files.txt.
- Merge: `git merge-tree --write-tree origin/main 53d38475ef2f` (origin/main 54cb72116423) exits 0, so there is no conflict (ev/merge_tree.txt).
- Untouched across b425502da8...53d38475ef2f: `VERSION`, the manifest and `RELEASE_NOTES.md`. The role contracts are current: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty.
- CI: `merge_train.py classify 53d38475ef2f... --pr 3628` was polled every ~90 s for about 30 minutes. Every run exited 3 with `WAIT 53d38475ef2f31f5baf17bd2c9c171881b8ccf17 pending: gate red: none` (ev/classify_log.txt), so this verdict carries `pending-ci: gate`. At the last read (ev/check_runs.txt), `tests / lane-proofs` was queued, and the test lanes had finished.
  - The packet's digest read `gate` failure and `tests / nightly-status` failure.
  - `nightly-status` is not in the `merge_train.py owed-reds` set, so it is neither answered nor a block.
  - The body's `## Red checks` answers `instrument-self-tests`, which is also outside the owed-reds set.
- Steps 1–3 and 14–16 were carried from the round-2 verdict, because the PR's own diff is unchanged. No finder's harness is named.
