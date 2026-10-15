"""Finding JSON for round 10's extra seats whose returns were not schema-shaped
(orchestrator decision of 2026-10-15): ARCH-s2 (its JSON lacks most evidence
fields) and the two study branches (prose reports, no JSON).

Mechanical extraction only. ARCH-s2's fields are mapped from its own JSON
(command, result -> value, the harness named in its command). The study fields
are copied from the seats' report text, which reached the orchestrator as the
seats' replies; the study texts carry figures from the owner's install, so
only test-house / synthetic figures are copied and the rest is cited by commit
(study/r10-identifiability @ 4f2d513c9, study/r10-reseed @ 2c42ba4a0).
A required field the source does not state is NOT filled: it is listed in the
finding's `missing_in_source`, and intake rejects the finding naming it.

Usage: python3 dev/audit/rounds/round10/intake/extras_r10.py <arch-s2.json> <out_dir>
writes <out_dir>/ARCH-s2.json, STUDY-ident.json, STUDY-reseed.json.
"""
import json
import os
import re
import sys

ARCH2_DIR = "dev/audit/rounds/round10/D7/arch-s2/"


def arch_s2(src):
    rep = json.load(open(src))
    out = []
    for f in rep["findings"]:
        ev0 = f.get("evidence", {})
        cmd = ev0.get("command", "")
        m = re.search(r"(dev/audit/rounds/round10/D7/arch-s2/\S+?\.(?:py|sh))", cmd) or \
            re.search(r"\b([a-z_]+\.(?:py|sh))\b", cmd)
        hp = m.group(1) if m else None
        if hp and not hp.startswith("dev/"):
            hp = ARCH2_DIR + hp
        p0 = f.get("perturbation", {})
        g = dict(f)
        g["scope"] = None  # set from the re-keyed id by intake
        g["evidence"] = {"command": cmd, "harness_path": hp, "value": ev0.get("result"),
                         "baseline_sha": rep.get("baseline_sha")}
        g["perturbation"] = {"change": p0.get("change"), "expected_direction": p0.get("expect")}
        g["missing_in_source"] = ["evidence.unit", "evidence.machine", "evidence.cpu_or_wall",
                                  "evidence.contention_note", "evidence.tolerance", "evidence.load1",
                                  "evidence.thread_factor"]
        out.append({k: v for k, v in g.items() if v is not None})
    return {"dimension": "D7", "baseline_sha": rep.get("baseline_sha"), "findings": out}


def ev(**kw):
    return {k: v for k, v in kw.items() if v is not None}


STUDY_IDENT = {"dimension": "D2", "baseline_sha": "a77faf30d", "findings": [
    {"id": "R10-ID-01", "step": "D2.M5", "severity": "medium", "stop_rule_class": "bug", "class_guess": "new",
     "title": "Heat-loss learners absorb solar-model error: UA bias +0.094 to +0.254 per unit aperture error over 6 plants",
     "claim": "the heat-loss learners absorb solar-model error.",
     "instrumented_symbol": "coordinator:HeatPumpOptimizerCoordinator._async_learn_house_heat_loss and _async_learn_lower_floor_loss",
     "metric_definition": "effective house UA / truth - 1, mean of the last 7 of 42 days.",
     "evidence": ev(command="dev/audit/rounds/round10/study-ident/run_q1.sh OUTDIR; python3 dev/audit/rounds/round10/study-ident/collect_q1.py OUTDIR",
                    harness_path="dev/audit/rounds/round10/study-ident/ident_rolling.py",
                    value="slope +0.094 to +0.254 per unit aperture error over 6 plants; leave-one-out +0.161 to +0.254",
                    unit="relative UA error per unit relative aperture error", baseline_sha="a77faf30d",
                    cpu_or_wall="ratio", thread_factor=1.0),
     "null_control": {"command": "flat irradiance arm of run_q1.sh", "value": "spread 0.0000"},
     "perturbation": {"change": "night-only folding", "expected_direction": "down", "observed_value": "spread <= 0.0001"},
     "phenomenon_property": "a learner must not fold a residual containing an unmodelled regressor whose mean is not zero",
     "seam_rule": "grep -n \"_replay_interval(\" custom_components/heatpump_optimizer/coordinator.py",
     "files": ["custom_components/heatpump_optimizer/coordinator.py"],
     "proposed_fix_scope": "G-ID-1: heat-loss learners fold night intervals only (coordinator.py, const.py)",
     "missing_in_source": ["evidence.machine", "evidence.contention_note", "evidence.tolerance", "evidence.load1"]},
    {"id": "R10-ID-02", "step": "D2.M5", "severity": "high", "stop_rule_class": "bug", "class_guess": "new",
     "title": "Open-window detector trips on model bias and freezes every learner: 15-19 % of intervals at delivery 0.4, 0 at 1.0",
     "claim": "the open-window detector trips on model bias and freezes every learner, including the ones that would remove the bias.",
     "instrumented_symbol": "_vent_cusum.update, reached through _async_learn_house_heat_loss",
     "metric_definition": "share of intervals tripped.",
     "evidence": ev(command="dev/audit/rounds/round10/study-ident/run_q1.sh OUTDIR",
                    harness_path="dev/audit/rounds/round10/study-ident/ident_rolling.py",
                    value="15-19 % tripped at delivery 0.4, 0 % at 1.0 (windows closed); owner install figure cited by commit 4f2d513c9",
                    unit="share of intervals", baseline_sha="a77faf30d", cpu_or_wall="ratio", thread_factor=1.0),
     "null_control": {"command": "--delivery 1.0", "value": "0.000 on 6 plants"},
     "perturbation": {"change": "--delivery 1.0", "expected_direction": "to_zero"},
     "files": ["custom_components/heatpump_optimizer/coordinator.py"],
     "proposed_fix_scope": "G-ID-2: ventilation detector distinguishes bias from an open window",
     "missing_in_source": ["phenomenon_property", "seam_rule", "evidence.machine", "evidence.contention_note",
                           "evidence.tolerance", "evidence.load1"]}]}

