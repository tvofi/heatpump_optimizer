#!/usr/bin/env python3
"""Box D3-g36: REPORT.json and REPORT.md from results/*.json (run after build_results.py).
Command: python3 dev/audit/rounds/round11/D3/s1/wave/D3-g36/build_report.py   (from the tree root)"""
import json
from pathlib import Path
W = Path(__file__).resolve().parent
S1 = W.parents[1]
REL = "dev/audit/rounds/round11/D3/s1/wave/D3-g36"
BASE = "92d38ecb640bd462f2e19c0814d0f0b7df1ee692"
keys = [l.split("\t")[0] for l in (W / "keys.tsv").read_text().splitlines()[1:] if l.strip()]
R = {k: json.loads((W / "results" / f"{k}.json").read_text()) for k in keys if (W / "results" / f"{k}.json").exists()}
boxes = [l.split("\t") for l in (W / "wave-boxes.tsv").read_text().splitlines() if l.strip()]
null = json.loads((W / "gates/null.json").read_text())
machine = (W / "MACHINE.txt").read_text()
u1b = json.loads((S1 / "REPORT-D3-u1b.json").read_text())

timeouts = [k for k, r in R.items() if r["class"] == "timeout"]
gated_ok = [k for k, r in R.items() if r["class"] != "timeout"]
missing = [k for k in keys if k not in R]
cov = []
for row in u1b["coverage"]:
    if row["step"] == "D3.M3":
        m3 = {
            "step": "D3.M3",
            "enumerator": "awk -F'\\t' '$6==\"gate\"' SURVIVORS.tsv",
            "universe": 742,
            "examined": len(gated_ok),
            "not_reached": [f"assigned to box {b} ({n} keys)" for b, n in boxes if b != "D3-g36"]
                           + [f"{k} (TIMEOUT on box D3-g36)" for k in timeouts]
                           + [f"{k} (not gated on box D3-g36)" for k in missing],
            "redispatched": row["redispatched"],
            "evidence": (f"this box: {len(gated_ok)} of its {len(keys)} keys gated with `python3 dev/audit/rounds/round11/D3/s1/fullgate.py run --src complete --key <key>` "
                         f"(GATE_SCOPE=full GOLDEN_MODE=drift GATE_JOBS=1, driven by {REL}/gate_wave.sh), records {REL}/gates/<key>.json; null {REL}/gates/null.json. "
                         "Universe: the 742 deduped u1 full-net survivors of the owner's 2026-11-22 ruling, split over boxes D3-g01..D3-g47 "
                         f"({REL}/wave-boxes.tsv: the 47 dispatch refs' keys.tsv, 742 keys, no key on two boxes). SURVIVORS.tsv is the orchestrator's wave list and is not in this tree. "
                         "Earlier boxes' D3.M3 rows (D3-top6: 30 of 35 examined; D3-rem: 5) gated keys deduped OUT of this universe, so they add 0 to it."),
            "carried": False,
        }
        cov.append(m3)
    else:
        cov.append(dict(row, carried=True))

gated = [{"key": k, "site": r["site"], "verdict": r["gate"]["verdict"], "killed_by": r["gate"].get("killed_by"), "class": r["class"]} for k, r in R.items()]
surv = [r for r in R.values() if r["class"] == "candidate"]
equiv = [r for r in R.values() if r["class"] == "equivalent-candidate"]
nf = []
for k, r in R.items():
    if r["class"] == "killed":
        nf.append({"claim": f"{r['site']} `{r['patch']}`: the full gate fails on it (KILLED by {r['gate'].get('killed_by')})",
                   "command": r["gate_command"], "value": f"gate_rc={r['gate']['gate_rc']}; fail_lines={r['gate'].get('fail_lines')} vs null {null['fail_lines']}"})
    elif r["class"] == "equivalent-candidate":
        nf.append({"claim": f"{r['site']} `{r['patch']}`: equivalent-candidate, the full gate survives it ({r['gate']['verdict']}) and no input tried moves the outcome",
                   "command": r["probe"]["command"], "value": f"moved={r['probe']['results'].get('moved')} of inputs: {r['probe']['inputs_tried']}"})
nf.append({"claim": "full-gate null control on box D3-g36 (comment-only marker): red only on the three artefact scripts box D3-rem's null named",
           "command": "python3 dev/audit/rounds/round11/D3/s1/fullgate.py null",
           "value": f"gate_rc={null['gate_rc']} failed={null['failed_scripts']} fail_lines={null['fail_lines']} wall={null['wall_s']} s (provisional)"})
unf = [{"step": "D3.M3", "what": f"{k}: TIMEOUT past the {R[k]['gate'].get('cap_s')} s cap; last script {R[k].get('last_script')}"} for k in timeouts]
unf += [{"step": "D3.M3", "what": f"{k}: not gated on this box"} for k in missing]
harn = ["dev/audit/rounds/round11/D3/s1/fullgate.py", f"{REL}/gate_wave.sh", f"{REL}/build_results.py", f"{REL}/probes/g36_common.py"] + \
       [f"{REL}/probes/probe_{k}.py" for k in keys]
