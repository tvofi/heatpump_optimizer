#!/usr/bin/env python3
"""Fold the judged D3 wave (handoff/audit-r11-judge-D3 at a826f55f8c) into the round-11 roster.

    python3 -I build_d3_fold.py --judge JUDGE.json --roster LIVE_ROSTER.json \
        --out-roster wave-r11-groups.json --out-fold D3-FOLD.json [--per-finding-carries] [--bug-only]

Run from a checkout that has the wave baseline as a git object.
Every survivor is assigned to the seam that owns its enclosing function at the
baseline (SEAM_OF_FILE and COORDINATOR below: the plan's component view, one
owner per concern). A seam with a roster group not yet dispatched folds into it
as carries, one per enclosing function; a seam with none gets one tests-only
group. --per-finding-carries prices every pin as one carry (the count-priced
projection); --bug-only keeps high and medium survivors and defers the rest
(option B of CHANGES-R5.md).
"""
from __future__ import annotations

import argparse
import ast
import collections
import copy
import json
import subprocess

BASE = "92d38ecb640bd462f2e19c0814d0f0b7df1ee692"
JUDGE_SHA = "a826f55f8c"
# the commit that carries d3_fnstate.py, D3-FOLD.json and ADR-011, for a brief to cite before the plan lands on main
PLAN_SHA = "3222bb016d"
PKG = "custom_components/heatpump_optimizer/"
SEAM_OF_FILE = {"optimizer.py": "solver", "dhw_planner.py": "solver", "sysid.py": "sysid",
                "thermal_model.py": "plant", "defrost.py": "plant", "flow_lift.py": "plant",
                "price_model.py": "money", "tariff.py": "money", "grid_fee.py": "money"}
COORDINATOR = {
    "actuation": "_async_drive_pumps _check_pump_mode_expired _command_frequency _command_valve_target "
                 "_guard_floor_hold _immersion_dhw_margin _max_pump_rise _external_heat_override "
                 "async_shutdown _outage_recovery_active _open_loop_plan_value",
    "fabric": "_apply_learner_payloads _async_learn_buffer_cooling _async_learn_house_heat_loss "
              "_async_watch_learning_drift _fold_capacity_envelope _fold_internal_gains _fold_solar_aperture "
              "_fold_flow_lift _observe_cop_health _record_quiet_comfort_period _run_system_identification "
              "_settle_defrost _track_curve_comfort _update_external_heat_detection _confidence_margins "
              "_file_lead_predictions _external_heat_config _interval_space_power _on_power_event",
    "inputs": "_apply_open_meteo _entity_state _fetch_weather_forecast _forecast_arrays _pv_forecast "
              "_pv_measured_production _update_current_state _weather_fetch_failed _weather_fetch_recovered "
              "_plausible_forecast_rows _price_entity_state _outage_reading _dhw_inlet_c _liquid_fraction "
              "_update_snow_memory",
    "cycle": "async_run_optimization async_simulate _capacity_caps _power_headroom _maybe_run_fuse_advisor "
             "_warm_seeded _build_data_dict _build_plan_views _narrative_view _thermal_view _mixing_valve_view "
             "_contract_comparison _close_score_day _accumulate_energy async_diagnose_interval _dhw_setpoint_sweep",
    "store": "_async_load_energy_totals _learned_pair _storable_sample_count",
}
CO_FN = {f: s for s, v in COORDINATOR.items() for f in v.split()}
# seam -> (group, new?, unused, after-edges added, seam label, production files read); the size is size_for()
PLAN = {
    "solver": ("R11-D3-PINS-solver", True, "XL", ["R11-OUTSIDE-START-APPROACH", "R11-SEAM-cycle-reporting"],
               "solver", ["optimizer.py", "dhw_planner.py"]),
    "sysid": ("R11-D3-PINS-sysid", True, "L", ["R11-SEAM-learners"], "learners", ["sysid.py"]),
    "fabric": ("R11-D3-PINS-fabric", True, "L",
               ["R11-ARCH-fabric-learner", "R11-SEAM-cycle-reporting", "R11-OUTSIDE-START-APPROACH"],
               "learners", ["coordinator.py"]),
    "plant": ("R11-D3-PINS-plant", True, "L", [], "plant model", ["thermal_model.py", "defrost.py", "flow_lift.py"]),
    "money": ("R11-D3-PINS-money", True, "L", [], "money", ["price_model.py", "tariff.py", "grid_fee.py"]),
    "actuation": ("R11-D3-PINS-actuation", True, "M", ["R11-SEAM-actuation-writes", "R11-OWNER-FAULT-HOLD"],
                  "actuation", ["coordinator.py"]),
    # Not folded into R11-SEAM-inputs-freshness (not started, same seam): that group holds a coordinator
    # slot ahead of R11-SEAM-cycle-solve on the binding chain, and the fold moved closure (CHANGES-R5.md).
    "inputs": ("R11-D3-PINS-inputs", True, "M", [], "input boundary", ["coordinator.py"]),
    "cycle": ("R11-SEAM-cycle-reporting-p2", False, "M", ["R11-SEAM-actuation-writes", "R11-SEAM-learners"],
              None, None),
    "store": ("R11-SEAM-store-p2", False, None, [], None, None),
}
PIN_FILES = ["tests/guard_pins.py", "tests/mutation_ledger/"]
SIZE_ORDER = ["S", "M", "L", "XL"]


