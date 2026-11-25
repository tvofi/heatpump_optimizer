#!/usr/bin/env python3
"""Build REPORT.json and REPORT.md for box D3-g35 (seat D3-s1, round 11) from results/ and gates/."""
import csv, json, os, platform
from pathlib import Path

SP = Path("/tmp/claude-0/-home-user-heatpump-optimizer/7d8210e3-06a0-5026-9403-56518ba5807c/scratchpad")
TREE = Path("/root/audit-r11-D3-s1")
S1 = TREE / "dev/audit/rounds/round11/D3/s1"
W = S1 / "wave/D3-g35"
REL_W = "dev/audit/rounds/round11/D3/s1/wave/D3-g35"
BASE = "92d38ecb640bd462f2e19c0814d0f0b7df1ee692"

keys = [r for r in csv.DictReader(open(W / "keys.tsv"), delimiter="\t")]
res = {k["key"]: json.loads((W / "results" / f"{k['key']}.json").read_text())
       for k in keys if (W / "results" / f"{k['key']}.json").exists()}
null = json.loads((W / "gates/null.json").read_text())
boxes = json.loads((SP / "boxes.json").read_text())
u1b = json.loads((S1 / "REPORT-D3-u1b.json").read_text())
machine = (W / "MACHINE.txt").read_text()

carried = []
for row in u1b["coverage"]:
    if row["step"] in ("D3.M1", "D3.M2", "D3.M4", "D3.M5"):
        r = dict(row)
        r["evidence"] = "CARRIED verbatim from REPORT-D3-u1b.json (not re-driven on box D3-g35): " + r["evidence"]
        carried.append(r)

gated = [k for k in keys if k["key"] in res and res[k["key"]]["gate"]["verdict"] in
         ("KILLED", "SURVIVED", "RED-AS-NULL")]
timeouts = [k for k in keys if k["key"] in res and res[k["key"]]["gate"]["verdict"] == "TIMEOUT"]
missing = [k for k in keys if k["key"] not in res]
not_reached = [f"assigned to box D3-{b}: {v['n']} key(s): {v['desc']}"
               for b, v in sorted(boxes.items()) if b != "g35"]
not_reached += [f"TIMEOUT on box D3-g35 (4 h cap): {k['key']} sysid.py:{k['line']} {k['kind']}" for k in timeouts]
not_reached += [f"not gated on box D3-g35 (run ended early): {k['key']} sysid.py:{k['line']} {k['kind']}" for k in missing]
m3 = {
    "step": "D3.M3",
    "enumerator": "awk -F'\\t' '$6==\"gate\"' SURVIVORS.tsv",
    "universe": 742,
    "examined": len(gated),
    "not_reached": not_reached,
    "redispatched": [{"item": "C3", "state": "examined"}, {"item": "C5", "state": "examined"}],
    "evidence": ("the wave list (742 keys) split over boxes D3-g01..D3-g47; SURVIVORS.tsv itself is not in this box's "
                 "tree, so the universe and each box's share were re-counted from the 47 dispatch refs' keys.tsv "
                 "(git ls-remote origin 'refs/heads/dispatch/finder-r11-D3-g*': 47 refs, 742 keys, box D3-g35 16). "
                 "Box D3-g35 gated its 16 with `python3 dev/audit/rounds/round11/D3/s1/fullgate.py run --src complete --key <key>` "
                 "(GATE_SCOPE=full GOLDEN_MODE=drift GATE_JOBS=1 ./tests/run.sh, one gate at a time, via gate_wave.sh run), records "
                 f"{REL_W}/gates/<key>.json, null {REL_W}/gates/null.json; earlier boxes' D3.M3 gates (D3-top6, D3-rem: 35 keys) "
                 "are outside this 742-key universe and carried in their own reports. C3/C5: examined by box D3-rem (carried)."),
}

nf, gs, eq, gated_rows = [], [], [], []
tally = {"KILLED": 0, "SURVIVED": 0, "RED-AS-NULL": 0, "TIMEOUT": 0}
killed_by = {}
for k in keys:
    r = res.get(k["key"])
    if not r:
        continue
    g = r["gate"]
    tally[g["verdict"]] = tally.get(g["verdict"], 0) + 1
    gated_rows.append({"key": k["key"], "site": r["site"], "verdict": g["verdict"],
                       "killed_by": g.get("killed_by") or [], "class": r["class"]})
    gcmd = f"PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/fullgate.py run --src complete --key {k['key']}"
    if r["class"] == "killed":
        for s in g.get("killed_by") or []:
            killed_by[s] = killed_by.get(s, 0) + 1
        nf.append({"claim": f"D3.M3 full gate {k['key']} {r['site']} ({r['patch']}): KILLED by {', '.join(g.get('killed_by') or [])}"
                            + (f" -- {r['kill_note']}" if r.get("kill_note") else ""),
                   "command": gcmd,
                   "value": f"gate_rc={g['gate_rc']}; killed_by={g.get('killed_by')}; failing lines {r.get('failing_check_lines') or r.get('failing_lines')}; wall {g['wall_s']} s, load1 {g['load1_start']}..{g['load1_end']} (provisional)"})
    elif r["class"] == "equivalent-candidate":
        eq.append(r)
        nf.append({"claim": f"D3.M3 full gate {k['key']} {r['site']} ({r['patch']}): {g['verdict']} (read as survived) and equivalent-candidate: {r['should_fail']['assertion']}",
                   "command": r["probe"]["command"],
                   "value": f"differing_cases={r['probe']['differing_cases']} of {r['probe']['cases']} inputs ({', '.join(r['probe']['inputs_tried'])}); hunt {r['probe']['hunt']}; gate_rc={g['gate_rc']}, wall {g['wall_s']} s (provisional)"})
    elif r["class"] == "candidate":
        gs.append(r)

