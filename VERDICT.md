Fix review: merge 77b042d4f51acc23f620914377d9b765fc2c7347

bus-nonce: e5dd7ddcf3db1d7fc6641f7208b678dc

Round 1, a full review. No earlier verdict was posted on #2285: the issue-comments API returned 0 comments and there were 0 reviews.
Measured head: 77b042d4f51acc23f620914377d9b765fc2c7347. Merge base: 8747bbfc4. Worktree: a detached, sparse checkout at that head.
Evidence: /private/tmp/claude-501/-Users-timmalmstrom-heatpump-optimizer--claude-worktrees-round-10-audit-programme-de1185/ab673435-c91c-44f8-bd8e-6fa54b531db8/scratchpad/rev-fahrenheit/ev

## Head (step 7, step 12)
- The body names 0266dab15, and 0a68026da as the code head.
- The live head adds two bot commits on top:
  - 512e5fdda, `ci: pin killed mutants`. It adds one file, the `inputs.py:391` `setpoint_and_unit.GUARD_OFF` pin.
  - 77b042d4f, `ci: merge main`. Main changed no production file this PR touches.
- The three-dot content delta from 0266dab15 to the head is that pin plus closures.json context lines from main.
- `git merge-tree --write-tree origin/main HEAD` against 39b77a467 gives rc=0, with no conflict.

## Mutation proof (step 1)
Each mutant was applied at the head and run with `features_block.py "°F set-points: one unit rule"`, then restored. The tree was clean afterwards.
- M1, the `setpoint_unit` climate predicate set to off: 3 of 5 checks failed.
- M2, `write_setpoint_c` writing the value unconverted: 3 of 5 failed.
- M3, the valve written through the raw `write_setpoint` (P2's wiring): 1 of 5 failed (L1).
- M4, `_RANGE_KEYS` emptied: 1 of 5 failed (L2).
- M5, the `inputs.py:391` `if not entity_id` guard set to off: 1 of 5 failed. The bot pinned this kill at 512e5fdda, so the survivor is killed.

My own mutants:
- R1, `setpoint_range_c` read in the state's unit: 1 of 5 failed.
- R2, `_bounded` with no high clamp: 1 of 5 failed.
- R3, `_bounded` with no low clamp: 1 of 5 failed.
- R4, `write_setpoint_c` ignoring the reading's unit: 2 of 5 failed.
- R5, the arbiter `_write` going through the raw `write_setpoint`: 2 of 5 failed.

At the head: `ALL 5 FEATURES BLOCK PASSED`.

## Finder harnesses at both ends (steps 2, 3)
The base is a `git archive` of 8747bbfc4. The head is the worktree. The sha1 of every harness matches the body.

RESULT surface_units (D12-s3-01)
- base: misdelivered 2 of 6, null 0. Base `--perturb`: 0 and 0.
- head: 0 of 6, null 0.
- At the head it runs through my wrapper, `ev/su_wrap.py`. The wrapper aliases `setpoint_check._read_setpoint` to `inputs.read_setpoint` and restores `pump_arbiter.state_unit`. Neither alias is on the write path.

RESULT setpoint_unit (D7-s6-91)
- base: defect 42.222 K, null 0.000.
- head: 0.000 and 0.000.

RESULT realha_climate (the real Home Assistant 2026.9.3 oracle)
- base imperial: payload 55.0, device 12.778 degC, error 42.222 K.
- head imperial: payload 131.0, device 55.000 degC, error 0.000 K.
- The metric null is 0.000 K at both ends.

RESULT l1_valve_unit (L1)
- base: abs_err 48.8 on both arms, nulls 0.0, perturbed arm 0.0, sibling arbiter climate write 48.8.
- head: the main arms are 0.0 on all four. The perturbed arm stops with `anchor moved`, as the body discloses.

RESULT l2_bounded_climate (L2)
- base: 3 of 4 out of range, null 0, perturbed 0. Its reach arm has `command.dhw=55.0`, 1 outside the range.
- head: the harness raises TypeError on the new signature, as the body discloses. My own adapter, `ev/l2_head_adapter.py`, uses the same states, values and reach arm. It reads 0 of 4 on the climate arm, on a degC instance and on a degF instance (a 44.6..122 degF range), and 0 on both number nulls. The reach arm has `command.dhw=50.0`, 0 outside the range, in degC and in degF.

RESULT companion `r10_fahrenheit_setpoints.py` (written by the fixer and disclosed as the fixer's)
- base: 2, 0, 2, 2, 0, 3, 3, 0.
- head: all 0.
- head `--perturb`: no_target 2 of 2 and range_climate_degF 2 of 4, with every degC null at 0.
- Every figure matches the body.

## Claims, version (steps 4, 5)
- No golden or claim file is in the diff. CI's golden and env-matrix checks are green at the head.
- `VERSION`, the manifest and `RELEASE_NOTES.md` are untouched.

## Class (step 6)
- I ran the body's rule at the head: `git grep -nE 'set_temperature|"set_value"|temperature_from_c\(|state_unit\(|get\("(min|max|min_temp|max_temp)"\)' -- custom_components`. Every hit matches the body's disposition.
- I also listed every `services.async_call` in the package. The other calls are MQTT displace, homeassistant turn_on/off, weather get_forecasts and switch_supply. None writes a temperature set-point.
- Every consumer of `dhw_setpoint_entity`, `space_setpoint_entity` or `mixing_valve_write_entity` now goes through the inputs owner. No seam is left open.
- Zero-evidence install, with no slot entity: `_bounded` and `setpoint_range_c` return None and (None, None), as at the base.

## Red checks (step 11)
I read the check-runs API for every commit in the range.
- The head has no red; pr-contract is green at 19:49:35Z.
- The reds earlier in the range:
  - `mutation`, at e4b4c6fed, 720d3636b, a590f11ee, 9ab42b06d and 0266dab15. The logs at a590f11ee, 9ab42b06d and 0266dab15 all read `ADDED UNPINNED ... inputs.py:391 GUARD_OFF`.
  - `pr-contract`, at e4b4c6fed and 720d3636b.
- The body answers both under `## Red checks`. The cancellations at 9ab42b06d were superseded runs, not reds.

## Earned numbers (step 14)
- `max_class_loc` went 8705 → 8690. With only `coordinator.py` reverted to the merge base, `structure.py` reads `FAIL max_class_loc 8705 > 8690 (+15)`. The drop is earned by the valve write that now goes through the owner.
- `closures.json` gains `issues.py` in 22 places, the body's 21 recorded closures plus 1 added by hand. It also gains the companion in one `inert_reads`, and nothing is removed.
- The mutation-ledger moves are anchor re-keys of moved lines and the bot's pins.

## Forward-carry (step 10)
The body says "none". The roster's three carries for this group are all met in the diff:
- P1 lands first, `issues.py` is classified, and no runtime gain is claimed.
- The unit is chosen by domain, and a test covers a climate with no target attribute.
- The degC null reads 0 at both ends.

## Architecture (step 15)
The coordinator hunks are the `inputs`/`issues` imports, the P1 `_create_issue` alias and `_command_valve_target`. There is no new coordinator state. The shape matches the architect note.

## Not re-derived (step 8)
- I did not rebuild the "P1+P2 as exported" tree, so its "3 of 4 failed" is not verified.
- The archscore `dS +0.0028` is not re-run; CI's arch-score is green.
- The "4 of 4 fail at the merge base" figure for the new block is not re-run; the companion and finder bases above stand for it.
