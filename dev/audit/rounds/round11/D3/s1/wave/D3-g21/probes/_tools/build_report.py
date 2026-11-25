#!/usr/bin/env python3
"""build_report.py: box D3-g21's REPORT.json and REPORT.md from keys.tsv, gates/, results/,
REPORT-D3-u1b.json's carried coverage rows and the 47 wave boxes' keys.tsv (dir in argv[1],
fetched from each dispatch/finder-r11-D3-gNN tip)."""
import json, sys
from pathlib import Path

BOXKEYS = Path(sys.argv[1])
S1 = Path.home() / "audit-r11-D3-s1/dev/audit/rounds/round11/D3/s1"
W = S1 / "wave/D3-g21"
REL = "dev/audit/rounds/round11/D3/s1/wave/D3-g21"
BASE = "92d38ecb640bd462f2e19c0814d0f0b7df1ee692"

keys = [l.split("\t") for l in (W / "keys.tsv").read_text().splitlines()[1:] if l.strip()]
res, gated, missing = {}, [], []
for row in keys:
    k = row[0]
    p = W / "results" / f"{k}.json"
    if p.exists():
        res[k] = json.loads(p.read_text())
    else:
        missing.append(k)
for row in keys:
    k = row[0]
    if k in res:
        r = res[k]
        gated.append({"key": k, "site": r["site"], "verdict": r["gate"]["verdict"],
                      "killed_by": r["gate"].get("killed_by") or [], "class": r["class"]})

u1b = json.loads((S1 / "REPORT-D3-u1b.json").read_text())
carried = []
for c in u1b["coverage"]:
    if c["step"] == "D3.M3":
        continue
    c = dict(c)
    c["evidence"] = "carried verbatim from dev/audit/rounds/round11/D3/s1/REPORT-D3-u1b.json (box D3-u1b): " + c["evidence"]
    c["carried"] = True
    carried.append(c)
m3_old = next(c for c in u1b["coverage"] if c["step"] == "D3.M3")

not_reached = []
for f in sorted(BOXKEYS.glob("g*.tsv")):
    box = "D3-" + f.stem
    if box == "D3-g21":
        continue
    ks = [l.split("\t")[0] for l in f.read_text().splitlines()[1:] if l.strip()]
    not_reached.append(f"assigned to box {box}: {len(ks)} key(s) {', '.join(ks)}")
timeouts = [k for k in res if res[k]["class"] == "timeout"]
for k in timeouts:
    not_reached.append(f"TIMEOUT on this box (D3-g21): {k} ({res[k]['site']}), past the {res[k].get('cap_s', 14400)} s cap")
for k in missing:
    not_reached.append(f"not gated on this box (D3-g21): {k}")
examined = len(gated) - len(timeouts)
universe = 742
m3 = {"step": "D3.M3",
      "enumerator": "awk -F'\\t' '$6==\"gate\"' SURVIVORS.tsv (the wave list, 742 keys; the same keys are the union of keys.tsv on the 47 dispatch/finder-r11-D3-g01..g47 tips)",
      "universe": universe, "examined": examined, "not_reached": not_reached,
      "redispatched": m3_old.get("redispatched", []),
      "evidence": ("box D3-g21 full gates: python3 dev/audit/rounds/round11/D3/s1/fullgate.py run --src complete --key <key> "
                   "(GATE_SCOPE=full GOLDEN_MODE=drift GOLDEN_REF=" + BASE + " GATE_JOBS=1 ./tests/run.sh), one gate at a time via gate_wave.sh run; "
                   "records " + ", ".join(f"{REL}/gates/{k}.json" for k in res) + "; null control " + REL + "/gates/null.json. "
                   "examined counts this box's gated keys with a verdict; the earlier boxes' D3.M3 gates (D3-top6, D3-rem) cover the 8 keys deduped out of the 742 and are their reports' rows. "
                   "Redispatched C-items carried from REPORT-D3-u1b.json's D3.M3 row.")}

