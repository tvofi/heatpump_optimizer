#!/usr/bin/env python3
# Box D3-g24's REPORT.json / REPORT.md builder (step 4 of the box brief). Reads results/<key>.json (written by
# build_results.py), gates/null.json, the slice report REPORT-D3-u1b.json (carried coverage rows) and
# boxkeys/D3-g<NN>.tsv (each wave box's keys.tsv, taken from its dispatch ref, for the D3.M3 not_reached list).
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g24/build_report.py
import json, sys
from pathlib import Path

W = Path(__file__).resolve().parent
S1 = W.parents[1]
BOX = "D3-g24"
REL = f"dev/audit/rounds/round11/D3/s1/wave/{BOX}"
FG = "dev/audit/rounds/round11/D3/s1/fullgate.py"
BASE = "92d38ecb640bd462f2e19c0814d0f0b7df1ee692"

rows = (W / "keys.tsv").read_text().splitlines()
hdr = rows[0].split("\t")
keys = [dict(zip(hdr, l.split("\t"))) for l in rows[1:] if l.strip()]
recs = {}
for k in keys:
    p = W / "results" / f"{k['key']}.json"
    if p.exists():
        recs[k["key"]] = json.loads(p.read_text())
null = json.loads((W / "gates/null.json").read_text())
u1b = json.loads((S1 / "REPORT-D3-u1b.json").read_text())

gated = [k for k in keys if k["key"] in recs and recs[k["key"]]["class"] != "timeout"]
timeouts = [k["key"] for k in keys if k["key"] in recs and recs[k["key"]]["class"] == "timeout"]
missing = [k["key"] for k in keys if k["key"] not in recs]

others = []
for f in sorted((W / "boxkeys").glob("D3-g*.tsv")):
    b = f.stem
    if b == BOX:
        continue
    for l in f.read_text().splitlines()[1:]:
        if l.strip():
            c = l.split("\t")
            others.append(f"assigned to box {b}: {c[0]} {c[2].split('/')[-1]}:{c[3]} {c[8]}")
universe = len(others) + len(keys)

cov = []
for r in u1b["coverage"]:
    if r["step"] == "D3.M3":
        nr = others + [f"TIMEOUT on box {BOX} (4 h cap): {k}" for k in timeouts] + [f"not gated on box {BOX}: {k}" for k in missing]
        cov.append({"step": "D3.M3", "enumerator": "awk -F'\\t' '$6==\"gate\"' SURVIVORS.tsv",
                    "universe": universe, "examined": len(gated), "not_reached": nr,
                    "redispatched": r.get("redispatched", []),
                    "evidence": f"this box's wave list keys.tsv ({len(keys)} keys) of the 742-key wave (47 boxes' keys.tsv, {REL}/boxkeys/); per key `PYTHONPATH=tests/hastub python3 {FG} run --src complete --key <key>` (GATE_SCOPE=full GOLDEN_MODE=drift GATE_JOBS=1) recorded at {REL}/gates/<key>.json, null at {REL}/gates/null.json. Earlier boxes' D3.M3 rows (D3-top6, D3-rem; 8 deduped keys gated there) are theirs and are not re-counted here; redispatched items carried verbatim from REPORT-D3-u1b.json",
                    "carried": False})
    else:
        x = dict(r); x["carried"] = True
        x["evidence"] = f"carried verbatim from REPORT-D3-u1b.json (not re-driven by box {BOX}): " + str(r.get("evidence", ""))
        cov.append(x)

def gate_row(k):
    r = recs.get(k["key"])
    if not r:
        return {"key": k["key"], "site": f"{k['file']}:{k['line']} {k['kind']}", "verdict": None, "killed_by": [], "class": "not gated"}
    return {"key": k["key"], "site": r["site"], "verdict": r["gate"].get("verdict"), "killed_by": r["gate"].get("killed_by") or [], "class": r["class"]}

survivors = [recs[k["key"]] for k in keys if k["key"] in recs and recs[k["key"]]["class"] == "candidate"]
equiv = [recs[k["key"]] for k in keys if k["key"] in recs and recs[k["key"]]["class"] == "equivalent-candidate"]
killed = [recs[k["key"]] for k in keys if k["key"] in recs and recs[k["key"]]["class"] == "killed"]

nf = [{"claim": f"null control: a comment-only marker under the full gate on box {BOX} is red only on worktree/strip artefacts ({', '.join(null.get('failed_scripts', []))})",
       "command": f"PYTHONPATH=tests/hastub python3 {FG} null",
       "value": f"gate_rc={null.get('gate_rc')} fail_lines={json.dumps(null.get('fail_lines'))} wall_s={null.get('wall_s')} (provisional)"}]
nf += [r["non_finding"] for r in killed + equiv]

harn = [FG, f"{REL}/build_results.py", f"{REL}/build_report.py", "gate_wave.sh (out-of-tree box driver from dispatch/finder-r11-D3-g24: fullgate.py run per key, one at a time, 4 h cap)"]
harn += sorted({r["probe"]["path"] for r in recs.values() if r.get("probe")})
harn += [f"{REL}/probes/{p.name}" for p in sorted((W / "probes").glob("_*.py"))]

unfinished = [{"step": "D3.M3", "what": f"TIMEOUT on box {BOX}: {k} (4 h cap; last script {recs[k].get('timeout', {}).get('last_script_running')})"} for k in timeouts]
unfinished += [{"step": "D3.M3", "what": f"not gated on box {BOX}: {k}"} for k in missing]

