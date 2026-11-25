#!/usr/bin/env python3
"""Box D3-g08: build wave/D3-g08/REPORT.json and REPORT.md from keys.tsv, gates/ and results/.

usage: build_report.py <dir holding the other boxes' keys.tsv as D3-gNN.tsv>
"""
import json, sys
from pathlib import Path

HOME = Path.home()
TR = HOME / "audit-r11-D3-s1"
S1 = TR / "dev/audit/rounds/round11/D3/s1"
W = S1 / "wave/D3-g08"
REL = "dev/audit/rounds/round11/D3/s1/wave/D3-g08"
BASE = "92d38ecb640bd462f2e19c0814d0f0b7df1ee692"
OTHER = Path(sys.argv[1])

lines = (W / "keys.tsv").read_text().splitlines()
hdr = lines[0].split("\t")
rows = [dict(zip(hdr, l.split("\t"))) for l in lines[1:] if l.strip()]
keys = [r["key"] for r in rows]
gates = {k: json.loads((W / "gates" / f"{k}.json").read_text()) for k in keys if (W / "gates" / f"{k}.json").exists()}
res = {k: json.loads((W / "results" / f"{k}.json").read_text()) for k in keys if (W / "results" / f"{k}.json").exists()}
null = json.loads((W / "gates/null.json").read_text())
u1b = json.loads((S1 / "REPORT-D3-u1b.json").read_text())

cov = []
for c in u1b["coverage"]:
    if c["step"] == "D3.M3":
        continue
    c = dict(c)
    c["carried"] = "carried verbatim from dev/audit/rounds/round11/D3/s1/REPORT-D3-u1b.json (not re-driven by box D3-g08)"
    cov.append(c)
m3_old = next(c for c in u1b["coverage"] if c["step"] == "D3.M3")

not_reached = []
for f in sorted(OTHER.glob("D3-g*.tsv")):
    box = f.stem
    if box == "D3-g08":
        continue
    ol = f.read_text().splitlines()
    oh = ol[0].split("\t")
    for l in ol[1:]:
        if not l.strip():
            continue
        r = dict(zip(oh, l.split("\t")))
        not_reached.append(f"assigned to box {box}: {r['key']} {r['file']}:{r['line']} {r['kind']}")
timeouts = [k for k in keys if gates.get(k, {}).get("verdict") == "TIMEOUT"]
ungated = [k for k in keys if k not in gates]
for k in timeouts:
    r = next(x for x in rows if x["key"] == k)
    not_reached.append(f"TIMEOUT on box D3-g08 (4 h cap, neither killed nor survived): {k} {r['file']}:{r['line']} {r['kind']}")
for k in ungated:
    r = next(x for x in rows if x["key"] == k)
    not_reached.append(f"not gated on box D3-g08 (STOP/SKIP): {k} {r['file']}:{r['line']} {r['kind']}")
examined = len([k for k in keys if k in gates and gates[k].get("verdict") != "TIMEOUT"])
m3 = {
    "step": "D3.M3",
    "enumerator": "awk -F'\\t' '$6==\"gate\"' SURVIVORS.tsv",
    "universe": 742,
    "examined": examined,
    "not_reached": not_reached,
    "redispatched": m3_old.get("redispatched", []),
    "evidence": "the wave list: 742 u1 full-net survivors after dedupe, split over boxes D3-g01..D3-g47 (each box's keys.tsv on dispatch/finder-r11-D3-gNN; 742 keys, 0 duplicates). This box: "
                f"{len(keys)} keys, each `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/fullgate.py run --src complete --key <key>` "
                "(GATE_SCOPE=full GOLDEN_MODE=drift GOLDEN_REF=" + BASE + " GATE_JOBS=1 ./tests/run.sh), driven by gate_wave.sh run, records "
                + ", ".join(f"{REL}/gates/{k}.json" for k in keys if k in gates)
                + f"; null control {REL}/gates/null.json. The earlier boxes' D3.M3 rows (D3-top6, D3-rem full gates; REPORT-D3-top6.json, REPORT-D3-rem.json) cover the 8 deduped keys and are carried, not counted in this universe.",
}
cov.insert(next(i for i, c in enumerate(cov) if c["step"] == "D3.M4"), m3)

gated, surv, equiv, nf = [], [], [], []
for r in rows:
    k = r["key"]
    g = gates.get(k)
    x = res.get(k, {})
    gated.append({"key": k, "site": f"{r['file']}:{r['line']} {r['kind']}", "verdict": g.get("verdict") if g else None,
                  "killed_by": g.get("killed_by", []) if g else [], "class": x.get("class"),
                  "gate_record": f"{REL}/gates/{k}.json" if g else None, "result": f"{REL}/results/{k}.json" if x else None})
    if x.get("class") == "candidate":
        surv.append(x)
    elif x.get("class") == "equivalent-candidate":
        equiv.append(x)
        nf.append({"claim": f"equivalent-candidate: mutant {k} at {x['site']} ({x['patch']}) survives the full gate ({g['verdict']}) and no probed input moves the number",
                   "command": x["probe"]["command"], "value": "; ".join(x["probe"]["result_lines"][-3:]),
                   "inputs_tried": x["probe"]["inputs_tried"]})
    elif x.get("class") == "killed":
        nf.append(x["non_finding"])
nf.insert(0, {"claim": "null control: this box's full gate on a comment-only marker",
              "command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/fullgate.py null",
              "value": f"gate_rc={null.get('gate_rc')}, failed scripts {null.get('failed_scripts')}, fail_lines {null.get('fail_lines')}, wall_s {null.get('wall_s')} (provisional; nproc 4, Intel Xeon @ 2.10GHz, load1 {null.get('load1_start')}..{null.get('load1_end')})",
              "note": f"{REL}/gates/null-note.txt: every red check is a branch/worktree artefact; no production file involved"})

