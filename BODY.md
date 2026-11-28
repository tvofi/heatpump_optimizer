R11-HOTFIX-MAIN-FAST. Main a59a1b0d9a (#3940's merge, R11-OWNER-FEATURES-SPLIT) is red on `tests / fast (3.14, 1/4)` (job 141046932402, run 46166992651). The failing script is `tests/entities.py`, in its freeze section "The tests/features.py freeze (R11-OWNER-FEATURES-SPLIT)". It prints:

`FAIL tests/features.py keeps the freeze: ... [lines: tests/features.py has 104990 lines, above the 104695 tests/features_frozen_budgets.json records; ...]`

The span's two null controls, span ids and seam home, also print FAIL. Each one only repeats that live `lines` refusal, which they inherit from the live tree.

**Cause: a baseline race between merges.** #3940 recorded `lines` = 104695 with `features_freeze.py --record` at its own branch head. That head merged main `cb2026c3b5`, which did not yet contain two PRs that merged to main before #3940:
- #3925 (`98541868ad`) added 130 lines to `tests/features.py`, inside existing spans.
- #3934 (`ac9045c223`) added 165 lines, inside existing spans.

Measured with `git show <ref>:tests/features.py | wc -l`, the counts are: #3940's head 104695, `98541868ad` 104825, `ac9045c223` 104990, a59a1b0d9a 104990. Each PR was green alone, and the merge result is red. Neither PR added a span id, so only the `lines` condition fires.

#3940 changes no production behaviour, so no revert is warranted. Only its manifest's baseline is stale.

**The fix.** I re-ran `python3 dev/audit/harnesses/features_freeze.py --record` on origin/main a59a1b0d9a. It moved one line, `tests/features_frozen_budgets.json` `lines` 104695 -> 104990. `spans` and `seam_pins` are byte-identical. The manifest was not edited by hand.

## Raise justification

This is a `lines` raise (MAX key) of `tests/features_frozen_budgets.json` under budget-raise-gate, at 104695 -> 104990. It is made under mandate 6893738184, scope `all`.

- What the raise records: the 295 lines were already on main before the freeze merged, from #3925 and #3934. The raise records the file as it stood at the freeze's merge result, and `tests/features.py` grows by nothing in this diff. #3940 meant to freeze the file at its state when it landed, and recorded it one race earlier. The race: #3940 recorded the manifest at its branch head instead of at the merge result.
- Payments tried: three, numbered below.
  1. Move the 295 lines (the #3925 and #3934 tests) out of `tests/features.py` into seam scripts, which nets `lines` back to 104695. This is not hotfix-sized, for three reasons:
     - Both additions sit inside spans that already exist, so a move splits an existing section's tests away from it.
     - Their mutation-ledger `killed_by` rows would need re-keying.
     - The first seam script must ship with its `tests/run.sh` line, a closure from `tests/derive_closures.sh` on Linux (a full derivation off Linux is forbidden, per `gate-scoping.md`), a `case_select.SCRIPTS` entry, and a `tests/ci_budgets.json` raise of 2 on both `script_runs_per_push` and `script_runs_full_case_pr`. That raise is a second budget raise, larger than this one.
     Meanwhile main stays red for every push.
  2. Net the 295 lines out elsewhere in `tests/features.py`. This would delete or compress working tests merely to fit, which rule 2 forbids.
  3. Revert #3940. Refused: the freeze is sound, and its only defect is the stale baseline.
- Architecture score: dS +0.0000 NULL

  The score was printed by `python3 tools/audit/archscore/score.py --diff origin/main HEAD` at head 4f6d53ba25. No gate metric moved.

## Head

`4f6d53ba2528078834e4ef30e17e51f1c89f62bf`, one commit on origin/main `a59a1b0d9ac782fabbe01eb84f4d4ff5a17aee43`. The diff is `git diff a59a1b0d9a...4f6d53ba25`, one file, one line.

## Mutation proof

Each mutation was applied to `tests/features_frozen_budgets.json` in a detached worktree at the head, checked with `python3 dev/audit/harnesses/features_freeze.py --check`, then restored with `git checkout`:
- M1, `lines` 104990 -> 104989: `lines: tests/features.py has 104990 lines, above the 104989 ... records` / `FEATURES FREEZE: REFUSED (1 refusal(s))`, rc=1.
- Unmutated head: `FEATURES FREEZE: HOLDS (0 refusal(s))`, rc=0.

## Null control

The manifest from a59a1b0d9a (main, unmodified) prints `lines: tests/features.py has 104990 lines, above the 104695 tests/features_frozen_budgets.json records; ...` / `FEATURES FREEZE: REFUSED (1 refusal(s))`, rc=1. CI's job 141046932402 printed the same refusal. This is the failing check, and it fails before the fix.

## Figures

none

## Red checks

- `tests / fast (3.14, 1/4)` on main a59a1b0d9a (run 46166992651) is the red this PR repairs. A cheaper detector exists: `features_freeze.py --check` run on the merge result rather than the branch head would have caught it at #3940's train admission. Its cost test and countermeasure belong to the separate defect-root-cause seat, with this root-cause candidate: the freeze manifest was recorded at a branch head instead of the merge result. Any PR that grows `tests/features.py` and merges between a manifest record and that manifest's landing reproduces it.
- `budget-raise-gate` is red until the mandate approval lands at this head: `tests/features_frozen_budgets.json: lines: 104695 -> 104990`. That is the raise `## Raise justification` answers. No cheaper detector applies, because the gate is itself the detector, working as designed.

## Forward-carry

none

## Friction

none
