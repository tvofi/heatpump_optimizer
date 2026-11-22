#!/usr/bin/env python3
"""Box D3-g20: the per-key step-4 classification table (keymeta.json) mkresult.py reads. Values from the probes'
runs on this box (load1 ~1, thread_factor 1.000); re-running the probe re-derives each."""
import json
from pathlib import Path

W = Path(__file__).resolve().parent.parent
EXEC = {  # state/reach.tsv: closure scripts whose traced baseline executes the line
    3402: "block_duty, boost_drift_replay, config_flow_steps, doc_claims, entities, env_drift, features, manual_plan, optimality, plan_view, validate",
    3969: "block_duty, doc_claims, entities, env_drift, features, manual_plan, optimality, plan_view, validate",
    4766: "entities, env_drift, features", 4802: "block_duty, boost_drift_replay, config_flow_steps, doc_claims, entities, env_drift, features, manual_plan, optimality, plan_view, validate",
    4828: "env_drift, features", 6069: "env_drift, features, validate", 6091: "env_drift, features, validate", 6093: "features", 6097: "features",
}
EXEC[3405] = EXEC[3408] = EXEC[3402]
EXEC[6070] = EXEC[6069]
SYM = "custom_components.heatpump_optimizer.optimizer:HeatPumpOptimizer."


def cand(title, claim, sev, metric, direction, null, symbol, fix):
    return {"title": title, "claim": claim, "class_guess": "I1", "severity_claimed": sev, "metric_definition": metric,
            "instrumented_symbol": SYM + symbol, "perturbation": {"change": "the key's one-line mutant, applied in memory by the probe",
                                                                  "expected_direction": direction},
            "null_control": null, "stop_rule_class": "bug", "proposed_fix_scope": fix}


M = {}
M["a0722b8c635d2d93"] = dict(cls="equivalent-candidate", baseline="weights all 1.0 at dt>8 h", mutant="weights all 1.0 (np.mean([])=nan, nan>0.5/1.1 False)",
    inputs="450: dt {0.25,0.5,1,8,9,24} h x n {1,4,96} x solar {0,0.5,next(0.5),2,nan} x loss {1,1.1,next(1.1),2,nan}; moved 0",
    why="end == i only when int(8/dt) == 0 (dt > 8 h); the empty window's mean is nan and both comparisons are False, so the weight is unchanged",
    should_fail=f"none: no input separates the arms at the returned weights (executed by tests/{{{EXEC[3402]}}}.py)")
M["d800d2857a698d22"] = dict(cls="candidate", baseline="weight[0]=1.0 at mean solar exactly 0.5 kW", mutant="weight[0]=0.85",
    inputs="450-input grid (as a0722b8c); moved 60, every one at solar == 0.5",
    should_fail=f"tests/features.py (or any of tests/{{{EXEC[3405]}}}.py that executes line 3405) lacks an _anticipatory_weights check at solar gain exactly 0.5 kW asserting the weight is unchanged (1.0)",
    finding=cand("Anticipatory warm-start weight at exactly 0.5 kW solar is unpinned (> vs >=)",
        "HeatPumpOptimizer._anticipatory_weights returns weight 1.0 for a constant 0.5 kW solar window, and the full gate stays green when the comparison is made >=, which returns 0.85.",
        "low", "weight[0] of _anticipatory_weights(n=4, dt=0.25, solar=0.5 const, loss=1.0 const)", "1.0 -> 0.85 (down) under the mutant",
        "solar = loss = 2.0 constant: null_delta 0", "_anticipatory_weights", "tests: one boundary assertion at solar == 0.5 kW"))
M["176e4dd6d5aec097"] = dict(cls="candidate", baseline="weight[0]=1.0 at mean loss factor exactly 1.1", mutant="weight[0]=1.1",
    inputs="450-input grid (as a0722b8c); moved 70, every one at loss == 1.1",
    should_fail=f"tests/features.py (or any of tests/{{{EXEC[3408]}}}.py) lacks an _anticipatory_weights check at heat-loss factor exactly 1.1 asserting weight 1.0",
    finding=cand("Anticipatory warm-start weight at a heat-loss factor of exactly 1.1 is unpinned (> vs >=)",
        "HeatPumpOptimizer._anticipatory_weights returns weight 1.0 for a constant 1.1 heat-loss factor window, and the full gate stays green when the comparison is made >=, which returns 1.1.",
        "low", "weight[0] of _anticipatory_weights(n=4, dt=0.25, solar=0 const, loss=1.1 const)", "1.0 -> 1.1 (up) under the mutant",
        "solar = loss = 2.0 constant: null_delta 0", "_anticipatory_weights", "tests: one boundary assertion at loss == 1.1"))