def nf_killed(r):
    return {"claim": f"mutant {r['key']} at {r['site']} ({r['patch']}) is KILLED by the full gate: {', '.join(r['gate'].get('killed_by') or [])}",
            "command": f"python3 dev/audit/rounds/round11/D3/s1/fullgate.py run --src complete --key {r['key']}",
            "value": f"verdict=KILLED gate_rc={r['gate']['gate_rc']} killed_by={r['gate'].get('killed_by')}"}

non_findings = [{"claim": "null control: the full gate on the unmutated baseline tree (comment-only marker) on this box",
                 "command": "python3 dev/audit/rounds/round11/D3/s1/fullgate.py null",
                 "value": json.dumps({k: json.loads((W / 'gates/null.json').read_text()).get(k) for k in ('gate_rc', 'failed_scripts', 'fail_lines', 'wall_s')})}]
for k, r in res.items():
    if r["class"] == "killed":
        non_findings.append(nf_killed(r))
    elif r["class"] == "equivalent-candidate":
        p = r["probe"]
        non_findings.append({"claim": f"mutant {k} at {r['site']} ({r['patch']}) survives the full gate ({r['gate']['verdict']}); equivalent-candidate: {r.get('note', '')}",
                             "command": p["command"],
                             "value": "; ".join(f"{a}={b}" for a, b in p["results"].items()) + f"; inputs tried: {' | '.join(p['inputs_tried'])}"})

harnesses = ["dev/audit/rounds/round11/D3/s1/fullgate.py"]
harnesses += sorted(f"{REL}/probes/{p.name}" for p in (W / "probes").glob("probe_*.py"))
harnesses += sorted(f"{REL}/probes/_tools/{p.name}" for p in (W / "probes/_tools").glob("*.py") if p.name != "build_report.py") + [f"{REL}/probes/_tools/build_report.py"]

unfinished = [{"step": "D3.M3", "what": f"TIMEOUT: {k} ({res[k]['site']}) past the {res[k].get('cap_s', 14400)} s cap; last script running: {res[k].get('last_script', 'see gate log')}"} for k in timeouts]
unfinished += [{"step": "D3.M3", "what": f"not gated: {k}"} for k in missing]

cands = [res[k] for k in res if res[k]["class"] == "candidate"]
equivs = [res[k] for k in res if res[k]["class"] == "equivalent-candidate"]
rep = {"dimension": "D3", "baseline_sha": BASE, "box": "D3-g21", "report_path": f"{REL}/REPORT.md",
       "exposure": ("No docs/ or GitHub read. Read COMMON.md, D3.md, dev/audit/README.md, finding.schema.json and the carried slice reports and probes in the stripped "
                    "worktree, this box's dispatch/inbox/wip refs, and the other 46 wave boxes' dispatch keys.tsv only to name their keys under not_reached. "
                    "Re-fire: resumed from handoff-wip/finder-r11-D3-g21 @ d9d4e225 (8 of 16 gated, the null control and all 16 probes executed on the first machine); "
                    "gates 9-16 ran on a second machine (nproc 4, Intel Xeon @ 2.30GHz) against the restored null."),
       "coverage": carried[:2] + [m3] + carried[2:], "unfinished": unfinished, "findings": [],
       "non_findings": non_findings, "harnesses": harnesses, "leads": [],
       "gated": gated, "gate_survivors": cands, "equivalent_candidates": equivs}
(W / "REPORT.json").write_text(json.dumps(rep, indent=1) + "\n")

tally = {}
for g in gated:
    tally[g["verdict"]] = tally.get(g["verdict"], 0) + 1
