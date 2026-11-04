R10-PARTLOAD-PRICING: the residue of R10-COP-PARTLOAD (#2872, #3006). The brief says to measure first and to change a cost law only where the error is material. This pull request does three things:

- It closes the last inline small-buffer fallback (carry 1).
- It lands the instrument that measures carries 2 and 3, `dev/audit/harnesses/r10_partload_pricing.py`, with a zero-derate null on every arm.
- It re-measures carry 0 at this merge base.

It changes no cost law. Carry 6 and the decision on carry 2 wait, as stated under each carry below.

**Carry 1, built.** `ThermalModel._substeps_and_loss`'s two-zone throttled branch had its own copy of the `c_buf < 1e-6 -> 0.04` fallback. Its comment says it mirrors `_simulate_step_two_zone`, and that function has called `_buffer_capacity` since #3006. Now this branch calls `_buffer_capacity(p)` too. The predicate and the value are the same, and the substep counts are identical bit for bit (Null control). This was the last copy (Figures, Class enumeration). The carry names `optimizer.py`, but the copy was in `thermal_model.py`.

**Carry 2: linear valuations under a convex cost. Measured, not segmented.** The scenarios are #3006 round 2's: `r10_cop_partload.py`'s 16 installs on its spread and flat days, at d=0 and at the central plant's derate d=0.112.

- The hot-water LP's objective `price * E / cop`, evaluated on the plan it published, under-prices the derated per-step cost by at most 0.173/day (spread) and 0.267/day (flat). The hot-water cost those plans pay is up to 8.07 and 7.01/day, so the error is at most about 3.8 % of the figure it prices. That is below what I would call material for a planner whose COP law itself carries larger errors. I did not segment the LP.
- `_terminal_cost` and `_deferred_energy_cost` state no refill rate, so their error is a range, not a number:
  - At a modulation-floor refill it is 0.
  - At a max-power refill it is the figure times `d / (1 - d)` (12.6 % at d=0.112): up to 4.37/day for the terminal and 2.13/day for the deferred figure.
  - Which end is true depends on a refill rate the tree does not state. Choosing one is the D0 decision the carry reserves for "a later D0 pass on `_plan_dhw_min_cost` and `_terminal_cost`". I made no change, and the measurement goes forward to that pass (Forward-carry).
- The wood advisor's pump-heat price (`wood_fuel.cheaper_hour_count`, `_scan_wood_night`) has the same secant factor, `P_r / heat_per_cop_kw(P_r) - 1`, at whatever rate the pump would run. It was not measured separately. It goes to the same destination.

**Carry 3: mean-draw pricing. Measured; no change.** Each production cost law was re-run with its module's `power_for_heat_per_cop_kw` swapped, for that call only, for run-power pricing `E * P_run / heat_per_cop_kw(P_run)`. `P_run` is the published hot-water plan's own peak draw (4.0 kW on every hot-water cell).

- **The setpoint sweep's chosen setpoint moved in 0 of 16 cells** at d=0.112 (8 hot-water cells, each on 2 price days). This holds by construction: `P_run` does not depend on the candidate, so run-power pricing scales every candidate's cost by the same factor and cannot reorder them. Only the displayed `cost_per_day` would change.
- **The always-hot baseline's cost rises by up to +0.673/day** against a baseline of about 23/day (+2.9 %). It rises in the same direction on every derated cell, and never falls. The baseline today is the cheaper of the two laws, so `predicted_savings` errs low, which is the conservative direction the baseline's own docstring states for the wood coil.
- Neither change is material to a decision, so neither cost law changes. The carry calls this a design change. Without a decision that moves, I judged it not worth making.

**Carry 0: live buffer store CPU. Re-measured; no fix built.** `r10_buffer_store.py bench 3` at this head (production code identical to the merge base except carry 1's bitwise-identical line) gives:

- owner shape: median 1.57 s, max 2.853 s;
- null: median 0.797 s;
- ratio 1.97x. #3006 measured 2.44x at `507a9ec26`.

The null differs from the owner shape in two levers, flat prices and no buffer, so the ratio is not a one-lever figure. The 272 s owner-box outlier does not reproduce here: max 2.85 s on a 4-core x86_64 container. A bound or warm start has nothing measured here to earn it, so none is built and the carry stays open (Forward-carry).

**Carry 6: the relaxed start's CPU on the owner's Pi. Waits on the owner.** It is owed as a measured `process_time` on the owner's Pi install. A cloud seat cannot take it, and an x86 figure would be the estimate the carry already rejects. It waits for the owner's run.

**Carry 7.** No `coordinator.py` edit. The harness calls `_dhw_setpoint_sweep` on a stub, read-only.

Alternatives considered:

- Segmenting the hot-water LP per step: refused on the measured magnitude, at most 3.8 % of hot-water cost.
- Choosing a terminal refill rate here: refused, because the carry reserves that choice for D0.
- Run-power pricing of the sweep: refused, because it cannot move the recommendation.

**Roster carries, by the checker's numbering.** The brief numbers carries by 0-based roster index. `review_packet.py`'s `brief-carries` count numbers them 1..8. Each roster entry is answered under both numbers:

- Carry 1 (roster index 0, live buffer store CPU): re-measured, not built. See "Carry 0" above. Carry: dismissed: already held open on this group's roster entry at index 0
- Carry 2 (roster index 1, inline 35 L fallback): built. See "Carry 1" above.
- Carry 3 (roster index 2, linear valuations): measured, routed to D0. See "Carry 2" above. Carry: dismissed: already held open on this group's roster entry at index 2
- Carry 4 (roster index 3, mean-draw pricing): measured, no change. See "Carry 3" above.
- Carry 5 (roster index 4): dismissed on the roster as a duplicate of index 2. It is answered by the measurement of index 2, and its flat-price null is in the harness's `flat` arm.
- Carry 6 (roster index 5): dismissed on the roster as a duplicate of index 3. It is answered by the measurement of index 3, flat-price arm included.
- Carry 7 (roster index 6, the relaxed start's Pi CPU): waits on the owner's Pi install. See "Carry 6" above. Carry: dismissed: already held open on this group's roster entry at index 6
- Carry 8 (roster index 7, coordinator lane): no `coordinator.py` edit. See "Carry 7" above.

## Head

f835d03b469189fb4b56a6082846edc17e19aad3. Its parent chain from the merge base `c3a279e3252a8b57bb00b5a677318cd4fe20387f`:

- the carry-1 edit and the harness;
- the INERT entry and the two stale ledger pins;
- the structure record.

origin/main is still `c3a279e3252a` at `date -u` Wed Nov  4 06:51:44 UTC 2026, so no merge was needed, and `prepr.sh` ran once on an unmoved main.

## Mutation proof

Carry 1 is a deduplication that changes no float, so it has no failing test to write first. The mutation evidence is that the edited branch is load-bearing on the shared helper:

- Mutant: `_buffer_capacity`'s fallback `0.04` changed to `0.08`.
- Driver: a scratch driver over `_substeps_and_loss` with a two-zone, manual-valve install at buffer volumes {0, 1e-6, 35, 200, 750} L.
- Result: at 0 L the substep count goes from 8 to 4. Before this diff the branch kept its own copy, so the same mutant left it at 8. That copy is the duplication this pull request removes.

The two ledger pins on the deleted guard line (`_substeps_and_loss` CMP_BOUND and GUARD_OFF `e26455a8`, killed by `tests/features.py`) were named STALE by `ci_predict.py` and are deleted. The guard they pinned now exists only inside `_buffer_capacity`.

## Null control

- **Carry 1, bitwise.** The same driver, run at the merge base (via `git stash`) and at the head, printing `repr` of `(n_sub, u_upper, u_lower)`: `diff base head && echo IDENTICAL` printed `IDENTICAL`. The fallback arm is reached at 0 L and 1e-6 L (mass 1.16e-9 kWh/K), where n_sub is 8. The control on the comparator itself is the 0.08 mutant above, which the same diff sees (8 to 4).
- **Carries 2 and 3, zero derate.** At d=0 the harness prints the following on all 32 rows: `lp_err` 0.000000, terminal and deferred at-max 0.000000, baseline change +0.000000, and sweep setpoint unchanged. It counts any non-zero d=0 row in `null rows not zero`, which reads 0. A non-zero row exits 1.
- **Carry 3, a flat price day.** It does not null the baseline: the baseline change is identical on the spread and flat days (+0.672589). That is expected, because the change is a fixed energy times a mean price.

## Figures

- `PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/r10_partload_pricing.py` (sha1 8b5cdfa93b3e) at the head prints `central plant derate 0.112`, then:
  - `spread d=0.112`: `lp_err max 0.173106 (dhw cost max 8.0681) terminal-at-max max 3.720568 deferred-at-max max 1.381800 baseline change min +0.000000 max +0.672589 sweep setpoint moved 0`.
  - `flat d=0.112`: `lp_err max 0.267290 (dhw cost max 7.0145) terminal-at-max max 4.374372 deferred-at-max max 2.125411 baseline change ... max +0.672589 sweep setpoint moved 0`.
  - Both `d=0.0` summaries read all zeros.
  - Closing lines: `null rows not zero 0`, `failures 0`.
  - The baseline's "min +0.000000" comes from the 8 cells without hot water, which have no hot-water baseline. "Moved 0" is counted over the 8 hot-water cells per day.
- Carry 0: `PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/r10_buffer_store.py bench 3` (sha1 1ed68fea6f69) prints:
  - `owner_buffer_spread median_s 1.57 max_s 2.853`;
  - `null_flat_nobuffer median_s 0.797 max_s 0.884`;
  - 4 CPUs, load average 0.73.
- The venvs were refreshed by `bash tools/audit/seat/cloud-setup.sh`. `cloud-setup.sh --check` reads OK. `python3 -c 'import numpy,scipy;print(...)'` prints `2.5.4 1.18.1`, matching `tests/requirements-ci.txt`.
- Gate scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` -> `MODE: SCOPED -- 27 script(s) run, 6 scoped out`.
- Scoped gate: `GATE_SCOPE=auto GOLDEN_MODE=drift PYTHONPATH=tests/hastub bash tests/run.sh` -> `MODE: SCOPED -- 27 script(s) run, 6 scoped out`, `29 TEST SCRIPT(S) PASSED; 5 SCOPED OUT AND NOT RUN`, among them `ALL 4777 FEATURE CHECKS PASSED`, `ALL 84 OPTIMALITY CHECKS PASSED`, `ALL 113 STRESS CHECKS PASSED` and `ALL 112 HARNESS HEADER CHECKS PASSED`.
- Structure: `python3 tests/structure.py --record` moves `class_excess_loc` from 17640 to 17637. The ThermalModel span lost 3 lines. `STRUCTURE RATCHET PASSED` at the head.
- Architecture score: `python3 tools/audit/archscore/score.py --diff c3a279e3252a8b57bb00b5a677318cd4fe20387f HEAD` -> `Architecture score: dS +0.0000 NULL`.
- CI predict: `python3 tools/pr/ci_predict.py` -> `no closures, fast, governance or instrument red predicted against c3a279e3252a`, after `--apply-inert` wrote the harness's INERT entry for `tests/harness_headers.py`.
- Class enumeration for carry 1. The rule is `git grep -nE "c_buf *= *0\.04|0\.04 if c_buf" -- custom_components/heatpump_optimizer/`, which finds every inline small-buffer fallback:
  - At the head it returns one hit: `thermal_model.py`, `_buffer_capacity`'s return line, which is the shared helper.
  - At the merge base `c3a279e32` it returns that line and `_substeps_and_loss`'s copy (`c_buf = 0.04  # the step's own fallback`). This diff closes the copy.
  - The null control is `git grep -n "0\.04" -- custom_components/heatpump_optimizer/optimizer.py | wc -l`, which prints 0: no copy is in `optimizer.py`.

## Red checks

none. The local scoped gate is green at the head. `ci_predict.py` predicts no red after the INERT entry and the two deleted stale pins, which it named and which were repaired before the handoff.

## Forward-carry

- **Carry 2, measured.** The LP secant is at most 0.267/day, about 3.8 % of hot-water cost, at d=0.112. The terminal and deferred figures range from 0 at a floor refill to `d / (1 - d)` (up to 4.37 and 2.13/day) at a max-power refill. The wood advisor's price takes the same factor. Choosing a refill rate is the D0 decision. Destination: the D0 pass on `_plan_dhw_min_cost` and `_terminal_cost`, which the roster entry's index 2 already names. The instrument is `dev/audit/harnesses/r10_partload_pricing.py`. Carry: dismissed: already held open on this group's roster entry at index 2, which this pull request does not close; landing a duplicate is the standing-roster seat's
- **Carry 0.** The live buffer store's CPU is 1.97x the null's median at this head, which is not a one-lever null. The 272 s outlier was not reproduced. No bound or warm start is built. Carry: dismissed: already held open on this group's roster entry at index 0, which this pull request does not close; landing a duplicate is the standing-roster seat's
- **Carry 6.** The Pi `process_time` of the relaxed start is owed from the owner's install. It waits on the owner. Carry: dismissed: already held open on this group's roster entry at index 6, which this pull request does not close; landing a duplicate is the standing-roster seat's

## Friction

- frugal-routing: cost: a session-local plugin's inline-read budget blocked plain reads and `git grep`s mid-task; lookups were delegated instead. Carry: dismissed: a session-local plugin, not repository policy
- review-packet-brief-carries: contradiction: the dispatch brief numbers carries by 0-based roster index ("Carry 0" to "Carry 7"), while `review_packet.py`'s `unnamed_carries` requires the 1-based `Carry 1..N`, so a body that follows the brief is refused on carries it answered. Carry: dismissed: reported to the orchestrator in this body
