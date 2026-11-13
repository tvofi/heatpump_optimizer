CLOUD REVIEWER seat for PR #3574 of tvofi/heatpump_optimizer, at head 22e9330193f147e8b02b0171890b9c338ef6b0e3. Bus nonce: 06b928f51a6c4e4ccb145654e9ded7ee. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. The session-start `toolchain:` line says whether venv-ci's python3 is on PATH: on REFUSE, start each Bash call with `eval "$(bash .claude/hooks/session-start.sh --env-lines)"`. Then run `bash tools/audit/seat/cloud-setup.sh --check`, and on REFUSE stop: report its line as your result and start no work. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead. Read your policy once, verbatim: `python3 -I tools/policy/role_pack.py render fix-review --out $HOME/role-pack.md`, then that file in place of your role contract and INSTRUMENTS.md; on REFUSE read those files as before.
Role: read dev/governance/roles/fix-review.md and its rules from main, and follow them exactly. Fetch the PR head with `git fetch origin 22e9330193f147e8b02b0171890b9c338ef6b0e3`; the PR body is in the PR. Start from the review packet, which you render here rather than read from the dispatcher, whose copy is a path on its own machine: `python3 -I tools/audit/seat/review_packet.py render --pr 3574 --head 22e9330193f147e8b02b0171890b9c338ef6b0e3 --out $HOME/review-packet.md`. A refusal names its signal and the packet is still written unless the signal is `host-path`; re-read the live checks either way. Verify each claim adversarially: mutate the fix and check the tests fail, and check every figure in the body at this head. Check that it merges with origin/main (`git merge-tree --write-tree origin/main <head>`); block on main only when that reports a conflict, never on a head that is behind main but merges cleanly (the train re-proves it on the current main). Wait for CI on this head only by re-running `python3 tools/audit/seat/merge_train.py classify 22e9330193f147e8b02b0171890b9c338ef6b0e3 --pr 3574` in the background, at least 60 s between runs, until it exits 0 (GREEN), 1 (RED), 2 (unreadable: say so in the verdict) or 4 (APPROVAL-OWED: the only red is the budget raise's approval, which follows your verdict; judge the head as GREEN and quote the line); 3 is WAIT, so run it again. Never wait with `pgrep` or `pkill`, whose `-f` pattern matches the waiter's own command line, nor on a context the ruleset does not require, such as `prelude`. A review_packet `required-red` signal does not stop you while classify prints WAIT: classify decides. If your review is otherwise complete and classify still prints WAIT after about 30 minutes of polling, stop waiting: put the line `pending-ci: <the context names it printed>` straight after the `bus-nonce:` line and return the verdict as below; the relay posts it once CI is green at this head, refuses it over a red, and refuses it if the head moves. If the review is not complete then, push `Fix review: blocked 22e9330193f147e8b02b0171890b9c338ef6b0e3 ci-wait: <the last classify line>` as below.
Output: in a fresh directory of your own (`W=$(mktemp -d)`), write verdict.md, whose first line is exactly `Fix review: merge 22e9330193f147e8b02b0171890b9c338ef6b0e3` or `Fix review: blocked 22e9330193f147e8b02b0171890b9c338ef6b0e3 <class>: <reason>` (no brackets; the class is lower-case letters and dashes), in the format the role file gives, then a blank line, then `bus-nonce: 06b928f51a6c4e4ccb145654e9ded7ee`, then the body in sections. A blocked verdict's block goes under `## Block`. Each finding this PR does not settle (a defect, a surviving mutant, a deferral, a follow-up, a task owed after the merge) is its own bullet under `## Findings` ending in its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>` (finding-propagation.md). Everything else (RESULT lines, re-runs, CI state, figures you could not re-derive) goes under `## Evidence`: tools/audit/carry_audit.py reads an item there, and under any heading of a merge verdict but `## Findings`, `## Friction`, a block heading and a note heading (Residuals, Follow-ups, Notes ...), by its shape alone: a finding only when it opens with a lead word (Residual:, Follow-up:, Out of scope: ...) or carries a `Carry:`, so a defect you hand on goes under `## Findings`, and bus.sh refuses a verdict holding a finding with no valid `Carry:`. Put the evidence files in `ev/` beside it, under 25 MB in all (cite a large log by path and keep its tail: a ~30 MB ev/ once failed its push), and make at least one file under `ev/` contain the full 40-hex head `22e9330193f147e8b02b0171890b9c338ef6b0e3` (e.g. `ev/HEAD.txt` holding the head you reviewed, beside your command output): bus.sh refuses a verdict whose `ev/` names no head. Do NOT run bus.sh: its dispatch record lives on the orchestrator's machine, which publishes the verdict there (cloud_relay.sh). Return the verdict on a probe ref, and push nothing else; this builds one parentless commit with a private index and touches no branch of your checkout: `R=$(git rev-parse --show-toplevel); G=$(git rev-parse --absolute-git-dir); mkdir -p $W/pr && cp -r $W/verdict.md $W/ev $W/pr/ && cd $W/pr && T=$(GIT_DIR=$G GIT_INDEX_FILE=$W/idx GIT_WORK_TREE=$W/pr sh -c 'git add -A -f . && git write-tree') && C=$(GIT_DIR=$G git -c user.name=hpo-fixer -c user.email=70032254+tvofi@users.noreply.github.com commit-tree $T -m "verdict 3574 22e9330193f147e8b02b0171890b9c338ef6b0e3") && git -C $R push -q origin $C:refs/heads/probe/rev-3574-06b928f5`. That ref is the return signal. Do not post comments, approve or merge.
Every way your turn ends pushes a verdict to that ref: a setup or hook refusal that stops you pushes `Fix review: blocked 22e9330193f147e8b02b0171890b9c338ef6b0e3 seat-refused: <the refusing line>`; never end your turn while a background poll runs. After the push, read the ref back with `git ls-remote origin refs/heads/probe/rev-3574-06b928f5`, and push again if it does not print your commit.
A red is owed a `## Red checks` answer, and may block, only when its name is in the set `python3 tools/audit/seat/merge_train.py owed-reds` prints (defect-root-cause.md); any other red is neither answered nor a block.
Never write to any branch except your return refs. Never work around a hook or a refusal; report it in your result instead.
Discovery reads (search, list, read across files) go through Agent subagents, as the frugal routing guard requires: when it refuses inline work, dispatch a haiku or sonnet Agent subagent to do it rather than bypassing the guard; never set FRUGAL_ALLOW_INLINE and never edit .claude/settings.json.

Brief (snapshotted when this payload was rendered):
# Review packet #3574
head: 22e9330193f147e8b02b0171890b9c338ef6b0e3
base: 50373173d486faf394b24637c177ab38b691b394

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=132239629672 success
arch-score / arch-score id=132239124850 success
arm id=132238838388 skipped
budget-raise-gate / budget-raise-gate id=132239124829 success
cancel-superseded id=132238840270 success
codeql id=132239120081 skipped
codeql / Analyze (actions) id=132239124844 success
codeql / Analyze (javascript-typescript) id=132239124994 success
codeql / Analyze (python) id=132239124840 success
gate id=132239746278 failure
governance id=132239120215 skipped
governance / delivery-status id=132239124730 success
governance / delivery-status-publish id=132239126606 skipped
governance / env-matrix id=132239124650 success
governance / instrument-self-tests id=132239124835 success
governance / policy-docs id=132239124805 success
governance / record id=132239127207 skipped
governance / wave-script id=132239124662 success
hassfest id=132239121573 skipped
hassfest / hassfest id=132239124887 success
kernel-points id=132239126114 skipped
pr-contract id=132239747092 skipped
prelude id=132238840083 success
refresh id=132238840523 success
sweep-self id=132240318736 skipped
tests id=132239119473 skipped
tests / arch-instrument id=132239468242 success
tests / briefs id=132239124832 success
tests / browser id=132239467780 success
tests / closure-scope id=132239124917 success
tests / closures id=132239467811 in_progress
tests / coverage id=132239467755 in_progress
tests / fast (3.14) id=132239467843 in_progress
tests / mutation id=132239124982 success
tests / mutation-autofix id=132239632393 skipped
tests / mutation-pins id=132239631741 skipped
tests / nightly-ha id=132239469744 skipped
tests / nightly-status id=132239124901 success
tests / replay id=132239467769 success
tests / typing id=132239467790 success
validate id=132239120801 skipped
validate / validate-hacs id=132239124760 success

## Refusals
none

## Advisories
required-wait: required context `gate` reads concluded failure at 22e9330193f147e8b02b0171890b9c338ef6b0e3 in the digest, but merge_train.py classify --pr reads WAIT (pending: gate red: none): classify decides, as bus.sh's dispatch does, and a pending check never refuses

## carry_audit at the head
NOTE body item b7f80482: dismissed:evidence for Carry 14 and Carry 15, not a finding
NOTE body item 24c2f43a: dismissed:already this group's roster Carry 9, still pending; this body re-measures it for the orchestrator's ruling on its owner
NOTE body item b12e9ca3: dismissed:already this group's roster Carry 10, still pending; this body re-measures it for the owner's or orchestrator's display ruling
CARRY-AUDIT: 3 finding item(s): 3 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
unverified MODE: SCOPED -- 27 script(s) run, 6 scoped out.
             no segment of this names a program this check knows
  ok         PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_sav_held_capacity_census.py
             `dev/audit/harnesses/r10_sav_held_capacity_census.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_sav_residual_attribution.py flat
             `dev/audit/harnesses/r10_sav_residual_attribution.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_sav_wood_reference.py valve-flat
             `dev/audit/harnesses/r10_sav_wood_reference.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/r10_combi_tank.py exchange
             `dev/audit/harnesses/r10_combi_tank.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub GOLDEN_MODE=drift python3 tests/golden.py
             `tests/golden.py` is in the tree at this head
  ok         tests/env_drift.py
             `tests/env_drift.py` is in the tree at this head
  ok         tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         python3 tests/structure.py --record
             `tests/structure.py` is in the tree at this head

FIGURES: 8 resolved, 1 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._apportion_by_steady_demand.CMP_BOUND.a0bdc820.json b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._apportion_by_steady_demand.CMP_BOUND.a0bdc820.json
deleted file mode 100644
index fd11aa094b..0000000000
--- a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._apportion_by_steady_demand.CMP_BOUND.a0bdc820.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/optimizer.py:HeatPumpOptimizer._apportion_by_steady_demand CMP_BOUND a0bdc820",
-  "killed_by": "tests/features.py",
-  "old": "            if not (over := ~held & (spread > cap)).any():",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if not (over := ~held & (spread >= cap)).any():`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._apportion_by_steady_demand.CMP_BOUND.bcdccc59.json b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._apportion_by_steady_demand.CMP_BOUND.bcdccc59.json
deleted file mode 100644
index 5b9f7bef6e..0000000000
--- a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._apportion_by_steady_demand.CMP_BOUND.bcdccc59.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/optimizer.py:HeatPumpOptimizer._apportion_by_steady_demand CMP_BOUND bcdccc59",
-  "killed_by": "tests/features.py",
-  "old": "        while (total := float(np.sum(steady[~held]))) > 0.0:",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`while (total := float(np.sum(steady[~held]))) >= 0.0:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._apportion_by_steady_demand.GUARD_OFF.a0bdc820.json b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._apportion_by_steady_demand.GUARD_OFF.a0bdc820.json
deleted file mode 100644
index 33f07b65db..0000000000
--- a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._apportion_by_steady_demand.GUARD_OFF.a0bdc820.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/optimizer.py:HeatPumpOptimizer._apportion_by_steady_demand GUARD_OFF a0bdc820",
-  "killed_by": "tests/typing_ruler.py",
-  "old": "            if not (over := ~held & (spread > cap)).any():",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/typing_ruler.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._apportion_by_steady_demand.RETURN_DEL.cb4dc380.json b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._apportion_by_steady_demand.RETURN_DEL.cb4dc380.json
deleted file mode 100644
index b22474b7e5..0000000000
--- a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._apportion_by_steady_demand.RETURN_DEL.cb4dc380.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/optimizer.py:HeatPumpOptimizer._apportion_by_steady_demand RETURN_DEL cb4dc380",
-  "killed_by": "tests/features.py",
-  "old": "        return simulated",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._compute_baseline_power.GUARD_OFF.efb0739b.json b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._compute_baseline_power.GUARD_OFF.efb0739b.json
deleted file mode 100644
index d3ea61f19f..0000000000
--- a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._compute_baseline_power.GUARD_OFF.efb0739b.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/optimizer.py:HeatPumpOptimizer._compute_baseline_power GUARD_OFF efb0739b",
-  "killed_by": "tests/features.py",
-  "old": "        if mixing_valve.is_throttling(p.mixing_valve_mode):",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=5."
-}
diff --git a/tests/mutation_ledger/survivor_triage/optimizer.py/HeatPumpOptimizer._apportion_by_steady_demand.BOOLOP.c2a57544.json b/tests/mutation_ledger/survivor_triage/optimizer.py/HeatPumpOptimizer._apportion_by_steady_demand.BOOLOP.c2a57544.json
deleted file mode 100644
index 448636a1cc..0000000000
--- a/tests/mutation_ledger/survivor_triage/optimizer.py/HeatPumpOptimizer._apportion_by_steady_demand.BOOLOP.c2a57544.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/optimizer.py:HeatPumpOptimizer._apportion_by_steady_demand BOOLOP c2a57544",
-  "old": "        assert weather.wind_speeds is not None and weather.precipitation is not None",
-  "reason": "Equivalent on every reachable input (BOOLOP, `and` -> `or` in a type-narrowing assert). The mutant differs from the head only when exactly one of `weather.wind_speeds` and `weather.precipitation` is None. `_apportion_by_steady_demand` has one caller, `HeatPumpOptimizer._compute_baseline_power`, which opens with the identical assertion `assert wind_speeds is not None and precipitation is not None` on the same WeatherSeries before it reaches the call (behind `mixing_valve.is_throttling`), so a series with either field None is refused there, under both the head and the mutant, and never reaches this line; with both fields set the two assertions pass alike. The line exists for the type checker's narrowing inside the method. Measured: the site survived every driver whose closure holds optimizer.py in the R10-HOTFIX-SAV-ESTIMATE pin drive (`mutation-autofix`, run 42024722714, which named it a survivor), and no driver can kill it without calling the private method with a series its only caller refuses.",
-  "verdict": "equivalent"
-}