null = json.loads((W / "gates/null.json").read_text())
md = [f"# D3-s1 wave box D3-g21: full gate for 16 D3.M3 full-net survivors", "",
      f"Baseline `{BASE}`. Seat D3-s1, round 11. Procedure: `gate_wave.sh` (dispatch tip of dispatch/finder-r11-D3-g21) runs "
      "`dev/audit/rounds/round11/D3/s1/fullgate.py run --src complete --key <key>` per key of keys.tsv, one gate at a time "
      "(`GATE_SCOPE=full GOLDEN_MODE=drift GATE_JOBS=1 ./tests/run.sh`), capped at 14400 s.", "",
      "## Machine and controls", "",
      "First machine (null and gates 1-8): nproc 4, Intel Xeon @ 2.10GHz, 16 GB. Re-fire machine (gates 9-16): nproc 4, Intel Xeon @ 2.30GHz, 16 GB. "
      f"See `{REL}/MACHINE.txt`. All wall, CPU and load numbers are provisional: true (the judge re-takes them).", "",
      f"Null control `{REL}/gates/null.json`: gate_rc {null.get('gate_rc')}, red scripts {null.get('failed_scripts')}, fail lines {null.get('fail_lines')}, "
      f"wall {null.get('wall_s')} s. All three are artefact checks (see `gates/null-note.txt`); usable, not re-taken.", "",
      "## Tally", "",
      f"- gated: {len(gated)} of {len(keys)}; " + ", ".join(f"{v} {n}" for v, n in sorted(tally.items())),
      f"- KILLED: {sum(1 for g in gated if g['verdict']=='KILLED')}" + "".join(f"; {g['key']} by {', '.join(g['killed_by'])}" for g in gated if g['verdict'] == 'KILLED'),
      f"- candidates (survive, probe moves): {len(cands)}: " + ", ".join(r['key'] for r in cands),
      f"- equivalent-candidates: {len(equivs)}: " + ", ".join(r['key'] for r in equivs),
      f"- TIMEOUT: {len(timeouts)}" + (": " + ", ".join(timeouts) if timeouts else ""), "",
      "Findings: [] by the brief; candidates are under `gate_survivors` for the orchestrator's id assignment.", "",
      "## Per key", ""]
for row in keys:
    k = row[0]
    r = res.get(k)
    if not r:
        md += [f"### {k}", "", "not gated (unfinished).", ""]
        continue
    g = r["gate"]
    md += [f"### {k} — {r['site']} ({r['class']})", "",
           f"`{r['patch']}` in `{r['function']}`. Gate: {g['verdict']} (gate_rc {g['gate_rc']}, wall {g.get('wall_s')} s, load1 {g.get('load1_start')}..{g.get('load1_end')}, provisional), "
           f"red scripts {g.get('failed_scripts')} = the null's; more fails than null: {g.get('more_fails_than_null')}.", ""]
    if "probe" in r:
        p = r["probe"]
        md += [f"Step 4: probe `{p['path']}` (`{p['command']}`), metric: {p['metric']}. Baseline {p['baseline_name']}={p['baseline_value']}, "
               f"mutant {p['mutant_name']}={p['mutant_value']}. All RESULT lines: " + "; ".join(f"{a}={b}" for a, b in p["results"].items()) + ".",
               "", "Inputs tried: " + " | ".join(p["inputs_tried"]) + ".", "", f"Should fail: {r.get('should_fail')}.", ""]
        if r["class"] == "candidate":
            md += [f"Candidate: {r.get('title')}. Severity claimed {r.get('severity_claimed')}; {r.get('perturbation', {}).get('expected_direction', '')}.", ""]
        else:
            md += [f"Equivalent-candidate: {r.get('note', '')}", ""]
md += ["## Harnesses", ""] + [f"- `{h}`" for h in harnesses] + ["- `gate_wave.sh` (out of tree, dispatch tip): the per-key driver named above", "",
       "## Unfinished", ""] + ([f"- {u['what']}" for u in unfinished] or ["- none"]) + ["", "## Exposure", "", rep["exposure"], ""]
(W / "REPORT.md").write_text("\n".join(md))
print(f"REPORT gated={len(gated)} candidates={len(cands)} equivalent={len(equivs)} timeouts={len(timeouts)} missing={len(missing)}")
