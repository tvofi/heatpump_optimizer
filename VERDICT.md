Fix review: blocked 9894911a81cdceb51eecec093a2527f93576d34e red-check: pr-contract red at this head on the body's stale scope-line figure block (body-only; code review complete, no code finding)

bus-nonce: 726c78d84bb93219cfb28be599619661

## Block

`merge_train.py classify 9894911a81 --pr 3662` exits 1: `RED 9894911a81cdceb51eecec093a2527f93576d34e pending: none red: gate`. `gate` fails only on `FAIL pr-contract / pr-contract: failure (run 44147689564)`. The only error in that run is `[figure-block] line 171: block scope-line names head=f52f265d5b8b mb=30991a6b0d4c, this run is head=9894911a81cd mb=5e2ef89b4e73; re-render with figure_block.py refresh <body>`. This is paperwork (C5), and on its own it would be a Note under `merge`. A red head takes no `merge`, though (C8), so the verdict stays blocked until the body is refreshed. Refreshing the body with `figure_block.py refresh` re-runs pr-contract. The code, the tests and the harness below carry no finding, so a re-dispatch at an unchanged diff needs only the live checks re-read.

## Red checks

- `pr-contract / pr-contract` and `gate` are both in the owed-reds set. The cause is a body figure block left stale by the main merge 4e722000ab. The cheaper detector is `figure_block.py verify` on the body, run before the push that merged main. It takes seconds and is in the seat's prepr path. Classified root-cause-detectable. `tests / replay` (1 of 198 replay checks FAILED) and `tests / nightly-status` are red but not in `owed-reds`, so they are neither answered nor a block.

## Evidence

- Round: this is the third review of this PR. Round 1 at 1134fe3655 blocked it with class-open (probe/rev-3662-e230047b). Round 2 is probe/rev-3662-f2fe353e. The packet's scope reads `delta` over 1134fe3655. `review_carry.py 1134fe3655 9894911a81` prints FRESH-REVIEW: 37 branch-only commits, among them the dither-probe redesign d171c345d and the row-to-row judgement 0c822e649/511e53a8e. The delta is a production change in `custom_components/heatpump_optimizer/accuracy.py` (ScaleDither, ScaleProbe) and in `coordinator._fold_measured_cop`.
- Previous finding resolved. RESULT from the round-1 harness `ev/attack_drift_rows.py` (copied to ev/rows.py, 672 intervals, seed 1):
  - At 1134fe3655 it reproduces the block: ±15% p64, ±15% p80, ±30% p96 and the mix at π each give `follows` with the scale at 0.500.
  - At 9894911a81 every row gives `does_not_follow` at scale 1.000. That is identical to the null control, which reads swing0 → 1.000, does_not_follow (ev/B_head.txt, ev/B_prev.txt).
- Perturbation: with the dither removed (`step()` returns `base`), every row reads `pending` at 1.000 (ev/C_swing_under_dither_noop.txt). The harness moves under its own perturbation, and without the dither the probe cannot latch a false `follows`.
- Mutation proof. I made 7 hand mutants of accuracy.py and ran them one at a time through the features block driver (ev/drive.sh, ev/mut.py). All 7 were KILLED (ev/C_summary.txt):
  - dither_noop: 25 checks failed
  - coin_always_plus: 3
  - no_pair_differencing_levels: 17
  - follows_inverted: 18
  - no_bound: 2
  - drop_clamp_reseed: 3
  - follows_no_owed: 3

  The unmutated block prints `ALL 116 FEATURES BLOCK PASSED`.
- Full suite: `PYTHONPATH=tests/hastub python3 tests/features.py` at the head prints `ALL 5875 FEATURE CHECKS PASSED`, rc 0 (ev/D_features_head.txt).
- The commits since 1134fe3655 that are not merges are four `ci: pin killed mutants` commits, and they add only `tests/mutation_ledger/killed_by/*.json`. The `--remerge-diff` output of every first-parent merge is empty. The merge driver resolved `tests/structure_budgets.json` and `tests/closures.json` (LEDGER-MERGE: resolved).
- `git merge-tree --write-tree origin/main 9894911a81` exits 0 (ev/merge-tree.txt). There is no conflict, and the driver printed `LEDGER-MERGE: resolved tests/closures.json`.
- The three-dot diff from 5e2ef89b4e to 9894911a81 leaves VERSION, the manifest version and RELEASE_NOTES.md untouched.
- `git diff merge-base...origin/main -- dev/governance/roles/` is empty, so the contract is current.
- The head re-read at the verdict is 9894911a81, which equals the PR branch tip (ev/HEAD.txt).
- Not re-derived: I ran rows.py with seed 1 only and did not re-run round 1's seed 1–5 sweep. The mutants ran on the features block only; the full script was not re-run per mutant. At the head the null control folds 0 of 672 intervals, against 48 at 1134fe3655. Over this window the probe stays at 1.000 without folding. The features block's follower rows still fail under follows_inverted, so true-follower detection is pinned by tests.