## Review scope: full (first round: no --reviewed-head)

## Three-dot diff
diff --git a/custom_components/heatpump_optimizer/optimizer.py b/custom_components/heatpump_optimizer/optimizer.py
index a7bb65b82e..7122bda293 100644
--- a/custom_components/heatpump_optimizer/optimizer.py
+++ b/custom_components/heatpump_optimizer/optimizer.py
@@ -5977,41 +5977,8 @@ class HeatPumpOptimizer:
                 humidity=hum_i,
             )
 
-        if mixing_valve.is_throttling(p.mixing_valve_mode):
-            baseline_power = self._apportion_by_steady_demand(baseline_power, weather, targets)
         return baseline_power, state
 
-    def _apportion_by_steady_demand(
-        self, simulated: np.ndarray, weather: WeatherSeries, targets: list[float]
-    ) -> np.ndarray:
-        """The simulated horizon's energy, spread by the steady demand per step.
-
-        Behind a valve the first steps are the stores' transient, not the
-        thermostat's power: a tank above the curve zeroes them, one below it
-        overshoots. The settlement books step 0 of a plan re-made every
-        interval, so it would book only the transient. The simulation decides
-        how much the horizon draws; the demand decides when, never past the
-        pump: a step held at it gives its excess to the rest by the same demand.
-        """
-        assert weather.wind_speeds is not None and weather.precipitation is not None
-        assert weather.solar_radiation is not None
-        steady = np.array([
-            max(0.0, _floor_demand_at_target(
-                self.model, targets[i], float(weather.outdoor_temps[i]),
-                float(weather.wind_speeds[i]), float(weather.precipitation[i]),
-                float(weather.solar_radiation[i]),
-            ))
-            for i in range(len(simulated))
-        ])
-        energy, cap = float(np.sum(simulated)), float(self.model.params.max_electrical_power)
-        held = np.zeros(len(steady), dtype=bool)
-        while (total := float(np.sum(steady[~held]))) > 0.0:
-            spread = np.where(held, cap, steady * ((energy - cap * int(np.sum(held))) / total))
-            if not (over := ~held & (spread > cap)).any():
-                return spread
-            held |= over
-        return simulated
-
     def _settle_horizon(
         self,
         h: _Horizon,
diff --git a/dev/programme/delivery/3574.md b/dev/programme/delivery/3574.md
new file mode 100644
index 0000000000..20df7ea448
--- /dev/null
+++ b/dev/programme/delivery/3574.md
@@ -0,0 +1 @@
+- [#3574](https://github.com/tvofi/heatpump_optimizer/pull/3574) — **open**, R10-SAV-VALUATION-RESIDUE: r10 sav valuation residue (R10-SAV-VALUATION-RESIDUE)
diff --git a/tests/features.py b/tests/features.py
index a663d02b74..b089b3e594 100644
--- a/tests/features.py
+++ b/tests/features.py
@@ -46438,8 +46438,12 @@ R.check(
 )
 # R10-HOTFIX-SAV-ESTIMATE: the settlement books step 0 of a plan re-made every
 # interval, so behind a valve the first step must not be the stores' transient.
-# At one outdoor the steady demand is flat, so a sound step 0 IS the horizon mean;
+# At one outdoor the steady demand is flat, so a sound step 0 is the horizon mean;
 # spread across starts is no acceptance (all-zero first steps have spread 0).
+# The reference is booked as simulated from its held state (R10-SAV-VALUATION-
+# RESIDUE carry 15), so the bound is 1e-3, not exact: two zones held at one
+# temperature drift apart over the day by 1.6e-4 of the mean here (carry 9's
+# open seam), where a transient reads 0 or an overshoot of whole units.
 def _sb_first_steps(two_zone, wood_probe, valve="manual"):
     import numpy as _np
     from profiles import house as _h
@@ -46475,7 +46479,7 @@ for _sb_name, _sb_args in (
     _sb_ratios = {k: float(v[0] / v.mean()) if v.mean() > 0 else 0.0 for k, v in _sb_arms.items()}
     R.check(
         f"behind a valve with {_sb_name}, the thermostat's first step is its horizon mean, not 0 or an overshoot",
-        all(abs(r - 1.0) < 1e-9 for r in _sb_ratios.values()),
+        all(abs(r - 1.0) < 1e-3 for r in _sb_ratios.values()),
         repr(_sb_ratios),
     )
     R.check(
@@ -47258,9 +47262,7 @@ for _hb_two, _hb_dhw in ((False, False), (True, True)):
 
 # Behind a valve, at zero demand (a warm, sunny step: the steady demand at
 # target is negative, clamped to 0). The held tank keeps its measured
-# temperature, since no temperature delivers a need of nothing; and a horizon
-# with no steady demand anywhere has no shape to spread its energy by, so the
-# simulated schedule stands as simulated.
+# temperature, since no temperature delivers a need of nothing.
 _hz_ws = _HbWSeries(
     outdoor_temps=np.full(4, 30.0), wind_speeds=np.zeros(4),
     precipitation=np.zeros(4), solar_radiation=np.full(4, 800.0),
@@ -47274,25 +47276,17 @@ _hz_held = _hb_held_state(_hz_opt.model, _HbState(
     room_temperature=21.0, slab_temperature=22.0, outdoor_temperature=30.0,
     upper_floor_temperature=21.0, lower_floor_temperature=21.0, buffer_tank_temperature=37.5,
 ), _hz_ws, 21.0)
-_hz_sim = np.array([1.0, 2.0, 0.5, 0.0])
-try:
-    _hz_spread = _hz_opt._apportion_by_steady_demand(_hz_sim, _hz_ws, [21.0] * 4)
-except ZeroDivisionError as _hz_exc:
-    _hz_spread = _hz_exc
-R.check(
-    "behind a valve at zero demand the held tank keeps its measured temperature, "
-    "and a horizon with no steady demand keeps its simulated schedule",
-    _hz_held.buffer_tank_temperature == 37.5
-    and isinstance(_hz_spread, np.ndarray) and np.array_equal(_hz_spread, _hz_sim),
-    repr((_hz_held.buffer_tank_temperature, _hz_spread)),
-)
-
-# Behind a valve the reference spreads its energy by steady demand, and on a
-# small pump in a cold night with a sunny day the plain spread asked more than
-# the pump has (measured 1.23x on this house; R10-SAV-COMFORT carry fc24128d).
-# The spread holds such a step at the pump and gives its excess to the others
-# by the same demand, keeping the horizon's energy; the solve is seeded from
-# that reference unclamped, so every start lies inside its bounds.
+R.check(
+    "behind a valve at zero demand the held tank keeps its measured temperature",
+    _hz_held.buffer_tank_temperature == 37.5,
+    repr(_hz_held.buffer_tank_temperature),
+)
+
+# Behind a valve, on a small pump in a cold night with a sunny day, a reference
+# spread by steady demand once asked more than the pump has (measured 1.23x on
+# this house; R10-SAV-COMFORT carry fc24128d). The thermostat's own steps are
+# capped at the pump, and the solve is seeded from that reference unclamped, so
+# every start lies inside its bounds.
 from heatpump_optimizer import optimizer as _hz_omod
 
 _hz_n = 96
@@ -47319,16 +47313,6 @@ def _hz_spy_ms(objective, starts, bounds, **kw):
 
 _hz_baselines = []
 _hz_orig_bp = _HbOpt._compute_baseline_power
-_hz_spreads = []
-_hz_orig_ap = _HbOpt._apportion_by_steady_demand
-
-
-def _hz_spy_ap(self, simulated, *a, **kw):
-    out = _hz_orig_ap(self, simulated, *a, **kw)
-    _hz_spreads.append((np.array(simulated, float), np.array(out, float)))
-    return out
-
-
 def _hz_spy_bp(self, *a, **kw):
     out = _hz_orig_bp(self, *a, **kw)
     _hz_baselines.append(float(np.max(out[0])))
@@ -47337,7 +47321,6 @@ def _hz_spy_bp(self, *a, **kw):
 
 _hz_omod._multi_start_minimize = _hz_spy_ms
 _HbOpt._compute_baseline_power = _hz_spy_bp
-_HbOpt._apportion_by_steady_demand = _hz_spy_ap
 try:
     _hz_copt.optimize(inputs=solve_inputs(
         initial_state=_HbState(
@@ -47353,7 +47336,6 @@ try:
 finally:
     _hz_omod._multi_start_minimize = _hz_orig_ms
     _HbOpt._compute_baseline_power = _hz_orig_bp
-    _HbOpt._apportion_by_steady_demand = _hz_orig_ap
 _hz_pmax = float(_hz_cpar.max_electrical_power)
 R.check(
     "behind a valve, the reference seeds the space solve only inside its bounds",
@@ -47361,74 +47343,42 @@ R.check(
     f"worst excess over a bound {max(_hz_seen, default=None)!r}",
 )
 R.check(
-    "behind a valve, the spread reference holds a step at the pump, never past it, "
-    "and keeps the simulated horizon's energy",
-    bool(_hz_spreads)
-    and all(float(np.max(o)) <= _hz_pmax + 1e-12 for _, o in _hz_spreads)
-    and all(abs(float(np.sum(o)) - float(np.sum(s))) < 1e-9 for s, o in _hz_spreads)
-    and any(int(np.sum(o >= _hz_pmax - 1e-12)) >= 2 for _, o in _hz_spreads)
-    and max(_hz_baselines, default=0.0) <= _hz_pmax + 1e-12,
-    f"reference peak {max(_hz_baselines, default=None)!r} kW against {_hz_pmax!r}; "
-    f"steps at the pump {[int(np.sum(o >= _hz_pmax - 1e-12)) for _, o in _hz_spreads]}",
-)
-# Under the pump the spread keeps the demand's shape. Four steps, the last one
-# a -30 C step whose plain share of 0.8 pump-steps each would pass the pump:
-# it is held at the pump, and the other three share the rest as the same
-# multiple of their steady demand at target (read from the production helper).
-_hz_mws = _HbWSeries(
-    outdoor_temps=np.array([5.0, 0.0, -5.0, -30.0]), wind_speeds=np.zeros(4),
-    precipitation=np.zeros(4), solar_radiation=np.zeros(4),
-)
-_hz_mcap = float(_hz_par.max_electrical_power)
-_hz_msim = np.full(4, 0.8 * _hz_mcap)
-_hz_mout = _hz_opt._apportion_by_steady_demand(_hz_msim, _hz_mws, [21.0] * 4)
-_hz_mdem = np.array([_hb_floor_demand(_hz_opt.model, 21.0, t, 0.0, 0.0, 0.0)
-                     for t in _hz_mws.outdoor_temps])
-_hz_mr = _hz_mout[:3] / _hz_mdem[:3]
-# A horizon demanding little (under 1 kW summed) still has a shape: three
-# zero-demand steps and one mild one put all the energy on the mild one.
-_hz_lo = 21.0 - (_hz_par.internal_gains + 0.2) / _hz_par.heat_loss_coefficient
-_hz_lws = _HbWSeries(
-    outdoor_temps=np.array([30.0, 30.0, 30.0, _hz_lo]), wind_speeds=np.zeros(4),
-    precipitation=np.zeros(4), solar_radiation=np.zeros(4),
-)
-_hz_ldem = [max(0.0, _hb_floor_demand(_hz_opt.model, 21.0, t, 0.0, 0.0, 0.0))
-            for t in _hz_lws.outdoor_temps]
-_hz_lout = _hz_opt._apportion_by_steady_demand(np.array([0.1, 0.2, 0.05, 0.0]), _hz_lws, [21.0] * 4)
-R.check(
-    "behind a valve, a horizon with a small steady demand spreads by it, not by the simulation",
-    0.0 < sum(_hz_ldem) < 1.0 and _hz_ldem[:3] == [0.0, 0.0, 0.0]
-    and np.allclose(_hz_lout, [0.0, 0.0, 0.0, 0.35], atol=1e-12),
-    f"demand {_hz_ldem!r} spread {_hz_lout!r}",
-)
-# A step whose share lands exactly at the pump is at it, not past it: three
-# zero-demand steps and one cold one, the horizon's energy one pump-step, keep
-# the spread (all of it on the cold step) rather than handing the horizon back
-# to the simulation, as a step held with no demand left to share would.
-_hz_eout = _hz_opt._apportion_by_steady_demand(
-    np.full(4, 0.25 * _hz_mcap), _HbWSeries(
-        outdoor_temps=np.array([30.0, 30.0, 30.0, -5.0]), wind_speeds=np.zeros(4),
-        precipitation=np.zeros(4), solar_radiation=np.zeros(4),
-    ), [21.0] * 4,
-)
-R.check(
-    "behind a valve, a step spread exactly to the pump keeps the spread",
-    _hz_eout.tolist() == [0.0, 0.0, 0.0, _hz_mcap],
-    repr(_hz_eout),
-)
-R.check(
-    "precondition: the cold step's plain share of the horizon passes the pump",
-    bool(np.all(_hz_mdem > 0.0))
-    and float(np.sum(_hz_msim)) * _hz_mdem[3] / float(np.sum(_hz_mdem)) > _hz_mcap,
-    repr(_hz_mdem),
-)
-R.check(
-    "behind a valve, a step spread past the pump is held there and the uncapped steps "
-    "share the rest by their steady demand",
-    _hz_mout[3] == _hz_mcap and float(np.max(_hz_mout[:3])) < _hz_mcap
-    and abs(float(np.sum(_hz_mout)) - float(np.sum(_hz_msim))) < 1e-9
-    and float(np.ptp(_hz_mr)) <= 1e-12 * float(np.max(_hz_mr)),
-    repr(_hz_mout),
+    "behind a valve, the reference reaches the pump and never passes it",
+    bool(_hz_baselines)
+    and abs(max(_hz_baselines) - _hz_pmax) <= 1e-12,
+    f"reference peak {max(_hz_baselines, default=None)!r} kW against {_hz_pmax!r}",
+)
+
+# Behind a valve the booked reference holds the state it starts from: the held
+# state's census (dev/audit/harnesses/r10_sav_held_capacity_census.py) reads a
+# first-step store change of 0, so step 0 is the thermostat's holding power,
+# not a store transient to re-spread. The day's weather varies, so a reference
+# re-spread by steady demand books step 0 off the holding power (R10-SAV-
+# VALUATION-RESIDUE carry 15: +11.11 kWh_th stored over the valve arm).
+_hv_ws = _HbWSeries(
+    outdoor_temps=np.full(_hz_n, -5.0) + np.where(_hz_day, 8.0, 0.0),
+    wind_speeds=np.zeros(_hz_n), precipitation=np.zeros(_hz_n),
+    solar_radiation=np.where(_hz_day, 400.0, 0.0),
+)
+_hv_start = _HbState(
+    room_temperature=19.5, slab_temperature=21.0, outdoor_temperature=-5.0,
+    upper_floor_temperature=19.5, lower_floor_temperature=19.5, buffer_tank_temperature=45.0,
+)
+_hv_power, _ = _hz_opt._compute_baseline_power(_hv_ws, _hv_start, 0.25, np.full(_hz_n, 21.0))
+_hv_held = _hb_held_state(_hz_opt.model, _hv_start, _hv_ws, 21.0)
+_hv_next = _hz_opt.model.simulate_step(
+    _hv_held, float(_hv_power[0]), -5.0, 0.0, 0.0, 0.0, dt_hours=0.25,
+)
+R.check(
+    "behind a valve, the booked reference's first step holds its held state",
+    0.0 < float(_hv_power[0]) < float(_hz_par.max_electrical_power)
+    and abs(_hv_next.room_temperature - _hv_held.room_temperature) < 1e-6
+    and abs(_hv_next.slab_temperature - _hv_held.slab_temperature) < 1e-6
+    and abs(_hv_next.buffer_tank_temperature - _hv_held.buffer_tank_temperature) < 1e-6,
+    f"power {float(_hv_power[0])!r}; room {_hv_held.room_temperature!r} -> "
+    f"{_hv_next.room_temperature!r}, slab {_hv_held.slab_temperature!r} -> "
+    f"{_hv_next.slab_temperature!r}, tank {_hv_held.buffer_tank_temperature!r} -> "
+    f"{_hv_next.buffer_tank_temperature!r}",
 )
 
 # The start's settlement, at its limits (#2255, #2492). A pre-heated start
diff --git a/tests/golden/claimed_drift.txt b/tests/golden/claimed_drift.txt
index a107b76be2..62e9839bd4 100644
--- a/tests/golden/claimed_drift.txt
+++ b/tests/golden/claimed_drift.txt
@@ -68,6 +68,14 @@
 # next branch restates its own footprint, claims included.
 #
 config_flow # R10-OUTSIDE-DHW-START-HYSTERESIS: the entities_pump page gains the two start-hysteresis pickers (space_hysteresis_entity, dhw_hysteresis_entity), so the plain render, the seeded render and the seed each gain those two keys; every leaf that moves is "present on one side only" and ADDED at this head. Float-free and compared exactly, so re-recorded in the committed file (golden.py --record --only config_flow). No plan reads the options unset: the other 55 fixtures are byte-identical to the merge base (env_drift.py --all, one environment), which is the null.
+valve_storage  # baseline_cost LOWER (129.949 -> 129.189)
+valve_storage_low_target  # baseline_cost HIGHER (113.037 -> 115.889)
+valve_storage_small_tank  # baseline_cost LOWER (128.370 -> 126.962)
+valve_storage_smart_write  # baseline_cost LOWER (129.949 -> 129.189)
+valve_upper_direct_slab  # baseline_cost HIGHER (126.301 -> 129.925)
+wood_coil  # baseline_cost LOWER (144.781 -> 144.020)
+wood_two_tank  # baseline_cost LOWER (129.949 -> 129.189)
+wood_two_tank_smart_write  # baseline_cost LOWER (129.949 -> 129.189)
 # may-drift: flat_prices -- #1208 polish-every-candidate, owner ruling #1208 comment 208bed25
 # (option (a)): the move's margin is inside the noise band (objective rel
 # -1.2171e-03, deterministic on one box), so which runner sees it move is the
@@ -93,11 +101,16 @@ config_flow # R10-OUTSIDE-DHW-START-HYSTERESIS: the entities_pump page gains the
 # one was restored.
 #
 #
-# may-drift: valve_storage_smart_write -- machine-sensitive; the DHW plan can reach it, per local optimum
-# may-drift: wood_two_tank -- machine-sensitive; the DHW plan can reach it, per local optimum
-# may-drift: wood_two_tank_smart_write -- machine-sensitive; the DHW plan can reach it, per local optimum
-# may-drift: wood_coil -- machine-sensitive; the DHW plan can reach it, per local optimum
-# may-drift: valve_upper_direct_slab -- machine-sensitive; the DHW plan can reach it, per local optimum
+# (R10-SAV-VALUATION-RESIDUE suspends valve_storage_smart_write's may-drift entry for its claim below; restore it,
+#  verbatim, when the stamp empties the list) valve_storage_smart_write -- machine-sensitive; the DHW plan can reach it, per local optimum
+# (R10-SAV-VALUATION-RESIDUE suspends wood_two_tank's may-drift entry for its claim below; restore it,
+#  verbatim, when the stamp empties the list) wood_two_tank -- machine-sensitive; the DHW plan can reach it, per local optimum
+# (R10-SAV-VALUATION-RESIDUE suspends wood_two_tank_smart_write's may-drift entry for its claim below; restore it,
+#  verbatim, when the stamp empties the list) wood_two_tank_smart_write -- machine-sensitive; the DHW plan can reach it, per local optimum
+# (R10-SAV-VALUATION-RESIDUE suspends wood_coil's may-drift entry for its claim below; restore it,
+#  verbatim, when the stamp empties the list) wood_coil -- machine-sensitive; the DHW plan can reach it, per local optimum
+# (R10-SAV-VALUATION-RESIDUE suspends valve_upper_direct_slab's may-drift entry for its claim below; restore it,
+#  verbatim, when the stamp empties the list) valve_upper_direct_slab -- machine-sensitive; the DHW plan can reach it, per local optimum
 # may-drift: winter_two_zone_no_dhw -- #1208 polish-every-candidate, owner
 # ruling #1208 comment 208bed25 (option (a)): the move's margin is inside the
 # noise band (objective rel -1.3365e-03, predicted_cost rel +8.39e-03),
@@ -182,7 +195,8 @@ config_flow # R10-OUTSIDE-DHW-START-HYSTERESIS: the entities_pump page gains the
 # byte-identical on the dev box), runner-conditional for the same reason;
 # judged keys still fail. Remove when drift lanes are pinned or the polish
 # improvement scale leaves 5e-5-2e-2.
-# may-drift: valve_storage -- #1207 keep-gate (2e-2 -> 2e-5), widened to
+# (R10-SAV-VALUATION-RESIDUE suspends valve_storage's may-drift entry for its claim below; restore it,
+#  verbatim, when the stamp empties the list) valve_storage -- #1207 keep-gate (2e-2 -> 2e-5), widened to
 # the runner's union by the owner's ruling (i) on the options recorded in
 # #1207 comment 1ec15c8 (2026-09-20): 625 leaves moved on the CI
 # x86_64/py3.14 runner only (as recorded on that comment; byte-identical
@@ -764,3 +778,12 @@ config_flow # R10-OUTSIDE-DHW-START-HYSTERESIS: the entities_pump page gains the
 # changes exactly two leaves (the plain and the seeded render of
 # dhw_setpoint_entity.config.filter gain the water_heater domain); no plan reads
 # it, so every other fixture is byte-identical. Re-recorded in the committed file.
+# R10-SAV-VALUATION-RESIDUE part 2: behind a valve the reference is booked as
+# simulated from its held state, no longer re-spread by steady demand
+# (_apportion_by_steady_demand removed). Measured with golden.py and
+# env_drift.py against the merge base in one environment: exactly these eight
+# valved fixtures move, in baseline_cost and the savings derived from it (plan
+# leaves exempt); every unvalved fixture is unmoved, which is the null.
+# baseline_cost is a judged key a may-drift entry cannot excuse, so the six
+# with one are suspended above for this release (the wood_coil precedent).
+# Direction per fixture, branch vs base:
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._apportion_by_steady_demand.CMP_BOUND.a0bdc820.json b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._apportion_by_steady_demand.CMP_BOUND.a0bdc820.json
deleted file mode 100644
index fd11aa094b..0000000000
--- a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._apportion_by_steady_demand.CMP_BOUND.a0bdc820.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/optimizer.py:HeatPumpOptimizer._apportion_by_steady_demand CMP_BOUND a0bdc820",
-  "killed_by": "tests/features.py",
-  "old": "            if not (over := ~held & (spread > cap)).any():",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if not (over := ~held & (spread >= cap)).any():`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._apportion_by_steady_demand.CMP_BOUND.bcdccc59.json b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._apportion_by_steady_demand.CMP_BOUND.bcdccc59.json
deleted file mode 100644
index 5b9f7bef6e..0000000000
--- a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._apportion_by_steady_demand.CMP_BOUND.bcdccc59.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/optimizer.py:HeatPumpOptimizer._apportion_by_steady_demand CMP_BOUND bcdccc59",
-  "killed_by": "tests/features.py",
-  "old": "        while (total := float(np.sum(steady[~held]))) > 0.0:",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`while (total := float(np.sum(steady[~held]))) >= 0.0:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._apportion_by_steady_demand.GUARD_OFF.a0bdc820.json b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._apportion_by_steady_demand.GUARD_OFF.a0bdc820.json
deleted file mode 100644
index 33f07b65db..0000000000
--- a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._apportion_by_steady_demand.GUARD_OFF.a0bdc820.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/optimizer.py:HeatPumpOptimizer._apportion_by_steady_demand GUARD_OFF a0bdc820",
-  "killed_by": "tests/typing_ruler.py",
-  "old": "            if not (over := ~held & (spread > cap)).any():",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/typing_ruler.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._apportion_by_steady_demand.RETURN_DEL.cb4dc380.json b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._apportion_by_steady_demand.RETURN_DEL.cb4dc380.json
deleted file mode 100644
index b22474b7e5..0000000000
--- a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._apportion_by_steady_demand.RETURN_DEL.cb4dc380.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/optimizer.py:HeatPumpOptimizer._apportion_by_steady_demand RETURN_DEL cb4dc380",
-  "killed_by": "tests/features.py",
-  "old": "        return simulated",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._compute_baseline_power.GUARD_OFF.efb0739b.json b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._compute_baseline_power.GUARD_OFF.efb0739b.json
deleted file mode 100644
index d3ea61f19f..0000000000
--- a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._compute_baseline_power.GUARD_OFF.efb0739b.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/optimizer.py:HeatPumpOptimizer._compute_baseline_power GUARD_OFF efb0739b",
-  "killed_by": "tests/features.py",
-  "old": "        if mixing_valve.is_throttling(p.mixing_valve_mode):",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=5."
-}
diff --git a/tests/mutation_ledger/survivor_triage/optimizer.py/HeatPumpOptimizer._apportion_by_steady_demand.BOOLOP.c2a57544.json b/tests/mutation_ledger/survivor_triage/optimizer.py/HeatPumpOptimizer._apportion_by_steady_demand.BOOLOP.c2a57544.json
deleted file mode 100644
index 448636a1cc..0000000000
--- a/tests/mutation_ledger/survivor_triage/optimizer.py/HeatPumpOptimizer._apportion_by_steady_demand.BOOLOP.c2a57544.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/optimizer.py:HeatPumpOptimizer._apportion_by_steady_demand BOOLOP c2a57544",
-  "old": "        assert weather.wind_speeds is not None and weather.precipitation is not None",
-  "reason": "Equivalent on every reachable input (BOOLOP, `and` -> `or` in a type-narrowing assert). The mutant differs from the head only when exactly one of `weather.wind_speeds` and `weather.precipitation` is None. `_apportion_by_steady_demand` has one caller, `HeatPumpOptimizer._compute_baseline_power`, which opens with the identical assertion `assert wind_speeds is not None and precipitation is not None` on the same WeatherSeries before it reaches the call (behind `mixing_valve.is_throttling`), so a series with either field None is refused there, under both the head and the mutant, and never reaches this line; with both fields set the two assertions pass alike. The line exists for the type checker's narrowing inside the method. Measured: the site survived every driver whose closure holds optimizer.py in the R10-HOTFIX-SAV-ESTIMATE pin drive (`mutation-autofix`, run 42024722714, which named it a survivor), and no driver can kill it without calling the private method with a series its only caller refuses.",
-  "verdict": "equivalent"
-}
diff --git a/tests/structure_budgets.json b/tests/structure_budgets.json
index f0b2e8461e..826262debe 100644
--- a/tests/structure_budgets.json
+++ b/tests/structure_budgets.json
@@ -1,5 +1,5 @@
 {
- "class_excess_loc": 17503,
+ "class_excess_loc": 17470,
  "const_modules_over_50": 3,
  "coordinator_attrs": 139,
  "coordinator_multiassigned_attrs": 108,
@@ -16,6 +16,6 @@
  "methods_over_150": 15,
  "methods_over_200": 8,
  "name_kept_members": 38,
- "recorded_at": "f44e761c19dc07fff222bbd6a323bdc847ea9f04",
+ "recorded_at": "e23124ff6e45bac1d48b4a775dad555a37965355",
  "seam_cut_total": 421
 }

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
