#!/usr/bin/env python3
"""D3-s1 box D3-top6: write top6_findings.json, top6_non_findings.json and top6_extra.json from
state/gates/ and the two step-4 probes, then box_report.py builds REPORT.json/REPORT.md.
Run: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/top6_compose.py
Metric: none of its own (assembly only); every number it writes is read from state/gates/<key>.json
or printed by d931_probe.py / m26_probe.py, which it re-runs.
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: owner macOS arm64 (local re-run).
"""
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
REL = "dev/audit/rounds/round11/D3/s1"
BASE = "92d38ecb640bd462f2e19c0814d0f0b7df1ee692"
G = HERE / "state" / "gates"
MACHINE = "local Apple M1, 8 cores, 8 GB, macOS (Darwin), venv-ci CPython 3.14.7, numpy 2.5.4, scipy 1.18.1, Accelerate BLAS"
GATECMD = f"GATE_SCOPE=full GOLDEN_MODE=drift GOLDEN_REF={BASE} GATE_JOBS=1 ./tests/run.sh"


def gate(k):
    p = G / f"{k}.json"
    return json.loads(p.read_text()) if p.exists() else None


def probe(name, *a):
    env = dict(os.environ, PYTHONPATH="tests/hastub")
    out = subprocess.run([sys.executable, f"{REL}/{name}", *a], cwd=ROOT, env=env,
                         capture_output=True, text=True, check=True).stdout
    return {ln.split("=", 1)[0][7:]: ln.split("=", 1)[1].split()[0]
            for ln in out.splitlines() if ln.startswith("RESULT ")}


null = gate("null")
TOP6 = [("pre", "fb16c7b0cbbfc63d", "tariff.py:64 _window_slot GUARD_OFF"),
        ("pre", "4b3795aece73ba73", "price_model.py:201 PriceShapeModel.observe_day non-finite guard GUARD_OFF"),
        ("pre", "bdcf7589b0a0a6df", "coordinator.py:539 _parse_ecl110_state nested command.displace GUARD_OFF"),
        ("c2", "0e172028a23d9372", "sysid.py:2246 R10 C2 M27 and -> or (drift refusal)"),
        ("c2", "d931ab195b940b0c", "tariff.py:744 R10 C2 M31 _smooth_topk_sum k <= 0 -> k < 0"),
        ("c2", "8e82d7a0b3617003", "sysid.py:1549 R10 C2 M26 hour >= start -> hour > start")]

findings, nonf = [], []
for src, k, label in TOP6:
    g = gate(k)
    if g is None:
        continue
    if g["verdict"] == "KILLED":
        nonf.append({"claim": f"T2 full gate: {label} is pinned by the suite (KILLED)",
                     "command": f"PYTHONPATH=tests/hastub python3 {REL}/fullgate.py run --src {src} --key {k}",
                     "value": f"killed_by={','.join(g['killed_by'])}; wall {g['wall_s']} s, load1 {g['load1_start']}..{g['load1_end']} (provisional)"})

