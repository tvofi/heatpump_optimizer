# Review packet #3736
head: bdf096245858f5a381b67719c4174d7a2880974d
base: 9fe63d00b59f100aea67267ddddc95522e164aa1

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=134915274418 success
arch-score / arch-score id=134979663197 success
arm id=134899294932 skipped
budget-raise-gate / budget-raise-gate id=134979590667 success
cancel-superseded id=134979648893 success
codeql id=134979647811 skipped
codeql / Analyze (actions) id=134908699833 success
codeql / Analyze (javascript-typescript) id=134908699998 success
codeql / Analyze (python) id=134908699871 success
gate id=134979588226 failure
governance id=134979648548 skipped
governance / env-matrix id=134908700184 success
governance / instrument-self-tests id=134908700070 success
governance / policy-docs id=134908699852 success
governance / record id=134908703360 skipped
governance / wave-script id=134908699874 success
hassfest id=134979588933 skipped
hassfest / hassfest id=134908699449 success
kernel-points id=134979589629 skipped
pr-contract id=134979590081 skipped
pr-contract / pr-contract id=134971703670 failure
prelude id=134979647761 success
refresh id=134979667450 success
sweep-self id=134985243411 skipped
tests id=134979668037 skipped
tests / arch-instrument id=134916816183 success
tests / briefs id=134908699318 success
tests / browser id=134916816690 success
tests / ci-ratchet id=134957997666 skipped
tests / claims-autofix id=134957994479 success
tests / closure-scope id=134908699929 success
tests / closures id=134916816246 success
tests / closures-autofix id=134950484904 skipped
tests / coverage id=134916816343 success
tests / coverage-ratchet id=134953463767 success
tests / fast (3.14) id=134916816497 failure
tests / graders-head-copy id=134953463852 success
tests / lane-proofs id=134957994446 success
tests / mutation id=134908699995 failure
tests / mutation-autofix id=134940777396 failure
tests / mutation-pins (1) id=134920642610 success
tests / nightly-ha id=134916819216 skipped
tests / nightly-status id=134908699532 failure
tests / replay id=134916816362 failure
tests / typing id=134916816202 success
validate id=134979619535 skipped
validate / validate-hacs id=134908699732 success

## Refusals
red-unanswered: concluded red check `gate` is not named in ## Red checks
red-unanswered: concluded red check `pr-contract / pr-contract` is not named in ## Red checks
red-unanswered: concluded red check `tests / fast (3.14)` is not named in ## Red checks
red-unanswered: concluded red check `tests / mutation` is not named in ## Red checks
required-red: required context `gate` concluded failure at bdf096245858f5a381b67719c4174d7a2880974d (merge_train.py classify --pr reads RED pending: none red: gate)

## Advisories
none

## carry_audit at the head
NOTE body item 525b3b42: dismissed:outside D0-s2-01's mechanism by the finding's own perturbation; class P4's RCA, marked owed in ISSUES.json, is the seat that reads it
NOTE body item aa9c98dc: dismissed:corrected by the orchestrator's ruling before this fire
NOTE body item b2263e64: dismissed:the reproduction recipe is in this body's Figures, the reviewer's own surface
CARRY-AUDIT: 3 finding item(s): 3 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
unverified MODE: SCOPED -- 27 script(s) run, 6 scoped out.
             no segment of this names a program this check knows
  unverified git diff --stat 661c624c 261a3998 -- custom_components
             `git diff` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified git archive 819aa2e3 dev/audit/rounds/round11
             `git archive` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified python3 $EXPORT/dev/audit/rounds/round11/D1/leads/slot_reason_hashseed.py
             the path `$EXPORT/dev/audit/rounds/round11/D1/leads/slot_reason_hashseed.py` is a template or an expansion, not a literal
  unverified python3 $EXPORT/dev/audit/rounds/round11/D2/s3/m3_risk.py
             the path `$EXPORT/dev/audit/rounds/round11/D2/s3/m3_risk.py` is a template or an expansion, not a literal
  unverified python3 $EXPORT/dev/audit/rounds/round11/D0/s3/offstart.py --workers 2
             the path `$EXPORT/dev/audit/rounds/round11/D0/s3/offstart.py` is a template or an expansion, not a literal
  unverified python3 $EXPORT/dev/audit/rounds/round11/D0/s2/wood_seeds.py --census
             the path `$EXPORT/dev/audit/rounds/round11/D0/s2/wood_seeds.py` is a template or an expansion, not a literal
  unverified python3 $EXPORT/dev/audit/rounds/round11/D0/s2/wood_seeds.py --race
             the path `$EXPORT/dev/audit/rounds/round11/D0/s2/wood_seeds.py` is a template or an expansion, not a literal
  ok         PYTHONPATH=tests/hastub python3 tests/env_drift.py --all bc658f9ded3da4ce7daf8bb854b6bc24e67a9d5f
             `tests/env_drift.py` is in the tree at this head
  ok         tools/audit/seat/cloud-setup.sh --kernels
             `tools/audit/seat/cloud-setup.sh` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         python3 tools/audit/archscore/score.py --diff bc658f9ded3da4ce7daf8bb854b6bc24e67a9d5f
             `tools/audit/archscore/score.py` is in the tree at this head
  ok         python3 tests/closure.py select --diff bc658f9d
             `tests/closure.py` is in the tree at this head