M["c40e66fc9831672f"] = dict(cls="candidate", baseline="ceiling 35.0 C (buffer_max 70, out_mean -20 C, defaults)", mutant="ceiling 20.0 C",
    inputs="117: buffer_max {30,35,40,55,70,90} x out_mean {15,0,-10,-15,-20,-30} x buffer_cooling_rate {default,0,2.0} + 9 constructed exact ties net(hi|lo|mid)==0; moved 45 (every cold case where net(35 C) <= 0); max |delta| 15 C",
    should_fail="tests/features.py (its traced baseline reaches line 6093's `return lo`, the only script that does) lacks an assertion that a cold-weather _buffer_charge_ceiling never falls below the 35 C flow reference (cop_flow_reference_temp): heat below the reference is always chargeable",
    finding=cand("Buffer charge ceiling's floor at the COP flow reference is unpinned: dropping it lowers the cold-weather ceiling 35 -> 20 C",
        "With max(20, cop_flow_reference_temp) replaced by 20, HeatPumpOptimizer._buffer_charge_ceiling at out_mean -20 C returns 20.0 C instead of 35.0 C (45 of 117 probe inputs move), and the GATE_SCOPE=full GOLDEN_MODE=drift gate stays green.",
        "medium", "the value _buffer_charge_ceiling(out_mean) returns, C, default parameters, buffer_max_temp 70 C, out_mean -20 C",
        "35.0 -> 20.0 C (down) under the mutant", "out_mean 15 C (net(hi) > 0, returns buffer_max_temp on both arms): null_delta 0 C",
        "_buffer_charge_ceiling", "tests: a cold-weather ceiling assertion (>= cop_flow_reference_temp) in tests/features.py"))
M["7452dcf280ce931f"] = dict(cls="equivalent-candidate", baseline="ceiling == buffer_max_temp when hi == lo (35 C)", mutant="same value via net(hi)>0 -> hi, else net(lo)<=0 -> lo == hi",
    inputs="117 (grid incl. buffer_max 35 C at every out_mean, + 9 exact ties); moved 0",
    why="at hi == lo every remaining return path yields hi (== lo)", should_fail=f"none (executed by tests/{{{EXEC[6070]}}}.py)")
M["aa338654e7801916"] = dict(cls="candidate", baseline="ceiling 30.0 C (buffer_max 30 C, out_mean -20/-30 C)", mutant="ceiling 35.0 C, above the tank's own rating",
    inputs="117 (as c40e66fc); moved 6, all buffer_max 30 C (< the 35 C flow reference) in cold weather; ThermalParameters.from_config keeps buffer_max_temperature 30 unclamped (the flow's selector minimum is 40)",
    should_fail=f"tests/validate.py or tests/features.py (both execute line 6070) lack a _buffer_charge_ceiling(…) <= buffer_max_temp assertion for a rating below the flow reference",
    finding=cand("Buffer charge ceiling can exceed the tank rating when the rating is below the flow reference; the hi <= lo guard is unpinned",
        "With `if hi <= lo:` disabled, HeatPumpOptimizer._buffer_charge_ceiling returns 35.0 C for a 30 C-rated tank at out_mean -20 C (baseline 30.0 C), and the full gate stays green.",
        "low", "the value _buffer_charge_ceiling(out_mean) returns, C, buffer_max_temp 30 C, out_mean -20 C",
        "30.0 -> 35.0 C (up, past buffer_max_temp) under the mutant", "out_mean 15 C at default rating: null_delta 0 C",
        "_buffer_charge_ceiling", "tests: one assertion; reachable only through a config entry below the flow selector's 40 C minimum"))
M["7add4cd79387ec24"] = dict(cls="candidate", baseline="ceiling 54.99999999534339 C at a constructed exact tie net(55 C) == 0.0", mutant="ceiling 55.0 C",
    inputs="117 (as c40e66fc); moved 3, exactly the 3 constructed net(hi)==0.0 ties (buffer_max 55/70/90 C, out_mean ~-19.7 C, internal_gains and buffer_cooling_rate walked by ulps); max |delta| 1.28e-8 C",
    should_fail="tests/features.py / tests/validate.py (execute line 6091) have no input with net(hi) exactly 0.0; a pin would need a constructed float tie",
    finding=cand("Buffer charge ceiling's net(hi) > 0 boundary is unpinned (moves 1e-8 C at an exact float tie)",
        "At a constructed exact tie net(buffer_max_temp) == 0.0, HeatPumpOptimizer._buffer_charge_ceiling returns hi - 4.7e-9 C, and returns exactly hi under the >= mutant, which the full gate does not detect.",
        "low", "the value _buffer_charge_ceiling returns at the constructed net(hi)==0.0 tie, C", "up by (hi-lo)/2**32 (~1e-8 C) under the mutant",
        "out_mean 15 C: null_delta 0 C", "_buffer_charge_ceiling", "tests: none worth adding; a measure-zero tie with a 1e-8 C effect"))