RESEED_EV = dict(baseline_sha="17f1c55fa", machine="macOS arm64, Python 3.11", thread_factor=1.0,
                 contention_note="load1 18-35; no figure depends on timing", cpu_or_wall="ratio")
STUDY_RESEED = {"dimension": "D2", "baseline_sha": "17f1c55fa", "findings": [
    {"id": "D-1", "step": "D2.M1", "stop_rule_class": "bug", "class_guess": "new",
     "title": "_space_demand_kw uses lower_floor_heat_loss without the learned ratio: 43.7 % low on the test house; feeds the wood detector",
     "claim": "HeatPumpOptimizerCoordinator._space_demand_kw uses lower_floor_heat_loss without the learned ratio.",
     "instrumented_symbol": "coordinator:HeatPumpOptimizerCoordinator._space_demand_kw",
     "evidence": ev(command="PYTHONPATH=tests/hastub python3 tools/audit/round10/study-reseed/reparam_sites.py",
                    value="43.7 % low on the test house (owner install figure cited by commit 2c42ba4a0)", **RESEED_EV),
     "perturbation": {"change": "--ratio 1.0", "expected_direction": "to_zero"},
     "null_control": {"command": "reparam_sites.py --ratio 1.0", "value": "0"},
     "files": ["custom_components/heatpump_optimizer/coordinator.py"],
     "proposed_fix_scope": "G1: use lower_floor_heat_loss_learned in _space_demand_kw",
     "missing_in_source": ["severity", "metric_definition", "phenomenon_property", "seam_rule",
                           "evidence.harness_path (tools/audit/round10/study-reseed/ is outside the schema's harness_path pattern)",
                           "evidence.unit", "evidence.tolerance", "evidence.load1 (range only)"]},
    {"id": "D-2", "step": "D2.M5", "stop_rule_class": "bug", "class_guess": "new",
     "title": "sysid _zone_heat_loss and adoption_decision omit the lower-floor ratio: a perfect experiment adopts 43.7 % high (test house)",
     "claim": "sysid._zone_heat_loss and adoption_decision leave out the lower-floor ratio.",
     "instrumented_symbol": "sysid:_zone_heat_loss, sysid:adoption_decision",
     "evidence": ev(command="PYTHONPATH=tests/hastub python3 tools/audit/round10/study-reseed/reparam_sites.py",
                    value="a perfect experiment adopted 43.7 % too high on the test house (owner figure cited by commit 2c42ba4a0)", **RESEED_EV),
     "perturbation": {"change": "--ratio 1.0", "expected_direction": "to_zero"},
     "null_control": {"command": "reparam_sites.py --ratio 1.0", "value": "0"},
     "files": ["custom_components/heatpump_optimizer/sysid.py"],
     "proposed_fix_scope": "G1: use lower_floor_heat_loss_learned in sysid._zone_heat_loss and adoption_decision",
     "missing_in_source": ["severity", "metric_definition", "phenomenon_property", "seam_rule",
                           "evidence.harness_path (outside the schema's pattern)", "evidence.unit",
                           "evidence.tolerance", "evidence.load1 (range only)"]},
    {"id": "D-3", "step": "D12.M2", "stop_rule_class": "bug", "class_guess": "new",
     "title": "Lower-floor ratio has no anchor: an options edit of the lower-floor nameplate double-applies it, total kept, zone split wrong",
     "claim": "the lower-floor ratio has no anchor, so changing the lower-floor nameplate through options double-applies it.",
     "instrumented_symbol": "coordinator:_apply_learner_payloads, _async_load_thermal_learning",
     "evidence": ev(command="PYTHONPATH=tests/hastub python3 tools/audit/round10/study-reseed/reparam_sites.py",
                    value="per-zone heat loss after reload: upper -36.8 %, lower +21.5 %; total within 0.1 % (figures cited by commit 2c42ba4a0)", **RESEED_EV),
     "perturbation": {"change": "--ratio 1.0", "expected_direction": "to_zero"},
     "files": ["custom_components/heatpump_optimizer/coordinator.py", "custom_components/heatpump_optimizer/store.py"],
     "proposed_fix_scope": "G2: store a lower_floor_loss_anchor and extend the re-anchor law to the ratio",
     "missing_in_source": ["severity", "metric_definition", "phenomenon_property", "seam_rule",
                           "evidence.harness_path (outside the schema's pattern)", "evidence.unit",
                           "evidence.tolerance", "evidence.load1 (range only)"]}]}


def main():
    src, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    json.dump(arch_s2(src), open(os.path.join(out, "ARCH-s2.json"), "w"), indent=2)
    json.dump(STUDY_IDENT, open(os.path.join(out, "STUDY-ident.json"), "w"), indent=2)
    json.dump(STUDY_RESEED, open(os.path.join(out, "STUDY-reseed.json"), "w"), indent=2)
    print(f"wrote ARCH-s2.json, STUDY-ident.json, STUDY-reseed.json into {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
