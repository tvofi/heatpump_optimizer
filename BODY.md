R10-SAV-COMFORT: the two limits R10-SAV-BASELINE (#2255, PR #2411) left open in the savings figures, measured on the carry's own terms.

Closes #2492. Part of #201.

**(1) Comfort-matched reference.** The thermostat the savings settle against now holds the comfort schedule shifted down by the plan's mean shortfall below it (`_comfort_matched_targets`, optimizer.py), so comfort the plan gave up is no longer booked as a saving. Both solve paths compute it after the solve from the plan's room trajectory (two-zone: the floors' area-weighted mean, which `room_temps` already is); the unmatched run stays the space path's solver start, so **no plan changes** (the drift gate moves only `baseline_cost`, `deferred_energy_cost`, `predicted_savings`, `savings_percentage`). COP timing survives: a uniform shift keeps dips below target that the plan pays back with heat bought in a warmer hour, and the month row's flat-price null now reads the timing term on a varying outdoor and about 0 on a constant one.

**(2) Start bound.** `_start_gap_cost` debits a warm start by what its heat could displace — the space heat the thermostat buys plus the house's end credit — and never more; #2411 bounded only the part past the caps, so a summer house holding passive warmth was debited its capped gap and read its hot-water saving as a loss. A colder start is still credited at the caps. The end-less-start settlement both paths duplicated is now one method, `_settle_horizon`; on the hot-water path the start is bounded by the house's end alone (the start gap holds the tanks as measured).

**The advisor's degree** (R10-ADVISOR, #2257) differenced `baseline_cost` across what-ifs as "a thermostat held at the schedule". Matched, that figure followed each what-if plan's delivered comfort and parted a coasted from a pre-heated house (#2257's check went red). `OptimizationResult.held_cost` now carries the thermostat at the schedule itself, and `coordinator.py`'s `monthly_held_cost_delta` differences it: a one-token change outside the brief's two seams, taken because the alternative was regressing a merged group's figure.

Alternatives and why each lost (`fixer.md` step 17):
- per-step `min(target, delivered)` instead of the mean shift: books every load-shifting dip below target as comfort lost while the matching pre-heat above it buys nothing, so the timing saving the carry says must survive is eaten (mutant M4 below is this alternative; it fails 5 checks).
- a priced comfort shortfall added to the plan's cost with `baseline_cost` unchanged: `baseline_cost - predicted_cost - deferred_energy_cost` would stop equalling the published saving, and the month row books per-step baseline power, which a horizon-level price does not split.
- settling the start at the caps alone (the carry's measured alternative): summer 1.95 %, but `away_setback` 60.71 % — this bound leaves `away_setback` byte-identical (29.63 %, below).
- `baseline_cost` matched with no `held_cost`: the advisor degree regresses (M16).

Not changed: `ledger.py`. The month row books `baseline_power_schedule` through `get_current_action`, which now carries the matched reference; no ledger arithmetic needed to move.

## Head

50f27375e8a2dc87c807af2065b30ef78a175a84, on merge base 50af6174f53c0f9bec3f705c3a4bb99615f71acc. origin/main has since moved to 145bfe197 (read 2026-10-24T10:45Z); nothing here was re-measured against it.

## Mutation proof

`dev/audit/harnesses/r10_sav_comfort_mutants.py` (in this PR), run on a `git ls-files` copy of the head: each mutant rewrites one predicate, runs the "3L-G7 — monthly savings history" section of tests/features.py (M16: the whole script, since #2257's check solves through a coordinator), and restores. M0 (unmutated): rc=0 failing=0. Every mutant fails at least one check:

- M1 space path keeps the unmatched reference: failing=6 (the booked step depends on the start only through the comfort delivered (single-zone); steady holding power at the matched target; held house a steady state; published reference buys less than the thermostat at the schedule; ...)
- M2 hot-water path reference at the schedule: failing=2 (the booked step ... (two-zone, DHW))
- M3 shortfall never applied: failing=8
- M4 per-step min instead of the mean shift: failing=5
- M5 two-zone reference reads the floor the slab feeds: failing=1 (two-zone, DHW booked step)
- M6 start debit unbounded: failing=4 (thermostat that buys nothing debits nothing; whole debit stops at the thermostat's cost; end credit; never widens)
- M7 the #2411 rule (only the debit past the caps bounded): failing=4
- M8 bound without the end credit: failing=1
- M9 an end charge widens the bound: failing=1
- M10 negative thermostat cost unclamped: failing=1
- M11 the start is handed the tank-inclusive end: failing=1 (the hot-water path hands the start the house's end settlement)
- M12 space-path settlement held at the unmatched schedule: failing=1 (the start settlement holds the house at the schedule the published reference ran)
- M13 a cold start credited uncapped: failing=1
- M14 space-path held_cost read after the matching: failing=1 (held_cost is the thermostat at the schedule itself)
- M15 hot-water held_cost is the matched baseline_cost: failing=1
- M16 the advisor's degree reads baseline_cost again: failing=2 — `#2257: the held figure prices a degree from a steady start` plus `#363 recorded_at`, which fails on every run from a copy without `.git` (the runner's, `fixer.md` step 2; it fails on the unmutated full run of the same copy too).

## Null control

Each harness run at the merge base 50af6174 against the head (production code as at 50f27375; later commits touch tests, docs, the ledger and closures only) (the harness file copied into a detached worktree at the base, then restored):

- `r10_sav_comfort.py const` (outdoor at the window mean, one warm-up day, two booked): base +4.95 % saved with stored heat settled against timing +0.00 % (DEFECT: the comfort term); head +0.35 % (SOUND, |x| < 1.5 %).
- `r10_sav_comfort.py vary` (winter_cold): base +20.03 % against timing +15.30 % (DEFECT); head +16.04 % against timing +15.31 % (SOUND, within 2 points and above 3 %). Comfort: booked thermostat 128.4 kWh at base = steady at target 128.4; head 122.3 against steady at the delivered room 121.9.
- `r10_sav_baseline.py null`: base booked thermostat 128.4 kWh against steady at the delivered room 121.5 (DEFECT); head 121.8 against 121.5 (SOUND). Published row: base 12.34 % (the carry measured 10.83 % at #2411's head), head 7.59 %.
- `r10_sav_baseline.py transient`: base step 0 off the matched holding power by 1.81e-01 kW (DEFECT; 0.00 kW spread, the #2411 reading); head 8.88e-16 kW (SOUND; spread 0.07 kW, the comfort each start delivers).
- Golden `summer_dhw_only`: base -7.62 %, head +5.88 %; `negative_prices` -13.19 % -> +16.17 %; `away_setback` byte-identical at 29.63 % (the alternative the carry measured read 60.71 %).

## Figures

- Every flat-price null and term figure above: `PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_sav_comfort.py` (`dev/audit/harnesses/r10_sav_comfort.py`, sha1 6615a321e3169db377b9c661f689ade65c31f78e) and `python3 dev/audit/harnesses/r10_sav_baseline.py` (`dev/audit/harnesses/r10_sav_baseline.py`, sha1 88ac23e4b83a349789b5c6674e0cbee6021e736f at the head, its transient and null verdicts re-keyed in this PR; the same file ran at both ends), at each end.
- The carry's terms at the base: `python3 dev/audit/harnesses/r10_sav_null_terms.py` and `... r10_sav_null_terms.py const` (`dev/audit/harnesses/r10_sav_null_terms.py`, sha1 c981e7c840ede1a5fef95aa903e00e5809c92aa7): comfort gap 6.9 kWh (const 5.2), outdoor-timing gain +17.29 % (const +0.00 %), const drawdown 9.3 kWh_e; at the head the booked thermostat reads 121.8 kWh against steady-at-delivered 121.5 (const 119.2 against 119.4), so the comfort term is gone from the booking and the const gap (9.1) is the drawdown (9.3).
- The golden figures and the 41 claims: `PYTHONPATH=tests/hastub python3 tests/env_drift.py --all 50af6174f53c0f9bec3f705c3a4bb99615f71acc` — 41 fixtures move, only in the four savings keys (`baseline_cost` in 39; `summer_dhw_only` and `negative_prices` move only by the start bound); 15 of them carried may-drift entries, suspended with their restore obligation as R10-SAV-BASELINE did. Null control: the same command at the base reports none.
- Mutation table: `python3 dev/audit/harnesses/r10_sav_comfort_mutants.py <copy>` (`dev/audit/harnesses/r10_sav_comfort_mutants.py`, sha1 fd9b564dd8d3efd37cf814bd656cd18cd6f708e3), above.
- Seam census, the readers of the savings reference: `grep -rnE '\.baseline_cost|"baseline_cost"|baseline_power_schedule|"baseline_kw"|predicted_savings|savings_percentage|held_cost' custom_components/ --include=*.py`, excluding optimizer.py, returns these, each dispositioned:
  - sensor.py `predicted_savings`, `savings_percentage`, `baseline_cost` sensors; climate.py attributes; coordinator.py payload (`baseline_cost`, `predicted_savings`, `savings_percentage`), its optimisation log line and the what-if's `savings_percentage`: read the savings reference, and move with it by design (they stay mutually consistent: saving = baseline - cost - deferred).
  - ledger.py `baseline_kw` (via `get_current_action`) and coordinator.py's diagnostics `baseline_kw`: the month row's booking, the fix's target.
  - coordinator.py `monthly_held_cost_delta`: closed in this diff (`held_cost`).
  - coordinator.py what-if `"baseline_cost": round(result.predicted_cost, 2)`: the live plan's cost under a misleading key, not the reference; unaffected.
  - price_tiles.py `monthly_held_cost_delta` key: reads the coordinator's figure above.
- Structure: `python3 tests/structure.py` passes (class_excess_loc 18217 <= 18217, methods_over_200 9 <= 9). The fix first measured +19 / +1, then +11 with `held_cost`; paid by code improvement, not a raise: `_settle_horizon` removes the settlement both solve paths duplicated; the buffer and DHW marginal-COP corrections in `_deferred_energy_cost` are one loop with the same arithmetic (no unclaimed fixture moved); spent history prose cut in `_deferred_energy_cost`, `_compute_baseline_power` and `_build_result`. Considered and not taken: moving the settlement to module level (a move to an unmeasured path, not an improvement), and a raise (no owner confirmation obtainable before the push).
- Architecture: `python3 tools/audit/archscore/score.py --diff 50af6174f53c0f9bec3f705c3a4bb99615f71acc` reads `dS +0.0000 NULL`; a first cut read `computed_attr_access 32 -> 34` (a `getattr` loop) and was rewritten to read the fields directly.
- Scoped gate: `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=50af6174f53c0f9bec3f705c3a4bb99615f71acc tests/run.sh` at 2aa2382d (the head less the closures commit), `MODE: SCOPED -- 28 script(s) run, 5 scoped out`: every script ok but `tests/entities.py` (2 of 2425, both under Red checks and red at the base) and `tests/stress.py` (1 of 113, under Red checks). After the closures commit: `tests/harness_headers.py` 112 passed, `tests/closure.py selftest` passed, `tools/pr/ci_predict.py --base origin/main` predicts no closures or fast red.
- Documented comfort-weight table: `tests/stress.py`'s "the README's comfort-weight table still holds" read w=5 51 % against the documented 53 % after the fix (19.44 °C / 50.93 %, 19.76 / 49.89, 20.20 / 47.80, 20.38 / 46.51 at the head; 52.18 / 50.77 / 48.12 / 46.60 % at the base, same temperatures — the plans do not move). docs/how-it-works.md's table and stress.py's copy now read 51 / 50 / 48 / 47 %, with one sentence saying the savings are against the comfort the plan delivered.
- Mutation ledger: three `killed_by` pins on `_start_gap_cost` keyed on its retired return and surplus lines are dropped (`tests/entities.py`'s `--anchor` check named them "disposition names no site the inventory generates"); the new sites are under Unpinned sites.

## Red checks

- `tests / stress` (local `tests/stress.py`, 1 of 113): "no scenario's production calls grew past what its work counts vouch for, on an unchanged plan" — winter/1z/space/pin-off 84263 production calls against the base's 78480 = 1.074x over the 1.05x allowance (thermal_model.py +4072, optimizer.py +1654). Cause: the space path's second thermostat run at the comfort-matched schedule (one 96-step `_compute_baseline_power` per solve; the unmatched run must stay because it is the solver start, and replacing that start would move every plan). It is the added work by design, not hidden interpreter work, so no cheaper detector is owed. stress.py's own rule for a legitimate firing is that it passes for this one PR on tvofi's approving review naming the merge and the growth, never by a raise: **this PR needs that review**.
- `tests / fast`'s `tests/entities.py`, 2 of 2425: "gate-sweep.yml: on CI's completion ... (U0c)" and "graders-head-copy's delivery_status step is red only when ...". Both fail identically on the merge base in this environment (`tests/entities.py` at 50af6174: 2 of 2425, the same two), so they are not this diff's; no root cause owed here.

## Unpinned sites

`tools/pr/ci_predict.py --base origin/main` lists 8; each was killed by a hand-applied mutant in `r10_sav_comfort_mutants.py` (above) and is left to `mutation-autofix` to pin, except one triage:

- `optimizer.py:345 CMP_BOUND` (`if not shortfall > 0.0:`): pinned by `mutation-autofix`; `>=` hands back a shifted copy at a 0.0 shortfall, which "a plan at or above the schedule ... leaves the schedule itself" (`is`) fails.
- `optimizer.py:345 GUARD_OFF`: pinned by `mutation-autofix` (M3, 8 checks).
- `optimizer.py:347 RETURN_DEL`: pinned by `mutation-autofix` (the reference becomes `None`; the section's solves fail).
- `optimizer.py:4600 GUARD_OFF` (`if reference_targets is not comfort_targets:`): pinned by `mutation-autofix` (M1, 6 checks).
- `optimizer.py:5193 GUARD_OFF` (`if cop_store != cop:`): written triage, equivalent: with the guard off and `cop_store == cop` the correction adds `gap / cop - gap / cop`, which is exactly `0.0` in IEEE arithmetic, so `electrical` is unchanged; the guard keeps the historical arithmetic path, not a different value. It is the guard both tank branches carried at the base, now on the one loop.
- `optimizer.py:5399 CLAMP_DROP*2` (`displaced = max(0.0, space_baseline_cost) + max(0.0, -end_cost)`): pinned by `mutation-autofix` (M10 and M9, one check each).
- `optimizer.py:5400 CLAMP_DROP*2` (`return max(min(capped, uncapped), -displaced)`): pinned by `mutation-autofix` (M6, 4 checks; M13, 1 check).
- `optimizer.py:5400 RETURN_DEL`: pinned by `mutation-autofix` (`None` settles nothing; every savings check of the section fails).

## Forward-carry

none: no not-started roster group consumes `baseline_cost`, `baseline_power_schedule` or the start settlement (the roster's briefs and carries searched for savings terms; R10-ADVISOR, R10-SAV-REASONS and R10-SCORES are done, and the one reader of theirs this moves is kept by `held_cost`).

## Friction

none
