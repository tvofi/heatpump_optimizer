#!/usr/bin/env python3
"""Box D3-g11: build REPORT.json / REPORT.md for seat D3-s1 from results/<key>.json, keys.tsv and REPORT-D3-u1b.json."""
import json, subprocess, sys
from pathlib import Path
TR = Path.home() / "audit-r11-D3-s1"
S1 = TR / "dev/audit/rounds/round11/D3/s1"
W = S1 / "wave/D3-g11"
REL = "dev/audit/rounds/round11/D3/s1/wave/D3-g11"
BASE = "92d38ecb640bd462f2e19c0814d0f0b7df1ee692"
boxes = [l.split() for l in (Path.home() / "boxes.txt").read_text().splitlines()]
keys = [l.split("\t") for l in (W / "keys.tsv").read_text().splitlines()[1:] if l.strip()]
R = {k[0]: json.loads((W / "results" / f"{k[0]}.json").read_text()) for k in keys}
u1b = json.loads((S1 / "REPORT-D3-u1b.json").read_text())
cov = []
for row in u1b["coverage"]:
    if row["step"] == "D3.M3":
        continue
    r = dict(row); r["carried"] = True
    r["evidence"] = "carried verbatim from REPORT-D3-u1b.json (not re-driven by box D3-g11): " + row["evidence"]
    cov.append(r)
timeouts = [k for k, r in R.items() if r["class"] == "timeout"]
examined_keys = [k for k, r in R.items() if r["class"] != "timeout"]
nr = []
for b, n, a, _, z in boxes:
    if b == "g11":
        continue
    nr.append(f"assigned to box D3-{b}: {n} keys ({a} .. {z})")
for k in timeouts:
    r = R[k]
    nr.append(f"TIMEOUT on box D3-g11: {k} {r['site']} (full gate past the {r['gate'].get('cap_s') or 14400} s cap; unfinished)")
m3 = {"step": "D3.M3", "enumerator": "awk -F'\\t' '$6==\"gate\"' SURVIVORS.tsv",
      "universe": 742, "examined": len(examined_keys), "not_reached": nr,
      "redispatched": [r for row in u1b["coverage"] if row["step"] == "D3.M3" for r in row.get("redispatched", [])],
      "evidence": ("box D3-g11 wave (the owner's 2026-11-22 ruling: every full-net survivor gets the full gate): "
                   f"{len(keys)} keys of keys.tsv, one at a time, GATE_JOBS=1, by gate_wave.sh run -> "
                   "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/fullgate.py run --src <src> --key <key> "
                   f"(GATE_SCOPE=full GOLDEN_MODE=drift GOLDEN_REF={BASE} ./tests/run.sh); records {REL}/gates/<key>.json; "
                   f"null control {REL}/gates/null.json. Examined {len(examined_keys)} of this box's {len(keys)}; the other "
                   f"{742 - len(keys)} wave keys are the other 46 boxes' (counts from each dispatch/finder-r11-D3-gNN keys.tsv; "
                   "SURVIVORS.tsv itself is not in this box's tree). The 8 keys deduped out of the wave were gated by D3-top6/D3-rem under other keys (their D3.M3 rows).")}
cov.insert(1 if cov and cov[0]["step"] == "D3.M1" else 0, m3)
cov.sort(key=lambda r: int(r["step"].split("M")[1]))
gated, surv, eq, nonf, unfinished = [], [], [], [], []
harn = ["dev/audit/rounds/round11/D3/s1/fullgate.py"]
for k in [x[0] for x in keys]:
    r = R[k]; g = r["gate"]
    gated.append({"key": k, "site": r["site"], "verdict": g["verdict"], "killed_by": g.get("killed_by") or [], "class": r["class"]})
    p = r.get("probe")
    if p and p.get("path"):
        harn.append(p["path"])
    if r["class"] == "candidate":
        surv.append(r)
    elif r["class"] == "equivalent-candidate":
        eq.append(r)
        nonf.append({"claim": f"equivalent-candidate {k} {r['site']} ({r['patch']}): full gate {g['verdict']}; no input moves the probe's number",
                     "command": p["command"], "value": "; ".join(p.get("inputs_tried") or p.get("results") or [])})
    elif r["class"] == "killed":
        nonf.append({"claim": f"killed {k} {r['site']} ({r['patch']}): the full suite fails on it, killed_by {', '.join(g['killed_by'])}",
                     "command": r["gate_command"], "value": f"gate_rc {g['gate_rc']}; failed scripts {len(g['failed_scripts'])} vs the null's 3; more than null: {', '.join(g['killed_by'])}"})
    elif r["class"] == "timeout":
        unfinished.append({"step": "D3.M3", "what": f"{k} {r['site']} ({r['patch']}): full gate TIMEOUT past the {g.get('cap_s') or 14400} s cap; last script running: {r.get('last_script_running') or 'see gates/'+k+'.log'}; {r.get('timeout_note','')}; neither finding nor non-finding (pre-gate probe: {'; '.join(r.get('probe_pregate') or [])})"})
