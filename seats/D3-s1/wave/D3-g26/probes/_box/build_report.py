#!/usr/bin/env python3
"""Box D3-g26 scratch: build REPORT.json and REPORT.md of the wave dir from results/<key>.json,
gates/null.json, keys.tsv, REPORT-D3-u1b.json's carried coverage rows and the 47-box key map
(boxmap.json, read from every dispatch/finder-r11-D3-g<NN> ref's keys.tsv)."""
import json
import sys
from pathlib import Path

W = Path.home() / "audit-r11-D3-s1/dev/audit/rounds/round11/D3/s1/wave/D3-g26"
S1 = W.parent.parent
BOXMAP = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.home() / "g26work/boxmap.json"
BASE = "92d38ecb640bd462f2e19c0814d0f0b7df1ee692"
REL = "dev/audit/rounds/round11/D3/s1/wave/D3-g26"
PDIR = REL + "/probes"

keys = [l.split("\t") for l in (W / "keys.tsv").read_text().splitlines()[1:] if l.strip()]
recs = {}
for row in keys:
    p = W / "results" / f"{row[0]}.json"
    if p.exists():
        recs[row[0]] = json.loads(p.read_text())
null = json.loads((W / "gates/null.json").read_text())
u1b = json.loads((S1 / "REPORT-D3-u1b.json").read_text())
boxmap = json.loads(BOXMAP.read_text())
machine = (W / "MACHINE.txt").read_text()

gated = []
for row in keys:
    k = row[0]
    r = recs.get(k)
    g = json.loads((W / "gates" / f"{k}.json").read_text()) if (W / "gates" / f"{k}.json").exists() else None
    gated.append({"key": k, "site": f"{row[2]}:{row[3]} {row[8]}",
                  "verdict": g["verdict"] if g else "NOT-GATED",
                  "killed_by": (g or {}).get("killed_by") or [],
                  "class": r["class"] if r else "unrecorded"})

timeouts = [g for g in gated if g["verdict"] == "TIMEOUT"]
missing = [g for g in gated if g["verdict"] == "NOT-GATED" or g["class"] == "unrecorded"]
examined = sum(1 for g in gated if g["verdict"] in ("KILLED", "SURVIVED", "RED-AS-NULL") and g["class"] != "unrecorded")

# coverage: M1, M2, M4, M5 carried verbatim from REPORT-D3-u1b.json; M3 is this wave's
cov = []
for c in u1b["coverage"]:
    if c["step"] == "D3.M3":
        nr = []
        for box in sorted(boxmap):
            if box == "D3-g26":
                continue
            ks = boxmap[box]
            files = sorted({x["file"].rsplit("/", 1)[-1] for x in ks})
            lines = [x["line"] for x in ks]
            nr.append(f"assigned to box {box}: {len(ks)} keys ({', '.join(files)}; lines {min(lines)}-{max(lines)}): "
                      + " ".join(x["key"] for x in ks))
        for g in timeouts:
            nr.append(f"TIMEOUT on box D3-g26 (gate past the 4 h cap, neither killed nor survived): {g['key']} {g['site']}")
        for g in missing:
            if g not in timeouts:
                nr.append(f"not gated or not recorded on box D3-g26: {g['key']} {g['site']}")
        cov.append({
            "step": "D3.M3",
            "enumerator": "awk -F'\\t' '$6==\"gate\"' SURVIVORS.tsv",
            "universe": 742,
            "examined": examined,
            "not_reached": nr,
            "redispatched": c.get("redispatched", []),
            "evidence": ("this wave's full gates: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/fullgate.py run --src complete --key <key> "
                         "(GATE_SCOPE=full GOLDEN_MODE=drift GOLDEN_REF=" + BASE + " GATE_JOBS=1 ./tests/run.sh), one gate at a time by gate_wave.sh run, "
                         f"records {REL}/gates/<key>.json for the {len(keys)} keys of {REL}/keys.tsv; null control {REL}/gates/null.json "
                         f"(gate_rc {null['gate_rc']}, red scripts {null['failed_scripts']}). The universe is the 742-key wave list (746 u1 full-net "
                         "survivors + 3 timeouts + 1 leak, less 8 already gated under other keys by boxes D3-top6/D3-rem, whose D3.M3 rows "
                         "(REPORT-D3-top6.json, REPORT-D3-rem.json) carry those gates); the other 726 keys are the 46 other wave boxes', named "
                         "under not_reached from each dispatch/finder-r11-D3-g<NN> ref's keys.tsv. SURVIVORS.tsv is not in the stripped tree; "
                         "the per-box keys.tsv files are its 742 gate rows (47 boxes, 742 distinct keys, counted on this box)."),
        })
    else:
        cc = dict(c)
        cc["carried"] = "REPORT-D3-u1b.json"
        cc["evidence"] = "carried verbatim from dev/audit/rounds/round11/D3/s1/REPORT-D3-u1b.json (not re-driven by box D3-g26): " + c["evidence"]
        cov.append(cc)

