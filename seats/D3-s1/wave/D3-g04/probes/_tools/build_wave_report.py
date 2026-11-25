#!/usr/bin/env python3
"""Box D3-g04: build REPORT.json / REPORT.md for seat D3-s1 from the wave dir's
gates/ and results/ records, the carried REPORT-D3-u1b.json rows and every box's
keys.tsv ($HOME/allkeys/<box>.tsv, taken from the 47 dispatch/finder-r11-D3-g* refs).
Run from the tree root: python3 $HOME/pgen/build_wave_report.py"""
import json, os
from pathlib import Path

BOX = "D3-g04"
BASE = "92d38ecb640bd462f2e19c0814d0f0b7df1ee692"
S1 = Path("dev/audit/rounds/round11/D3/s1")
W = S1 / "wave" / BOX
R = f"{W}"
ALL = Path(os.environ["HOME"]) / "allkeys"

keys = [l.split("\t") for l in (W / "keys.tsv").read_text().splitlines()[1:] if l.strip()]
recs, gated, surv, equiv, nonf, unfinished = {}, [], [], [], [], []
for row in keys:
    k = row[0]
    rp = W / "results" / f"{k}.json"
    if not rp.exists():
        unfinished.append(f"{k} ({row[2]}:{row[3]} {row[8]}): no gate record yet on box {BOX}")
        continue
    r = json.loads(rp.read_text()); recs[k] = r
    g = r["gate"]
    gated.append({"key": k, "site": r["site"], "verdict": g["verdict"], "killed_by": g.get("killed_by", []), "class": r["class"]})
    if r["class"] == "candidate":
        surv.append(r)
    elif r["class"] == "equivalent-candidate":
        equiv.append(r)
        p = r["probe"]
        nonf.append({"claim": f"equivalent-candidate {k} ({r['site']}, {r['patch']}): survives the full gate ({g['verdict']}, gate_rc {g['gate_rc']}) and no reachable production input distinguishes the arms",
                     "command": p["command"], "value": f"{p['baseline_value']} | {p['mutant_value']} | inputs tried: " + "; ".join(p.get("inputs_tried", []))})
    elif r["class"] == "killed":
        nonf.append({"claim": f"killed {k} ({r['site']}): the full gate fails on it, killed_by {g.get('killed_by')}",
                     "command": g["command"] + f" via {S1}/fullgate.py run --src complete --key {k}",
                     "value": f"gate_rc={g['gate_rc']} verdict=KILLED record {g['record']}"})
    elif r["class"] == "timeout":
        unfinished.append(f"{k} ({r['site']}): TIMEOUT past the {g.get('cap_s', 14400)} s cap; last script running: {r.get('timeout_last_script', '?')}")

null = json.loads((W / "gates" / "null.json").read_text())
nonf.insert(0, {"claim": f"null control: fullgate.py null (a comment-only marker) on box {BOX}; red only on artefact checks (gates/null-note.txt)",
                "command": f"bash $HOME/gate_wave.sh null  (= python3 {S1}/fullgate.py null)",
                "value": f"gate_rc={null.get('gate_rc')} failed_scripts={null.get('failed_scripts')} record {W}/gates/null.json"})

u1b = json.loads((S1 / "REPORT-D3-u1b.json").read_text())
cov = []
for row in u1b["coverage"]:
    if row["step"] == "D3.M3":
        continue
    row = dict(row); row["carried"] = True
    row["evidence"] = f"carried verbatim from {S1}/REPORT-D3-u1b.json: " + str(row.get("evidence", ""))
    cov.append(row)
m3_u1b = [r for r in u1b["coverage"] if r["step"] == "D3.M3"][0]
mine = {row[0] for row in keys}
not_reached = []
for f in sorted(ALL.glob("D3-g*.tsv")):
    b = f.stem
    if b == BOX:
        continue
    for l in f.read_text().splitlines()[1:]:
        if l.strip():
            c = l.split("\t"); not_reached.append(f"assigned to box {b}: {c[2]}:{c[3]} {c[8]} {c[0]}")
for r in recs.values():
    if r["class"] == "timeout":
        not_reached.append(f"TIMEOUT on box {BOX}: {r['site']} {r['key']}")
for k in sorted(mine - set(recs)):
    not_reached.append(f"not yet gated on box {BOX}: {k}")
examined = len([r for r in recs.values() if r["class"] != "timeout"])
cov.insert(2, {"step": "D3.M3", "enumerator": "awk -F'\\t' '$6==\"gate\"' SURVIVORS.tsv  (the wave list: the union of the 47 dispatch/finder-r11-D3-g*/keys.tsv, 742 keys)",
               "universe": 742, "examined": examined, "not_reached": not_reached,
               "redispatched": m3_u1b.get("redispatched", []),
               "evidence": f"box {BOX}: {examined} keys full-gated, one gate at a time: GATE_SCOPE=full GOLDEN_MODE=drift GOLDEN_REF={BASE} GATE_JOBS=1 ./tests/run.sh via python3 {S1}/fullgate.py run --src complete --key <key> (gate_wave.sh run); records {W}/gates/<key>.json; null {W}/gates/null.json. Earlier boxes' D3.M3 rows (D3-top6, D3-rem, D3-u1a..d) are theirs, carried in their own reports and not re-driven here."})