M["72d1e72dd0acdfc1"] = dict(cls="equivalent-candidate", baseline="ceiling == lo (35 C) when net(lo) <= 0", mutant="bisection moves only hi; returns lo == 35 C",
    inputs="117 (as c40e66fc); moved 0", why="with net(lo) <= 0 and net decreasing every net(mid) <= 0, so only hi moves and the loop returns lo unchanged",
    should_fail="none (executed by tests/features.py)")
M["bdb9a95deedcc8fe"] = dict(cls="equivalent-candidate", baseline="ceiling 35.0 C at a constructed exact tie net(35 C) == 0.0", mutant="35.0 C",
    inputs="117 (as c40e66fc, incl. 3 exact net(lo)==0.0 ties); moved 0", why="at net(lo) == 0.0 the mutant bisects, every net(mid) < 0, and the loop returns lo unchanged",
    should_fail="none (executed by tests/features.py)")
M["bf2229e3f179f4b6"] = dict(cls="candidate", baseline="ceiling 44.99999999534339 C at a constructed exact tie net(45 C) == 0.0 (first midpoint, buffer_max 55)", mutant="45.0 C",
    inputs="117 (as c40e66fc); moved 3, exactly the 3 constructed net(mid)==0.0 ties; max |delta| 1.28e-8 C",
    should_fail="tests/features.py (the only script reaching line 6097) has no input whose bisection midpoint is an exact root",
    finding=cand("Buffer charge ceiling's bisection comparison net(mid) > 0 is unpinned (moves 1e-8 C at an exact float tie)",
        "At a constructed exact root at the first bisection midpoint, HeatPumpOptimizer._buffer_charge_ceiling returns mid - 4.7e-9 C, and exactly mid under the >= mutant, which the full gate does not detect.",
        "low", "the value _buffer_charge_ceiling returns at the constructed net(mid)==0.0 tie, C", "up by ~1e-8 C under the mutant",
        "out_mean 15 C: null_delta 0 C", "_buffer_charge_ceiling", "tests: none worth adding; a measure-zero tie with a 1e-8 C effect"))
M["19141bef62ecb4a6"] = dict(cls="equivalent-candidate", baseline="identical bounds for every array input", mutant="identical; a 0-d floor raises on both arms (IndexError vs ValueError)",
    inputs="66: n {1,4,96} x floors.size {0,1,n-1,n,n+1,2n} x fill {18,25,nan,-inf} + 0-d floor + short list with margins; moved 1, beyond exception type 0",
    why="at f.size == n_steps the mutant concatenates an empty pad (a no-op); the only other moved input raises on both arms",
    should_fail=f"none (executed by tests/{{{EXEC[4766]}}}.py)")
M["47430bf93e309e76"] = dict(cls="candidate", baseline="min bounds shape (n,) with the short mold-floor series padded by -inf", mutant="min bounds shape (0,) for an empty series (silent), ValueError for 2..n-1 floors, the one floor broadcast over all n steps for a single floor",
    inputs="66 (as 19141bef); moved 33",
    should_fail="tests/features.py / tests/entities.py / tests/env_drift.py (execute line 4766) never pass min_temp_floors shorter than n_steps; lacks a padding assertion (short floors -> trailing -inf, bounds shape (n,))",
    finding=cand("Mold-floor padding in _build_comfort_bounds is unpinned: without it a short floor series silently empties or mis-broadcasts the comfort band",
        "With the `f.size < n_steps` padding disabled, HeatPumpOptimizer._build_comfort_bounds returns a (0,)-shaped minimum-bound array for an empty mold-floor series and raises ValueError for a series of 2..n-1 floors (33 of 66 probe inputs move), and the full gate stays green.",
        "low", "the (targets, min, max, (comfort floors, mold floors)) tuple _build_comfort_bounds returns, compared by shape and value",
        "shape (n,) -> (0,) / ValueError under the mutant", "min_temp_floors None (branch not entered): null_delta 0",
        "_build_comfort_bounds", "tests: one short-floors assertion; production floors come from _mold_floor_series over the horizon's outdoor temps, so reach needs a horizon shorter than n_steps"))
