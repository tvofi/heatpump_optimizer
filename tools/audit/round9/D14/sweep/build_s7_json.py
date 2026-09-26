#!/usr/bin/env python3
"""Assembles S7.json from the per-class dispositions in this sweep.

Run: python3 tools/audit/round9/D14/sweep/build_s7_json.py > tools/audit/round9/D14/sweep/S7.json
"""
import json

CLASSES = [
    {
        "class": "new: CPU work inline on the event loop",
        "N": 2,
        "rca": False,
        "seams": [
            {"path": "custom_components/heatpump_optimizer/coordinator.py:10478,10512",
             "disposition": "instance", "probe": "D9-s1-03 (finder's own)",
             "note": "_sysid.arm/.step via _run_system_identification, called directly from _async_update_data:5079, no executor"},
            {"path": "custom_components/heatpump_optimizer/sensor.py:111",
             "disposition": "instance", "probe": "D9-s2-01 (finder's own)",
             "note": "rank_sensor_advisor -> topology.py:850 simulate_step, called from extra_state_attributes property"},
        ],
        "barrier_proposal": "none (N<3): finders' own scope is route both through hass.async_add_executor_job, or precompute sensor_advisor once per cycle",
        "gate_seconds": 0.05,
    },
    {
        "class": "new: persisted future instant trusted without bound",
        "N": 7,
        "rca": True,
        "seams": [
            {"path": "custom_components/heatpump_optimizer/drift.py:148", "disposition": "instance", "probe": "D1-s1-04", "note": "verified finding"},
            {"path": "custom_components/heatpump_optimizer/snapshots.py:74", "disposition": "instance", "probe": "D1-s1-04", "note": "verified finding"},
            {"path": "custom_components/heatpump_optimizer/curve_learning.py:111", "disposition": "instance", "probe": "D1-s1-04", "note": "verified finding"},
            {"path": "custom_components/heatpump_optimizer/comfort_learning.py:256", "disposition": "instance", "probe": "D1-s1-04", "note": "verified finding"},
            {"path": "custom_components/heatpump_optimizer/boost.py:166", "disposition": "instance", "probe": "D1-s3-05", "note": "weakened(low) finding"},
            {"path": "custom_components/heatpump_optimizer/coordinator.py:8007,8023-8024", "disposition": "instance", "probe": "probe_fuse_advisor.py", "note": "sweep-confirmed: fuse-advisor 7-day recompute cooldown"},
            {"path": "custom_components/heatpump_optimizer/coordinator.py:2953,6306", "disposition": "instance", "probe": "probe_more_instances.py:check_snow_damping", "note": "sweep-confirmed: heavy-snow damping window"},
            {"path": "custom_components/heatpump_optimizer/coordinator.py:7343,8099-8114", "disposition": "instance", "probe": "probe_more_instances.py:check_outage_detection", "note": "sweep-confirmed: outage staggered-recovery window"},
            {"path": "custom_components/heatpump_optimizer/pump_arbiter.py:629,405-407", "disposition": "instance", "probe": "probe_more_instances.py:check_echo_grace", "note": "sweep-confirmed: write-echo grace period"},
            {"path": "custom_components/heatpump_optimizer/coordinator.py:8381", "disposition": "instance", "probe": "not probed (low confidence)", "note": "immersion-event recency count; same shape, capped by needing >=3 corrupted entries, not separately probed"},
            {"path": "custom_components/heatpump_optimizer/accuracy.py:78", "disposition": "not applicable", "probe": None, "note": "position-pruned (entry[-512:]), not a now-gated window"},
            {"path": "custom_components/heatpump_optimizer/accuracy.py:406", "disposition": "not applicable", "probe": None, "note": "position-pruned, not a now-gated window"},
            {"path": "custom_components/heatpump_optimizer/away.py:590", "disposition": "not applicable", "probe": None, "note": "different class: tz-naive return_time crash (D1-s3-01)"},
            {"path": "custom_components/heatpump_optimizer/coordinator.py:583", "disposition": "not applicable", "probe": None, "note": "shared tz-coercion helper, not itself a gate"},
            {"path": "custom_components/heatpump_optimizer/coordinator.py:6330", "disposition": "not applicable", "probe": None, "note": "different class: stale 15-min quarter read (D2-s3-01/D8-s1-01)"},
            {"path": "custom_components/heatpump_optimizer/coordinator.py:7554,7566", "disposition": "not applicable", "probe": None, "note": "keyed by calendar-day string, not a now-gated comparison"},
            {"path": "custom_components/heatpump_optimizer/open_meteo.py:206", "disposition": "not applicable", "probe": None, "note": "fresh per-cycle fetch, nothing persisted"},
            {"path": "custom_components/heatpump_optimizer/price_model.py:487", "disposition": "not applicable", "probe": None, "note": "fresh per-cycle fetch, nothing persisted"},
            {"path": "custom_components/heatpump_optimizer/manual_plan.py:82,236,246", "disposition": "not applicable", "probe": None, "note": "belongs to 'service input without an upper-bound clamp' (D1-s2-54), its own class"},
        ],
        "barrier_proposal": "AST lint over every fromisoformat call reachable from a persisted-store async_load that flows into a now-restored/restored-now comparison with no intervening min/max clamp at the restore site; sub-second cost",
        "gate_seconds": 0.3,
    },
    {
        "class": "I2",
        "N": 1,
        "rca": False,
        "seams": [
            {"path": "tests/doc_claims.py (9 seams via tests/plan_view.py child)", "disposition": "instance", "probe": "closure_divergence.py (reused finder harness)", "note": "D14-s5-01"},
            {"path": "tests/deployment_shape.py (22 seams via its own -P/--driver child)", "disposition": "instance", "probe": "closure_divergence.py (reused finder harness)", "note": "D14-s5-01"},
        ],
        "barrier_proposal": "wrap --exec-record in strace -f -y on Linux, union with the audit-hook set; ~9.4s strace wall vs 5.9s audit-hook seconds (finder's own, not re-measured)",
        "gate_seconds": 15,
    },
    {
        "class": "P7",
        "N": 1,
        "rca": False,
        "seams": [
            {"path": "custom_components/heatpump_optimizer/coordinator.py:6207 (_forecast_arrays step_offset)", "disposition": "instance", "probe": "p7_dst_seams.py (reused finder harness)", "note": "D14-s4-01, high severity"},
            {"path": "custom_components/heatpump_optimizer/accuracy.py:182 (score_lead_predictions)", "disposition": "instance", "probe": "p7_dst_seams.py", "note": "D14-s4-01"},
            {"path": "custom_components/heatpump_optimizer/coordinator.py:9405 (_file_dhw_lead_predictions)", "disposition": "instance", "probe": "p7_dst_seams.py", "note": "D14-s4-01"},
            {"path": "custom_components/heatpump_optimizer/coordinator.py:9445 (_file_lead_predictions)", "disposition": "instance", "probe": "p7_dst_seams.py", "note": "D14-s4-01"},
            {"path": "custom_components/heatpump_optimizer/coordinator.py:9205 (_record_accuracy elapsed)", "disposition": "instance", "probe": "p7_dst_seams.py", "note": "D14-s4-01"},
            {"path": "custom_components/heatpump_optimizer/dhw_learning.py:347 (async_learn_dynamics)", "disposition": "instance", "probe": "p7_dst_seams.py", "note": "D14-s4-01"},
            {"path": "custom_components/heatpump_optimizer/external_heat.py:206 (_rate)", "disposition": "instance", "probe": "p7_dst_seams.py", "note": "D14-s4-01"},
            {"path": "custom_components/heatpump_optimizer/coordinator.py:4684 (_next_optimization)", "disposition": "instance", "probe": "p7_dst_seams.py", "note": "D14-s4-01"},
            {"path": "custom_components/heatpump_optimizer/tariff.py:58 (_window_slot)", "disposition": "not applicable", "probe": None, "note": "wall-clock label by definition"},
            {"path": "custom_components/heatpump_optimizer/coordinator.py:3169 (close)", "disposition": "guarded", "probe": None, "note": "reached but never crosses a transition boundary in this fixture"},
        ],
        "barrier_proposal": "tests/ lane running the DST tracer over two replay days (11.0s wall, provisional); extend tests/dst_checks.py with a post-transition clock (finder's own, not built here)",
        "gate_seconds": 91,
    },
    {
        "class": "new: an approval bound to an exact head is re-bought on a diff-identical move",
        "N": 1,
        "rca": False,
        "seams": [
            {"path": "tools/audit/briefs/fix-review.md (re-verification trigger on any head move)", "disposition": "instance", "probe": "yield_rounds.mjs (reused finder harness)", "note": "D13-s1-02"},
        ],
        "barrier_proposal": "none (N<3): rerun re-verification only when the diff against the last-reviewed head is non-empty; policy change needs owner approval",
        "gate_seconds": 1,
    },
    {
        "class": "new: compatibility duplicate entity enabled by default",
        "N": 1,
        "rca": False,
        "seams": [
            {"path": "custom_components/heatpump_optimizer/sensor.py:918-958 (UpperFloorTempSensor)", "disposition": "instance", "probe": "enumerate.py", "note": "D8-s3-03"},
            {"path": "custom_components/heatpump_optimizer/sensor.py:2174 (ContractComparisonSensor)", "disposition": "not applicable", "probe": None, "note": "distinct computed value, regex false positive"},
            {"path": "custom_components/heatpump_optimizer/sensor.py:2329 (MixedHotWaterSensor)", "disposition": "not applicable", "probe": None, "note": "derived transform, not a byte-duplicate, regex false positive"},
        ],
        "barrier_proposal": "none (N<3): lint flagging any sensor whose native_value reads exactly the same coordinator.data key as another entity, with a positive allowlist for intentional duplicates",
        "gate_seconds": 0.01,
    },
    {
        "class": "new: explicit-Euler stability judged per store instead of on the coupled step matrix",
        "N": 1,
        "rca": False,
        "seams": [
            {"path": "custom_components/heatpump_optimizer/thermal_model.py:2419-2470 (_stability_substeps)", "disposition": "instance", "probe": "finder's own m1_stability.py, not re-run", "note": "D2-s1-01; all five bounded stores judged on diagonal ratio only"},
        ],
        "barrier_proposal": "none (N<3): judge the coupled step matrix, or at minimum the valve-throttled buffer<->zone pair",
        "gate_seconds": 0.01,
    },
    {
        "class": "new: learned-correction clamp sized against an assumed range, not the model's curve",
        "N": 1,
        "rca": False,
        "seams": [
            {"path": "custom_components/heatpump_optimizer/flow_lift.py:64,179,221 (FLOW_BIAS_CLAMP_K)", "disposition": "instance", "probe": "finder's own, not re-run", "note": "D2-s2-02"},
        ],
        "barrier_proposal": "none (N<3): derive the clamp from curve_supply_temp's actual range for the configured emitter_design_delta_t",
        "gate_seconds": 0.01,
    },
    {
        "class": "new: missing icons.json services block",
        "N": 1,
        "rca": False,
        "seams": [
            {"path": "custom_components/heatpump_optimizer/services.py (12 registered services)", "disposition": "instance", "probe": "enumerate.py", "note": "D4-s2-08; icons.json has no services key"},
        ],
        "barrier_proposal": "none (N<3): tests/ check asserting every registered service has a matching icons.json[\"services\"] key",
        "gate_seconds": 0.01,
    },
    {
        "class": "new: pointer-only editing with no keyboard route",
        "N": 1,
        "rca": False,
        "seams": [
            {"path": "custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:10266-10270 (setup layout editor)", "disposition": "instance", "probe": "enumerate.py", "note": "D4-s1-04"},
            {"path": "custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:5572 (chart pan gesture)", "disposition": "guarded", "probe": None, "note": "equivalent zoom in/out/reset buttons, keyboard-operable natively"},
            {"path": "custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:8502-8507 (dialog drag surface)", "disposition": "guarded", "probe": None, "note": "own keydown handler at :8507"},
            {"path": "custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:9660-9698 (picker surface)", "disposition": "guarded", "probe": None, "note": "own keydown handler at :9698"},
        ],
        "barrier_proposal": "none (N<3): lint for pointerdown with no keydown AND no adjacent button-wired equivalent (needs the equivalent-control relation taught by hand)",
        "gate_seconds": 0.02,
    },
    {
        "class": "new: selector minimum off its own step grid",
        "N": 1,
        "rca": False,
        "seams": [
            {"path": "custom_components/heatpump_optimizer/config_flow.py (8 box-mode NumberSelector fields at defaults)", "disposition": "instance", "probe": "finder's own step_grid.py (Playwright, not re-run: no browser stack in this box)", "note": "D4-s2-05"},
            {"path": "custom_components/heatpump_optimizer/config_flow.py (4 more once derived values are stored)", "disposition": "instance", "probe": "finder's own step_grid.py", "note": "D4-s2-05"},
            {"path": "custom_components/heatpump_optimizer/config_flow.py (42 slider-mode fields)", "disposition": "not applicable", "probe": None, "note": "sliders render no <input type=number>, stepMismatch cannot apply"},
        ],
        "barrier_proposal": "none (N<3): config_flow._number sets step='any' for box fields, or move each RANGE_* minimum onto its step grid",
        "gate_seconds": 0.01,
    },
    {
        "class": "new: service input without an upper-bound clamp",
        "N": 1,
        "rca": False,
        "seams": [
            {"path": "custom_components/heatpump_optimizer/services.py:867 (handle_apply_manual_plan expires_at)", "disposition": "instance", "probe": "enumerate.py + finder's own manual_plan_expiry.py", "note": "D1-s2-54"},
            {"path": "custom_components/heatpump_optimizer/services.py:86-111 (SERVICE_SCHEMA_SIMULATE_PLAN, 6 unbounded fields)", "disposition": "not applicable", "probe": None, "note": "read-only what-if simulator, no persisted/actuating effect"},
            {"path": "custom_components/heatpump_optimizer/services.py (SET_THERMAL_PARAMS, assign-entity range-bound fields)", "disposition": "guarded", "probe": None, "note": "already vol.Range-clamped"},
        ],
        "barrier_proposal": "none (N<3): clamp expires_at to now + MANUAL_PLAN_WINDOW_HOURS (or the plan horizon)",
        "gate_seconds": 0.02,
    },
    {
        "class": "new: solve-scoped mutation of shared live config seen by a concurrent reader",
        "N": 1,
        "rca": False,
        "seams": [
            {"path": "custom_components/heatpump_optimizer/climate.py:157 / coordinator.py:2495-2498 (target_temperature)", "disposition": "instance", "probe": "not independently reproduced (weakened(low), no mutant harness)", "note": "D1-s3-04"},
        ],
        "barrier_proposal": "none (N<3): publish target_temperature from the same per-cycle coordinator.data snapshot every other entity reads",
        "gate_seconds": 0.02,
    },
    {
        "class": "new: state-blind menu re-offers a completed path",
        "N": 1,
        "rca": False,
        "seams": [
            {"path": "custom_components/heatpump_optimizer/config_flow.py:2473-2493 (async_step_finish_setup)", "disposition": "instance", "probe": "finder's own quick_menu.py/flow_rubric.py, not re-run", "note": "D4-s2-07"},
            {"path": "custom_components/heatpump_optimizer/config_flow.py:~3123-3129 (options-flow 'missed quick setup' menu)", "disposition": "guarded", "probe": None, "note": "conditioned on prior state per its own comment, different code path"},
        ],
        "barrier_proposal": "none (N<3): track whether quick setup already ran and drop that option from the menu",
        "gate_seconds": 0.02,
    },
    {
        "class": "new: text producer takes no language parameter",
        "N": 1,
        "rca": False,
        "seams": [
            {"path": "custom_components/heatpump_optimizer/topology.py:117 (_SLOTS catalog)", "disposition": "instance", "probe": None, "note": "D4-s2-81"},
            {"path": "custom_components/heatpump_optimizer/topology.py:389 (describe_setup)", "disposition": "instance", "probe": None, "note": "D4-s2-81"},
            {"path": "custom_components/heatpump_optimizer/topology.py:538 (render_text_summary)", "disposition": "instance", "probe": None, "note": "D4-s2-81"},
            {"path": "custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js (setup overview/diagram)", "disposition": "instance", "probe": None, "note": "D4-s2-81, same mechanism"},
        ],
        "barrier_proposal": "none (N<3): route _SLOTS labels through strings.json/translations/, thread a language argument through both functions",
        "gate_seconds": 0.02,
    },
    {
        "class": "new: whole-entity availability gated on an optional input",
        "N": 1,
        "rca": False,
        "seams": [
            {"path": "custom_components/heatpump_optimizer/climate.py:122-131 (available)", "disposition": "instance", "probe": None, "note": "D8-s2-01, weakened(medium)"},
            {"path": "custom_components/heatpump_optimizer/button.py:83 (available, optimization_running)", "disposition": "not applicable", "probe": None, "note": "coordinator-state gate, not an optional-input gate"},
            {"path": "custom_components/heatpump_optimizer/button.py:112 (available, system_identification_active)", "disposition": "not applicable", "probe": None, "note": "same, different mechanism"},
        ],
        "barrier_proposal": "none (N<3): drop the whole-entity gate, let current_temperature alone go unknown",
        "gate_seconds": 0.02,
    },
]


def main():
    print(json.dumps({
        "_note": "Round 9 D14 class sweep, thread S7, baseline 1936d5ca. Commit and per-class N/rca reported to the orchestrator alongside this file.",
        "classes": CLASSES,
    }, indent=2))


if __name__ == "__main__":
    main()