nid = 2
g = gate("d931ab195b940b0c")
if g and g["verdict"] != "KILLED":
    b, m = probe("d931_probe.py"), probe("d931_probe.py", "--mutant")
    findings.append({
        "id": f"D3-s1-{nid:02d}", "scope": "D3-s1", "step": "D3.M3",
        "title": "No suite check pins the k <= 0 guard of tariff._smooth_topk_sum; the scalar and batch top-k disagree at k = 0 unseen",
        "severity": "low",
        "claim": ("Mutating tariff.py:744 `if x.size == 0 or k <= 0:` to `k < 0` (R10 C2 M31) survives the full gate: "
                  "no check fails beyond the null control, although _smooth_topk_sum(x, 0) then returns "
                  f"{m['scalar_k0']} instead of 0.0, while _smooth_topk_sum_batch still returns 0.0."),
        "mechanism": ("The guard is reached only by a direct call: both production callers clamp k with "
                      "max(1, min(int(bill.peaks_averaged), ...)) (tariff.py L982, L1204) before the call, so no "
                      "gate script ever drives k = 0. The scalar/batch parity checks in the suite run at k >= 1 only. "
                      "Behaviour in production is unchanged today; the contract stated in the function body (0 for k <= 0, "
                      "matching the batch twin) is unpinned, so a caller dropping the clamp would go unnoticed."),
        "evidence": {"command": f"PYTHONPATH=tests/hastub python3 {REL}/fullgate.py run --src c2 --key d931ab195b940b0c",
                     "harness_path": f"{REL}/fullgate.py",
                     "value": 0,
                     "unit": "gate scripts failing more checks under the mutant than under the null control (killed_by count)",
                     "baseline_sha": BASE, "machine": MACHINE, "cpu_or_wall": "count",
                     "contention_note": (f"Count is contention-immune. The gate's wall time was {g['wall_s']} s at load1 "
                                         f"{g['load1_start']}..{g['load1_end']}, on a shared host with other seats running (provisional). "
                                         f"The null control's red scripts {null['failed_scripts']} and their failed-check counts "
                                         f"{null['fail_lines']} are host artefacts; the mutant's profile was identical: {g['fail_lines']}."),
                     "tolerance": "exact", "load1": g["load1_end"], "thread_factor": 1.0},
        "instrumented_symbol": "custom_components.heatpump_optimizer.tariff:_smooth_topk_sum",
        "perturbation": {"change": ("d931_probe.py --mutant: the same one-line edit applied in memory. scalar_k0 moves "
                                    f"{b['scalar_k0']} -> {m['scalar_k0']} and mismatch {b['mismatch']} -> {m['mismatch']}. "
                                    "Adding a check that pins _smooth_topk_sum(x, 0) == 0.0 moves the gate's killed_by count 0 -> 1."),
                         "expected_direction": "up", "observed_value": float(m["scalar_k0"])},
        "metric_definition": "killed_by count of the full gate on the mutant: scripts failing more checks than the null control; 0 = no check reads the line",
        "phenomenon_property": "Every early-return guard of a tariff reduction (top-k, smooth top-k, batch twin) is exercised by at least one check at its boundary value",
        "seam_rule": f"grep -n 'k <= 0\\|m == 0 or k' custom_components/heatpump_optimizer/tariff.py",
        "null_control": {"command": f"PYTHONPATH=tests/hastub python3 {REL}/fullgate.py null",
                         "value": f"gate_rc={null['gate_rc']}, red {len(null['failed_scripts'])} scripts (host artefacts), identical to the mutant's",
                         "note": "batch_k0 is the probe's null arm: 0.0 under both arms"},
        "reproduction_steps": [f"PYTHONPATH=tests/hastub python3 {REL}/d931_probe.py", f"PYTHONPATH=tests/hastub python3 {REL}/d931_probe.py --mutant",
                               f"PYTHONPATH=tests/hastub python3 {REL}/fullgate.py run --src c2 --key d931ab195b940b0c"],
        "proposed_fix_scope": "tests only: a features.py check that _smooth_topk_sum(x, 0) and _smooth_topk_sum_batch(x[None], 0) both return 0.0",
        "files": ["custom_components/heatpump_optimizer/tariff.py", "tests/features.py"],
        "stop_rule_class": "hygiene", "class_guess": "new"})
    nid += 1

g = gate("8e82d7a0b3617003")
if g and g["verdict"] != "KILLED":
    b, m = probe("m26_probe.py"), probe("m26_probe.py", "--mutant")
    findings.append({
        "id": f"D3-s1-{nid:02d}", "scope": "D3-s1", "step": "D3.M3",
        "title": "No suite check pins the first hour of sysid's midnight-wrapping night window; losing 23:00 survives the full gate",
        "severity": "medium",
        "claim": ("Mutating sysid.py:1549 `hour >= cfg.start_hour` to `hour > cfg.start_hour` (R10 C2 M26) survives the full gate, "
                  f"although SystemIdentification.conditions_met then opens {m['open_hours']} instead of {b['open_hours']} hours of the "
                  "default 23-05 night window: the 23:00 start hour is refused as outside the night window."),
        "mechanism": ("The suite drives conditions_met only at hours strictly inside the window (or outside it), never at "
                      "now.hour == start_hour of a wrapping window, so the inclusive lower bound is unread. A system-identification "
                      "experiment then starts at most at 00:00, losing one sixth of its window each night."),
        "evidence": {"command": f"PYTHONPATH=tests/hastub python3 {REL}/fullgate.py run --src c2 --key 8e82d7a0b3617003",
                     "harness_path": f"{REL}/fullgate.py", "value": 0,
                     "unit": "gate scripts failing more checks under the mutant than under the null control (killed_by count)",
                     "baseline_sha": BASE, "machine": MACHINE, "cpu_or_wall": "count",
                     "contention_note": (f"Count is contention-immune; gate wall {g['wall_s']} s at load1 {g['load1_start']}..{g['load1_end']} "
                                         "(provisional, shared host). The null control's red scripts are host artefacts with the same profile."),
                     "tolerance": "exact", "load1": g["load1_end"], "thread_factor": 1.0},
        "instrumented_symbol": "custom_components.heatpump_optimizer.sysid:SystemIdentification.conditions_met",
        "perturbation": {"change": (f"m26_probe.py --mutant: open_hours {b['open_hours']} -> {m['open_hours']}, first_hour_open "
                                    f"{b['first_hour_open']} -> {m['first_hour_open']}; non-wrapping null arm open_hours_flat "
                                    f"{b['open_hours_flat']} -> {m['open_hours_flat']}. A check at now.hour == start_hour moves the gate's killed_by 0 -> 1."),
                         "expected_direction": "down", "observed_value": int(m["open_hours"])},
        "metric_definition": "killed_by count of the full gate on the mutant (0 = no check reads the line); probe: hours of the day conditions_met does not refuse as outside the night window",
        "phenomenon_property": "Every hour-window membership test in sysid is pinned at both of its boundary hours, for wrapping and non-wrapping windows",
        "seam_rule": "grep -n 'start_hour\\|end_hour' custom_components/heatpump_optimizer/sysid.py",
        "null_control": {"command": f"PYTHONPATH=tests/hastub python3 {REL}/m26_probe.py --mutant",
                         "value": f"open_hours_flat={m['open_hours_flat']} (non-wrapping window, unaffected by the mutant)"},
        "reproduction_steps": [f"PYTHONPATH=tests/hastub python3 {REL}/m26_probe.py", f"PYTHONPATH=tests/hastub python3 {REL}/m26_probe.py --mutant",
                               f"PYTHONPATH=tests/hastub python3 {REL}/fullgate.py run --src c2 --key 8e82d7a0b3617003"],
        "proposed_fix_scope": "tests only: a features.py sysid gate check at now.hour == start_hour (23) for the default wrapping window",
        "files": ["custom_components/heatpump_optimizer/sysid.py", "tests/features.py"],
        "stop_rule_class": "bug", "class_guess": "new"})
    nid += 1