surv = [recs[k] for k in recs if recs[k]["class"] == "candidate"]
equiv = [recs[k] for k in recs if recs[k]["class"] == "equivalent-candidate"]
killed = [recs[k] for k in recs if recs[k]["class"] == "killed"]

nonf = []
for r in killed:
    nonf.append({"claim": r["non_finding"]["claim"], "command": r["non_finding"]["command"], "value": r["non_finding"]["value"]})
for r in equiv:
    nonf.append({"claim": r["non_finding"]["claim"], "command": r["non_finding"]["command"],
                 "value": r["non_finding"]["value"] + f" | gate {r['gate']['verdict']} gate_rc {r['gate']['gate_rc']}"})

harn = ["dev/audit/rounds/round11/D3/s1/fullgate.py", f"{PDIR}/g26_common.py"]
for row in keys:
    p = W / "probes" / f"probe_{row[0]}.py"
    if p.exists() and recs.get(row[0], {}).get("class") in ("candidate", "equivalent-candidate"):
        harn.append(f"{PDIR}/probe_{row[0]}.py")

unf = []
for g in timeouts:
    r = recs.get(g["key"], {})
    unf.append({"step": "D3.M3", "what": f"{g['key']} {g['site']}: TIMEOUT past the {r.get('timeout', {}).get('cap_s', 14400)} s cap; last script in the log: {r.get('timeout', {}).get('last_script')}"})
for g in missing:
    if g not in timeouts:
        unf.append({"step": "D3.M3", "what": f"{g['key']} {g['site']}: {g['verdict']}, class {g['class']}"})

report = {
    "dimension": "D3",
    "baseline_sha": BASE,
    "box": "D3-g26",
    "report_path": REL + "/REPORT.md",
    "exposure": ("Box D3-g26 (resumed from a predecessor seat's wip checkpoint ff992c67 on handoff-wip/finder-r11-D3-g26: null gate and 9 gates, "
                 "probes and per-key step-4 notes restored, never redone). Read the dispatch brief, the D3 s1 evidence archived from e3cb5c01 "
                 "(fullgate.py, state/results/complete, the u1 slice reports and M4 answers, earlier boxes' probes), the 47 dispatch refs' keys.tsv "
                 "for the box map; no GitHub reads, no register, no round11/J, no verifier report."),
    "coverage": cov,
    "unfinished": unf,
    "findings": [],
    "non_findings": nonf,
    "harnesses": harn,
    "leads": [],
    "gated": gated,
    "gate_survivors": surv,
    "equivalent_candidates": equiv,
}
(W / "REPORT.json").write_text(json.dumps(report, indent=1) + "\n")

# ---- markdown
tally = {}
for g in gated:
    tally[g["verdict"]] = tally.get(g["verdict"], 0) + 1
kb = {}
for r in killed:
    for s in r.get("killed_by") or []:
        kb[s] = kb.get(s, 0) + 1