M["0275af9776ae709e"] = dict(cls="candidate", baseline="space-power ceiling 0.0 kW at every step when space heating is blocked", mutant="ceiling max_electrical_power (5.0 kW): the block is ignored",
    inputs="264: n {1,4,96} x blocked {F,T} x off steps {None,alternate} x extra caps {None, sizes 0..2n x fill 0/2.5/99/nan, 0-d}; moved 85 (blocked rows without off steps/zero caps covering them)",
    should_fail=f"tests/features.py (one of tests/{{{EXEC[4802]}}}.py) lacks a direct ceiling assertion (power_caps == 0 when space_blocked)",
    finding=cand("Space-heating mode block's zero ceiling is unpinned at _build_space_power_caps",
        "With `if space_blocked:` disabled, HeatPumpOptimizer._build_space_power_caps returns a 5.0 kW space ceiling instead of 0.0 kW while space heating is blocked.",
        "high", "power_caps[0] returned by _build_space_power_caps(n, None, True, None), kW", "0.0 -> 5.0 kW (up) under the mutant",
        "space_blocked False: null_delta 0", "_build_space_power_caps", "tests: assert the zero ceiling directly"))
M["9e71bd23e996ec6a"] = dict(cls="equivalent-candidate", baseline="identical caps for every array input", mutant="identical; a 0-d extra cap raises on both arms (IndexError vs ValueError)",
    inputs="264 (as 0275af97); moved 4, beyond exception type 0", why="at extra.size == n_steps the mutant concatenates an empty pad (a no-op)",
    should_fail=f"none (executed by tests/{{{EXEC[4828]}}}.py)")
M["3652dbb5880d62c8"] = dict(cls="candidate", baseline="(replanned, 1 pinned step) at space == headroom - 1e-3 exactly, dhw 1.0 kW", mutant="(ok, 0): the DHW re-plan is skipped",
    inputs="42: dhw {0,1e-6,next/prev(1e-6),1,4,5} kW x space {head-2e-3, head-1e-3 (tie), prev/next of the tie, head, 0}; moved 4, exactly the tie rows with dhw > 1e-6",
    should_fail=f"tests/features.py (one of tests/{{{EXEC[3969]}}}.py) has no co-optimize case with space power at exactly headroom - 1e-3",
    finding=cand("DHW co-optimize pin test `space >= headroom - 1e-3` is unpinned at its tolerance edge",
        "With >= made >, HeatPumpOptimizer._co_optimize no longer pins a step whose space power is exactly headroom - 1e-3 and skips the DHW re-plan (status replanned -> ok), and the full gate stays green.",
        "low", "(status, pinned steps handed to the DHW re-plan) from _co_optimize on a one-step input, recording planner stand-in",
        "(replanned, 1) -> (ok, 0) under the mutant", "dhw 1.0, space 1.0: null_delta 0", "_co_optimize", "tests: a tolerance-edge case; measure-zero in production"))
M["b1926550efd8eac4"] = dict(cls="candidate", baseline="(ok, 0) at dhw exactly 1e-6 kW with space at its headroom", mutant="(replanned, 1): the step is pinned and the DHW re-plan runs",
    inputs="42 (as 3652dbb5); moved 3, exactly the dhw == 1e-6 rows with space >= headroom - 1e-3",
    should_fail=f"tests/features.py (one of tests/{{{EXEC[3969]}}}.py) has no co-optimize case with hot-water power exactly 1e-6 kW",
    finding=cand("DHW co-optimize pin test `dhw > 1e-6` is unpinned at its threshold",
        "With > made >=, HeatPumpOptimizer._co_optimize pins a step with hot-water power exactly 1e-6 kW and runs the DHW re-plan (status ok -> replanned), and the full gate stays green.",
        "low", "(status, pinned steps handed to the DHW re-plan) from _co_optimize on a one-step input, recording planner stand-in",
        "(ok, 0) -> (replanned, 1) under the mutant", "dhw 1.0, space 1.0: null_delta 0", "_co_optimize", "tests: a threshold case; measure-zero in production"))
out = {}
for k, v in M.items():
    v = dict(v)
    out[k] = {"class": v.pop("cls"), "baseline": v.pop("baseline"), "mutant": v.pop("mutant"), "inputs": v.pop("inputs"),
              "should_fail": v.pop("should_fail").replace("{", "").replace("}", ""), **v}
(W / "tools" / "keymeta.json").write_text(json.dumps(out, indent=1) + "\n")
print(len(out))
