# Metric: REPORT.json / REPORT.md of box D3-g07 (seat D3-s1, round 11), assembled from the box's
#   per-key records results/<key>.json, its gates/null.json, REPORT-D3-u1b.json's carried coverage rows
#   and the wave's key->box map (each dispatch/finder-r11-D3-gNN ref's keys.tsv).
# Command: python3 dev/audit/rounds/round11/D3/s1/wave/D3-g07/tools/build_report.py <boxmap.tsv>   (cwd = tree root)
# Expected: one gated row per key of keys.tsv (16); D3.M3 universe 742, examined 16, not_reached = the 46
#   other boxes' key sets; candidates under gate_survivors, equivalent-candidates under equivalent_candidates.
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g07 (see MACHINE.txt).
# Instrumented symbol: none (an assembler; every number it writes is read from a gate or probe record).
# Perturbation: none; it refuses a key with no record.
import json, sys
from collections import defaultdict
from pathlib import Path

BASE = "92d38ecb640bd462f2e19c0814d0f0b7df1ee692"
S1 = Path("dev/audit/rounds/round11/D3/s1")
W = S1 / "wave/D3-g07"
REL = str(W)

keys = [l.split("\t") for l in (W / "keys.tsv").read_text().splitlines()[1:] if l.strip()]
recs = {}
for row in keys:
    p = W / "results" / f"{row[0]}.json"
    if not p.exists():
        raise SystemExit(f"REFUSE no record for {row[0]}")
    recs[row[0]] = json.loads(p.read_text())

boxmap = defaultdict(list)
for l in Path(sys.argv[1]).read_text().splitlines():
    b, k = l.split("\t")
    boxmap[b].append(k)
universe = sum(len(v) for v in boxmap.values())
assert sorted(boxmap["D3-g07"]) == sorted(recs), "keys.tsv is not this box's map entry"

null = json.loads((W / "gates/null.json").read_text())
u1b = json.loads((S1 / "REPORT-D3-u1b.json").read_text())
cov = []
for r in u1b["coverage"]:
    if r["step"] == "D3.M3":
        continue
    r = dict(r)
    r["carried"] = "REPORT-D3-u1b.json (box D3-u1b), verbatim"
    cov.append(r)
m3_old = next(r for r in u1b["coverage"] if r["step"] == "D3.M3")

timeouts = [k for k, r in recs.items() if r["gate"]["verdict"] == "TIMEOUT"]
examined = len(recs) - len(timeouts)
not_reached = [f"{len(v)} keys assigned to box {b} ({', '.join(sorted(v)[:2])}, ...)"
               for b, v in sorted(boxmap.items()) if b != "D3-g07"]
not_reached += [f"{k} TIMEOUT on box D3-g07 (past the 4 h cap)" for k in timeouts]
m3 = {
    "step": "D3.M3",
    "enumerator": "awk -F'\\t' '$6==\"gate\"' SURVIVORS.tsv",
    "universe": universe,
    "examined": examined,
    "not_reached": not_reached,
    "redispatched": m3_old.get("redispatched", []),
    "evidence": (f"box D3-g07 gated {examined} of its {len(recs)} keys with "
                 f"`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/fullgate.py run --src complete --key <key>` "
                 f"(gate_wave.sh run; records {REL}/gates/<key>.json, per-key {REL}/results/<key>.json); "
                 f"null control {REL}/gates/null.json (gate_rc {null['gate_rc']}, fail lines {json.dumps(null['fail_lines'])}). "
                 f"The wave list (742 keys, the 746 u1 full-net survivors less 8 gated by D3-top6/D3-rem, plus timeouts and the leak, "
                 f"deduplicated) is split over boxes D3-g01..D3-g47; the key->box map is each dispatch/finder-r11-D3-gNN ref's keys.tsv. "
                 f"Earlier D3.M3 rows carried: REPORT-D3-u1b.json's row (universe {m3_old['universe']}, examined {m3_old['examined']}), "
                 f"D3-top6/D3-rem full gates (REPORT-D3-rem.json)."),
}
cov.insert([r["step"] for r in cov].index("D3.M4") if any(r["step"] == "D3.M4" for r in cov) else len(cov), m3)

