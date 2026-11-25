"""VD3L: assemble REPORT.json, partial.json and verify-late.md from the votes below and the full-gate outputs."""
import json, os, re, sys
D = os.path.expanduser("~/vout/D3-vlate"); G = D + "/gates"
def gate(key):
    p = f"{G}/{key}.out"
    if not os.path.exists(f"{G}/{key}.done"):
        return None
    t = open(p).read()
    r = dict(re.findall(r"^RESULT (\w+)=(\S+)", t, re.M))
    v = re.search(r"^VERDICT \S+ (\S+)", t, re.M)
    return {"verdict": v.group(1) if v else "NONE", "gate_rc": r.get("gate_rc"), "failed_scripts": r.get("failed_scripts"),
            "killed": r.get("killed"), "wall_s": r.get("wall"), "load1": r.get("load1"), "thread_factor": r.get("thread_factor")}
NULL = gate("null")
B = "baseline tree 92d38ecb64 (+ e3cb5c019b's D3 evidence)"; H = "evidence tree e3cb5c019b"
ATH = ("targeted at head: mutant applied in %s at %s, then tests/guard_pins.py and tests/features.py (PYTHONPATH=tests/hastub, "
       "seats/D3-vlate/athead.sh): %s; the full gate was not re-run at head (about an hour per mutant)")
