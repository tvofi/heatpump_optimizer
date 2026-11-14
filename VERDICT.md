Fix review: merge a0784de911887f5690a6183123c556757cd63fe7

bus-nonce: 575e412de92c0c2741261e3880fcdd30
pending-ci: gate

## Findings

- The open-window relax sentence ("lowers the coldest indoor temperature the plan accepts by 1 °C, never below 15 °C", the train's wording kept by the merge) is false in one corner, and the cause is production code, not the text. `away.solve_bands` (custom_components/heatpump_optimizer/away.py:404-405) applies each widening as `max(ECONOMY_ABSOLUTE_FLOOR, min_temp - by)`. With an away setback below 15 °C (the away target accepts 5–21 °C), the open window, or Economy, raises the floor to 15 °C instead of lowering it. Measured at this head: away target 10 °C gives min_temp 10.0 with no widening and 15.0 with `OPEN_WINDOW_RELAX_C`; at home 19.0 becomes 18.0 (ev/open_window_relax_during_away.txt). The line is the same on origin/main a77d71fb and is not in this PR's diff, and PR 3564's own dropped wording made the same claim, so the reconcile choice is not wrong. Carry: R11-INTAKE-R10-RESIDUE
- `dhw_free_disinfection_enabled`: the merge drops PR 3564's "(within 1 °C)". The code credits at `target - 1.0` with the option off, and at `target - 0.5` held for `DHW_LEGIONELLA_HOLD_MINUTES` with it on (legionella.py:217-235). The kept sentence says nothing false; it only leaves out the tolerance, and the dropped one gave the off-band and not the on-band. The body already puts the choice to the owner. Carry: dismissed: no false statement; tolerance detail only, owner's choice raised in the body
- The body's `## Forward-carry` list is partly settled at this head by the merged #3576/#3561. docs/configuration.md:530 now says the legionella cycle "runs on its usual interval; it is not timed to your return". away.py's docstring is corrected and `AwayConfig.legionella_before_return` is removed. The main-fuse row (docs/configuration.md:1132) and docs/setup.md:91 (entry name) now carry the corrected wording. The intake stage should re-measure each carried line at its own base before acting, not treat the list as open. Carry: R11-INTAKE-R10-RESIDUE

## Evidence

- Head measured: a0784de911887f5690a6183123c556757cd63fe7 (ev/HEAD.txt), the PR's head per the API when I started. Scope is `delta` over d6a7b00b (packet `## Review scope`). `review_carry.py d6a7b00b a0784de9` prints FRESH-REVIEW, so this round is the delta. The previous verdict at d6a7b00b was `merge`, so this is not a re-cut round.
- Shape of the delta: a0784de9 = merge(d6a7b00b, 002bdfea), with the same tree (899cbc41). 002bdfea re-anchors tests/doc_claims.py on a117bad4 = merge(d6a7b00b, #3561 head 6f477159). `git show --remerge-diff a117bad4` shows hand resolutions only in strings.json, en/de/sv.json and tests/doc_claims.py (the two calls kept). closures.json was resolved by the ledger driver. `git diff --stat 6f477159 a0784de9` is exactly this PR's 10 files, so every production .py change in the delta (away.py, off_restore.py, pump_arbiter.py, RELEASE_NOTES.md) is #3561's head and outside this review. This PR adds no production Python, and doc_claims stays green over #3561's code. No widening is warranted (fix-review.md step 12).
- RESULT eight rows, checked against code at this head (ev/eight_keys_three_sides.txt prints head, #3561 and #3564 for every catalogue):
  - `name` is true. config_flow.py:2896 sets `title=self._data.get(CONF_NAME, ...)`, coordinator.py:4214 has the fixed `name="Heat Pump Optimizer"`, and entity.py:204 sets `_attr_has_entity_name = True`.
  - `space_setpoint_unit` is true. Its only writer is modbus_prefill.py:243 (`WRITE_TARGET_FLOW if water else None`); config_flow.py:1670 is a read, so nothing infers the unit from the entity. `_space_target` (pump_arbiter.py:618-626) writes `_flow_target` for flow and return (`_flow_unit`: `SPACE_SETPOINT_WATER_UNITS`) and `_planned_room` for indoor. pump_arbiter.py:1793 returns before `_command` unless `DUTY_CONTROL`. PR 3564's fact is kept.
  - `pv_production_entity` is true. coordinator.py:9839 has `production[0] = min(self._pv_production, config.peak_kw)`, and the rest of the horizon stays modelled.
  - `away_dhw_min_temperature` is true. legionella.py:641 computes due from `dhw_legionella_interval_days`, and no away-mode code reads legionella timing (`git grep` shows only the docstring).
  - `dhw_free_disinfection_enabled` is true (see Findings for the tolerance). See legionella.py:217-235 and const.py:1058 `DHW_LEGIONELLA_HOLD_MINUTES = 20.0`.
  - `vvc_pump_entity` is true. coordinator.py:4512-4522 uses empty windows unless `dhw_enabled and dhw_windows_active`, and pump_schedule.vvc_should_run returns True with no windows.
  - `main_fuse_amperes` is true. coordinator.py:8889-8927 takes min(fuse, threshold), and returns `{"available": False}` with neither a fuse nor a billing capacity tariff.
  - `open_window_relax_enabled` is true at home (coordinator.py:6279-6280, away.py:404-405). The away corner is under Findings.
  - None of the eight rests on a comment, a docstring or another string. Each decision reads a code line.
- RESULT de and sv carry the same decisions as en. Seven rows are byte-equal to #3561's head. For `space_setpoint_unit`, de and sv both end with the train's declaration sentence plus the Control sentence, using the catalogue's own labels: de „Steuerung der Pumpenfunktion“/„Steuern“, sv "Styrning av pumpens uppgift"/"Styrning".
- RESULT union (ev/union_check.txt, ev/union.py): in all four catalogues, 1507 leaves, 8 conflicting leaves (the eight keys), 0 other leaves changed on both sides, 0 mismatches. Outside the eight, every leaf equals #3561's head, or this branch's value where only this branch changed it (three-way against merge base c987209c). en.json equals strings.json leaf for leaf.
- RESULT doc_claims at the head: `ALL 386 checks PASSED`, rc 0 (ev/doc_claims_head.txt). At a117bad4, before the re-anchor: `2 of 386 checks FAILED` (the hold-minutes pin, and the exemption null check), matching the body.
- RESULT perturbation controls (ev/perturbations.txt). Each was run on the tree with tests/doc_claims.py, then restored:
  - P1 strings 20→30 min: `quotes 30, the code holds 20.0`, 1 FAILED.
  - P2 strings 1→2 °C: `quotes 2, the code holds 1.0`, 1 FAILED.
  - P3 pre-fix "never recommends" space_setpoint_unit sentence: the written-slot arm names `space_setpoint_unit`, 1 FAILED.
  - P4 removing the planted `_OWNED_ELSEWHERE` sentence: `null: the other group's sentence is found once it is not exempted` FAILS, so the re-anchored null check needs its plant.
  - C1 const `DHW_LEGIONELLA_HOLD_MINUTES` 25: `quotes 20, the code holds 25.0`.
  - C2 const `OPEN_WINDOW_RELAX_C` 2.0: 3 FAILED, the pin plus #3561's two residue checks.
  - Restored: ALL 386 PASSED, clean tree.
  - The three re-anchored pins still pin what they pinned.
- Previous verdict's items: the "conflict with #3561" item is settled by a117bad4, with the resolution measured above. The other round-1 items (translations unpinned, the written-slot set, menu_options rows, the pump_duty_mode unit, main's hysteresis texts) are untouched by this delta and keep the destinations the previous verdict gave them.
- `git merge-tree --write-tree origin/main a0784de9` (origin/main a77d71fb): rc 0, one tree (ev/merge_tree_main.txt).
- VERSION, the manifest and both claim files do not differ from the merge base. The RELEASE_NOTES.md delta is one paragraph under an existing heading, from #3561's head.
- The review packet refused `introduced-red: unreadable` (instrument-self-tests queued at render). classify decides; see the CI line below. owed-reds set: ev/owed_reds.txt.
- CI at this head: I polled `merge_train.py classify a0784de9… --pr 3564` from 10:40 to 11:09 UTC, at least 75 s apart. Every run printed `WAIT a0784de911887f5690a6183123c556757cd63fe7 pending: gate red: none`, rc 3 (ev/classify_poll.txt). Nothing was red. The review is otherwise a merge, so I return it with `pending-ci: gate`, for the relay to post once the gate is green at this head.
- The head was re-read at post: `refs/heads/fix/r10-config-flow-text-verify` is a0784de9 (ev/head_at_post.txt).