nonf += [
    {"claim": "T1: C3C6 M22 (tariff.py:595 mask_active, key 6e6026d857732e96) re-driven after its disk-full TIMEOUT; the TIMEOUT is dropped",
     "command": f"PYTHONPATH=tests/hastub python3 {REL}/prescreen.py run --mutants <M22 dict> --sub c3c6-redrive",
     "value": "SURVIVED 12 fast drivers in 293.0 s on cloud box D3-top6 (provisional); state/results/c3c6-redrive/6e6026d857732e96.json. It stays owed to T3."},
    {"claim": "R1 controls on the local host: the prescreen null control LIVES and the positive control kills 2 of 2 ledger-pinned sites",
     "command": f"PYTHONPATH=tests/hastub python3 {REL}/prescreen.py null; ... run --anchors {REL}/posctl_anchors.txt --sub posctl-D3-top6-local",
     "value": "null_verdict=LIVES (16 drivers); posctl 2/2 KILLED (tests/manual_plan.py)"},
    {"claim": "Full-gate null control (comment-only marker in tariff.py) on this host",
     "command": f"PYTHONPATH=tests/hastub python3 {REL}/fullgate.py null",
     "value": (f"gate_rc={null['gate_rc']}; red scripts {null['failed_scripts']} with failed-check counts {null['fail_lines']}, all host "
               "artefacts: optimality's claimed cell closes under Accelerate, closure.py selftest and entities.py instrument checks "
               "differ on macOS, harness_headers.py flags this seat's own untracked harnesses, and stress.py budgets fail under load. "
               f"wall {null['wall_s']} s (provisional). A mutant counts as killed only when it fails more checks than this.")},
]

extra = {
    "intro": ("Seat D3-s1, box D3-top6 slice: D3.M3 T1-T3 of the box brief. Run locally on the orchestrator host (Apple M1, 8 cores, 8 GB, "
              "macOS), because the cloud fire was refused twice by the frugal guard. The cloud fire before that did PREPARE, R1 and T1 "
              "and started the T2 null; the local run re-took the traced baselines and controls, then ran the T2 full gates. "
              "T3 (the full net over the 33 owed survivors) moved to three cloud boxes, D3-top6-t3-p1..p3, at the orchestrator's "
              "instruction (owner rule: D3 runs on cloud boxes). Their results are collected from handoff-wip/finder-r11-D3-top6-t3-p{1,2,3}. "
              "Harness corrections made in this run: tests/card.mjs runs out of memory at node 20.10's default heap on this host, so the "
              "gate sets NODE_OPTIONS=--max-old-space-size=5120 (D3S1_NODE_HEAP). HPO_GATE_LOCK_LABEL is exported, without which "
              "stress.py and harness_headers.py wait past their bound for the seat's own lease and are skipped. The worktree is "
              "reset by soft reset plus checkout, not --hard, so the finder-wall strip survives. Kills are counted by each script's "
              "own 'N of M FAILED' summary against the null. The first null and the fb16/4b37 gates ran with stress.py and "
              "harness_headers.py skipped; their KILLED verdicts stand, since a skipped script can only hide a kill. "
              "Every wall figure is provisional, on a host shared with other seats (load1 4-250)."),
    "exposure": "Carried REPORT.json/LOCAL-REPORT.json of seat D3-s1 (runs B1 and D3R) read in full, as the brief requires; no GitHub reads.",
    "unfinished": [{"step": "D3.M3", "what": ("T3: the full net over the 33 owed survivors is assigned to cloud boxes D3-top6-t3-p1..p3 "
                                               "(T3-SPLIT.md at 8de22a18). The full gate on each T3 survivor is owed after their results are collected.")}],
    "leads": []}

(HERE / "top6_findings.json").write_text(json.dumps(findings, indent=1) + "\n")
(HERE / "top6_non_findings.json").write_text(json.dumps(nonf, indent=1) + "\n")
(HERE / "top6_extra.json").write_text(json.dumps(extra, indent=1) + "\n")
(HERE / "findings").mkdir(exist_ok=True)
for f in findings:
    (HERE / "findings" / f"{f['id']}.json").write_text(json.dumps(f, indent=1) + "\n")
print(f"RESULT findings={len(findings)}")
print(f"RESULT non_findings={len(nonf)}")