FIGURES: 5 resolved, 8 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._optimize_space_only.GUARD_OFF.6a3be0ea.json b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._optimize_space_only.GUARD_OFF.6a3be0ea.json
deleted file mode 100644
index e6d1570aff..0000000000
--- a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._optimize_space_only.GUARD_OFF.6a3be0ea.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/optimizer.py:HeatPumpOptimizer._optimize_space_only GUARD_OFF 6a3be0ea",
-  "killed_by": "tests/optimality.py",
-  "old": "        if self.model.params.two_zone_enabled:",
-  "reason": "arrived with round 7 D0-01 (#1447): the gate that scopes the deep low-energy anchor to the two-zone path, so every single-zone plan stays byte-identical to origin/main and the certificate's three claims keep their calibration. Killed by tests/optimality.py -- `if self.model.params.two_zone_enabled:` -> `if False:` never appends the anchor, which is the same tree as deleting it: FAIL two|winter_typical|winter_cold: no unclaimed gap above the bar [ladder 0.4374%, bar 0.4000%], 1 of 84, measured on this branch."
-}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._solve_objectives.RETURN_DEL.ac696c3f.json b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._solve_objectives.RETURN_DEL.ac696c3f.json
deleted file mode 100644
index ee3dfe4d02..0000000000
--- a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._solve_objectives.RETURN_DEL.ac696c3f.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/optimizer.py:HeatPumpOptimizer._solve_objectives RETURN_DEL ac696c3f",
-  "killed_by": "tests/doc_claims.py",
-  "old": "        return _space_traj, objective, objective_batch, energy_cost_of",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 2b6c5b876ec297bf2b0ef4a127d09cf97fc40b5d: RETURN_DEL (`pass`) took tests/doc_claims.py from rc=0 failed=0 to rc=1 failed=1."
-}


## Review scope: full (first round: no --reviewed-head)