md = [f"# Round 11 D3-s1, box D3-g26: full gate of {len(keys)} D3.M3 full-net survivors", "",
      f"Baseline `{BASE}`. Every count below is final; every wall, CPU and load number is provisional (nproc 4; the judge re-takes it).", "",
      "## Machine and controls", "", "```", machine.rstrip(), "```", "",
      f"Null control (`fullgate.py null`, a comment-only marker, through `gate_wave.sh null`): gate_rc {null['gate_rc']}, wall {null['wall_s']} s, "
      f"load1 {null['load1_start']}..{null['load1_end']}, red scripts {', '.join(null['failed_scripts'])} with fail lines {json.dumps(null['fail_lines'])}. "
      "All three are artefact checks reading no production file (closure.py selftest merge-tool pins, entities.py branch environment, "
      "harness_headers.py on a round-4 D6 harness whose docs the finder-wall strip removes); the same three as D3-rem's usable null. Usable, not re-taken. "
      "A key is KILLED only on a red script beyond this null or more FAIL lines in one.", "",
      "Procedure: `gate_wave.sh run` (the dispatch ref's driver) runs `fullgate.py run --src complete --key <key>` "
      "(GATE_SCOPE=full GOLDEN_MODE=drift GATE_JOBS=1 ./tests/run.sh) for each key of keys.tsv in order, one gate at a time, capped at 4 h. "
      "Probes run in a separate baseline worktree (never the gate's tree), each applying its one-line mutant in memory and printing "
      "`RESULT <metric>=<value>` for the baseline and the mutant.", "",
      "This box was resumed: a predecessor seat on another container took the null and the first nine gates and wrote the probes; "
      "this seat restored them from the wip checkpoint, re-ran the nine probes (identical RESULT values) and took the remaining gates.", "",
      "## Tally", "",
      f"- gated: {sum(v for k, v in tally.items() if k != 'NOT-GATED')}/{len(keys)}",
      f"- KILLED: {tally.get('KILLED', 0)} ({', '.join(f'{s}: {n}' for s, n in kb.items()) or '-'})",
      f"- SURVIVED: {tally.get('SURVIVED', 0)}",
      f"- RED-AS-NULL: {tally.get('RED-AS-NULL', 0)}",
      f"- TIMEOUT: {tally.get('TIMEOUT', 0)}",
      f"- candidates (gate survivors whose probe moves): {len(surv)}",
      f"- equivalent-candidates: {len(equiv)}", "",
      "| key | site | verdict | killed_by | class |", "|---|---|---|---|---|"]
for g in gated:
    md.append(f"| {g['key']} | {g['site']} | {g['verdict']} | {', '.join(g['killed_by']) or '-'} | {g['class']} |")
md += ["", "## Survivors: step-4 answers", ""]
for r in surv + equiv:
    p = r["probe"]
    md.append(f"### {r['key']} ({r['class']}) — {r['site']}")
    md.append("")
    para = (f"`{r['patch']}` in `{r['function']}`. Gate {r['gate']['verdict']} (gate_rc {r['gate']['gate_rc']}, wall {r['gate']['wall_s']} s provisional). "
            f"Probe `{p['path']}` (`{p['command']}`): {p['metric']} ({p['unit']}) baseline {p['baseline_value']}, mutant {p['mutant_value']}. "
            f"Inputs tried: {'; '.join(p['inputs_tried'])}. Should fail: {r['should_fail']['script']}: {r['should_fail']['assertion']}.")
    if r["class"] == "candidate":
        para += f" Candidate: {r['finding']['title']}."
    else:
        para += " Equivalent-candidate: a non-finding unless a later seat finds a distinguishing input reachable through production."
    md += [para, ""]
md += ["## Killed", ""]
for r in killed:
    md.append(f"- {r['key']} {r['site']}: {r['non_finding']['value']}; fail lines {json.dumps(r.get('fail_lines', {}))}")
md += ["", "## Coverage", "", "D3.M1, D3.M2, D3.M4, D3.M5 and their redispatched C-items are carried verbatim from REPORT-D3-u1b.json. "
       f"D3.M3 is this wave's: universe 742, examined {examined} here; the other keys are assigned by box (D3-g01..D3-g47) under not_reached.", "",
       "## Unfinished", ""]
md += [f"- {u['what']}" for u in unf] or ["- none"]
md += ["", "findings: [] — the wave's candidates go under `gate_survivors` for the orchestrator's cross-box id assignment."]
(W / "REPORT.md").write_text("\n".join(md) + "\n")
print(f"REPORT gated={len(gated)} examined={examined} candidates={len(surv)} equiv={len(equiv)} killed={len(killed)} timeouts={len(timeouts)} missing={len(missing)}")