def size_for(pins: int) -> str:
    """One rule for every group and both options: pins per pull request."""
    return "S" if pins <= 12 else "M" if pins <= 30 else "L" if pins <= 70 else "XL"
TESTS_GROUP = "R11-SEAM-tests"
_src: dict = {}


def spans(name: str):
    if name not in _src:
        text = subprocess.run(["git", "show", f"{BASE}:{PKG}{name}"], capture_output=True, text=True,
                              check=True).stdout
        out = []

        def walk(node, pre):
            for c in ast.iter_child_nodes(node):
                if isinstance(c, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    out.append((c.lineno, c.end_lineno, pre + c.name))
                    walk(c, pre + c.name + ".")
                else:
                    walk(c, pre)
        walk(ast.parse(text), "")
        _src[name] = out
    return _src[name]


def enclosing(name: str, line: int) -> str:
    best = None
    for a, b, q in spans(name):
        if a <= line <= b and (best is None or a >= best[0]):
            best = (a, q)
    return best[1] if best else "<module>"


def seam_of(v: dict, fn: str) -> str:
    name = v["site"].split(":")[0]
    if name != "coordinator.py":
        return SEAM_OF_FILE[name]
    leaf = fn.split(".")[-1]
    if leaf == "<module>":
        return "cycle" if ("SOLVE_FAILURE" in v["title"] or "WORKER_FALLBACK" in v["title"]) else "fabric"
    return CO_FN[leaf]


BRIEF = (
    "Tests-only pins for the {seam} seam: {n} production mutants the full gate did not kill (class I1, issue #3755), "
    "judged in dev/audit/rounds/round11/D3/wave-judge/JUDGE.json at {sha}; the ids are this group's findings. "
    "No production file is edited; the seam's production files ({reads}) are read. Each pin goes beside the seam's existing "
    "checks or in tests/guard_pins.py, with one row per mutant under tests/mutation_ledger/. "
    "Per finding, in this order. (1) Re-derive: the wave's lines are at its baseline 92d38ecb64; "
    "dev/audit/rounds/round11/PLAN/d3_fnstate.py, run on dev/audit/rounds/round11/PLAN/D3-FOLD.json (both at {plan}), "
    "prints which enclosing functions differ at your merge base, and a "
    "finding in one is re-located by its patch text, never by its line. (2) Apply the finding's one-line patch and "
    "run the judge's probe: a number that no longer moves, or a check that already fails under the patch, is a "
    "non-finding at your base; list it for the judge and write no pin. (3) Failing test first: the pin fails under "
    "the patch and passes without it, both runs in the body. A pin asserts the behaviour the probe measured through "
    "the production entry point and never re-states the production expression (tests/README.md). "
    "High and medium survivors are built before low ones. A pin that cannot pass on the unpatched tree has found a "
    "production defect: stop, and carry it to the seam's owning group; it is not fixed here. "
    "A kill is claimed from the pin under the patch on Linux CI; the wave's survivor claim rests on gate logs "
    "compared with a red null, and its re-take is a carry of R11-SEAM-tests that this group does not wait for. "
    "Pin home and proof are fixed by dev/audit/rounds/round11/PLAN/ADR-011-survivor-pins.md (at {plan}): no "
    "design is owed. tests/guard_pins.py is a hot file: an open pull request that touches it lands first and this "
    "group rebases. {edges}"
)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--judge", required=True)
    ap.add_argument("--roster", required=True)
    ap.add_argument("--out-roster", required=True)
    ap.add_argument("--out-fold", required=True)
    ap.add_argument("--per-finding-carries", action="store_true")
    ap.add_argument("--bug-only", action="store_true")
    a = ap.parse_args()
    verdicts = json.load(open(a.judge))["verdicts"]
    roster = json.load(open(a.roster))
    by_name = {g["group"]: g for g in roster["groups"]}
    template = by_name["R11-SEAM-store-p2"]
    fold = {"judge": JUDGE_SHA, "baseline": BASE, "groups": {}, "merged": {}, "refused": {}, "deferred": {},
            "carries": {}}
    per: dict = collections.defaultdict(list)
    for v in verdicts:
        name, line = v["site"].split(":")
        fn = enclosing(name, int(line))
        if v["verdict"] == "merged":
            fold["merged"][v["id"]] = v["into"]
            continue
        if v["verdict"] == "unreproduced":
            fold["refused"][v["id"]] = ("unreproduced by the judge on arm64; Linux x86 re-take owed "
                                        "(R11-D3-JUDGE-LINUX, a carry of R11-SEAM-tests)")
            continue
        row = {"id": v["id"], "file": name, "fn": fn, "severity": v["severity"], "gap_kind": v["gap_kind"],
               "box": v["box"], "patch": v["patch"]}
        if a.bug_only and v["severity"] not in ("high", "medium"):
            fold["deferred"][v["id"]] = "round 12: hygiene survivor (low or nit), option B"
            continue
        per[seam_of(v, fn)].append(row)
    for seam, rows in sorted(per.items()):
        group, new, _, after, label, prod = PLAN[seam]
        size = size_for(len(rows))
        if not new:
            was = by_name[group].get("size") or "S"
            size = max(was, size, key=SIZE_ORDER.index)
        sev = collections.Counter(r["severity"] for r in rows)
        ids = [r["id"] for r in rows]
        fns: dict = collections.defaultdict(list)
        for r in rows:
            fns[(r["file"], r["fn"].split(".")[-1])].append(r)
        fold["groups"][group] = {"seam": seam, "new": new, "size": size, "after_added": after, "count": len(rows),
                                 "severity": dict(sev), "findings": rows}
        if new:
            g = copy.deepcopy(template)
            g.update({
                "group": group, "severity": "high" if sev["high"] else "medium", "size": size, "issues": [3755],
                "findings": ids, "classes": ["I1"], "seam": label, "after": after, "carry": [],
                "hot_files": ["guard_pins.py", "features.py", "closures.json"],
                "files": list(PIN_FILES), "reads": [PKG + p for p in prod],
                "architect_note": f"D3 wave fold (plan revision 5): the {label} seam owns these {len(rows)} "
                                  "survivors; its register group is merged or in review, so the pins are one "
                                  "tests-only group.",
                "brief": BRIEF.format(seam=label, n=len(rows), sha=JUDGE_SHA, reads=", ".join(PKG + p for p in prod), plan=PLAN_SHA,
                                      edges=("After: " + ", ".join(after) + ", each of which rewrites a function "
                                             "pinned here." if after else "No edge: no open pull request changes a "
                                             "function pinned here.")),
                "resume": {"stage": "not-started", "branch": "handoff/" + group.lower(), "commit": None,
                           "last_step": "plan revision 5 (D3 wave fold) drafted on handoff/plan-r11-d3-amend",
                           "next_step": "plan review, then the owner; dispatch per the edges"},
            })
            if a.per_finding_carries:
                g["carry"] = [f"pin {i}" for i in range(len(rows))]
            roster["groups"].append(g)
            by_name[group] = g
        else:
            g = by_name[group]
            g["findings"] = list(g.get("findings") or []) + ids
            if "I1" not in g.setdefault("classes", []):
                g["classes"].append("I1")
            g["size"] = size
            g["after"] = list(g.get("after") or []) + [e for e in after if e not in (g.get("after") or [])]
            g["files"] = list(g.get("files") or []) + [f for f in PIN_FILES if f not in (g.get("files") or [])]
            carries = []
            for (name, leaf), rs in sorted(fns.items()):
                c = collections.Counter(r["severity"] for r in rs)
                where = f"{leaf} in {name}" if leaf != "<module>" else f"the module constants of {name}"
                text = (
                    "D3 wave fold (plan revision 5, judge record dev/audit/rounds/round11/D3/wave-judge/JUDGE.json "
                    f"at {JUDGE_SHA}): tests-only pins for {where}, survivors by severity "
                    + ", ".join(f"{k} {c[k]}" for k in ("high", "medium", "low", "nit") if c[k])
                    + "; ids in this group's findings, boxes " + " ".join(sorted({r["box"] for r in rs}))
                    + ". Class I1 (#3755). Re-derive at your merge base with "
                      f"dev/audit/rounds/round11/PLAN/d3_fnstate.py on dev/audit/rounds/round11/PLAN/D3-FOLD.json "
                      f"(both at {PLAN_SHA}), apply the one-line patch, pin failing first; "
                      "a patch an existing check already kills is a non-finding for the judge, not a pin.")
                carries += [text] * (len(rs) if a.per_finding_carries else 1)
            g["carry"] = list(g.get("carry") or []) + carries
            fold["carries"][group] = len(carries)
    t = by_name[TESTS_GROUP]
    strata = sorted({(v["site"].split(":")[0], v["gap_kind"]) for v in verdicts
                     if v["verdict"] in ("verified", "weakened")})
    extra = [
        "R11-D3-JUDGE-GATE (judge record dev/audit/rounds/round11/D3/wave-judge/JUDGE.md at " + JUDGE_SHA + "): the "
        "D3 wave's survivor claim compares each mutant's gate log with a null that was red on its box, so a mutant "
        "killed only by an already-red check reads as a survivor. Re-take on a quiet Linux box, on a tree whose "
        "null gate is green: one key per production file and gap kind present in the record (the first key of each "
        "in the record's order), the full gate per key. A key the green-null gate kills is a non-finding returned to the judge, and its stratum's "
        "other keys are then re-taken too. Run as a cloud box, never on the shared host. The R11-D3-PINS groups "
        "do not wait for it: each claims its kills from its own pin under the patch.",
        "R11-D3-JUDGE-LINUX (same record at " + JUDGE_SHA + "): three sysid.py exact-float boundary findings are "
        "unreproduced on arm64, where no input lands on the boundary. Re-run their probes on Linux x86 in the same "
        "box as the gate re-take; one that moves goes to R11-D3-PINS-sysid as a carry, one that does not is closed "
        "as void.",
        "Class I1 (#3755), D3 wave: the judge adds the wave's survivors as I1 instances, counted per group in "
        "dev/audit/rounds/round11/PLAN/D3-FOLD.json at " + PLAN_SHA + ". The class's root-cause analysis under "
        "dev/governance/rules/defect-root-cause.md is owed by a root-cause seat beside these groups, never inside "
        "them; this group owns the class issue and records the analysis path on it. The sweep for each "
        "R11-D3-PINS group is the wave's own keys for its seam, re-run after its merge.",
    ]
    t["carry"] = list(t.get("carry") or []) + extra
    fold["carries"][TESTS_GROUP] = len(extra)
    fold["strata"] = len(strata)
    fold["totals"] = {"judged": len(verdicts), "placed": sum(g["count"] for g in fold["groups"].values()),
                      "merged": len(fold["merged"]), "refused": len(fold["refused"]),
                      "deferred": len(fold["deferred"])}
    json.dump(roster, open(a.out_roster, "w"), indent=1)
    if a.out_fold != "/dev/null":
        json.dump(fold, open(a.out_fold, "w"), indent=1)
    print(json.dumps(fold["totals"]), {k: (v["count"], v["size"]) for k, v in fold["groups"].items()})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