leads = [
 {"owner_seat": "unknown", "file": "custom_components/heatpump_optimizer/sysid.py", "symbol": "_declared_night_halfwidth",
  "what": "r1 - r0 (line 1208-1212, the upper-floor response to 0 vs 1 kW over one SYSID_ROLLOUT_STEP) is exactly 0.0 on 9 of 12 declared plants probe_85eb19919a6b995a.py tried, incl. the ThermalParameters defaults, so `hold` always takes the else 0.0 branch there: the declared plant is not held at its own hold power"},
 {"owner_seat": "unknown", "file": "custom_components/heatpump_optimizer/sysid.py", "symbol": "SystemIdentification.identify_slab",
  "what": "on the baseline a night with one nan room reading COMPLETES with confidence nan and ua_profile_halfwidth nan (probe_de6bbadf1499bae9.py RESULT baseline_nan); a non-finite reading is not refused"},
 {"owner_seat": "unknown", "file": "custom_components/heatpump_optimizer/sysid.py", "symbol": "SystemIdentification.identify_slab / _lm_solve",
  "what": "on the baseline identify_slab raises numpy LinAlgError (uncaught) for C_r prior 1e-3 with data C_r 0.5, and for prior 0.02 with data C_r 0.05 and 0.03 C noise (box D3-g36 exploration, g36_common.slab_sid; not a committed harness)"},
]
rep = {
 "dimension": "D3", "baseline_sha": BASE, "box": "D3-g36", "report_path": f"{REL}/REPORT.md", "exposure": "",
 "coverage": cov, "unfinished": unf, "findings": [], "non_findings": nf, "harnesses": harn, "leads": leads,
 "gated": gated, "gate_survivors": surv, "equivalent_candidates": equiv,
}
(W / "REPORT.json").write_text(json.dumps(rep, indent=1) + "\n")

tally = {}
for g in gated:
    tally[g["verdict"]] = tally.get(g["verdict"], 0) + 1
killed_by = {}
for r in R.values():
    if r["class"] == "killed":
        for s in r["gate"].get("killed_by") or []:
            killed_by[s] = killed_by.get(s, 0) + 1
md = [f"# D3-s1, box D3-g36: full gate for 16 u1 full-net survivors (sysid.py), baseline {BASE[:8]}", "",
      "## Machine and controls", "", "```", machine.strip(), "```", "",
      f"Null control (`fullgate.py null`, comment-only marker): gate_rc={null['gate_rc']}, red {null['failed_scripts']}, fail lines {null['fail_lines']}, "
      f"wall {null['wall_s']} s, load1 {null['load1_start']} -> {null['load1_end']} (provisional). Same three scripts and counts as box D3-rem's null; all artefact checks "
      "(gates/null-note.txt). A verdict is KILLED only when a script fails beyond these lines. The gates ran one at a time (GATE_JOBS=1, 4 h cap) through gate_wave.sh, "
      "which applies the mutant, commits, runs `GATE_SCOPE=full GOLDEN_MODE=drift GATE_JOBS=1 ./tests/run.sh` under the gate_lock lease, records and resets. "
      "The probes load sysid.py from `git show <baseline>` and apply the mutant in memory, so a gate's committed mutant never reaches them. Their first takes ran beside the gates (load1 up to ~5); "
      "the numbers quoted are a final re-take after the last gate, nothing else running, with the same values. Counts are exact; walls are provisional.", "",
      "## Tally", "",
      f"- gated: {len(gated)} of {len(keys)}; verdicts {tally}",
      f"- KILLED by script: {killed_by or 'none'}",
      f"- candidates (survived, probe moves): {len(surv)}; equivalent-candidates: {len(equiv)}; TIMEOUT: {len(timeouts)}", "",
      "| key | site | patch | verdict | class | probe baseline | probe mutant |", "|---|---|---|---|---|---|---|"]
for k, r in R.items():
    md.append(f"| {k} | {r['site']} | `{r['patch']}` | {r['gate']['verdict']} | {r['class']} | {r['probe']['baseline_value']} | {r['probe']['mutant_value']} |")
md += ["", "## Survivors: the step-4 answer and the probe numbers", ""]
for k, r in R.items():
    if r["class"] in ("candidate", "equivalent-candidate"):
        f = r.get("finding", {})
        md.append(f"**{k}** `{r['site']}` (`{r['patch']}`), gate {r['gate']['verdict']} (gate_rc {r['gate']['gate_rc']}, wall {r['gate'].get('wall_s')} s). "
                  f"{f.get('claim', 'Equivalent-candidate: no input tried moves the outcome.')} "
                  f"Probe `{r['probe']['command']}`: baseline {r['probe']['baseline_value']!s}, mutant {r['probe']['mutant_value']!s}; inputs: {r['probe']['inputs_tried']}. "
                  f"Should have failed: {r['should_fail']}."
                  + (f" Severity claimed {f['severity_claimed']} ({f['severity_reason']}); class_guess {f['class_guess']}." if f else ""))
        md.append("")
md += ["## Killed (non-findings)", ""]
for k, r in R.items():
    if r["class"] == "killed":
        md.append(f"- {k} `{r['site']}`: KILLED by {r['gate'].get('killed_by')} (`{r['gate_command']}`; fail lines {r['gate'].get('fail_lines')})")
md += ["", "## Coverage (D3.M3)", "", f"Universe 742 (the wave list), examined {len(gated_ok)} on this box; not reached: every other key, grouped as `assigned to box <id>` (D3-g01..D3-g47 less g36), plus this box's TIMEOUT keys {timeouts or 'none'}. D3.M1, M2, M4, M5 rows are carried verbatim from REPORT-D3-u1b.json.", "",
       "## Unfinished", ""] + [f"- {u['what']}" for u in unf] + (["- none"] if not unf else []) + ["", "## Leads", ""] + [f"- {l['file']} {l['symbol']}: {l['what']}" for l in leads] + ["",
       "## Findings", "", "None numbered here: finding ids are assigned at the orchestrator's consolidation across boxes. The candidates are under `gate_survivors` in REPORT.json, each with its finding fields.", ""]
(W / "REPORT.md").write_text("\n".join(md) + "\n")
print(f"RESULT gated={len(gated)} candidates={len(surv)} equivalent={len(equiv)} timeouts={len(timeouts)} missing={len(missing)}")