V = [
 dict(id="D3-s1-02", key="d931ab195b940b0c", site="tariff.py:744", vote="weaken", severity="nit",
  value="_smooth_topk_sum(x,0) 0.0 -> 1.473806 under the mutant, batch stays 0.0 (mismatch 0 -> 1)",
  metric_definition="scalar _smooth_topk_sum(x,0) minus batch _smooth_topk_sum_batch(x[None],0), base vs whole-module mutant; reach = production calls with k<=0",
  reproduced="base_d931.out (%s): scalar_k0 0.000000 -> 1.473806, batch_k0 0.000000 both arms, mismatch 0 -> 1; m31 harness topk_k0 0.0 -> 19.9986 kW, null_delta 0.0; load1 0.73 thread_factor 1.0" % B,
  independent_value="v2_simple.py (own input, whole-module mutant): 02_scalar_k0 0.0 -> 3.999998, batch [0.0]; nulls k=2 and k<0 delta 0.0",
  reachable="no: reach_calls_k_le_0 = 0 of 111 production calls; both callers clamp k with max(1, ...) (tariff.py 982, 1204); hastub not involved",
  class_="I1 (guard whose mutation leaves the gate green); class_guess 'new' corrected",
  seam="enumerates: the grep names both sibling guards (744 scalar, 798 batch), the phenomenon's two seams",
  at_head=("02", "tariff.py:744", "guard_pins rc=0, features rc=0: not killed"),
  attacks="contention (load1 < 2, thread_factor 1.0: none); null control k=2/k<0 (0.0); reachability (0 of 111 calls, so severity cut to nit: the divergence is unreachable today)"),
 dict(id="D3-s1-52", key=None, site="tests/closure.py _widen", vote="verify", severity="low",
  value="0 of 45 card_drift states move under two payload-changing production edits; 44 move under a one-token card edit; card_drift selected on 11 of 12 cell-file diffs",
  metric_definition="states card_drift.mjs reports changed (of 45) per arm, with sha256 of the plan payload changed or not; plus closure.select hits",
  reproduced="m5_card_drift_payload.py (%s): base moved 0; prod_small moved 0 payload_changed 1; prod_large moved 0 payload_changed 1; card moved 44 rc 1; closure edges 11, cell diffs selecting 11; load1 1.51 thread_factor 1.00" % B,
  independent_value="own runs of tests/card_drift.mjs over a doubled payload (v2_card_drift_plan-x2): 'identical in all 45 states'; same over the plain payload: identical in all 45",
  reachable="CI-only (gate scheduling), not a Home Assistant path; the cost is gate time on every cell-file diff, no product consequence",
  class_="I2 (measured closure diverges from the real dependency graph); class_guess 'new' corrected",
  seam="demonstrated seam only: --select-only enumerates the 12 D3-s1 cell files (11 select card_drift), not every closure _widen unions",
  at_head=None, at_head_text="in the evidence tree e3cb5c019b: `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/m5_card_drift_payload.py --select-only` -> card_drift_cell_closure_edges 11, cell_diffs_selecting_card_drift 11 (load1 2.22, thread_factor 1.00): the over-selection stands at head; the full harness refuses at head (rc 1, AssertionError: its card-edit anchor `ha-card { padding: 12px 12px 8px 12px; }` has moved in heatpump-optimizer-card.js), so the 0-of-45 half was not re-measured at head",
  attacks="null (no edit: moved 0); positive control (card edit: 44 moved, so the harness can move); payload doubled (still 0): the finder's claim holds"),
 dict(id="D3-s1-62", key="121362d48b408236", site="grid_fee.py:173", vote="verify", severity="low",
  value="rule text '0.5': rules -1 (GridFeeError) -> 1 parsed; verdict invalid_grid_fee_rules -> None",
  metric_definition="_parse_rule/from_config outcome on a rule with no '=': error (-1) or parsed rule count; config_flow spec_problem verdict",
  reproduced="probe_121362d4.py (%s): rules -1 -> 1, delta 2; verdict invalid_grid_fee_rules -> None; null_delta 0; reach_calls_without_eq 2" % B,
  independent_value="v2_simple.py: bare rate '0.5' -1 -> 1 and problem invalid_grid_fee_rules -> None; bare tokens 'a b' stay -1 in both arms (the mutant only opens the numeric case); null 0",
  reachable="yes: config_flow.spec_problem (config_flow.py:3927) and GridFeeSchedule.from_config (grid_fee.py:287) take user option text; no divergent hastub symbol on the path",
  class_="I1; class_guess 'new' corrected",
  seam="phenomenon-wide: the tabulate --tsv | grep SURVIVED rule lists all 992 surviving mutants of the round, a superset including this one",
  at_head=("62", "grid_fee.py:173", "guard_pins rc=0, features rc=0: not killed"),
  attacks="null (0); malformed-but-non-numeric input (no move: narrows the gap to bare numerics); reachability through config flow (yes)"),
 dict(id="D3-s1-63", key="95779f9d6d71c50d", site="grid_fee.py:355", vote="weaken", severity="nit",
  value="max_abs_component label fixed -> rules on a |rate| tie; value delta 0.0",
  metric_definition="(value, source label) returned by max_abs_component on a fixed/rule |rate| tie",
  reproduced="probe_95779f9d.py (%s): label fixed -> rules, label_changed 1, value_delta 0.0, rules-only tie delta 0, null 0, reach_from_config_tie 1" % B,
  independent_value="v2_simple.py own tie: (0.4,'fixed') -> (0.4,'rules'); null 0",
  reachable="yes via from_config, but only the repair-issue placeholder text (coordinator.py:7623) reads the label; the number is equal in both arms",
  class_="I1; class_guess 'new' corrected",
  seam="phenomenon-wide (SURVIVED listing, 992 rows)",
  at_head=("63", "grid_fee.py:355", "guard_pins rc=0, features rc=0: not killed"),
  attacks="consequence: value_delta 0.0 on a tie, so only a message label changes -> severity cut to nit"),
 dict(id="D3-s1-64", key="5cc84148fa68bda1", site="grid_fee.py:383", vote="weaken", severity="nit",
  value="min_component label fixed -> rules on a rate tie; value delta 0.0",
  metric_definition="(value, source label) returned by min_component on a fixed/rule rate tie",
  reproduced="probe_5cc84148.py (%s): label fixed -> rules, label_changed 1, value_delta 0.0, null 0, reach_from_config_tie 1" % B,
  independent_value="v2_simple.py own tie: (0.1,'fixed') -> (0.1,'rules'); null 0",
  reachable="yes via from_config; the label is read only when the value is < 0 (coordinator.py:7628), so a message label at most",
  class_="I1; class_guess 'new' corrected",
  seam="phenomenon-wide (SURVIVED listing, 992 rows)",
  at_head=("64", "grid_fee.py:383", "guard_pins rc=0, features rc=0: not killed"),
  attacks="consequence: equal value, label read only on a negative minimum -> nit; the finder's gate status was RED-AS-NULL, so the gate re-run decides survival"),
 dict(id="D3-s1-65", key="0c3e91a6a349409a", site="flow_lift.py:47", vote="verify", severity="low",
  value="learned flow bias 3.638040 K -> 4.689280 K (delta 1.051240 K)",
  metric_definition="FlowBias learned bias after the probe's sample sequence, FLOW_BIAS_ALPHA 0.1 vs 0.2",
  reproduced="probe_0c3e91a6.py (%s): 3.638040 -> 4.689280 K, null_delta 0.0" % B,
  independent_value="v2_simple.py own one-fold input: 1.0 -> 2.0; null 0.0",
  reachable="yes: every fold after the warm-up (coordinator.py:986) on any plant with flow sensing",
  class_="I1 (an unpinned behaviour constant); class_guess 'new' corrected",
  seam="phenomenon-wide (SURVIVED listing, 992 rows)",
  at_head=("65", "flow_lift.py:47", "guard_pins rc=0, features rc=0: not killed"),
  attacks="null (0.0); a doc check reads the constant rather than pinning 0.1, so it follows the mutant (confirmed by the survivor)"),
 dict(id="D3-s1-66", key="a0b3b28854fa500c", site="flow_lift.py:188", vote="verify", severity="low",
  value="bias 3.000000 K -> 3.666667 K at the sample one past FLOW_BIAS_MIN_SAMPLES",
  metric_definition="FlowBias learned bias after MIN_SAMPLES+1 folds, '<' vs '<=' warm-up guard",
  reproduced="probe_a0b3b288.py (%s): 3.000000 -> 3.666667 K, delta 0.666667, null 0.0, reach_samples_eq_min 1" % B,
  independent_value="v2_simple.py: 1.0 -> 1.666667; null 0.0; a 7-sample input moves 0.6 (the boundary is crossed on every plant)",
  reachable="yes: every plant passes samples == FLOW_BIAS_MIN_SAMPLES once",
  class_="I1; class_guess 'new' corrected",
  seam="phenomenon-wide (SURVIVED listing, 992 rows)",
  at_head=("66", "flow_lift.py:188", "guard_pins rc=0, features rc=0: not killed"),
  attacks="null 0.0; leave-one-out not applicable (single-number claim)"),
 dict(id="D3-s1-67", key="050fdc4a20eba212", site="thermal_model.py:169", vote="verify", severity="low",
  value="unset holiday-DHW-windows option parses to [] instead of None in 3 of 3 unset forms; consequence: a holiday day has 0 DHW windows instead of 2",
  metric_definition="_holiday_dhw_windows(config) for absent/''/None; consequence = len(windows_for_day(..., holiday=True)) with the parser's value",
  reproduced="probe_050fdc4a.py (%s): None -> [] for absent, '' and None; unset_forms_moved 3; null 0; reach_unset_calls 3" % B,
  independent_value="v2_67_consequence.py (own, dhw_schedule.windows_for_day): holiday day windows in force 2 -> 0; null (not a holiday day) 2 -> 2, delta 0",
  reachable="yes: the default install leaves the option unset and the holiday overlay is consulted whenever holiday mode is on (dhw_schedule.py:413 'holiday_windows is not None')",
  class_="I1; class_guess 'new' corrected",
  seam="phenomenon-wide (SURVIVED listing, 992 rows)",
  at_head=("67", "thermal_model.py:169", "guard_pins rc=0, features rc=0: not killed"),
  attacks="consequence measured beyond the parser: holiday mode loses every DHW window (2 -> 0); the judge may weigh a raise above low"),
 dict(id="D3-s1-68", key="22b5ec8775d5bd50", site="thermal_model.py:2593", vote="weaken", severity="nit",
  value="direct call at dt=0.25 h: delivered 0.278400 -> 2.800000 kW; through simulate_step: 0 of 287299 calls differ",
  metric_definition="(q_rad+q_floor) of _valve_two_zone_delivery, base vs whole-module mutant on the same arguments, over every call simulate_step makes in a plant sweep",
  reproduced="probe_22b5ec87.py (%s): 0.278400 -> 2.800000 kW, delta 2.521600, null 0.0, reach_valve_calls 64 (single-tank 64)" % B,
  independent_value="v2_valve_calls.py (own spy over simulate_step): 287299 calls, 0 differ, max delta 0.000000 kW, dt_hours seen 0.00198..0.5; v2_valve_dt.py direct: dt 0.25/0.1/0.05 h differ (2.52/2.10/1.41 kW), dt <= 0.02 h equal; the finder's plant substeps at dt 0.01923 h",
  reachable="the function is reached in real HA, but the public path's substepping keeps the tank bound from binding in every swept call, so the mutant is behaviour-equivalent there",
  class_="I1; class_guess 'new' corrected",
  seam="phenomenon-wide (SURVIVED listing, 992 rows)",
  at_head=("68", "thermal_model.py:2618 (moved from 2593)", "guard_pins rc=0, features rc=0: not killed"),
  attacks="reachability on the public path (0 of 287299 calls separate): the moving number exists only on a direct call with a coarse dt; severity cut to nit"),
 dict(id="D3-s1-69", key="0911281eca895664", site="dhw_planner.py:1559", vote="weaken", severity="nit",
  value="dhw_kwh 2.5056 -> 1.9948 at prices x1000; realistic profiles delta 0.0; separation needs >= 8000 per kWh",
  metric_definition="solved DHW energy (kWh) from HeatPumpOptimizer.optimize, base vs mutant shortfall price, per price-profile cell",
  reproduced="probe_0911281e.py (%s): 2.5056 -> 1.9948 kWh (delta -0.5108), null 0, realistic_delta 0.0, min_price_for_separation 8000" % B,
  independent_value="v2_dhw.py (own, tests/profiles.py profiles x1000): 32 cells, 0 moved, max |delta| 0.0000; positive control (shortfall price 0.0) moves 1 of 1 cell by 1.0849 kWh, so the harness can move",
  reachable="only with a price spread of >= 8000 per kWh, which no real tariff carries; the shortfall penalty does not bind on any realistic input",
  class_="I1; class_guess 'new' corrected",
  seam="phenomenon-wide (SURVIVED listing, 992 rows)",
  at_head=("69", "dhw_planner.py:1559", "guard_pins rc=0, features rc=0: not killed"),
  attacks="grid artefact: 0 of 32 cells move at x1000 prices (positive control moves); consequence only at absurd prices -> nit"),
 dict(id="D3-s1-70", key="5e8d48eff7e4fa8d", site="coordinator.py:8806", vote="verify", severity="low",
  value="tariff disabled with peaks held: threshold (5.0,10.0) -> (5.0,3.0), suppressing False -> True",
  metric_definition="(projection, threshold) handed to GuardState.update and guard.suppressing after _on_power_event, base vs and->or",
  reproduced="probe_5e8d48ef.py (%s): enabled,factor0 (5.0,10.0) -> (0.0,3.0); disabled,factor1 (5.0,10.0) -> (5.0,3.0) suppressing False -> True; null_moved 0" % B,
  independent_value="v2_power.py (own, real PeakTracker/GuardState): disabled+fuse 8 ((6,8),False) -> ((6,4),True); enabled factor0 no fuse ((6,inf),False) -> ((0,4),False); enabled factor0 fuse 8 unmoved; 2 of 3 cells moved; null 0",
  reachable="yes: a tariff switched off while the tracker holds peaks restored by from_dict (coordinator.py:8378) suppresses heating against a stale peak",
  class_="I1; class_guess 'new' corrected",
  seam="phenomenon-wide (SURVIVED listing, 992 rows)",
  at_head=("70", "coordinator.py:8774 (moved from 8806)", "guard_pins rc=0, features rc=0: not killed"),
  attacks="null 0; one of three cells does not move (fuse caps the enabled-factor0 case); the disabled case alone carries the user-visible suppression"),
 dict(id="D3-s1-71", key="c38d53ab787ddbfa", site="price_model.py:252", vote="weaken", severity="nit",
  value="a day whose mean is exactly 1e-6: accepted 0 -> 1",
  metric_definition="observe_day_quarters acceptance (0/1) of a hand-built day at mean == 1e-6",
  reproduced="probe_c38d53ab.py (%s): accepted 0 -> 1, quarter_days_delta 1, null 0, reach_real_price_days_at_boundary 0" % B,
  independent_value="v2_head71.py (own): observe_day_quarters base 0 mut 1; sibling observe_day (sharing _usable_day at head) base 0 mut 1",
  reachable="only with a day whose mean price is exactly 1e-6; no real price day sits on that boundary (reach 0)",
  class_="I1; class_guess 'new' corrected",
  seam="phenomenon-wide (SURVIVED listing, 992 rows)",
  at_head=("71", "price_model.py:163 (moved from 252, now in _usable_day)", "guard_pins rc=0, features rc=1 '1 of 6034 FEATURE CHECKS FAILED' (null at head: features rc=0): KILLED at head"),
  attacks="reachability: exact-boundary input only -> nit; the finder's own gate status was RED-AS-NULL, so the re-run gate decides survival; main has since pinned it"),
]
def at_head_text(v):
    if v["at_head"] is None:
        return v["at_head_text"]
    i, site, res = v["at_head"]
    return ATH % (H, site, res)