unfinished = [{"step": "D3.M3", "what": f"TIMEOUT {k['key']} (4 h cap); see results/{k['key']}.json for the last script running"} for k in timeouts]
unfinished += [{"step": "D3.M3", "what": f"{k['key']} not gated on this box"} for k in missing]
unfinished.append({"step": "D3.M3", "what": f"finding ids: the {len(gs)} gate_survivors candidates carry no id (D3-s1-01..71 are taken); the orchestrator's consolidation assigns them before verification"})

harn = ["dev/audit/rounds/round11/D3/s1/fullgate.py", f"{REL_W}/probes/sysid_probe_common.py"] + \
       [f"{REL_W}/probes/probe_{k['key']}.py" for k in keys]

exposure = ("Read COMMON.md, D3.md, dev/audit/README.md and finding.schema.json (through a haiku extractor), the u1 slice "
            "M4 answers for this box's 16 keys and the mutant records state/results/complete/<key>.json, REPORT-D3-u1b.json's "
            "coverage rows, REPORT-D3-rem.json's M3 row and two non-findings, m26_probe.py (the probe pattern), sysid.py "
            "1890-2262 and 337-460, and the other 46 boxes' dispatch keys.tsv (key counts and sites only, for not_reached). "
            "No register, round11/J/, verifier report, docs/ page or GitHub record read; no gh run.")

rep = {
    "dimension": "D3", "baseline_sha": BASE, "box": "D3-g35",
    "report_path": f"{REL_W}/REPORT.md",
    "exposure": exposure,
    "coverage": carried[:2] + [m3] + carried[2:],
    "unfinished": unfinished,
    "findings": [],
    "non_findings": [{"claim": "Box D3-g35 full-gate null control (comment-only marker): red only on instrument/artefact checks "
                               "(closure.py selftest merge-reason pins, entities.py's scoped-path record check, harness_headers.py's "
                               "round-4 D6 claims count and committed-output check in the stripped tree, and the inlined-walk check "
                               "naming this box's own untracked probe helper); used as the kill threshold per script",
                      "command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/fullgate.py null",
                      "value": f"gate_rc={null['gate_rc']}; fail_lines={null['fail_lines']}; wall {null['wall_s']} s, load1 {null['load1_start']}..{null['load1_end']} (provisional)"}] + nf,
    "harnesses": harn,
    "leads": [],
    "gated": gated_rows,
    "gate_survivors": gs,
    "equivalent_candidates": eq,
}
(Path(os.environ.get("OUT", W)) / "REPORT.json").write_text(json.dumps(rep, indent=1) + "\n")

# ---- markdown
L = []
A = L.append
A("# D3-s1, box D3-g35: full gate for 16 D3.M3 full-net survivors (audit round 11)\n")
A(f"Baseline {BASE}. Seat D3-s1, dimension D3, step D3.M3 with the D3.md step-4 answer per survivor. "
  "All 16 keys are mutants of `SystemIdentification.identify` in `custom_components/heatpump_optimizer/sysid.py` (lines 2141-2246).\n")
A("## Machine and controls\n")
A("```\n" + machine.strip() + "\n```\n")
A(f"Null control (`fullgate.py null`, comment-only marker): gate_rc={null['gate_rc']}, red scripts {null['failed_scripts']}, "
  f"failed-check counts {null['fail_lines']}, wall {null['wall_s']} s, load1 {null['load1_start']}..{null['load1_end']} (provisional). "
  "All red lines are instrument or artefact checks: closure.py selftest's two merge-reason pins (status skip-not-under-scoped), "
  "entities.py's one scoped-path record check, and harness_headers.py's round-4 D6 claims header (123 vs 122 in the stripped tree), "
  "its committed-output check, and its inlined-walk check naming this box's own untracked probes/sysid_probe_common.py. "
  "A key counts KILLED only when a script is red beyond these counts. Not re-taken: no production-behaviour script is red, and no script red for the machine.\n")
A("Procedure: `gate_wave.sh run` runs `fullgate.py run --src complete --key <key>` for each key of keys.tsv in order, one gate at a time "
  "(GATE_SCOPE=full GOLDEN_MODE=drift GATE_JOBS=1, 4 h cap), and checkpoints after each; the per-key record is "
  f"`{REL_W}/gates/<key>.json` with its log beside it. Every wall and load figure is provisional (nproc 4, Intel Xeon @ 2.10GHz, the box alone on its machine). "
  "One container restart happened mid-wave; the gate processes and the checkpointed records survived it.\n")
