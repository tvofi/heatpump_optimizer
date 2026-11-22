#!/usr/bin/env python3
"""REPORT.json and REPORT.md for box D3-g10 (seat D3-s1), from results/*.json and the gate records."""
import glob, json, os, collections
TR = os.path.expanduser("~/audit-r11-D3-s1")
S1 = f"{TR}/dev/audit/rounds/round11/D3/s1"
W = f"{S1}/wave/D3-g10"
REL = "dev/audit/rounds/round11/D3/s1/wave/D3-g10"
BASE = "92d38ecb640bd462f2e19c0814d0f0b7df1ee692"
keys = [l.split("\t")[0] for l in open(f"{W}/keys.tsv").read().splitlines()[1:]]
recs = {k: json.load(open(f"{W}/results/{k}.json")) for k in keys if os.path.exists(f"{W}/results/{k}.json")}
null = json.load(open(f"{W}/gates/null.json"))
mach = open(f"{W}/MACHINE.txt").read()
u1b = json.load(open(f"{S1}/REPORT-D3-u1b.json"))
EXTRA_UNFINISHED = json.loads(os.environ.get("EXTRA_UNFINISHED", "[]"))

# --- coverage: u1b's M1/M2/M4/M5 carried verbatim; M3 is this wave's ---
cov = []
for r in u1b["coverage"]:
    r = dict(r)
    if r["step"] == "D3.M3":
        continue
    r["evidence"] = "carried verbatim from REPORT-D3-u1b.json (not re-driven on box D3-g10): " + r["evidence"]
    cov.append(r)
others = []
for f in sorted(glob.glob(os.path.expanduser("~/wavekeys/g*.tsv"))):
    box = "D3-" + os.path.basename(f)[:-4]
    if box == "D3-g10":
        continue
    ks = [l.split("\t") for l in open(f).read().splitlines()[1:]]
    sites = sorted({f"{x[2].split('/')[-1]}:{x[3]}" for x in ks})
    others.append((box, len(ks), f"assigned to box {box}: {len(ks)} keys ({', '.join(x[0] for x in ks)})"))
gated = [k for k in keys if k in recs and recs[k]["class"] != "timeout"]
timeouts = [k for k in keys if k in recs and recs[k]["class"] == "timeout"]
missing = [k for k in keys if k not in recs]
nr = [o[2] for o in others] + [f"TIMEOUT on box D3-g10 (4 h cap, no verdict): {k} {recs[k]['site']}" for k in timeouts] \
     + [f"not gated on box D3-g10 (stopped/skipped): {k}" for k in missing]
m3old = [r for r in u1b["coverage"] if r["step"] == "D3.M3"][0]
cov.insert(2, {
    "step": "D3.M3",
    "enumerator": "awk -F'\\t' '$6==\"gate\"' SURVIVORS.tsv",
    "universe": 742,
    "examined": len(gated),
    "not_reached": nr,
    "redispatched": m3old.get("redispatched", []),
    "evidence": (f"box D3-g10 gated {len(gated)} of its {len(keys)} keys with a verdict through gate_wave.sh run -> "
                 f"`fullgate.py run --src complete --key <key>` (GATE_SCOPE=full GOLDEN_MODE=drift GOLDEN_REF={BASE} GATE_JOBS=1 ./tests/run.sh), "
                 f"one gate at a time, records {REL}/gates/<key>.json, null control {REL}/gates/null.json (`fullgate.py null`). "
                 f"The other 726 wave keys are named by box (D3-g01..D3-g47 key lists read from each dispatch/finder-r11-D3-gNN keys.tsv; 742 in all). "
                 f"The earlier boxes' D3.M3 rows (D3-top6 and D3-rem full gates; the u1a..u1d full nets) cover the 8 keys deduped out of this wave and are "
                 f"carried by reference in their own reports, not counted in this 742-key universe. Redispatched items are u1b's, carried verbatim.")
})

