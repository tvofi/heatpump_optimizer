Fix review: merge 313a19d9189f7bbd87bcfbfe8dc231b8dbb4d3df

bus-nonce: 9895de2a44181f8f1185f1faa1586e5d

Round 1 (first review of the fixer's handoff) of PR #2834, R10-ADVISOR-RESIDUE. Measured head `313a19d9189f7bbd87bcfbfe8dc231b8dbb4d3df`, still the PR head at 2026-10-25T21:10Z (`git ls-remote`). Reviewed from detached worktrees at the head and at the merge base `da12aa37d`. `dev/governance/roles/` on my worktree matches origin/main (three-dot diff empty).

## Findings

- Seam (a) stays open at the Plan page's what-if panel. `WhatIf.summary` still reads the single-solve `monthly_cost_delta`, which moves with the house's start: re-run `whatif` gives `null 00:00 target_plus_1 plan … spread 132.0`. The settled figure gives the wrong sign across two schedules (`varying 00:00 target_minus_1 … settled +24.6`, `target_plus_1 … settled -25.5`, re-derived). The held figure leaves out a draft's non-comfort edits. The body hands this to an estimator design or the owner's acceptance of the disclosed copy. Carry: #2257
- The brief said this group is the last on #2257 and closes it. The body uses `Part of #2257` instead, so the issue stays open with seam (a) as its only residual and no live group owns it. The orchestrator owes a disposition: a design group or a dismissal. Carry: #2257
- Seam (c), the held estimator's per-solve asymmetry, is measured and left unfixed. Re-run gives `asym null … worst 21.0 %` and `asym varying … worst 3.0 %`. No reader compares the two tiles' magnitudes: the card's `degreeRow` sign check is the only relation, confirmed by grep. Carry: dismissed: no reader compares the two tiles' magnitudes and the published 30-day mean averages it over rotation starts; a later convexity check starts from the `asym` arm
- The 30-day mean mixes schedules. This is measured and left unfixed. Re-run gives `mixing worst spread 28.5 %` and `null 07:00 … spread 16.7 %`. Carry: dismissed: a per-schedule reset brings back the day-to-day swing (#2257 item 6) that the horizon exists to remove
- 10 `custom_components/` sites are unpinned (body § Unpinned sites), so `tests / mutation` is red at this head. Under ci-autofix.md the `mutation-autofix` bot commit pins them on this PR. Three of the sites are already killed by existing checks in my own mutants (RS4 at coordinator.py:2007, RS2/RS5 in `recent_kwh_price`). Carry: dismissed: owned by the mutation-autofix lane on this PR per ci-autofix.md, not a reviewer carry

## Evidence

CARRY CHECK, item by item:
- [0] seam (a). Satisfied for the cap readers. The fuse advisor reads `monthly_settled_cost_delta` (custom_components/heatpump_optimizer/coordinator.py:8793), and so does the cap tile (price_tiles.py `monthly_figure`). Both come from `price_tiles.monthly_deltas`. Mutants MA1, MA3 and RS1 (sign of the deferred term flipped) are each killed. I checked that the settled figure is sound for a cap: `_compute_baseline_power(weather, initial_state, dt, comfort_targets)` takes no cap, so the live and capped solves share the thermostat baseline and their `deferred_energy_cost` difference is comparable. The comfort-move residual at `WhatIf.summary` is forwarded with `Carry: #2257` (body Forward-carry; Findings above). `docs/dashboard-card.md` still discloses the one-off in the what-if figure.
- [1] seam (b). Satisfied. The sensor-gap row reads `recent_kwh_price` first (sensor.py `_gap_energy_rate`). The hot-water sweep is priced in `_build_data_dict` at the same level (coordinator.py:7987, `_sweep_price`). The level is defined in `MonthlyLedger.recent_kwh_price` (ledger.py:273) as this month's and last month's time-mean spot plus their grid fee per kWh. That matches `_get_current_price`'s spot+fee definition, and ledger.py:192 samples the same spot. Mutants MB2, MB4, RS2, RS3 and RS5 are each killed.
- [2] seam (c). Shown not to apply as a fix, and measured with the arm re-run. It is dispositioned in the body and in Findings above.
- [3] MX4. Satisfied. The new check `#2257: a day solved once and a day solved three times weigh alike in the published mean` (tests/features.py, uneven 1/3 counts) kills the pooled mean: `monthly_cost_delta 9.0`, want 6.0 (ev/mut-MX4.*).
- [4] per-degree copy. Satisfied. The copy is decided as "Keeping the house a degree cooler is cheaper" / "Keeping it a degree warmer costs … more", in en and sv (www/heatpump-optimizer-card.js:210-211, 947-948). `docs/dashboard-card.md` states the room-vs-setting distinction. The owner's-screenshot pair checks in tests/card.mjs still pass, and mutant MC1 (title reverted) turns `price of a degree: …` red (ev/card-MC1.log). Delivered fraction re-derived: `r10_advisor_degree.py null` gives `delivered -0.514 K … held +54.4 (-8.4 %)` and `+0.327 K … held +54.4`, identical to the body.
- [5] MX4, round 2. Satisfied by the same check as [3].
- [6] tile overstates per degree of setting. Satisfied by the same copy decision as [4]. The tile now names what it prices (a degree held), and rescaling was considered and rejected with a reason.
- [7] null control and copy question. Satisfied as in [4].
- [8] mixing. Measured (`mixing` arm re-run reproduces 28.5 % / 16.7 %) and dismissed with a reason (Findings above).
- [9] P141. Absent as expected. The diff has 0 lines touching `_plan_slots` or `PlanSlot` (`git diff c9cbe6b45...313a19d91 | grep -c` → 0), so it is not half-done.

Mutation proof. 10 mutants, each in its own detached worktree at the head, each followed by `PYTHONPATH=tests/hastub python3 tests/features.py`. All were killed (ev/mut-*.diff, ev/mut-*.summary):
- MX4 pooled mean: 1 of 4407 FAILED
- MA1 fuse reads `monthly_cost_delta`: 1 of 4407 FAILED (got -35.0)
- MA3 settled drops the deferred term: 1 of 4407 FAILED (settled = plan)
- RS1 deferred term sign flipped (mine): 1 of 4407 FAILED
- MB2 sweep unpriced: 1 of 4407 FAILED
- MB4 no fee: 1 of 4407 FAILED
- RS2 previous month via `now - 1 day` (mine): 2 of 4407 FAILED
- RS3 gap rate takes a zero recent price (mine): 1 of 4407 FAILED
- RS4 `_sweep_price` floor removed (mine): 2 of 4407 FAILED (existing negative-price checks)
- RS5 fee from this month only (mine): 1 of 4407 FAILED

MC1 on the card: 1 CARD CHECK(S) FAILED. The unmutated head gives `ALL 4407 FEATURE CHECKS PASSED` (rc 0, 5m36s) and `ALL CARD CHECKS PASSED`.

Harness. The finder's named instrument, `r10_sav_null_terms.py`, drives none of these readers: a grep for `async_simulate`, `_dhw_setpoint_sweep`, `rank_sensor_gaps`, `_gap_energy_rate` and `monthly_cost_delta` finds nothing in it. So the finding had no committed harness for these seams (step 9). The fixer disclosed `dev/audit/harnesses/r10_advisor_residue.py` (sha1 ffb5f71b…, matches the body) as their own instrument and landed it, classified in tests/closures.json. I ran it myself:
- `inbox` at the head: `varying gap … (max/min 1.03) widest_day 2.9`, `hot_water … (max/min 1.04)`.
- `inbox` at the base `da12aa37d` with the same harness: `gap … (max/min 18.50) widest_day 453.6`, `hot_water … (max/min 3.08)`.
- `inbox` null: flat (1.00) at both ends.
- `whatif`: `rows 24 plan_moves_by_start 24 held_moves_by_start 0` and `caps rows 12 … plan 50.4 settled 10.1; … plan 18/36 settled 1/36`.
- `asym` and `mixing`: as quoted above.

Every figure the body quotes from these arms re-derived exactly (ev/*-head.log).

Claims, budgets and versions:
- `env_drift.py --all c9cbe6b45` at the head: `NO UNCLAIMED DRIFT: 56 scenario(s)`, `NO STALE FIXTURE: 56`, rc 0. `claims-for: 7.0.4` = VERSION.
- VERSION, the manifest and RELEASE_NOTES.md are untouched (`git diff da12aa37d 367afeb85` empty on them).
- `tests/structure.py`: `class_excess_loc 18101 <= 18101`, `max_class_loc 8306 <= 8306`, `STRUCTURE RATCHET PASSED`. The re-record moves the budgets down only, with its reason in commit 7e0156de8. The movement comes from `monthly_deltas` and `_sweep_price` leaving the class body, so it is earned. No budget rises.

Head and merge:
- Body head = measured head. `fd43a3549` → `313a19d91` adds only `dev/programme/delivery/2834.md`. `367afeb85` → `fd43a3549` changes nothing under custom_components, tests or docs.
- `git merge-tree --write-tree origin/main(f3ffb1c63) 313a19d91` gives rc 0, with `LEDGER-MERGE: resolved tests/closures.json` (ev/merge-tree.txt).

CI on the head (check-runs API, read at about 21:10Z), not all concluded:
- `tests / mutation` is failure. The body names it and answers it: predicted, unpinned sites, ci_predict as the cheaper detector.
- `governance / delivery-status` is failure: `DELIVERY STATUS OVERDUE … 8 overdue`, all of them other PRs' rows (#2798, #2799, #2780, …). The job log says it is NOT a required context and a red there blocks no merge, and this diff's own row is not among the overdue ones. Not this PR's.
- Every other concluded run is success or skipped: arch-score, budget-raise-gate, closure-scope, briefs, policy-docs, wave-script, env-matrix, hassfest, validate-hacs, codeql actions/js.
- Still queued or in progress: fast, typing, closures, replay, browser, coverage, mutation-pins 1/2, instrument-self-tests, codeql python. Their outcome was not available to this review.