gated, survivors, equivs, nonf, unfinished = [], [], [], [], []
harn = [f"{S1}/fullgate.py", f"{REL}/tools/build_record.py", f"{REL}/tools/build_report.py"]
for row in keys:
    k = row[0]
    r = recs[k]
    g = r["gate"]
    gated.append({"key": k, "site": r["site"], "verdict": g["verdict"], "killed_by": g.get("killed_by", []),
                  "class": r["class"]})
    if r.get("probe", {}).get("path"):
        harn.append(r["probe"]["path"])
    if r["class"] == "candidate":
        survivors.append(r)
    elif r["class"] == "equivalent-candidate":
        equivs.append(r)
        pr = r["probe"]
        nonf.append({"claim": f"full gate {k} {r['site']} ({r['patch']}): {g['verdict']}, equivalent-candidate: "
                              f"no input found that moves {pr['baseline_result']} (tried: {pr['inputs_tried']})",
                     "command": pr["command"],
                     "value": f"{pr['baseline_result']}={pr['baseline_value']} baseline, {pr['mutant_value']} mutant; "
                              f"gate wall {g['wall_s']} s, load1 {g.get('load1_start')}..{g.get('load1_end')} (provisional)"})
    elif r["class"] == "killed":
        nonf.append({"claim": f"full gate {k} {r['site']} ({r['patch']}): KILLED by {', '.join(g.get('killed_by') or [])}",
                     "command": r["gate_command"],
                     "value": f"gate_rc {g['gate_rc']}; fail lines {json.dumps(g.get('fail_lines', {}))} vs null "
                              f"{json.dumps(null['fail_lines'])}; failing checks: {json.dumps(r.get('failing_checks', []))[:600]}"})
    elif r["class"] == "timeout":
        unfinished.append({"step": "D3.M3", "what": f"{k} {r['site']}: TIMEOUT past the 4 h cap; last script running: "
                                                    f"{r.get('last_script', 'see gate log')}"})

harn = list(dict.fromkeys(harn))
tally = defaultdict(int)
for x in gated:
    tally[x["verdict"]] += 1
rep = {
    "dimension": "D3",
    "baseline_sha": BASE,
    "report_path": f"{REL}/REPORT.md",
    "box": "D3-g07",
    "exposure": "Slice reports REPORT-D3-u1{a,b,c,d}, REPORT-u1a, REPORT-D3-top6 and REPORT-D3-rem and the M4 answer files "
                "under dev/audit/rounds/round11/D3/s1/ read as the brief requires; the box's own wip checkpoint "
                "(handoff-wip/finder-r11-D3-g07) restored from a stalled predecessor seat; the dispatch refs' keys.tsv "
                "read for the key->box map; no GitHub reads, no register, no J/ or verifier report.",
    "coverage": cov,
    "unfinished": unfinished,
    "findings": [],
    "non_findings": nonf,
    "harnesses": harn,
    "leads": [],
    "gated": gated,
    "gate_survivors": survivors,
    "equivalent_candidates": equivs,
}
(W / "REPORT.json").write_text(json.dumps(rep, indent=1) + "\n")

machine = (W / "MACHINE.txt").read_text()
md = [f"# D3-s1 wave box D3-g07: full gate of 16 D3.M3 full-net survivors (round 11)", "",
      f"Baseline `{BASE}`. Every wall, CPU and load number is provisional: true (the judge re-takes it).", "",
      "## Machine and controls", "", "```", machine.strip(), "```", "",
      f"Null control (`fullgate.py null`, comment-only marker in tariff.py): gate_rc {null['gate_rc']}, "
      f"red scripts {', '.join(null['failed_scripts'])}, fail lines {json.dumps(null['fail_lines'])}, wall {null['wall_s']} s. "
      "All three are artefact checks that read no production cell file (gates/null-note.txt); a mutant is KILLED only by "
      "a script beyond the null or more failing checks in one.", "",
      "## Tally", "",
      f"Gated {len(gated)} of {len(keys)}: " + ", ".join(f"{v} {n}" for v, n in sorted(tally.items())) +
      f". Candidates {len(survivors)}, equivalent-candidates {len(equivs)}, timeouts {len(timeouts)}. findings: [] "
      "(ids are assigned by the orchestrator's consolidation step).", "",
      "| key | site | verdict | killed_by | class |", "|---|---|---|---|---|"]
for x in gated:
    md.append(f"| {x['key']} | {x['site']} | {x['verdict']} | {', '.join(x['killed_by']) or '-'} | {x['class']} |")
retake = W / "gates/7ec91efc2c6deffd.try1-note.txt"
if retake.exists():
    md += ["", "## Re-take of 7ec91efc2c6deffd", "", retake.read_text().strip()]
md += ["", "## Survivors: the step-4 answer per key", ""]
for r in survivors + equivs:
    pr = r["probe"]
    md += [f"### {r['key']} {r['site']} ({r['class']})", "",
           f"Patch `{r['patch']}` in {r['function']}. Gate {r['gate']['verdict']} (wall {r['gate']['wall_s']} s). "
           f"Probe `{pr['command']}`: {pr['baseline_result']}={pr['baseline_value']} on the baseline, "
           f"{pr['mutant_result']}={pr['mutant_value']} under the mutant. Inputs: {pr['inputs_tried']}. "
           f"Traced reach: {', '.join(r.get('traced_reach', [])) or 'none'}. Should fail: {r.get('should_fail', '')}"
           + (f" Finding candidate: {r['finding']['title']} (severity {r['finding'].get('severity_claimed')}, class {r['finding'].get('class_guess')})." if r.get("finding") else ""),
           ""]
for k in timeouts:
    md += [f"### {k} TIMEOUT", "", "Under unfinished.", ""]
(W / "REPORT.md").write_text("\n".join(md) + "\n")
print(f"RESULT gated={len(gated)} candidates={len(survivors)} equivalent={len(equivs)} killed={sum(1 for x in gated if x['class']=='killed')} timeouts={len(timeouts)}")