## Three-dot diff
diff --git a/custom_components/heatpump_optimizer/optimizer.py b/custom_components/heatpump_optimizer/optimizer.py
index 876fee23ad..7db38b1ebc 100644
--- a/custom_components/heatpump_optimizer/optimizer.py
+++ b/custom_components/heatpump_optimizer/optimizer.py
@@ -2111,6 +2111,66 @@ def _better_objective(
     return left
 
 
+
+def _lower_bound_start(bounds: list[tuple[float, float]]) -> np.ndarray:
+    """The all-off start: every step at its lower bound (D0-s3-02).
+
+    Zero where a step is free, a forced-on pin's running floor where one
+    holds. Every other start buys energy, so without this one a day whose
+    optimum is to buy none -- negative prices on a storage plant, a house
+    the wood tank already carries -- is reached only if a descent finds it.
+    """
+    return np.array([low for low, _ in bounds], dtype=float)
+
+
+def _space_only_starts(
+    model: ThermalModel,
+    state: ThermalState,
+    target: float,
+    initial_power: np.ndarray,
+    reference_power: np.ndarray,
+    prices: np.ndarray,
+    bounds: list[tuple[float, float]],
+    p_max: float,
+    dt: float,
+) -> list[np.ndarray]:
+    """The space-only solve's multi-start set, the initial guess first.
+
+    The smooth price-weighted guess, a bang-bang schedule that buys the
+    cheapest steps first, the reference thermostat's own schedule, and the
+    low-energy bang-bang seeds (R1-D0-01 and R7-D0-01 -- see the two
+    fractions' comments for why the same-energy candidates all refine into
+    one basin on arbitrage prices, and why 0.35x alone does not bracket the
+    optimum's energy); the deep low-energy anchor is two-zone only, see its
+    own comment for why the reach is deliberately this narrow. See
+    ``_multi_start_minimize`` for why one guess is not enough.
+
+    The seeds scale with the share of the reference the wood tank covers,
+    so a tank covering it whole collapses them onto zero (D0-s2-01): the
+    price-ranked seeds are then also drawn at the reference's own energy,
+    and the all-off start brackets the set from below (D0-s3-02).
+    """
+    reference_kwh = float(np.sum(reference_power) * dt)
+    covered = _wood_covered_share(model, state, reference_kwh, target)
+    seed_power = reference_power * (1.0 - covered)
+    energy = float(np.sum(seed_power) * dt)
+    fractions = (_LOW_ENERGY_START_FRACTION,) + (
+        (_DEEP_LOW_ENERGY_START_FRACTION,) if model.params.two_zone_enabled else ()
+    )
+    starts = [
+        initial_power,
+        _price_ranked_start(prices, energy, p_max, dt),
+        seed_power,  # inside the bounds: the reference never passes the pump
+        *(_price_ranked_start(prices, energy * f, p_max, dt) for f in fractions),
+    ]
+    if covered > 0.0:
+        starts.extend(
+            _price_ranked_start(prices, reference_kwh * f, p_max, dt)
+            for f in (1.0, *fractions)
+        )
+    starts.append(_lower_bound_start(bounds))
+    return starts
+
 def _price_ranked_start(
     prices: np.ndarray, energy_kwh: float, p_max: float, dt: float
 ) -> np.ndarray:
@@ -2887,6 +2947,9 @@ class _Horizon:
     """
 
     initial_state: ThermalState
+    #: The prices the objective weighs: the input plus the risk premium
+    #: ``_stash_price_horizon`` adds on guessed steps (#34). Never a money
+    #: figure: those read ``money_prices``.
     prices: np.ndarray
     outdoor_temps: np.ndarray
     wind_speeds: np.ndarray
@@ -2973,6 +3036,19 @@ class _Horizon:
     comfort_floors: np.ndarray | None = None
     mold_floors: np.ndarray | None = None
     away_floor_drops: np.ndarray | None = None
+    #: The input prices before the risk premium, what a bill pays (D2-s3-01).
+    #: ``None`` means ``prices`` carries no premium.
+    raw_prices: np.ndarray | None = None
+
+    @property
+    def money_prices(self) -> np.ndarray:
+        """The prices every published money figure is booked on: the input's.
+
+        The premium is a solver preference, not a price anyone pays, so it
+        stays in the objective and out of the plan's cost, the reference's,
+        the settlement and the published price series.
+        """
+        return self.prices if self.raw_prices is None else self.raw_prices
     #: ``SolveInputs.compressor_running``.
     compressor_running: bool = False
 
@@ -3887,7 +3963,7 @@ class HeatPumpOptimizer:
             ),
             objective_value=objective_value,
             timestamps=h.timestamps,
-            prices=h.prices.tolist(),
+            prices=h.money_prices.tolist(),
             outdoor_temps=h.outdoor_temps.tolist(),
             predicted_cost=predicted_cost,
             baseline_cost=baseline_cost,
@@ -4385,9 +4461,9 @@ class HeatPumpOptimizer:
         if start_time is None:
             start_time = datetime.now()
 
-        prices = prices[:n_steps]
+        raw_prices = np.asarray(prices[:n_steps], dtype=float)
         prices = self._stash_price_horizon(
-            initial_state, n_steps, price_known, price_sigma, prices, pv_surplus
+            initial_state, n_steps, price_known, price_sigma, raw_prices, pv_surplus
         )
         # One hot-water planner per solve, from this solve's inputs (#1743).
         planner = DhwPlanner(
@@ -4506,6 +4582,7 @@ class HeatPumpOptimizer:
                 comfort_floors=floors[0],
                 mold_floors=floors[1],
                 away_floor_drops=away_drops,
+                raw_prices=raw_prices,
                 compressor_running=inputs.compressor_running,
             )
             if dhw_enabled:
@@ -4990,6 +5067,7 @@ class HeatPumpOptimizer:
                     headroom,
                 )
             )
+            starts.append(_lower_bound_start(bounds))
         descent = _descent_pair(self, objective, objective_batch)[0]
         try:
             res, relaxed = _relaxed_plans(self, rescope, scope, headroom, starts, dhw_plan)
@@ -5323,6 +5401,7 @@ class HeatPumpOptimizer:
     ]:
         """Both solve paths' trajectory, objective, batch twin and price (#1743).
 
+        The price is the bill's, on ``h.money_prices`` (D2-s3-01).
         The DHW path passes its fixed plan as ``dhw_plan_power``; with
         ``None`` the arithmetic is the space-only path's, operand for operand.
         """
@@ -5458,7 +5537,10 @@ class HeatPumpOptimizer:
                 comfort_band=comfort_band,
             )
 
-        return _space_traj, objective, objective_batch, energy_cost_of
+        return (
+            _space_traj, objective, objective_batch,
+            self._energy_cost_fn(h.money_prices, dt),
+        )
 
     def _optimize_space_only(self, h: _Horizon) -> OptimizationResult:
         """Optimize space heating only (no DHW)."""
@@ -5484,7 +5566,7 @@ class HeatPumpOptimizer:
         anticipatory_weights = self._anticipatory_weights(
             n_steps, dt, solar_gains_per_step, forecast_heat_loss_factors
         )
-        _space_traj, objective, objective_batch, energy_cost_of = (
+        _space_traj, objective, objective_batch, paid_cost_of = (
             self._solve_objectives(h)
         )
 
@@ -5513,44 +5595,15 @@ class HeatPumpOptimizer:
         bounds = _apply_pins_to_bounds(bounds, h.space_pins, self._pin_on_power(p_max))
         initial_power = self._seed_pinned_guess(initial_power, bounds)
 
-        # Multiple starting points: the smooth price-weighted guess above, a
-        # bang-bang schedule that buys the cheapest steps first, a flat
-        # schedule, and the low-energy bang-bang seeds (R1-D0-01 and R7-D0-01
-        # -- see the two fractions' comments for why the same-energy
-        # candidates all refine into one basin on arbitrage prices, and why
-        # 0.35x alone does not bracket the optimum's energy). See
-        # _multi_start_minimize for why one guess is not enough.
         # Computed once and reused below for the savings reference; the same
         # simulation also makes a good solver start.
         baseline_power, baseline_end = self._compute_baseline_power(
             weather, initial_state, dt, comfort_targets,
         )
-        seed_power = baseline_power * (1.0 - _wood_covered_share(
-            self.model, initial_state, float(np.sum(baseline_power) * dt), self.config.target_temp,
-        ))
-        baseline_energy = float(np.sum(seed_power) * dt)
-        starts = [
-            initial_power,
-            _price_ranked_start(prices, baseline_energy, p_max, dt),
-            seed_power,  # inside the bounds: the reference never passes the pump
-            _price_ranked_start(
-                prices,
-                baseline_energy * _LOW_ENERGY_START_FRACTION,
-                p_max,
-                dt,
-            ),
-        ]
-        if self.model.params.two_zone_enabled:
-            # The deep low-energy anchor, two-zone only -- see its own
-            # comment for why the reach is deliberately this narrow.
-            starts.append(
-                _price_ranked_start(
-                    prices,
-                    baseline_energy * _DEEP_LOW_ENERGY_START_FRACTION,
-                    p_max,
-                    dt,
-                )
-            )
+        starts = _space_only_starts(
+            self.model, initial_state, self.config.target_temp, initial_power,
+            baseline_power, prices, bounds, p_max, dt,
+        )
         descent, descent_batch = _descent_pair(self, objective, objective_batch)
 
         def move_starts(
@@ -5588,9 +5641,10 @@ class HeatPumpOptimizer:
                 descent, starts, bounds, maxiter=200,
                 batch_objective=descent_batch, move_starts=move_starts,
             )
+            # The start-blind descent can out-rank the off plan (D0-s3-02).
             optimal_power = _commit_runs(
                 self, h, (bounds, objective, objective_batch, None),
-                [np.asarray(result.x, dtype=float)], None, 200,
+                [np.asarray(result.x, dtype=float), _lower_bound_start(bounds)], None, 200,
             )[0]
             status = _solver_status(result, descent, initial_power)
         except Exception as e:
@@ -5620,8 +5674,8 @@ class HeatPumpOptimizer:
         # (#2255): a counterfactual that runs all along must not depend on where
         # the optimiser left the house, so the booked baseline is not the plan's
         # own recovery transient.
-        baseline_cost = float(energy_cost_of(baseline_power))
-        predicted_cost = float(energy_cost_of(optimal_power))
+        baseline_cost = float(paid_cost_of(baseline_power))
+        predicted_cost = float(paid_cost_of(optimal_power))
 
         optimized_end = self._replay_end_state(
             initial_state, optimal_power, outdoor_temps, wind_speeds,
@@ -5795,7 +5849,7 @@ class HeatPumpOptimizer:
         # profile it actually has to share the pump with.
 
         # ``_solve_objectives`` builds the objective both paths share.
-        _, objective, objective_batch, energy_cost_of = (
+        _, objective, objective_batch, paid_cost_of = (
             self._solve_objectives(h)
         )
 
@@ -5895,7 +5949,7 @@ class HeatPumpOptimizer:
         baseline_dhw, baseline_cost, predicted_cost, dhw_cost = (
             planner._baseline_dhw_economics(
                 initial_state, outdoor_temps, n_steps, dhw_setpoint,
-                energy_cost_of, baseline_power, heat_space, optimal_dhw, h.humidity,
+                paid_cost_of, baseline_power, heat_space, optimal_dhw, h.humidity,
             )
         )
 
@@ -5911,7 +5965,7 @@ class HeatPumpOptimizer:
         # cold tank at midnight is not treated as borrowed heat.
         deferred_cost = self._settle_horizon(
             h, weather, comfort_targets, _sharing_wood_side(baseline_end, optimized_end), optimized_end,
-            float(energy_cost_of(baseline_power)),
+            float(paid_cost_of(baseline_power)),
             dhw_caps=self._settlement_caps(
                 outdoor_temps, dhw_cap=float(dhw_floor_temps[-1]), humidity=h.humidity
             ),
@@ -6337,15 +6391,15 @@ class HeatPumpOptimizer:
         """
         caps = self._settlement_caps(h.outdoor_temps, humidity=h.humidity)
         house_end = self._deferred_energy_cost(
-            baseline_end, optimized_end, h.prices, h.outdoor_temps,
+            baseline_end, optimized_end, h.money_prices, h.outdoor_temps,
             caps=caps, humidity=h.humidity,
         )
         end = house_end if dhw_caps is None else self._deferred_energy_cost(
-            baseline_end, optimized_end, h.prices, h.outdoor_temps,
+            baseline_end, optimized_end, h.money_prices, h.outdoor_temps,
             include_dhw=True, caps=dhw_caps, humidity=h.humidity,
         )
         return end - self._start_gap_cost(
-            h.initial_state, weather, reference_targets, h.prices, h.outdoor_temps,
+            h.initial_state, weather, reference_targets, h.money_prices, h.outdoor_temps,
             caps, h.humidity, space_baseline_cost, house_end,
         )
 
diff --git a/custom_components/heatpump_optimizer/plan_slots.py b/custom_components/heatpump_optimizer/plan_slots.py
index deac00c608..6edcdb056a 100644
--- a/custom_components/heatpump_optimizer/plan_slots.py
+++ b/custom_components/heatpump_optimizer/plan_slots.py
@@ -83,8 +83,10 @@ def plan_slots(
             ]
             if codes:
                 # The most frequent code within the slot, which reads
-                # better than a list when a slot spans two motivations.
-                slot["reason"] = max(set(codes), key=codes.count)
+                # better than a list when a slot spans two motivations; a tie
+                # goes to the code the slot reached first, not to a set's
+                # hash-seeded order (D1-s1-51).
+                slot["reason"] = max(dict.fromkeys(codes), key=codes.count)
                 slot["reasons"] = sorted(set(codes))
         slots.append(slot)
 
diff --git a/dev/programme/delivery/3736.md b/dev/programme/delivery/3736.md
new file mode 100644
index 0000000000..c3e46c32ed
--- /dev/null
+++ b/dev/programme/delivery/3736.md
@@ -0,0 +1 @@
+- [#3736](https://github.com/tvofi/heatpump_optimizer/pull/3736) — **open**, R11-SEAM-solver: solver (R11-SEAM-solver)
diff --git a/tests/features.py b/tests/features.py
index 0868f72811..29db859be0 100644
--- a/tests/features.py
+++ b/tests/features.py
@@ -96912,4 +96912,167 @@ R.check(
 )
 
 
+# --- R11-SEAM-solver: the start set brackets the all-off and wood-covered
+# optima, the risk premium stays out of every published money figure, and a
+# slot's reason tie is ordered ------------------------------------------------
+import contextlib as _sv_ctx  # noqa: E402
+from unittest import mock as _sv_mock  # noqa: E402
+
+_sv_optmod = sys.modules[type(_rk["optimizer"]).__module__]
+
+# D1-s1-51: a 2:2 reason tie inside one slot. ``max`` over a ``set`` picks by
+# the set's iteration order, which is PYTHONHASHSEED's, so the two spellings
+# of one tie read the same winner and one of them is not its first code.
+_sv_ts = [_G_START + timedelta(minutes=15 * i) for i in range(4)]
+_sv_ties = [
+    plan_slots(_sv_ts, [1.0] * 4, [1.0] * 4, 0.25, reasons=list(order))
+    for order in (("cheap_price", "cheap_price", "pre_heat", "pre_heat"),
+                  ("pre_heat", "pre_heat", "cheap_price", "cheap_price"))
+]
+R.check(
+    "a plan slot's reason tie reads the slot's first code, whatever the "
+    "hash seed (D1-s1-51)",
+    [s[0].get("reason") for s in _sv_ties] == ["cheap_price", "pre_heat"],
+    str([s[0].get("reason") for s in _sv_ties]),
+)
+
+# D2-s3-01: the premium lambda*sigma prices the objective only. The reference
+# thermostat's cost does not depend on the plan, so lambda moves it only if
+# the premium is booked as money; the published prices are the input's; the
+# plan's own cost is its draw on the input prices; and every settlement price
+# the solve hands the stored-heat booking is the input's.
+_sv_raw = np.asarray(_rk["prices"], dtype=float)
+_sv_settle_prices = []
+_sv_opt = _rk["optimizer"]
+_sv_real_def, _sv_real_gap = _sv_opt._deferred_energy_cost, _sv_opt._start_gap_cost
+
+
+def _sv_spy_def(base, opt_end, prices, *a, **kw):
+    _sv_settle_prices.append(np.array(prices, dtype=float))
+    return _sv_real_def(base, opt_end, prices, *a, **kw)
+
+
+def _sv_spy_gap(state, weather, targets, prices, *a, **kw):
+    _sv_settle_prices.append(np.array(prices, dtype=float))
+    return _sv_real_gap(state, weather, targets, prices, *a, **kw)
+
+
+_sv_opt._deferred_energy_cost, _sv_opt._start_gap_cost = _sv_spy_def, _sv_spy_gap
+try:
+    _sv_on = _rk_solve(1.0, _rk_sigma)
+finally:
+    del _sv_opt._deferred_energy_cost, _sv_opt._start_gap_cost
+_sv_zero = _rk_solve(0.0, _rk_sigma)
+_sv_n = len(_sv_on.power_schedule)
+_sv_draw = np.asarray(_sv_on.power_schedule, dtype=float) + np.asarray(
+    _sv_on.dhw_power_schedule, dtype=float)
+_sv_opt.optimize(inputs=solve_inputs(
+    initial_state=_rk["state"], prices=_rk["prices"], outdoor_temps=_rk["outdoor"],
+    wind_speeds=_rk["wind"], precipitation=_rk["rain"], solar_radiation=_rk["solar"],
+    start_time=_G_START, price_known=_rk_known, price_sigma=_rk_sigma,
+))  # re-stashes this solve's surplus for the pricing closure below
+_sv_paid = float(_sv_opt._energy_cost_fn(_sv_raw[:_sv_n], 24.0 / _sv_n)(_sv_draw))
+R.check(
+    "lambda=1 books no premium as money: the published prices are the input's, "
+    "the reference's cost is lambda=0's, the plan's cost is its draw on the "
+    "input prices, and every settlement price is the input's (D2-s3-01)",
+    np.array_equal(np.asarray(_sv_on.prices, dtype=float), _sv_raw[:_sv_n])
+    and _sv_on.baseline_cost == _sv_zero.baseline_cost
+    and abs(_sv_on.predicted_cost - _sv_paid) <= 1e-9
+    and len(_sv_settle_prices) > 0
+    and all(np.array_equal(p, _sv_raw[: p.size]) for p in _sv_settle_prices),
+    f"prices premium {np.max(np.asarray(_sv_on.prices) - _sv_raw[:_sv_n]):.4f}, "
+    f"baseline {_sv_on.baseline_cost:.4f} vs {_sv_zero.baseline_cost:.4f}, "
+    f"predicted {_sv_on.predicted_cost:.4f} vs paid {_sv_paid:.4f}, "
+    f"{len(_sv_settle_prices)} settlement prices",
+)
+R.check(
+    "the premium still prices the objective: lambda=1 moves the plan "
+    "(the D2-s3-01 fix's null control)",
+    not np.array_equal(_sv_draw, np.asarray(_sv_zero.power_schedule, dtype=float)
+                       + np.asarray(_sv_zero.dhw_power_schedule, dtype=float)),
+)
+_rk["optimizer"].config.price_risk_lambda = 0.0
+
+# D0-s3-02 and D0-s2-01: every first solve's start set holds the lower bound
+# (the all-off plan, a forced-on pin at its floor), on both solve paths; and a
+# reference the wood tank covers whole leaves the set an energy-anchored start,
+# not four copies of zero.
+_sv_calls = []
+_sv_ms_real = _sv_optmod._multi_start_minimize
+
+
+def _sv_ms_spy(objective, starts, bounds, *a, **kw):
+    _sv_calls.append(([np.array(s, dtype=float) for s in starts],
+                      np.array([b[0] for b in bounds], dtype=float)))
+    return _sv_ms_real(objective, starts, bounds, *a, **kw)
+
+
+_sv_commits = []
+_sv_commit_real = _sv_optmod._commit_runs
+
+
+def _sv_commit_spy(opt, h, scope, relaxed, *a, **kw):
+    _sv_commits.append(([np.array(r, dtype=float) for r in relaxed],
+                        np.array([b[0] for b in scope[0]], dtype=float)))
+    return _sv_commit_real(opt, h, scope, relaxed, *a, **kw)
+
+
+def _sv_starts(dhw, share=None):
+    sc = _mk_golden(hours=24, dhw=dhw)
+    _sv_calls.clear()
+    _sv_commits.clear()
+    patches = [_sv_mock.patch.object(_sv_optmod, "_multi_start_minimize", _sv_ms_spy),
+               _sv_mock.patch.object(_sv_optmod, "_commit_runs", _sv_commit_spy)]
+    if share is not None:
+        patches.append(_sv_mock.patch.object(
+            _sv_optmod, "_wood_covered_share", lambda *a, **k: share))
+    with _sv_ctx.ExitStack() as stack:
+        for p in patches:
+            stack.enter_context(p)
+        sc["optimizer"].optimize(inputs=solve_inputs(
+            initial_state=sc["state"], prices=sc["prices"], outdoor_temps=sc["outdoor"],
+            wind_speeds=sc["wind"], precipitation=sc["rain"],
+            solar_radiation=sc["solar"], start_time=_G_START,
+        ))
+    return list(_sv_calls)
+
+
+_sv_space = _sv_starts(False)
+_sv_space_commits = list(_sv_commits)
+_sv_dhw = _sv_starts(True)
+R.check(
+    "the first multi-start of each solve path starts one run at the lower "
+    "bound, the all-off plan (D0-s3-02)",
+    bool(_sv_space) and bool(_sv_dhw)
+    and all(any(np.array_equal(s, lb) for s in starts)
+            for starts, lb in (_sv_space[0], _sv_dhw[0])),
+    f"{len(_sv_space)} space-only and {len(_sv_dhw)} DHW multi-starts",
+)
+R.check(
+    "the space-only solve commits the all-off plan beside the descent's run, "
+    "so the true objective, not the start-blind descent, ranks it (D0-s3-02)",
+    len(_sv_space_commits) == 1
+    and any(np.array_equal(r, _sv_space_commits[0][1]) for r in _sv_space_commits[0][0]),
+    f"{len(_sv_space_commits)} commit stages",
+)
+R.check(
+    "a space-only solve no wood covers hands the multi-start no duplicate "
+    "start, so the reference-energy seeds are drawn only where a share "
+    "scaled the others (D0-s2-01)",
+    bool(_sv_space)
+    and len({s.tobytes() for s in _sv_space[0][0]}) == len(_sv_space[0][0]),
+    f"{len(_sv_space[0][0]) if _sv_space else 0} starts, "
+    f"{len({s.tobytes() for s in _sv_space[0][0]}) if _sv_space else 0} distinct",
+)
+_sv_covered = _sv_starts(False, share=1.0)
+_sv_live = {s.tobytes() for s in (_sv_covered[0][0] if _sv_covered else [])
+            if np.any(s > 0.0)}
+R.check(
+    "a reference the wood tank covers whole still leaves the space-only start "
+    "set a nonzero energy-anchored start beside the initial guess (D0-s2-01)",
+    len(_sv_live) >= 2,
+    f"{len(_sv_live)} distinct nonzero starts",
+)
+
 sys.exit(R.close("FEATURE CHECKS"))
diff --git a/tests/golden/claimed_drift.txt b/tests/golden/claimed_drift.txt
index 99d2e71d7a..d5935902b0 100644
--- a/tests/golden/claimed_drift.txt
+++ b/tests/golden/claimed_drift.txt
@@ -66,6 +66,8 @@
 #
 # v10.1.0: learned pump minimum, clamped start price, self-setting pump test, valve reference, generic heat-curve text. The stamp empties the list; the
 # next branch restates its own footprint, claims included.
+price_risk  # R11-SEAM-solver D2-s3-01: the lambda*sigma premium leaves every money figure and the published prices (CHEAPER baseline_cost, predicted_cost, deferred_energy_cost, dhw_heating_cost, predicted_savings; prices drop the premium on guessed steps); every plan key byte-identical
+start_below_band  # R11-SEAM-solver D0-s3-02: the all-off start reaches a LOWER objective_value on all four OpenBLAS kernel classes (cloud-setup.sh --kernels); one more compressor start, plan keys move with it
 #
 # may-drift: flat_prices -- #1208 polish-every-candidate, owner ruling #1208 comment 208bed25
 # (option (a)): the move's margin is inside the noise band (objective rel
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._optimize_space_only.GUARD_OFF.6a3be0ea.json b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._optimize_space_only.GUARD_OFF.6a3be0ea.json
deleted file mode 100644
index e6d1570aff..0000000000
--- a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._optimize_space_only.GUARD_OFF.6a3be0ea.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/optimizer.py:HeatPumpOptimizer._optimize_space_only GUARD_OFF 6a3be0ea",
-  "killed_by": "tests/optimality.py",
-  "old": "        if self.model.params.two_zone_enabled:",
-  "reason": "arrived with round 7 D0-01 (#1447): the gate that scopes the deep low-energy anchor to the two-zone path, so every single-zone plan stays byte-identical to origin/main and the certificate's three claims keep their calibration. Killed by tests/optimality.py -- `if self.model.params.two_zone_enabled:` -> `if False:` never appends the anchor, which is the same tree as deleting it: FAIL two|winter_typical|winter_cold: no unclaimed gap above the bar [ladder 0.4374%, bar 0.4000%], 1 of 84, measured on this branch."
-}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._solve_objectives.RETURN_DEL.ac696c3f.json b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._solve_objectives.RETURN_DEL.ac696c3f.json
deleted file mode 100644
index ee3dfe4d02..0000000000
--- a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._solve_objectives.RETURN_DEL.ac696c3f.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/optimizer.py:HeatPumpOptimizer._solve_objectives RETURN_DEL ac696c3f",
-  "killed_by": "tests/doc_claims.py",
-  "old": "        return _space_traj, objective, objective_batch, energy_cost_of",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 2b6c5b876ec297bf2b0ef4a127d09cf97fc40b5d: RETURN_DEL (`pass`) took tests/doc_claims.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/structure_budgets.json b/tests/structure_budgets.json
index 8f925f20e3..9e3544da8d 100644
--- a/tests/structure_budgets.json
+++ b/tests/structure_budgets.json
@@ -1,5 +1,5 @@
 {
- "class_excess_loc": 17382,
+ "class_excess_loc": 17360,
  "const_modules_over_50": 3,
  "coordinator_attrs": 136,
  "coordinator_multiassigned_attrs": 104,
@@ -16,6 +16,6 @@
  "methods_over_150": 14,
  "methods_over_200": 7,
  "name_kept_members": 38,
- "recorded_at": "e352724335c136b65562cd3e71f728549ad04a82",
+ "recorded_at": "bc658f9ded3da4ce7daf8bb854b6bc24e67a9d5f",
  "seam_cut_total": 415
 }

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