tally = {}
for r in recs.values():
    tally[r["gate"].get("verdict")] = tally.get(r["gate"].get("verdict"), 0) + 1

machine = (W / "MACHINE.txt").read_text()
rep = {
    "dimension": "D3", "baseline_sha": BASE, "box": BOX, "seat": "D3-s1",
    "report_path": f"{REL}/REPORT.md",
    "exposure": "Read COMMON.md, D3.md, dev/audit/README.md, the u1 slice reports, REPORT-D3-top6/rem, keys.tsv's m4_source answers and the production lines of the 16 keys in the stripped baseline worktree; each wave box's keys.tsv from its dispatch ref (for the not_reached list only). No register, round11/J/, verifier report, docs/ or GitHub read. The box was resumed on a second machine after its first seat stalled at 8/16 gates: gates 1-8, the null and all probes ran on the first (Xeon @ 2.10GHz, 4 cores), gates 9-16 on the second (Xeon @ 2.30GHz, 4 cores); both in MACHINE.txt.",
    "coverage": cov, "unfinished": unfinished, "findings": [], "non_findings": nf, "harnesses": harn, "leads": [],
    "gated": [gate_row(k) for k in keys], "gate_survivors": survivors, "equivalent_candidates": equiv,
    "tally": tally,
}

md = [f"# D3-s1 wave box {BOX}: full gate for 16 D3.M3 full-net survivors", "",
      f"Baseline `{BASE}`. Seat D3-s1, round 11. Findings are returned as `gate_survivors` (ids assigned at consolidation).", "",
      "## Machine and controls", "", "```", machine.strip(), "```", "",
      f"Null control (`python3 {FG} null`, comment-only marker): gate_rc={null.get('gate_rc')}, failed scripts {null.get('failed_scripts')} with fail_lines {null.get('fail_lines')}, wall {null.get('wall_s')} s (provisional). Every one of these is an artefact of the stripped detached worktree (gates/null-note.txt); a key is KILLED only by a script beyond these or more FAIL lines in one.", "",
      "Wall, CPU and load numbers are provisional (nproc 4; load1 per gate in its record); counts are final.", "",
      "## Tally", "",
      f"- gated: {len(gated)}/{len(keys)}; verdicts: {tally}",
      f"- KILLED: {len(killed)}" + (": " + ", ".join(f"{r['key']} by {r['gate'].get('killed_by')}" for r in killed) if killed else ""),
      f"- TIMEOUT: {len(timeouts)} {timeouts if timeouts else ''}",
      f"- candidates (gate survivors that change behaviour): {len(survivors)}",
      f"- equivalent-candidates: {len(equiv)}", "",
      "| key | site | verdict | class | probe metric baseline -> mutant |", "|---|---|---|---|---|"]
for k in keys:
    r = recs.get(k["key"])
    if not r:
        md.append(f"| {k['key']} | {k['file'].split('/')[-1]}:{k['line']} | - | not gated | - |"); continue
    p = r.get("probe") or {}
    md.append(f"| {r['key']} | {r['site'].split('/')[-1]} | {r['gate'].get('verdict')} | {r['class']} | {p.get('metric','-')} {p.get('baseline_value','-')} -> {p.get('mutant_value','-')} |")
md += ["", "## Survivors, one paragraph each", ""]
for r in survivors + equiv:
    p = r["probe"]
    md.append(f"### {r['key']} ({r['class']})")
    md.append("")
    s = f"`{r['site']}` `{r['patch']}` in `{r['function']}`; full gate {r['gate']['verdict']} (gate_rc {r['gate']['gate_rc']}, wall {r['gate']['wall_s']} s, load1 {r['gate']['load1_start']}..{r['gate']['load1_end']}). Probe `{p['command']}`: {p['metric']} baseline {p['baseline_value']} -> mutant {p['mutant_value']}"
    if p.get("extra"):
        s += " (" + ", ".join(f"{a}={b}" for a, b in p["extra"].items()) + ")"
    s += f". Inputs tried: {p['inputs_tried']}."
    if r["class"] == "candidate":
        f = r["finding"]
        s += f" Step-4 answer: {f['claim']} Severity claimed {f['severity_claimed']}: {f['severity_consequence']}. Should have failed: {r['should_fail']['assertion_lacking']}."
        if p.get("moving_cases"):
            s += " Moving case: `" + p["moving_cases"][0] + "`."
    else:
        s += f" Step-4 answer: {r['equivalent_reason']}. A check that would distinguish it: {r['should_fail']['assertion_lacking']}."
    md += [s, ""]
if unfinished:
    md += ["## Unfinished", ""] + [f"- {u['what']}" for u in unfinished] + [""]
md += ["## Coverage", "", "D3.M1, D3.M2, D3.M4, D3.M5 and their redispatched items are carried verbatim from REPORT-D3-u1b.json. D3.M3 is this wave's row: universe "
       f"{universe} (the wave list), examined {len(gated)} (this box's gated keys), the other {len(others)} keys named under not_reached by their box.", ""]
rep["report_md"] = "\n".join(md)
(W / "REPORT.json").write_text(json.dumps(rep, indent=1) + "\n")
(W / "REPORT.md").write_text(rep["report_md"] + "\n")
print(f"REPORT keys={len(keys)} gated={len(gated)} candidates={len(survivors)} equiv={len(equiv)} killed={len(killed)} timeouts={len(timeouts)} missing={len(missing)} universe={universe}")