probes = sorted(str(p) for p in (W / "probes").glob("probe_*.py"))
rep = {
    "dimension": "D3", "baseline_sha": BASE, "box": BOX, "seat": "D3-s1",
    "report_path": f"{W}/REPORT.md",
    "exposure": "No docs/, register, round11/J/ or verifier report and no GitHub read. Read: this box's keys.tsv, the gate logs and records it wrote, the slice boxes' m4_answers files for its 16 keys, REPORT-D3-u1b.json's coverage rows (carried) and the 47 dispatch refs' keys.tsv (only to name other boxes' keys under not_reached). Resumed from the predecessor seat's checkpoint (wip ref 31bc0f0c): 6 gates, their records and all 16 probes were that seat's; the remaining gates were run by this seat.",
    "coverage": cov, "unfinished": unfinished, "findings": [], "non_findings": nonf,
    "harnesses": [f"{S1}/fullgate.py",
                  "gate_wave.sh (dispatch/finder-r11-D3-g04 tip, out of tree): null control once, then fullgate.py run per key of keys.tsv in order, one gate at a time, 4 h cap (TIMEOUT never KILLED), checkpoint after each gate"] + probes,
    "leads": [], "gated": gated, "gate_survivors": surv, "equivalent_candidates": equiv,
}

def md():
    tally = {}
    for g in gated: tally[g["verdict"]] = tally.get(g["verdict"], 0) + 1
    L = [f"# D3-s1 box {BOX}: full gate for 16 D3.M3 full-net survivors (round 11)", "",
         f"Baseline `{BASE}`. Seat D3-s1, wave box {BOX}. Counts are final; wall, CPU and load numbers are provisional (the judge re-takes them).", "",
         "## Machine and controls", "", "```", (W / "MACHINE.txt").read_text().strip(), "```", "",
         (W / "gates" / "null-note.txt").read_text().strip(), "",
         "Procedure: `gate_wave.sh run` (the dispatch tip's driver) runs `python3 dev/audit/rounds/round11/D3/s1/fullgate.py run --src complete --key <key>` per key, one gate at a time: the one-line mutant is applied and committed, the gate_lock lease taken, `GATE_SCOPE=full GOLDEN_MODE=drift GATE_JOBS=1 ./tests/run.sh` run, the verdict recorded against this box's null, and the tree reset to the baseline. Probes run from a separate clean baseline worktree, never the gate's tree.", "",
         "## Tally", "",
         f"- gated: {len(gated)} of {len(keys)}",
         "- " + ", ".join(f"{v}: {n}" for v, n in sorted(tally.items())),
         f"- KILLED by script: " + (", ".join(f"{g['key']} by {g['killed_by']}" for g in gated if g["verdict"] == "KILLED") or "none"),
         f"- candidates (full-gate survivors whose probe moves): {len(surv)}",
         f"- equivalent-candidates: {len(equiv)}",
         f"- TIMEOUT / unfinished: {len(unfinished)}", "",
         "| key | site | verdict | class | probe baseline -> mutant |", "|---|---|---|---|---|"]
    for k, r in recs.items():
        L.append(f"| {k} | {r['site']} | {r['gate']['verdict']} | {r['class']} | {r['probe']['baseline_value']} -> {r['probe']['mutant_value']} |")
    L += ["", "## Survivors: step-4 answers", ""]
    for k, r in recs.items():
        if r["class"] not in ("candidate", "equivalent-candidate"): continue
        p = r["probe"]; f = r.get("finding", {})
        L.append(f"### {k} — {r['site']} ({r['class']})")
        L.append("")
        L.append(f"`{r['patch']}` in `{r['function']}`. Gate: {r['gate']['verdict']} (gate_rc {r['gate']['gate_rc']}, wall {r['gate']['wall_s']} s, load1 {r['gate']['load1_start']}..{r['gate']['load1_end']}). "
                 + (f"{f['claim']} " if f else "")
                 + f"Probe `{p['path']}`: baseline `{p['baseline_value']}`, mutant `{p['mutant_value']}`; inputs tried: {'; '.join(p.get('inputs_tried', []))}. "
                 + f"Should have failed: {r['should_fail']}")
        L.append("")
    if unfinished:
        L += ["## Unfinished", ""] + [f"- {u}" for u in unfinished] + [""]
    notes = W / "NOTES.md"
    if notes.exists():
        L += ["## Seat notes", "", notes.read_text().strip(), ""]
    return "\n".join(L) + "\n"

text = md()
(W / "REPORT.md").write_text(text)
rep["report_md"] = text
(W / "REPORT.json").write_text(json.dumps(rep, indent=1) + "\n")
print(f"RESULT gated={len(gated)} candidates={len(surv)} equivalent={len(equiv)} unfinished={len(unfinished)} not_reached={len(not_reached)}")