votes = []
for v in V:
    g = gate(v["key"]) if v["key"] else None
    if v["key"]:
        gtxt = ("full gate (%s, `fullgate.py run --key %s`): %s, gate_rc %s, failed_scripts %s, killed %s, wall %s s, load1 %s, thread_factor %s; null gate: gate_rc %s, failed %s" %
                (B, v["key"], g["verdict"], g["gate_rc"], g["failed_scripts"], g["killed"], g["wall_s"], g["load1"], g["thread_factor"], NULL["gate_rc"], NULL["failed_scripts"])) if g else "full gate PENDING"
    else:
        gtxt = "no full-gate claim"
    vote = v["vote"]
    if g and g["verdict"] == "KILLED":
        vote = "refute"
    votes.append(dict(id=v["id"], vote=vote, severity=v["severity"], value=v["value"], metric_definition=v["metric_definition"],
        method="V1 finder harness re-run in %s; V2 own harness under seats/D3-vlate/v2/; V3 reach/class/seam_rule; %s" % (B, gtxt),
        attacks=v["attacks"], reproduced=v["reproduced"] + "; " + gtxt, independent_value=v["independent_value"],
        reachable=v["reachable"], **{"class": v["class_"]}, seam_rule_enumerates=v["seam"], at_head=at_head_text(v), full_gate=g))