A("Probes: each `probes/probe_<key>.py` loads the baseline's sysid.py with `git show` (never the gate's worktree file), applies the one-line mutant "
  "in memory, and drives `identify()` on synthetic exact first-order step tests (`probes/sysid_probe_common.py`: C dT/dt = Q + G - UA (T - T_out), "
  "10-minute cadence, settle 1 h / step 2 h / relax 2 h) over a 29-case honest-search grid plus the key case. Boundary mutants (`<=` vs `<`) are reached "
  "by hunting a float input until an instrumentation arm (a `_TAP.append` before the mutated line, not the mutant) reads the boundary exactly. "
  "Metric `differing_cases`: inputs whose published result (completed, reason, UA, C, gains, drift, confidence) differs mutant vs baseline.\n")
A("## Tally\n")
A(f"- gated: {len(gated_rows)} of 16; KILLED {tally.get('KILLED',0)} ({', '.join(f'{s}: {n}' for s, n in killed_by.items()) or 'none'}); "
  f"SURVIVED {tally.get('SURVIVED',0)}; RED-AS-NULL {tally.get('RED-AS-NULL',0)}; TIMEOUT {tally.get('TIMEOUT',0)}")
A(f"- candidates (gate survivors whose probe moves): {len(gs)}; equivalent-candidates: {len(eq)}\n")
A("| key | site | patch | verdict | killed_by | class | probe key case (baseline -> mutant) | differing_cases |")
A("|---|---|---|---|---|---|---|---|")
for k in keys:
    r = res.get(k["key"])
    if not r:
        A(f"| {k['key']} | sysid.py:{k['line']} | | not gated | | | | |")
        continue
    p = r["probe"]
    A(f"| {k['key']} | {r['site'].split('/')[-1]} | `{r['patch']}` | {r['gate']['verdict']} | {', '.join(r['gate'].get('killed_by') or []) or '-'} | {r['class']} | "
      f"{p['baseline_value']} -> {p['mutant_value']} | {p['differing_cases']}/{p['cases']} |")
A("")
A("## Survivors: the step-4 answer, with probe numbers\n")
for k in keys:
    r = res.get(k["key"])
    if not r or r["class"] == "killed":
        continue
    p = r["probe"]
    A(f"### {k['key']} — {r['site']} ({r['gate']['verdict']}, {r['class']})\n")
    A(f"Patch `{r['patch']}`. Carried M4 answer: {r['m4_carried']}. Gate: gate_rc={r['gate']['gate_rc']}, wall {r['gate']['wall_s']} s, "
      f"load1 {r['gate']['load1_start']}..{r['gate']['load1_end']} (provisional).")
    if r["class"] == "candidate":
        A(f"Probe `{p['command']}`: key case {p['baseline_value']} -> {p['mutant_value']}, differing_cases {p['differing_cases']} of {p['cases']}"
          + (f"; hunt {p['hunt']}" if p.get("hunt") else "") + ".")
        A(f"Claim: {r['claim']}")
        A(f"Should have failed: {r['should_fail']['script']} — it lacks {r['should_fail']['assertion']}.")
        A(f"Severity claimed {r['severity_claimed']} ({r['severity_reason']}); class_guess {r['class_guess']}; perturbation direction {r['perturbation']['expected_direction']}.\n")
    else:
        A(f"Probe `{p['command']}`: differing_cases {p['differing_cases']} of {p['cases']}" + (f"; hunt {p['hunt']}" if p.get("hunt") else "") + ".")
        A(f"Equivalent-candidate: {r['should_fail']['assertion']}. Inputs tried: {', '.join(p['inputs_tried'])}.\n")
A("## Killed\n")
for k in keys:
    r = res.get(k["key"])
    if r and r["class"] == "killed":
        A(f"- {k['key']} {r['site']} (`{r['patch']}`): KILLED by {r['gate'].get('killed_by')}; {r.get('kill_note','')}")
A("")
A("## Non-findings, harnesses, unfinished, exposure\n")
A("Non-findings: the null control, every KILLED key and every equivalent-candidate, each with its command and number (REPORT.json `non_findings`). "
  "Findings: none numbered here; the " + str(len(gs)) + " candidates are under `gate_survivors` for the orchestrator's consolidation to number.\n")
A("Harnesses: " + ", ".join(f"`{h}`" for h in harn) + "; the box procedure is gate_wave.sh (dispatch ref tip b7a3ae2e).\n")
A("Unfinished: " + "; ".join(u["what"] for u in unfinished) + ".\n")
A("Exposure: " + exposure + "\n")
A("Note on severity: `identify()` is the harness-only one-state regression (#1395); the production sequence with a declared plant routes to "
  "`identify_slab`, so every candidate here is a gap in the suite's pin of a harness path, claimed low.\n")
(Path(os.environ.get("OUT", W)) / "REPORT.md").write_text("\n".join(L) + "\n")
print("REPORT written:", len(gated_rows), "gated", tally, "candidates", len(gs), "equiv", len(eq))