tally = collections.Counter(r["gate"]["verdict"] for r in recs.values())
killers = collections.Counter(s for r in recs.values() if r["class"] == "killed" for s in (r.get("killed_by") or []))
cands = [recs[k] for k in keys if k in recs and recs[k]["class"] == "candidate"]
equivs = [recs[k] for k in keys if k in recs and recs[k]["class"] == "equivalent-candidate"]
nonf = []
for k in keys:
    r = recs.get(k)
    if not r:
        continue
    if r["class"] == "killed":
        nonf.append({"claim": f"full gate KILLED {k} {r['site']} ({r['patch']}): the suite fails on it",
                     "command": r["gate_command"],
                     "value": f"killed_by={','.join(r.get('killed_by') or [])}; gate_rc={r['gate']['gate_rc']}; wall {r['gate']['wall_s']} s, load1 {r['gate']['load1_start']}..{r['gate']['load1_end']} (provisional)"})
    elif r["class"] == "equivalent-candidate":
        nonf.append({"claim": f"equivalent-candidate {k} {r['site']}: no input moved the probe", "command": r["probe"]["command"],
                     "value": f"baseline {r['probe']['baseline']} == mutant {r['probe']['mutant']}; inputs tried: {r['probe']['inputs_tried']}"})
unfinished = [{"step": "D3.M3", "what": f"TIMEOUT key {k} {recs[k]['site']} ({recs[k]['patch']}): the full gate passed the {recs[k]['timeout']['cap_s']} s cap; last script the log shows: {recs[k]['timeout']['last_script_seen']}; neither KILLED nor SURVIVED"} for k in timeouts]
unfinished += [{"step": "D3.M3", "what": f"key {k} not gated on box D3-g10"} for k in missing] + EXTRA_UNFINISHED
harn = ["dev/audit/rounds/round11/D3/s1/fullgate.py"] + [f"{REL}/probes/probe_{k}.py" for k in keys if os.path.exists(f"{W}/probes/probe_{k}.py")]
gated_rows = [{"key": k, "site": recs[k]["site"], "verdict": recs[k]["gate"]["verdict"], "killed_by": recs[k]["gate"].get("killed_by") or [],
               "class": recs[k]["class"]} for k in keys if k in recs]
rep = {
    "dimension": "D3", "baseline_sha": BASE, "box": "D3-g10", "seat": "D3-s1",
    "report_path": f"{REL}/REPORT.md",
    "exposure": ("No docs/ or GitHub API read. Read per the brief: COMMON.md, D3.md, dev/audit/README.md, the u1 slice reports, "
                 "REPORT-D3-top6.md / REPORT-D3-rem.md (method pattern), the carried M4 answers for this box's keys, and state/reach.tsv "
                 "(traced baseline: which closure scripts execute each line). The other boxes' keys.tsv were read from their "
                 "dispatch/finder-r11-D3-gNN refs only to name not_reached by box; none of their gates was run. "
                 "$HOME/venv-ci does not exist on this box: gate_wave.sh's PATH entry is inert and python3 resolves to /opt/hpo/venv-ci "
                 "(the session-start toolchain line: OK)."),
    "coverage": cov, "unfinished": unfinished, "findings": [], "non_findings": nonf, "harnesses": harn,
    "harness_procedure": "gate_wave.sh (dispatch/finder-r11-D3-g10 tip): null once, then fullgate.py run per key in keys.tsv order, one gate at a time, 4 h cap (TIMEOUT), checkpoint after each",
    "leads": [], "gated": gated_rows, "gate_survivors": cands, "equivalent_candidates": equivs,
    "null_control": {"command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/fullgate.py null", "record": f"{REL}/gates/null.json",
                     "gate_rc": null.get("gate_rc"), "failed_scripts": null.get("failed_scripts"), "fail_lines": null.get("fail_lines"),
                     "wall_s": null.get("wall_s"), "load1": [null.get("load1_start"), null.get("load1_end")], "summary": null.get("summary")},
}
# --- markdown ---
L = [f"# D3-s1, box D3-g10: the full gate for 16 D3.M3 full-net survivors", "",
     f"Baseline {BASE}. Walls and loads provisional; counts final.", "", "## Machine and controls", "", "```", mach.strip(), "```", "",
     f"Null control (`fullgate.py null`, comment-only marker): gate_rc={null.get('gate_rc')}, failed_scripts={null.get('failed_scripts')}, "
     f"fail_lines={null.get('fail_lines')}, wall {null.get('wall_s')} s, load1 {null.get('load1_start')}..{null.get('load1_end')}. "
     "RED-AS-NULL = red, but no script beyond the null's (read as survived).", "",
     "Procedure: gate_wave.sh run -> fullgate.py run --src complete --key <key> (GATE_SCOPE=full GOLDEN_MODE=drift GATE_JOBS=1 ./tests/run.sh), one at a time, 4 h cap. "
     "Probes apply each mutant in memory (the method recompiled from its own source, attached by mock.patch.object for the mutant arm) and ran from a separate "
     "baseline worktree, never the gate tree.", "", "## Tally", "",
     f"- gated: {len(recs)} of {len(keys)} (with a verdict: {len(gated)})",
     f"- KILLED: {tally.get('KILLED', 0)}" + (f" ({', '.join(f'{s} {n}' for s, n in killers.items())})" if killers else ""),
     f"- SURVIVED: {tally.get('SURVIVED', 0)}", f"- RED-AS-NULL: {tally.get('RED-AS-NULL', 0)}", f"- TIMEOUT: {tally.get('TIMEOUT', 0)}",
     f"- candidates: {len(cands)}", f"- equivalent-candidates: {len(equivs)}", "",
     "| key | site | patch | verdict | killed_by | wall s | load1 | class |", "|---|---|---|---|---|---|---|---|"]