harn.append(f"{REL}/probes/box-tools/build_result.py (gate_wave.sh's procedure: gate_wave.sh null/run/ckpt from the dispatch tip; this box's recorder writes results/<key>.json)")
harn = [h for h in harn if h.startswith("dev/audit/rounds/round11/D3/")]
machine = (W / "MACHINE.txt").read_text()
rep = {"dimension": "D3", "baseline_sha": BASE, "box": "D3-g11", "seat": "D3-s1",
       "report_path": f"{REL}/REPORT.md",
       "exposure": "Box D3-g11 read only this seat's carried evidence under dev/audit/rounds/round11/D3/s1/ (fullgate.py, prescreen state, the u1 slice and top6/rem reports, the m4 answers) and the 47 wave boxes' dispatch keys.tsv (key counts only); no docs/, register, round11/J/, verifier report or GitHub record.",
       "coverage": cov, "unfinished": unfinished, "findings": [], "non_findings": nonf, "harnesses": harn, "leads": [],
       "gated": gated, "gate_survivors": surv, "equivalent_candidates": eq}
(W / "REPORT.json").write_text(json.dumps(rep, indent=1) + "\n")
# markdown
from collections import Counter
vc = Counter(r["gate"]["verdict"] for r in R.values()); cc = Counter(r["class"] for r in R.values())
null = json.loads((W / "gates/null.json").read_text())
L = [f"# D3-s1 box D3-g11: full gate for 16 D3.M3 full-net survivors (round 11, baseline {BASE[:12]})", "",
     "## Machine and controls", "", "```", machine.strip(), "```", "",
     f"Null control (`fullgate.py null`, comment-only marker): gate_rc {null['gate_rc']}, wall {null['wall_s']} s (provisional), red scripts {', '.join(null['failed_scripts'])} -- artefact checks only ({REL}/gates/null-note.txt). A key is KILLED only on a script red beyond these or more FAIL lines in one.",
     "", "Procedure: `gate_wave.sh run` (one gate at a time, GATE_JOBS=1, 4 h cap) -> `fullgate.py run --src <src> --key <key>`; each recorded gate -> `probes/box-tools/build_result.py <key>` runs the key's probe in a clean baseline checkout and writes results/<key>.json. This seat resumed a stalled predecessor at 4/16 gated; nothing was re-gated.", "",
     "## Tally", "", f"- gated: {len(keys)} keys; verdicts {dict(vc)}",
     f"- KILLED: {', '.join(k+' by '+', '.join(r['gate']['killed_by']) for k,r in R.items() if r['gate']['verdict']=='KILLED') or 'none'}",
     f"- classes: {dict(cc)}", f"- candidates (gate_survivors): {len(surv)}; equivalent-candidates: {len(eq)}; timeouts: {len(timeouts)}", "",
     "Wall, CPU and load numbers are provisional (nproc 4, Intel Xeon @ 2.10GHz; the judge re-takes them); counts are final.", "",
     "| key | site | patch | verdict | class | probe baseline -> mutant |", "|---|---|---|---|---|---|"]
for k in [x[0] for x in keys]:
    r = R[k]; p = r.get("probe") or {}
    L.append(f"| {k} | {r['site'].replace('custom_components/heatpump_optimizer/','')} | `{r['patch']}` | {r['gate']['verdict']} | {r['class']} | {('equal on every input tried' if r['class']=='equivalent-candidate' else ('killed by the suite' if r['class']=='killed' else ('pre-gate: see below' if r['class']=='timeout' else str(p.get('baseline_value'))+' -> '+str(p.get('mutant_value')))))} |")
L += ["", "## Survivors: step-4 answers", ""]
for k in [x[0] for x in keys]:
    r = R[k]
    if r["class"] not in ("candidate", "equivalent-candidate", "timeout"):
        continue
    p = r.get("probe") or {}
    res = p.get("results") or r.get("probe_pregate") or []
    L.append(f"### {k} {r['function']} ({r['site'].replace('custom_components/heatpump_optimizer/','')}, `{r['patch']}`) -- {r['gate']['verdict']}, {r['class']}")
    L.append("")
    if r["class"] == "candidate":
        f = r["finding"]
        L.append(f"{f['claim']} Should have failed: {r['should_fail']}. Title: {f['title']} (class_guess {f['class_guess']}, severity {f['severity_claimed']}).")
    elif r["class"] == "equivalent-candidate":
        L.append(f"No input moved the number. {r.get('should_fail','')}")
    else:
        L.append(f"Full gate TIMEOUT (unfinished). Pre-gate probe numbers below.")
    L.append(""); L.append(f"`{p.get('command', '')}`"); L.append("")
    L += ["    " + x for x in res]; L.append("")
L += ["## Killed", ""]
for k, r in R.items():
    if r["class"] == "killed":
        L.append(f"- {k} {r['site']} `{r['patch']}`: killed by {', '.join(r['gate']['killed_by'])} (`{r['gate_command']}`), gate_rc {r['gate']['gate_rc']}.")
L += ["", "## Coverage", "", "D3.M1, D3.M2, D3.M4, D3.M5 and their C-items are carried verbatim from REPORT-D3-u1b.json. D3.M3 is this wave's row: universe 742, examined " + str(len(examined_keys)) + ", the rest named by box in REPORT.json's not_reached.", "",
      "## Unfinished", ""] + [f"- {u['what']}" for u in unfinished]
(W / "REPORT.md").write_text("\n".join(L) + "\n")
print("REPORT", len(gated), dict(cc))