pending = [x["id"] for x in votes if x["full_gate"] is None and x["id"] != "D3-s1-52"]
out = {"seat": "D3-vlate", "box": "VD3L", "round": 11, "baseline": "92d38ecb640bd462f2e19c0814d0f0b7df1ee692",
       "evidence_tree": "e3cb5c019b464a770cc7c6fe2fbc858ed29debf7", "null_gate": NULL, "gates_pending": pending, "votes": votes}
json.dump(out, open(D + ("/partial.json" if pending else "/REPORT.json"), "w"), indent=1)
if not pending:
    json.dump(out, open(D + "/partial.json", "w"), indent=1)
L = ["# Round 11 D3 late findings -- verifier report (seat D3-vlate, box VD3L)", "",
     "Baseline tree 92d38ecb64 with e3cb5c019b's D3 evidence copied over; at-head readings in the evidence tree e3cb5c019b. "
     "All three lenses on every finding. Machine: cloud container, 4 vCPU; thread_factor 1.0 throughout; load1 quoted per number. "
     "This seat resumed a stalled predecessor's wip ref (aae12cc390): its probe, V2 and at-head outputs were kept, and the full gates it had not checkpointed were re-run.", "",
     "Incident (2026-11-25): during the first run of gate 050fdc4a20eba212 (D3-s1-67) a git index.lock appeared in the baseline worktree at 09:38:07Z (empty, no git process holding it); the gate's run.sh still ended 'ALL TEST SCRIPTS PASSED' with the mutant committed (kept as gates/incident/050fdc4a20eba212.firstrun.log), but fullgate.py's reset to the baseline then failed (exit 128), and the four gates after it refused at once ('HEAD a33eacf352 is not the baseline'). The lock was removed, the tree reset to 92d38ecb64, the dead lease released, and all five gates re-run; the numbers below are the re-runs. The same empty lock recurred at 13:38:12Z during the re-run of gate 5e8d48eff7e4fa8d (D3-s1-70; first-run log again 'ALL TEST SCRIPTS PASSED', kept as gates/incident/5e8d48eff7e4fa8d.firstrun.log), so gates 70 and 71 were re-run once more under an environment-only guard (lock_guard.sh: removes an empty index.lock older than 120 s while no git process runs, logging each removal to gates/lock_guard.log); no tracked file was changed. The lock's origin was not identified: 2 of 14 gate runs, each about 15 min after the gate started.", "",
     "Null full gate: gate_rc %s, failed_scripts %s, wall %s s, load1 %s." % (NULL["gate_rc"], NULL["failed_scripts"], NULL["wall_s"], NULL["load1"]), "",
     "At-head method: the mutant applied in the evidence tree, then `tests/guard_pins.py` and `tests/features.py` only (seats/D3-vlate/athead.sh); the full gate was not re-run at head. A not-killed reading there is therefore 'not killed by those two scripts', not 'survives the full gate at head'.", ""]
if pending:
    L += ["**Gates still pending:** " + ", ".join(pending), ""]
L += ["| id | vote | severity | full gate | at head |", "|---|---|---|---|---|"]
for x in votes:
    g = x["full_gate"]; L.append("| %s | %s | %s | %s | %s |" % (x["id"], x["vote"], x["severity"], (g["verdict"] if g else ("n/a" if x["id"] == "D3-s1-52" else "pending")), x["at_head"].split(": ")[-1] if "KILLED" in x["at_head"] or "not killed" in x["at_head"] else "not re-run"))
for x in votes:
    L += ["", "## " + x["id"], "", "- vote: **%s**, severity %s" % (x["vote"], x["severity"]), "- value: " + x["value"], "- metric: " + x["metric_definition"],
          "- V1 reproduced: " + x["reproduced"], "- V2 independent: " + x["independent_value"], "- V3 reachable: " + x["reachable"],
          "- V3 class: " + x["class"], "- V3 seam_rule: " + x["seam_rule_enumerates"], "- attacks: " + x["attacks"], "- at head: " + x["at_head"]]
open(D + "/verify-late.md", "w").write("\n".join(L) + "\n")
print("pending:", pending)