for k in keys:
    r = recs.get(k)
    if not r:
        L.append(f"| {k} | | | not gated | | | | |"); continue
    g = r["gate"]
    L.append(f"| {k} | {r['site']} | `{r['patch']}` | {g['verdict']} | {','.join(g.get('killed_by') or []) or '-'} | {g.get('wall_s')} | {g.get('load1_start')}..{g.get('load1_end')} | {r['class']} |")
L += ["", "## Survivors: the step-4 answer and the probe", ""]
for r in cands + equivs:
    f = r.get("finding", {})
    L += [f"### {r['key']} {r['site']} ({r['class']})", "",
          f"`{r['patch']}` in {r['function']}. Gate: {r['gate']['verdict']} (gate_rc {r['gate']['gate_rc']}).",
          f"Probe `{r['probe']['command']}`: baseline {r['probe']['baseline']}, mutant {r['probe']['mutant']}; inputs tried: {'; '.join(r['probe']['inputs_tried'])}.",
          f"Should have failed: {', '.join(r['should_fail']['scripts_executing_line'])} execute the line (reach.tsv); {r['should_fail']['assertion_lacking']}.",
          (f"Candidate: {f.get('title')} (severity claimed {f.get('severity_claimed')}, class_guess {f.get('class_guess')})." if f else ""), ""]
L += ["## KILLED (non-findings)", ""] + [f"- {n['claim']}: `{n['command']}` -> {n['value']}" for n in nonf if 'KILLED' in n['claim']] + [""]
L += ["## Unfinished", ""] + ([f"- {u['what']}" for u in unfinished] or ["- none"]) + [""]
L += ["## Harnesses", ""] + [f"- {h}" for h in harn] + [f"- gate_wave.sh procedure: {rep['harness_procedure']}", ""]
L += ["## Exposure", "", rep["exposure"], ""]
md = "\n".join(L)
rep["report_md"] = md
open(f"{W}/REPORT.md", "w").write(md)
json.dump(rep, open(f"{W}/REPORT.json", "w"), indent=1)
print(f"REPORT written: gated {len(recs)}, tally {dict(tally)}, candidates {len(cands)}, equivalents {len(equivs)}, unfinished {len(unfinished)}")
