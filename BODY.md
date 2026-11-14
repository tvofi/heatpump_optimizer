R10-ARCH-DOCS-DELTA (#2395, part of #201): re-read `docs/architecture.md` and `dev/README.md` at the tree of origin/main (50373173d) with two stacked heads merged: PR 3481 at d712c2ba4a834afcb5d722468676d52ce3762681 (R10-ADVISOR-STEADY-START) and PR 3574 at 22e9330193f147e8b02b0171890b9c338ef6b0e3 (R10-SAV-VALUATION-RESIDUE). Reviewable now; it merges only after both pull requests have merged. At that point main is merged in and any sentence their final diffs changed is re-verified, enumerated by `git diff <stacked head> <merged head> --stat` for each of the two.

Result: a null delta for `docs/architecture.md` beyond what the two stacked heads already wrote (their own diff to it: module count 91 to 92, the `whatif.py` map row, the importer-complement 58 to 59). One correction in `dev/README.md`: the Governing-documents row sent volatile state to issue #201; `dev/governance/rules/writing-for-agents.md` says #3394.

## Head

f919d224caa9ecc39fad4f11434a8d0df7bbfacc (branch r10-arch-docs-delta; origin/main 50373173d486faf394b24637c177ab38b691b394 at 2026-11-14T00:48:12Z).

## Mutation proof

n/a: documentation-only diff (one table cell in dev/README.md); no production line to delete.

## Null control

Delta read, three-dot, `git diff $(git merge-base origin/main 45d21a6a6d)...origin/main -- custom_components/`: 26 files changed (boost, config_flow, const, coordinator, dhw_planner, duty_legs, duty_switch, early_cutoff, entry_config, heat_curve, inputs, mixing_valve, optimizer, pump_arbiter, sensor, setpoint_check, store, supply_hold, thermal_model, wear, strings/translations, card). Stacked heads' own diff: `git diff origin/main HEAD --stat -- custom_components/`, 12 files (coordinator, optimizer, price_tiles, whatif.py new, const, payload, services, card, strings). Each claim the page names checked at this tree: module count 92 (`ls custom_components/heatpump_optimizer/*.py | wc -l`), importer set of 32 (module-level `^(from|import) homeassistant` over the same files; boost, duty_switch, supply_hold, early_cutoff, heat_curve are already listed), learners that import homeassistant (accuracy.py:32, defrost.py:71, dhw_learning.py:28/30), symbols named in the diagram, the plan sketch and the "One owner per concern" bullets (all resolve: coordinator.py _forecast_arrays 7428, ForecastArrays 1565, _build_data_dict 8177, _publish_params 2760, compose_scores 3339, house_loss_converged 1695; optimizer.py OptimizationResult 2239, SolveInputs 2743, HeatPumpOptimizer.optimize 4051; inputs.py normalize_power_kw 327, state_power_kw 392, InputReader 962; const.py finite_float 1469; quiet_windows.py wall_clock 294; dhw_schedule.py format_clock 451; accuracy.py cop_observability 833; dhw_planner.py DhwPlanner 436; store.py QuarantiningStore 696; thermal_model.py ThermalModel 3165). The per-domain view list in coordinator.py is unchanged by the delta (_mixing_valve_view and _input_health_view exist at 45d21a6a6d and at main). The price-tile row's "30 days" is price_tiles.py:76 HORIZON_DAYS = 30. A page departure would have shown as a missing symbol or a changed count; none did.

Controls: `python3 tests/doc_claims.py` reads ALL 348 checks PASSED; `python3 tests/doc_claims.py --markers` reads "0 of 0 marker(s) due"; `python3 tests/entities.py` reads ALL 2711 ENTITY CHECKS PASSED. No marker is added for a landed group.

Departures named by causing group: none in `docs/architecture.md` (the three edits are the stacked groups' own). `dev/README.md` #201 vs #3394: older than the round; not caused by a product merge.

dev/README.md carries 8 and 14: f919d224c re-read. `git diff --name-only 45d21a6a6d...origin/main -- dev/governance tools/audit/seat .claude/workflows tools/pr tools/policy tests/run.sh tests/closure.py` lists 54 paths; about 20 are cited by dev/README.md rows, and every row's cited file and quoted text is machine-checked by tests/doc_claims.py (passes at this tree). The prose claim about ledger kinds is checked against `tools/audit/seat/ledger.py` KINDS: the derived kinds named (handoff-no-pr, handoff-update, probe-ref, review-owed, record-owed) and events (reviewer-fire, verdict-unposted, approve-held-runs, dispatch, train-stop, postmerge-owed) are all keys. No row needed a change.

Carry 5 (ruleset 23698884 requires only gate): not confirmed live. This seat has no ruleset read (no gh, no ruleset tool); the recorded tools/ci/fixtures/ruleset/ruleset_23698884.json (2026-10-02) is the pre-cutover list of 17 contexts and cannot confirm it. The sentence says "context", and nudge.md line 17 separately says the ruleset still requires one approving review, so the sentence is consistent as written and left unchanged. Needs a seat or the owner with a live ruleset read.

## Figures

- `ls custom_components/heatpump_optimizer/*.py | wc -l` (module count rule, the page's 92) .
- `python3 tests/doc_claims.py`, `python3 tests/doc_claims.py --markers`, `python3 tests/entities.py`: results above, run at the head's tree before the dev/README edit.
- Enumerators for the final re-merge: `git diff d712c2ba4a834afcb5d722468676d52ce3762681 <merged head of 3481> --stat`; `git diff 22e9330193f147e8b02b0171890b9c338ef6b0e3 <merged head of 3574> --stat`.

## Red checks

`tests / mutation` (predicted by prepr step 6d, not yet run on CI): the six unpinned sites below are in production lines this branch does not author; they arrive with the stacked heads, PR 3481 (whatif.py, coordinator.py, price_tiles.py) and PR 3574. Cheaper detector: the diff-mode mutant pass each of those pull requests runs on its own head, standing cost one `features_block.py` call per PR; it, not this docs-only branch, owes the pin, and merging after both PRs land (as the body above requires) re-derives the set against main. No countermeasure is built here.

`arch-score / arch-score` (predicted red at the merged tree): the score moves on the coordinator.py and optimizer.py changes the two stacked heads make, none of which this docs-only diff touches; the cheaper detector is `python3 tools/audit/archscore/score.py --diff` on each stacked PR's own head (standing cost one run per PR), and it is theirs to answer. Finding recorded: no detector on this branch's own diff exists to run.

`tests / briefs` (red on a commit inherited from a stacked head, not on this branch's own commit): `node tools/policy/brief_lint.mjs` at this head prints its fixtures ok and no brief error, and this diff changes no roster, carry or brief. Cheaper detector: that same local command, standing cost one second per run, already in prepr (step "brief_lint"); the red belongs to the stacked head's own branch and clears when it merges. The check is not in `merge_train.py owed-reds`.

`tests / fast (3.14)` (red on a commit the two stacked heads carry; this branch has no commit of its own with a check run yet, and its one edit is a docs table cell): this seat did not reproduce the failing script, so the failing check is not named further. Cheaper detector: the scoped gate each stacked pull request runs on its own head (`GATE_SCOPE=auto ./tests/run.sh`), standing cost the scoped run. Recorded finding: nothing in this diff's closure runs a script the docs cell can fail; at the re-merge after both PRs land, the red is re-read and answered here if it persists.

## Unpinned sites

All six are inherited from the stacked heads and answered by their owners' pins on merge; none is a line of this diff (its own diff is one cell of dev/README.md).

- custom_components/heatpump_optimizer/coordinator.py:10703 GUARD_OFF: inherited from the stacked heads (PR 3481/3574); the owner of that line pins it on its own head, not a line this diff writes.
- custom_components/heatpump_optimizer/price_tiles.py:130 RETURN_DEL: inherited from the stacked heads (PR 3481/3574); the owner of that line pins it on its own head, not a line this diff writes.
- custom_components/heatpump_optimizer/price_tiles.py:146 GUARD_OFF: inherited from the stacked heads (PR 3481/3574); the owner of that line pins it on its own head, not a line this diff writes.
- custom_components/heatpump_optimizer/price_tiles.py:148 CMP_BOUND*2: inherited from the stacked heads (PR 3481/3574); the owner of that line pins it on its own head, not a line this diff writes.
- custom_components/heatpump_optimizer/price_tiles.py:148 GUARD_OFF: inherited from the stacked heads (PR 3481/3574); the owner of that line pins it on its own head, not a line this diff writes.
- custom_components/heatpump_optimizer/whatif.py:149 RETURN_DEL: inherited from the stacked heads (PR 3481/3574); the owner of that line pins it on its own head, not a line this diff writes.

## Carries

- Carry 0, Carry 1, Carry 11, Carry 13: the split ruling and the wiring-checker run; the delta pass is this branch, `python3 tests/doc_claims.py` passes (348 checks) and `--markers` reads "0 of 0 marker(s) due", so no unresolved target marker survives at this tree.
- Carry 2: no marker is due; the ledger kinds `dev/README.md` names are keys of `tools/audit/seat/ledger.py` KINDS (checked above). The `--roster` form was not run: the roster branch file is not in this seat's reach, so the control is the default form.
- Carry 3, Carry 12: only the wiring rows the default `--markers` prints were read; comment-wrapped user-doc markers left to R10-USER-DOCS-VERIFY.
- Carry 4, Carry 6, Carry 9: the "One owner per concern" bullets' named symbols were re-resolved at this tree (listed under Null control); only symbol existence and location were re-measured, not each bullet's behavioural sentence, which no product merge in the delta diff touches.
- Carry 5, Carry 7, Carry 10: not confirmable here (see the Carry 5 paragraph above); stays owed.
- Carry 8, Carry 14: dev/README.md re-read against the 54 changed tooling paths (paragraph above); one correction (#3394).

## Forward-carry

Carry 5 stays owed: a live ruleset read of 23698884 confirming dev/README.md's "requires only gate" (path: dev/README.md, "The job graph"). Carry: R10-ARCH-DOCS-DELTA (the re-merge pass after both stacked PRs land, or the owner's read).

## Friction

none
