Fix review: blocked 97786d25bf0ba7cc2c56230799a03a919f84da9b class-open: dev/audit/harnesses/r10_demand_overbook.py:245 still unpacks the old 3-tuple from _build_comfort_bounds; ValueError at head, rc 0 at base

bus-nonce: 0a462e3c17df55fee273e800ae40a262

## Round

Round 1: the first fix review of PR 3274 (R10-WHY-NOW-WIDGET). The review ran from a detached worktree at 97786d25bf0ba7cc2c56230799a03a919f84da9b, against merge base 630bf533d838110be56ede0366756da3de0d941e, and checks by the three-dot diff. `git diff 630bf533...origin/main -- dev/governance/roles/` is empty, so the role contract is current.

## Block

- class-open: the diff changes `HeatPumpOptimizer._build_comfort_bounds` from a 3-tuple to a 4-tuple (optimizer.py, `-> tuple[np.ndarray, np.ndarray, np.ndarray, tuple[...]]`). It updates the production caller and the five in tests/features.py. It does not update the sixth caller, `dev/audit/harnesses/r10_demand_overbook.py:245`, whose `_dp_reference` still reads `targets, floors, ceilings = opt._build_comfort_bounds(...)`. The body does not dispose of this caller either. The enumeration rule is `grep -rn "_build_comfort_bounds(" custom_components tests tools dev --include=*.py`, which returns 7 hits: 6 callers and the def. Harness: `PYTHONPATH=tests/hastub:tests python3 dev/audit/harnesses/r10_demand_overbook.py --one owner_i01 dp`, which is the `--dp` path (R10-DEMAND-OVERBOOK's DP reference). Metric: the exit code and the RESULT line.
  - At base 630bf533: rc 0, and the RESULT line is `"dp_learned": {... "gap": -0.0006 ...}, "dp_true": {... "gap": -0.0012}` (ev/overbook_dp_base.log).
  - At head 97786d25: rc 1, `ValueError: too many values to unpack (expected 3, got 4)` at r10_demand_overbook.py:245 (ev/overbook_dp_wt.log).
  - Perturbation: the only change between the two runs is the PR's own diff. No gate check caught this, because the harness's only closure reference is tests/closures.json:4036 and no lane runs `--dp`.
  - Fix: either unpack four values there (`targets, floors, ceilings, _ = ...`), or keep the 3-tuple and return the floors through another channel. Re-run the harness at the new head.

## Findings

- The widget's direction disagrees with the solver's decision more often than a constant guess does. Claim: the shipped metric text says "The reasons behind this hour's decision ... the arrow shows whether it pushes the heat pump to run or to idle ... A high share means that reason mostly decides the hour". Harness: this is my own instrument, not the finder's (no finder harness exists; owner report). `ev/claim.py`, run at head, makes 12 production solves: 4 price profiles (flat_null, daily_curve, cheap_night, spiky) × room 20/21/22 °C, 24 h at 15 min, a sinusoidal outdoor temperature around −5 °C. At each step with `why_now_at` not None it compares the sign of the net push (Σ weights) and the top driver's direction with whether the solver actually ran (power_schedule > 0.05 kW). Metrics, per config:
  - Net-push agreement with run/idle: 37, 49, 59 (flat_null); 55, 57, 59 (daily_curve); 73, 67, 66 (cheap_night); 27, 34, 47 (spiky), each out of 96.
  - Top-driver agreement: 37–69 of 96.
  - The trivial "always idle" predictor scores 75–82 of 96 in every config, so the widget does worse than it in all 12.
  - Null control (flat prices, where price_rank is 0): 37 to 59 of 96, all non-neutral. The design's own all-neutral null needs flat weather, and a real forecast is never flat.
  - Top driver against the solver's own `space_reasons[i]`: frequent pairs are (comfort_floor, idle_coasting), (price_rank, idle_dearer) and (comfort_floor, cheap_price) (ev/claim_head.log).
  - Perturbation: negating every weight maps each agreement count a to n − a. For example, flat_null at 20 °C goes from 37 to 59. That figure is derived, not re-run.
  - Cause, as I read it: `comfort_floor` is computed from the solved room trajectory, and `price_rank` ranks a step against the whole horizon whatever the slab's state. Neither is the solver's marginal reason, so the dominant row often points away from what the pump does.
  - Status: the approved note never claimed agreement with the decision. The brief's point (2) asks for it, and the UI text asserts it. The fix is either to measure and gate an agreement figure against this baseline, or to reword the metric so it does not say the rows decide the hour. Either needs a design ruling. Carry: R10-WHY-NOW-WIDGET
- `why_now` is published as a recorded attribute. `SpaceHeatingPlanSensor` adds `why_now` to its attributes, but `_unrecorded_attributes` (sensor.py:1400) does not list it. The probe gives `RESULT unrecorded why_now: False | wood_fuel: True | slots: True` (ev/unrecorded.txt). The block's own comment says card-only attributes are "worth no SD-card writes per update", and `wood_fuel` is excluded although the card reads it from the attribute. why_now changes at every step, so on a Pi-class target (D9/D10) every update writes it to the recorder. The fix is one entry plus a check in tests/entities.py beside the wood_fuel one. Carry: R10-WHY-NOW-WIDGET
- Surviving mutant C, slot_drivers.py `why_now_at`: sorting by signed weight (`rows.sort(key=lambda d: -d["weight"])`) instead of magnitude leaves tests/features.py at rc 0 (ev/mutres_C_sort_signed.json). The check "drivers are sorted by magnitude, largest first" only reads step 0 of the cheap-first solve, which has no negative weight. A large idle driver would then be listed last, which is wrong. Any check over a step that has a negative-weight driver would kill it. Carry: R10-WHY-NOW-WIDGET
- Surviving mutant D, coordinator.py `_solve_record`: `away_floor_drop_c=away_mode.floor_drop_c(ctx._opt_config, self._away_state)` → `away_floor_drop_c=None`. tests/features.py stays at rc 0. tests/entities.py drops from 2644 passed to 1 failed, but the failing check is the tree-count self-test "main() passes the committed table at its own recorded count (the null control)", which reacts to any edit of the file and is not a behavioural pin (ev/mut_D_coord_away_none_entities.log, ev/entities_head.log). M12 pins `away.floor_drop_c` itself; nothing pins that the coordinator wires it into the solve. With D in place, the away row reads 0 in production while away is active. Carry: R10-WHY-NOW-WIDGET
- Surviving mutant E, optimizer.py `_build_comfort_bounds`: deleting `comfort_floors = temp_min_bounds` after the confidence margins are applied leaves tests/features.py at rc 0. No check pins that the comfort floor `slot_drivers` reads includes the T5 margins, so the comfort_floor and mold_guard pushes are unpinned against the margin path. Carry: R10-WHY-NOW-WIDGET
- `## Red checks` omits one concluded red at this head: `gate` job 128404815591 (run 42372899572, 12:46Z). It was an edit-run gate, `FAIL run(s) [42372900036, 42373556850] at this head are still being judged; their gate decides`, which is the mutual edit-run deferral (R10-HOTFIX-GATE-BUSY-DEFER). The later edit-run gate reds 128432994419 and 128433346279 (14:50Z and 14:51Z) are the same deferral to code run 42372900036, and that run decides. They came after the body's last edit, so the next body owes them too. Carry: R10-WHY-NOW-WIDGET

## Evidence

- HEAD: ev/HEAD.txt names 97786d25bf0ba7cc2c56230799a03a919f84da9b. The body's `## Head` names the same SHA. origin/main at review: ev/main_at_review.txt.
- Merge: `git merge-tree --write-tree origin/main 97786d25` returns rc 0 with `MERGE-CLAIM: resolved tests/golden/card_claimed_drift.txt` and `LEDGER-MERGE: resolved tests/closures.json` (ev/merge_tree.txt).
- Seam and shape against note 60d61fcf and verdict 043b31ad:
  - The solver seam owns the change, through the new pure module slot_drivers.py. `_build_result` makes one call, `get_current_action` does the one current-step search (`step_reasons(result, i)`), and `_step_index` stays private.
  - The coordinator's growth is one kwarg at `_solve_record` plus the `why_now` copy in the module-level `_apply_result_payload`, and the what-if path is untouched. `breakdownRow` is shared by `scoreBreakdownHtml` and `whyNowHtml`, `scoreDrivers` is not routed through for percents, and `knownCodes` is the shared filter.
  - The body raises its departures: the third `_Horizon` field, the `step_reasons` move, the sensor override instead of the base, and no coord_* claim. I judge them in the note's spirit. The unpack caller in the Block is a sibling of the 4-tuple change that the note did not foresee.
- Production formulas: I read away.py's `_setback_target` / `floor_drop_c` refactor of `solve_bands` and found it equivalent (the walrus guard keeps the old condition). `_build_comfort_bounds`' `temp_min_bounds` is unchanged; it only also returns the pre-mold floor and the padded mold floor. The `space_reason` / `dhw_reason` reads moved into `step_reasons` with the same bounds, and `i` is never negative (get_current_action's search). I found no production formula changed under cover of the widget.
- Mutation, mine, with each mutant alone in its own worktree at head and tests/features.py run (ev/mut.py, ev/mutres_*.json):
  - Killed: A (comfort push `floor + half - room` → `floor - room`) by 3 checks, including the null control; B (`total = |push|.sum` → `push.sum`) by 3, including "magnitudes summing to 100"; F (price_known guard deleted) by 2 `why_now_at` checks.
  - Survived: C, D and E, under Findings.
  - The unmutated head reads `ALL 4924 FEATURE CHECKS PASSED` (ev/features_head.log) and `ALL 2644 ENTITY CHECKS PASSED` (ev/entities_head.log).
  - I did not re-run the body's M1–M14, C1–C9 or the CI mutation table (the role says to cite CI's heavy runs). `tests / mutation` reads success at this head (job 128432836286).
- Body's `## Unpinned sites`: "none at b62b49ab9", with 14 pinned and 2 triaged equivalent. The two equivalents (L90 slice clamp, L136 `>=` after the neutral return) are sound by reading. The 49 sites ci_predict predicted are 33 bot-pinned plus these 16. That is the body's own count; I did not re-derive it.
- Null control: the flat-price, mid-band, flat-weather all-neutral check passes at head and is killed by mutant A. The plan is byte-identical with the drivers emptied (features check passes). This is the design's null, under flat weather. The real-forecast null is the first finding.
- Card:
  - `node tests/card.mjs` reads ALL CARD CHECKS PASSED after `tests/plan_view.py`.
  - `node tests/card_drift.mjs` reads `1 state(s) moved and claimed, 44 identical` (ev/card_mjs.log, ev/card_drift.log), and the claimed state is `score_open` only, as the note requires.
  - UI states: no-data, all-neutral and unknown price (the solver returns None, so no-data shows) are rendered and tested. Dark mode and narrow width rest on CI `tests / browser` success (job 128432805204); I did not re-run the browser locally.
- Ratchets: `python3 tests/structure.py` reads STRUCTURE RATCHET PASSED (ev/structure.log). VERSION, manifest.json, RELEASE_NOTES.md, tests/golden/claimed_drift.txt and every `*_budgets.json` are untouched (empty three-dot name-only diff). dev/programme/delivery/3274.md is in the diff. slot_drivers.py is in tests/closures.json (CI `tests / closures` and `closure-scope` read success).
- Figures I did not re-derive: the PIN KILLED 14/2 count, the ratchet's 2877/6886, the forecast scale's 0 of 96 saturated, archscore dS +0.0000 and P9's clip-walk control. All are cited from the body.
- CI on this head: see the CI state section below.

## CI state

- `python3 tools/audit/seat/merge_train.py classify 97786d25bf0ba7cc2c56230799a03a919f84da9b --pr 3274` exited 0 at 15:26:52Z: `GREEN 97786d25bf0ba7cc2c56230799a03a919f84da9b pending: none red: none` (ev/classify_final.txt, ev/classify_history.txt).
- Before that, from 14:53Z to 15:10Z, it read RED on `gate`. All three edit-run gate reds deferred to code run 42372900036 ("still being judged; their gate decides"). That run's re-run concluded, and its gate decided GREEN.
- The `tests / nightly-status` failure at this head grades main's last Nightly, and this diff reaches nothing that check reads. The body answers it, so it is not this PR's red.
- The red at this head was a gate deferral, now cleared. This block does not rest on CI.

## Closing

- Head re-read just before return: `git ls-remote origin refs/heads/fix/r10-why-now-widget` gives 97786d25bf0ba7cc2c56230799a03a919f84da9b, which is the measured head.
- `python3 -I tools/audit/carry_audit.py check --body verdict.md --pr-group R10-WHY-NOW-WIDGET` returns rc 0 (`CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)`). It counted none of the six `## Findings` bullets, although each ends in `Carry: R10-WHY-NOW-WIDGET`. That is reported here, not worked around.
- The instruments are my own: ev/claim.py and ev/mut.py, both disclosed. No finder harness exists (owner report), which is itself a finding the note already records ("No finder harness").