tally = {}
for g in gates.values():
    tally[g["verdict"]] = tally.get(g["verdict"], 0) + 1
killed_by = {}
for g in gates.values():
    for s in g.get("killed_by") or []:
        killed_by[s] = killed_by.get(s, 0) + 1

unfinished = [{"step": "D3.M3", "what": f"TIMEOUT {k}: the 4 h cap; last script running {res.get(k, {}).get('timeout', {}).get('last_script_running')}"} for k in timeouts]
unfinished += [{"step": "D3.M3", "what": f"not gated {k} (STOP/SKIP)"} for k in ungated]

probes = [f"{REL}/probes/probe_{k}.py" for k in keys if (W / "probes" / f"probe_{k}.py").exists() and res.get(k, {}).get("probe")]
rep = {
    "dimension": "D3", "baseline_sha": BASE, "box": "D3-g08", "seat": "D3-s1",
    "report_path": f"{REL}/REPORT.md",
    "exposure": "Read: COMMON.md, D3.md, dev/audit/README.md, the u1 slice reports and REPORT-D3-top6/rem, the keys' carried M4 answers, fullgate.py and the production methods the 16 mutants name; the other boxes' keys.tsv (dispatch refs, key lists only) to name not_reached by box. Not read: the register, round11/J/, any verifier report, docs/, GitHub. A predecessor seat on another account ran gates 1-7 and wrote the probes and analysis; this seat restored its checkpoint (handoff-wip e9db1f9881c5) and continued, re-running every probe from a clean baseline checkout when building each result.",
    "coverage": cov,
    "unfinished": unfinished,
    "findings": [],
    "non_findings": nf,
    "harnesses": ["dev/audit/rounds/round11/D3/s1/fullgate.py",
                  "gate_wave.sh (out of tree, dispatch/finder-r11-D3-g08: fullgate.py run per key of keys.tsv in order, one gate at a time, GATE_JOBS=1, 4 h cap, null first)",
                  f"{REL}/notes/build_result.py", f"{REL}/notes/build_report.py"] + probes,
    "leads": [],
    "gated": gated,
    "gate_survivors": surv,
    "equivalent_candidates": equiv,
    "tally": {"gated": len(gates), "verdicts": tally, "killed_by": killed_by,
              "candidates": len(surv), "equivalent_candidates": len(equiv), "timeouts": len(timeouts)},
}

md = [f"# D3-s1 wave box D3-g08 — full gate for 16 u1 full-net survivors (round 11)", "",
      f"Baseline `{BASE}`. Box alone on its machine: nproc 4, Intel(R) Xeon(R) Processor @ 2.10GHz, 16 GB (`MACHINE.txt`). Every wall, CPU and load1 number is provisional: true (the judge re-takes it).", "",
      "## Controls", "",
      f"Null control `fullgate.py null` (comment-only marker): gate_rc {null.get('gate_rc')}, red scripts {', '.join(null.get('failed_scripts', []))} with fail_lines {null.get('fail_lines')}, wall {null.get('wall_s')} s. All are branch/worktree artefacts (`gates/null-note.txt`); usable, not re-taken. A mutant is KILLED only on a script beyond it or more FAIL lines in one.", "",
      "## Tally", "",
      f"gated {len(gates)}/16; " + ", ".join(f"{k} {v}" for k, v in sorted(tally.items())) + f"; KILLED by: {killed_by or 'none'}; candidates {len(surv)}; equivalent-candidates {len(equiv)}; TIMEOUT {len(timeouts)}.", "",
      "| key | site | verdict | class |", "|---|---|---|---|"]
for g in gated:
    md.append(f"| `{g['key']}` | {g['site']} | {g['verdict']} | {g['class']} |")
md += ["", "## Survivors: step-4 answers and probe numbers", ""]
for r in rows:
    x = res.get(r["key"])
    if not x or x.get("class") not in ("candidate", "equivalent-candidate"):
        continue
    p = x["probe"]
    md.append(f"**`{x['key']}`** {x['site']} `{x['patch']}` ({x['function']}), gate {x['gate']['verdict']} — **{x['class']}**. "
              f"Reach: {x.get('reach')}. Baseline: {p['baseline_value']}. Mutant: {p['mutant_value']}. Inputs tried: {p['inputs_tried']}. "
              f"Probe `{p['path']}` prints {'; '.join(p['result_lines'][-2:])}. Should have failed: {x['should_fail']['script']}: {x['should_fail']['assertion']}."
              + (f" Equivalence: {x['equivalence']}." if x.get("equivalence") else ""))
    md.append("")
for r in rows:
    x = res.get(r["key"])
    if x and x.get("class") == "killed":
        md.append(f"**`{x['key']}`** {x['site']} KILLED by {x['killed_by']}: {x['non_finding']['value']}.")
        md.append("")
if unfinished:
    md += ["## Unfinished", ""] + [f"- {u['what']}" for u in unfinished] + [""]
md += ["## Coverage", "", "D3.M1, D3.M2, D3.M4, D3.M5 carried verbatim from REPORT-D3-u1b.json. D3.M3: the wave list, universe 742, "
       f"examined {examined} here, the other {len(not_reached)} named by box in REPORT.json's not_reached.", ""]
rep["report_md"] = "\n".join(md)
(W / "REPORT.json").write_text(json.dumps(rep, indent=1) + "\n")
(W / "REPORT.md").write_text(rep["report_md"] + "\n")
print(f"REPORT gated={len(gates)} tally={tally} candidates={len(surv)} equiv={len(equiv)} not_reached={len(not_reached)} examined={examined}")
