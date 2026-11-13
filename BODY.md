brief_lint data: re-anchor carry-1412's stale control by phrase and delist it from the legacy control files (R10-HOTFIX-CARRY-1412-CONTROL).

`dev/archive/carries/carry-1412.json` was on the legacy control list only because its first control cited `custom_components/heatpump_optimizer/optimizer.py` at a line whose statement has left the module. That error depended on the line number. A diff that grows the optimizer puts an identifier near the old line, the citation resolves by accident, and the legacy check in `tools/policy/brief_lint.mjs` reports `LEGACY-CONTROL VACUOUS: carry-1412.json: its controls lint clean without the exemption`. That is the red `tests / briefs` on #3481 and #3511.

The control now names the statement it describes by quoted phrase, with no line number: `solar_fraction = min(future_solar_6_12h / max(typical_heat_loss * 6, 0.1), 1.0)`. It resolves the same wherever the module's lines move. Because the control now lints clean, `carry-1412.json` leaves `tools/policy/legacy_control_files.json`. Since #3525 moved that list out of the pinned grader, the delisting is data-only, and the base grader grades this head directly. No bootstrap is needed.

`LEGACY_CONTROL_CAP` stays at 14. It is a ceiling checked with `>`, and lowering it would edit the pinned grader.

Merge route: the ordinary one. This pull request cures #3481 and #3511. Each needs main merged in after this lands.

## Head

d65839f2e2984e0106dd6896f1f79a7bccfabb6b, on main 7eadd75f3c420404aabc83d4b05f9691f3e49136.

## Mutation proof

Each mutation below, applied to this head, is measured with the base grader's functions on the head's tree:
- Put `carry-1412.json` back in `tools/policy/legacy_control_files.json`. `staleLegacyMembers` then returns `carry-1412.json: its controls lint clean without the exemption: remove it from LEGACY_CONTROL_FILES`, so `node tools/policy/brief_lint.mjs` goes red with LEGACY-CONTROL VACUOUS.
- Restore the stale control and keep the file delisted. `lintCarryFile` with no exemption then reports one control error, `custom_components/heatpump_optimizer/optimizer.py:4671: 'p_max' not found near custom_components/heatpump_optimizer/optimizer.py:4671; found at line 32 instead`, so the run goes red.

`node tools/policy/brief_lint.mjs` with the base grader 7eadd75f3c, before and after:
- before, main 7eadd75f3c merged with refs/pull/3481/head: `rc=1` `LEGACY-CONTROL VACUOUS: carry-1412.json: its controls lint clean without the exemption: remove it from LEGACY_CONTROL_FILES`
- after, this head merged with refs/pull/3481/head: `rc=0` `LEGACY-CONTROL ok`
- before, main 7eadd75f3c merged with refs/pull/3511/head: `rc=1`, the same VACUOUS line
- after, this head merged with refs/pull/3511/head: `rc=0` `LEGACY-CONTROL ok`
- this head: `rc=0` `LEGACY-CONTROL ok`

The re-anchored control cites no line number. `lintCarryFile` with no exemption finds 0 control errors in it on main, on main merged with #3481, on main merged with #3511, and with ten lines inserted into or deleted from the optimizer module around the old cited line. That count is from `lintCarryFile`, whose code #3525 did not change, run under the grader at 83e4e83d77.

## Null control

Plain main 7eadd75f3c, base grader: `rc=0`, `LEGACY-CONTROL ok`. It is unchanged by this head, whose own run is also `rc=0`.

`tools/pr/ci_predict.py --base origin/main` at this head: `CI PREDICT: no closures, fast, governance or instrument red predicted against 7eadd75f3c42 (a data-file read is not seen)`, rc 0.

The head also merges cleanly into main 3b9749dac5: no commit since 7eadd75f3c touches `tools/policy/`, `dev/archive/carries/` or the optimizer module.

## Figures

none

## Red checks

The red `tests / briefs` on #3481 and #3511 (`LEGACY-CONTROL VACUOUS: carry-1412.json`) is the trigger.

No cheaper detector of that red existed at the producing pull requests. The red was correct: the grader saw that an exemption was no longer needed. #3481 and #3511 were not wrong. The cause was a legacy member whose only control error was a line-number miss, which any diff that shifts the module can cure.

Neither PR's own prepr could have flagged it either. `tools/pr/ci_predict.py` prints `(a data-file read is not seen)` for a grader whose verdict turns on a data file outside the diff.

The countermeasure is #3525's move of the list to unpinned data. Delisting is now a one-step, data-only repair, and this pull request is that repair.

## Forward-carry

none

## Friction

none
