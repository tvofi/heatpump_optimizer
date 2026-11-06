Fix review: blocked bd0ee867e49bf6f0af414efcf2aa29ae775ac926 mutation-vacuous: water_heater dropped from _ATTRIBUTE_TARGET_DOMAINS survives tests/features.py, a degF water_heater's range then reads as degC

bus-nonce: 31dee38d7566e5a26f03decb6cc26cf0

## Block

Round 1 of this re-author (PR #3231, the outside contribution #3224). Measured head `bd0ee867e49bf6f0af414efcf2aa29ae775ac926`, base `785c2b604ba4c01891737a5285f4f4f49394c18f` (= origin/main at review).

The product code is correct. I found no defect in `inputs.py`, `config_flow.py` or the strings. But one of the four production seams the diff adds is not pinned by any check. That seam is `setpoint_unit` keying on `_ATTRIBUTE_TARGET_DOMAINS = ("climate", "water_heater")` (inputs.py:467, :478).

- Mutant m4 (`ev/mutant-m4.diff`): `_ATTRIBUTE_TARGET_DOMAINS = ("climate",)`. `PYTHONPATH=tests/hastub python3 tests/features.py` at the mutant prints `ALL 4859 FEATURE CHECKS PASSED`, rc=0 (`ev/features-m4.log`). The new water_heater check still passes.
- Effect of the surviving mutant, measured with my own instrument (`tools/null_control.py`, mine, not the finder's: no finder harness exists). A `water_heater` in a degF instance with min_temp 86 and max_temp 149 gets `setpoint_range_c` → `(86.0, 149.0)` instead of `(30.0, 65.0)` (`ev/null-control-m4.txt` against `ev/null-control.txt`). The arbiter's DHW clamp ceiling becomes 149 °C, so a degF water_heater is no longer held to its own max_temp.
- Why nothing fails: the new check's degF case covers only the write (`setpoint_and_unit` falls back to the instance unit when the state is non-numeric, so the write survives the mutant). It never checks the range or the clamp on degF. The GUARD_OFF pin `setpoint_unit.GUARD_OFF.d9727610` is killed, but only through climate checks. m6 (`if False:` at inputs.py:478) fails exactly three checks, all climate (`ev/features-m6.log`). No water_heater check is among them.
- Repair (small, test-only): add a degF leaf to the new check, `setpoint_range_c` on the degF water_heater == `(30.0, 65.0)` and/or `_df_dhw_command(..., _DF, 70.0)` clamped to 149 °F. Then show m4 failing it.

## Findings

- Follow-up: the GUARD_OFF pin reason in `setpoint_unit.GUARD_OFF.d9727610.json` says "failed=4". At this head the same mutant fails 3 checks (`3 of 4859 FEATURE CHECKS FAILED`, `ev/features-m6.log`). The kill verdict holds, but the count in the reason does not re-derive here. Carry: dismissed: kill verdict holds; count is the pin drive's own run, not a claim this PR depends on
- Non-blocking body gap: the body's feature figure `ALL 4831 FEATURE CHECKS PASSED` is the contributor's, at their head, and is not re-derivable at this head. Here the head reads 4859 and main reads 4858 (+1, the new check). The body says this itself. Carry: dismissed: contributor figure, disclosed as such; re-derived count is in Evidence
- Non-blocking: the seat commits 180dc5934 and b9743dcdf are authored as `seat`, not `hpo-fixer`, and the body discloses this. Carry: dismissed: disclosed in body, author identity of seat commits, not product code
- Non-blocking: the brief's GOLDEN-CLAIM premise (a) calls config_flow value-bearing. It is not: `carries_floats()` is False and env_drift compares it exactly at level 1 (claimed_drift.txt notes, #547). Re-recording plus claiming is the established practice for this fixture, and both were needed (the re-record clears the level-1 staleness; the claim clears the branch-vs-base drift). Carry: dismissed: brief premise, the claim is correct under #547's practice

## Evidence

- Patch identity: `git diff $(merge-base origin/main refs/pull/3224/head) refs/pull/3224/head | git patch-id --stable` = `9f2a5297…` = the same over `d1153ae86~1..1fe34a84f` (the head's first three commits). Per-commit patch-ids match (b89289d1fc8f, 0a0c45ed6c70, 8b291fd54604). All three commits are authored by Bankaifan. The messages differ from #3224's only by the removed `Co-Authored-By` and `Claude-Session` trailers.
- Seat commits beyond the three: 9376cfbc5 (delete the stale pin 2c91312e), 6f3b23fd9 (delivery row 3231.md), 180dc5934 (config_flow claim), b9743dcdf (new pin d9727610), and three merges of main. The three-dot diff against origin/main touches exactly the 11 files in the packet; the merges add nothing beyond main.
- RESULT features head: `ALL 4859 FEATURE CHECKS PASSED` rc=0 (`ev/features-head.log`); main: `ALL 4858 FEATURE CHECKS PASSED` rc=0 (`ev/features-main.log`).
- RESULT mutants on tests/features.py:
  - m1 (drop `water_heater` from SETPOINT_SERVICES): `2 of 4859 FEATURE CHECKS FAILED`. The #1526 service-table check (`water_heater.p6_dhw_setpoint_entity: the consumer issued no call`) and the new check both fail, as the body's mutation proof says.
  - m2 (drop it from _RANGE_KEYS): 1 failed, the new check.
  - m3 (drop it from _STEP_KEYS): 1 failed, the new check.
  - m4 (drop it from _ATTRIBUTE_TARGET_DOMAINS): 0 failed, which is the block.
  - m6 (GUARD_OFF at inputs.py:478): 3 failed, all climate.
  - m5 (drop `water_heater` from the config_flow selector): `GOLDEN_MODE=strict python3 tests/golden.py --only config_flow` reads `1 of 1 GOLDEN SCENARIOS CHANGED` rc=1 (`ev/golden-config_flow-m5.log`); the head reads `ALL 1 GOLDEN SCENARIOS UNCHANGED` rc=0.
- Null control (own instrument, `tools/null_control.py`, at main and head, degC and degF, states heat_pump/off/eco):
  - At main: `range=(None, None) step=1.0 write52.3=False calls=[]`. This matches the body.
  - At head: degC gives `range=(30.0, 65.0) step=0.5`, and a write of 52.3 calls `water_heater.set_temperature {'temperature': 52.5}`. degF gives `range=(30.0, 65.0)`, and 52.3 °C is written as 126 °F.
  - `unavailable` reads None.
  - The operation-mode state is never parsed as a number: `setpoint_and_unit` gets None from `temperature_c(state)` and falls back to the `temperature` attribute. The only consumers of the slot are pump_arbiter (`read_setpoint`, `write_setpoint_c`, `setpoint_range_c`, `quantise_setpoint_c`) and setpoint_check (`setpoint_and_unit`, `quantise_setpoint_c`, `read_setpoint`). None reads `state.state` as a number.
- HA schema, pinned venv-ha HA 2026.10.4, read from source:
  - `water_heater.set_temperature` requires `temperature` (ATTR_TEMPERATURE) and takes `operation_mode` as optional. This matches the SETPOINT_SERVICES row.
  - The registered services are exactly turn_on, turn_off, set_away_mode, set_temperature and set_operation_mode. This matches the `_P6_IMPLEMENTS` row.
  - The capability attributes are `min_temp`, `max_temp` and `target_temp_step` (the step is emitted only when truthy, and the default step of 1.0 then applies). The target attribute is `temperature`. All are converted with `display_temp` to the instance unit, and the state is `current_operation`.
- Other domain lists: the space set-point (config_flow.py:1590) and mixing-valve (:1693) selectors stay `number/input_number/climate`, which is correct because they are not DHW slots. No discovery or pre-fill list names set-point domains. No `== "climate"` branch exists on a set-point path outside inputs.py.
- Existing config entries: the slot stores an entity id. Widening the selector invalidates no stored value, and the climate and number paths are unchanged (features main == head except the +1 check; the climate L1/L2 checks pass).
- Translations: strings.json and en.json are byte-identical in the changed line, and sv.json is updated. CI hassfest and validate-hacs are green.
- RESULT env_drift: `python3 tests/env_drift.py --all 785c2b604…` at head reads `NO UNCLAIMED DRIFT: 56 scenario(s)` and `NO STALE FIXTURE: 56 committed fixture(s)`, rc=0 (`ev/env_drift-head.log`). `CLAIMED config_flow: 2 leaves moved`: exactly `_seeded.hot_water…dhw_setpoint_entity.config.filter` and `hot_water…dhw_setpoint_entity.config.filter`, both `[…'climate']` → `[…'climate', 'water_heater']`. Every other fixture is byte-identical or may-drift "did not move".
- Golden claim (a–e):
  - (a) The cause is the config_flow.py:1667 selector edit, shown by m5 reverting exactly those 2 leaves.
  - (b) The claim line states its direction ("gains water_heater"), and `claims-for: 7.1.1` = VERSION 7.1.1.
  - (c) config_flow is not a may-drift entry, and env_drift accepted the pair (rc=0).
  - (d) The three-dot diff of claimed_drift.txt adds only the config_flow claim line and a 4-line note. card_claimed_drift.txt is untouched.
  - (e) 2 leaves moved and 2 are claimed; numstat over config_flow.json is 2/2.
- VERSION, manifest.json and RELEASE_NOTES.md are untouched in the three-dot diff.
- RESULT structure: `STRUCTURE RATCHET PASSED` at head and at main. entities: `ALL 2632 ENTITY CHECKS PASSED` at head and at main.
- Merge simulation (`ev/merge-tree.txt`, claimnotes driver installed): `git merge-tree --write-tree` exits 0 against origin/main 785c2b604, PR 3220 e70dfd645, PR 3198 3f188f896 (`MERGE-CLAIM: resolved tests/golden/claimed_drift.txt`) and PR 3226 ba704972f.
- CI on this head: `python3 tools/audit/seat/merge_train.py classify bd0ee867… --pr 3231` exit 0: `GREEN bd0ee867e49bf6f0af414efcf2aa29ae775ac926 pending: none red: none` (`ev/ci-classify.txt`). Of all 39 check-runs (one page), the only concluded red at read time was `tests / nightly-status`, which is main's nightly, is not required, and is not reached by this diff. The body names the previous head's reds with causes and detectors. CI's green `mutation` lane does not refute the block: m4 edits a tuple literal, which the table's operators do not draw as a mutant. The pinned GUARD_OFF site is killed through climate checks only.
- Head re-read before return: `git ls-remote origin refs/pull/3231/head` = bd0ee867e49bf6f0af414efcf2aa29ae775ac926, the head measured.
- Figures not re-derived: the contributor's 4831, and the pin drive's "failed=4" (I measure 3). The body's `3091 against 3091` unpinned-sites figure was not re-run (the heavy mutation table is CI's; see the mutation lane).
