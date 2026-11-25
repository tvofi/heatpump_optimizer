#!/usr/bin/env python3
"""Box D3-g20: build the wave dir's REPORT.json and REPORT.md from keys.tsv, gates/*.json,
results/*.json, the null record and the carried REPORT-D3-u1b.json coverage rows.
Usage, from the tree root:  python3 dev/audit/rounds/round11/D3/s1/wave/D3-g20/tools/mkreport.py <wavekeys_dir>
<wavekeys_dir> holds D3-g01.tsv .. D3-g47.tsv, each box's keys.tsv taken from its dispatch ref tip
(git show origin/dispatch/finder-r11-D3-gNN:keys.tsv): together the 742-key wave list.
"""
import json, sys
from pathlib import Path

BOX = "D3-g20"
BASE = "92d38ecb640bd462f2e19c0814d0f0b7df1ee692"
S1 = Path("dev/audit/rounds/round11/D3/s1")
W = S1 / "wave" / BOX
WK = Path(sys.argv[1])

rows = [dict(zip(*[l.split("\t") for l in [(W / "keys.tsv").read_text().splitlines()[0], line]]))
        for line in (W / "keys.tsv").read_text().splitlines()[1:] if line.strip()]
mine = [r["key"] for r in rows]
gates = {k: json.loads((W / "gates" / f"{k}.json").read_text()) for k in mine if (W / "gates" / f"{k}.json").exists()}
res = {k: json.loads((W / "results" / f"{k}.json").read_text()) for k in mine if (W / "results" / f"{k}.json").exists()}
null = json.loads((W / "gates" / "null.json").read_text())

others = []
for f in sorted(WK.glob("D3-g*.tsv")):
    box = f.stem
    for line in f.read_text().splitlines()[1:]:
        if not line.strip():
            continue
        c = line.split("\t")
        if box != BOX:
            others.append(f"assigned to box {box}: {c[0]} {c[2]}:{c[3]} {c[8]}")
universe = len(others) + len(mine)

timeouts = [k for k in mine if gates.get(k, {}).get("verdict") == "TIMEOUT"]
ungated = [k for k in mine if k not in gates]
noresult = [k for k in mine if k in gates and k not in res]
examined_keys = [k for k in mine if k in gates and k not in timeouts]
site = {r["key"]: f"{r['file']}:{r['line']} {r['kind']}" for r in rows}

u1b = json.loads((S1 / "REPORT-D3-u1b.json").read_text())
cov = []
for c in u1b["coverage"]:
    if c["step"] == "D3.M3":
        c3 = [x for x in c.get("redispatched", [])]
        cov.append({
            "step": "D3.M3",
            "enumerator": "awk -F'\\t' '$6==\"gate\"' SURVIVORS.tsv",
            "universe": universe,
            "examined": len(examined_keys),
            "not_reached": others + [f"TIMEOUT on this box (past the {gates[k].get('cap_s', 14400)} s cap): {k} {site[k]}" for k in timeouts]
                           + [f"not gated on this box: {k} {site[k]}" for k in ungated],
            "redispatched": c3,
            "evidence": (f"box {BOX}: gate_wave.sh run -> per key `python3 dev/audit/rounds/round11/D3/s1/fullgate.py run --src complete --key <key>` "
                         f"(GATE_SCOPE=full GOLDEN_MODE=drift GOLDEN_REF={BASE} GATE_JOBS=1 ./tests/run.sh), records "
                         + ", ".join(f"{W}/gates/{k}.json" for k in mine if k in gates)
                         + f"; null control {W}/gates/null.json (gate_rc {null.get('gate_rc')}, failed {null.get('failed_scripts')}). "
                         f"Wave list (742 keys) = the 47 boxes' keys.tsv on refs dispatch/finder-r11-D3-g01..g47 (SURVIVORS.tsv itself is not in this tree); "
                         f"examined = the {len(examined_keys)} keys this box gated to a verdict; the 8 keys D3-top6/D3-rem already gated were deduped out of the wave list "
                         "and are carried in those boxes' own D3.M3 rows, so they add nothing inside this 742-key universe. "
                         "redispatched items carried verbatim from REPORT-D3-u1b.json's D3.M3 row."),
        })
    else:
        cc = dict(c)
        cc["carried"] = True
        cc["evidence"] = "carried verbatim from dev/audit/rounds/round11/D3/s1/REPORT-D3-u1b.json (not re-driven on box D3-g20): " + c["evidence"]
        cov.append(cc)

gated = [{"key": k, "site": site[k], "verdict": gates[k].get("verdict"), "killed_by": gates[k].get("killed_by") or [],
          "class": res.get(k, {}).get("class", "timeout" if k in timeouts else None)} for k in mine if k in gates]
survivors = [res[k] for k in mine if res.get(k, {}).get("class") == "candidate"]
equiv = [res[k] for k in mine if res.get(k, {}).get("class") == "equivalent-candidate"]
killed = [res[k] for k in mine if res.get(k, {}).get("class") == "killed"]

non_findings = [{"claim": "null control: fullgate.py null on box D3-g20 (comment-only marker, unmutated tree)",
                 "command": "python3 dev/audit/rounds/round11/D3/s1/fullgate.py null",
                 "value": f"gate_rc {null.get('gate_rc')}, failed_scripts {null.get('failed_scripts')}, fail_lines {null.get('fail_lines')}, wall_s {null.get('wall_s')} (provisional)"}]
non_findings += [r["non_finding"] for r in killed + equiv if "non_finding" in r]

probes = sorted(str(p) for p in (W / "probes").glob("*.py"))
harnesses = [str(S1 / "fullgate.py"),
             f"gate_wave.sh (out-of-tree driver on ref dispatch/finder-r11-D3-g20 tip c1223708: null/run/ckpt/restore; one gate at a time, 4 h cap)",
             str(W / "tools" / "mkresult.py"), str(W / "tools" / "mkres.sh"), str(W / "tools" / "mkreport.py")] + probes

unfinished = [f"TIMEOUT {k} {site[k]}: gate exceeded the {gates[k].get('cap_s', 14400)} s cap; last log lines {res.get(k, {}).get('timeout', {}).get('last_log_lines')}" for k in timeouts]
unfinished += [f"not gated: {k} {site[k]}" for k in ungated] + [f"gated, no results record: {k}" for k in noresult]

machine = (W / "MACHINE.txt").read_text()
exposure = ("Box D3-g20 (two seats: the first stalled after 7 gates, this successor resumed from its checkpoint on ref handoff-wip/finder-r11-D3-g20 @ 855a9a2f). "
            "Read COMMON.md, D3.md, dev/audit/README.md, the u1 slice reports and m4 answers, REPORT-D3-top6/rem, finding.schema.json, the carried harnesses and state in "
            "dev/audit/rounds/round11/D3/s1/, the 16 production lines of keys.tsv, and the other wave boxes' keys.tsv on their dispatch refs (to name not_reached). "
            "No docs/, register, round11/J/, verifier report or GitHub record was read.")

tally = {}
for g in gated:
    tally[g["verdict"]] = tally.get(g["verdict"], 0) + 1
rep = {
    "dimension": "D3", "baseline_sha": BASE, "box": BOX,
    "report_path": str(W / "REPORT.md"),
    "exposure": exposure, "coverage": cov, "unfinished": unfinished,
    "findings": [], "non_findings": non_findings, "harnesses": harnesses, "leads": [],
    "gated": gated, "gate_survivors": survivors, "equivalent_candidates": equiv,
    "tally": tally | {"candidates": len(survivors), "equivalent_candidates": len(equiv), "killed_class": len(killed)},
    "machine": machine, "provisional": True,
}
(W / "REPORT.json").write_text(json.dumps(rep, indent=1) + "\n")

md = [f"# D3-s1 wave box {BOX}: full gate for 16 D3.M3 full-net survivors", "",
      f"Baseline `{BASE}`. Dimension D3, seat D3-s1, step D3.M3/D3.M4. findings: [] (ids assigned at consolidation).", "",
      "## Machine and controls", "", "```", machine.strip(), "```", "",
      f"Null control `fullgate.py null` ({W}/gates/null.json): gate_rc {null.get('gate_rc')}, red scripts {null.get('failed_scripts')} "
      f"(fail lines {null.get('fail_lines')}), wall {null.get('wall_s')} s (provisional). These are the stripped-tree artefact checks; a mutant counts as KILLED only with a script, or more FAIL lines in one, beyond them.",
      "Gates 1-7 ran on the first seat's machine (Xeon @ 2.10GHz, where the null was taken); gates 8-16 on the successor's (Xeon @ 2.30GHz, nproc 4), the null restored from the checkpoint as gate_wave.sh does, not re-taken. Every wall/CPU/load number is provisional.", "",
      "## Tally", "",
      f"gated {len(gated)}/16: " + ", ".join(f"{k} {v}" for k, v in sorted(tally.items()))
      + f"; KILLED by: " + ("; ".join(f"{g['key']} {g['killed_by']}" for g in gated if g['verdict'] == 'KILLED') or "none")
      + f". Classes: candidates {len(survivors)}, equivalent-candidates {len(equiv)}, killed {len(killed)}, timeout {len(timeouts)}.", "",
      "| key | site | verdict | class |", "|---|---|---|---|"]
md += [f"| {g['key']} | {g['site']} | {g['verdict']} | {g['class']} |" for g in gated]
md += ["", "## Per key", ""]
for k in mine:
    r = res.get(k)
    if not r:
        md += [f"### {k} {site[k]}", "", f"No record: {'TIMEOUT' if k in timeouts else 'not gated'}.", ""]
        continue
    md += [f"### {k} {r['site']} ({r['gate']['verdict']}, {r['class']})", "", f"Patch `{r['patch']}` in `{r['function']}`."]
    if r["class"] == "killed":
        md += [f"Killed by {r['gate'].get('killed_by')}: " + "; ".join(r.get("killed_lines", [])[:5]), ""]
        if r.get("kill_note"):
            md += [f"Note: {r['kill_note']}", ""]
        continue
    if r["class"] == "timeout":
        md += [f"TIMEOUT: {r.get('timeout')}", ""]
        continue
    p = r["probe"]
    md += [f"Step 4: probe `{p['path']}` (`{p['command']}`), rc {p['rc']}. Baseline: {p['baseline_value']}. Mutant: {p['mutant_value']}. Inputs tried: {p['inputs_tried']}.",
           "Probe output: " + "; ".join(f"`{l}`" for l in p["result_lines"]), f"Should fail: {r.get('should_fail')}."]
    if r["class"] == "candidate":
        f = r["finding"]
        md += [f"Candidate: **{f['title']}**. {f['claim']} class_guess {f['class_guess']}, severity {f['severity_claimed']}; metric: {f['metric_definition']}; "
               f"perturbation {f['perturbation']}; null control {f['null_control']}."]
    else:
        md += [f"Equivalent-candidate: {r['non_finding']['claim']}."]
    md += [""]
md += ["## Unfinished", ""] + ([f"- {u}" for u in unfinished] or ["- none"]) + [""]
md += ["## Harnesses", ""] + [f"- {h}" for h in harnesses] + [""]
md += ["## Exposure", "", exposure, ""]
(W / "REPORT.md").write_text("\n".join(md))
print(f"REPORT gated={len(gated)} universe={universe} examined={len(examined_keys)} not_reached={len(cov[2]['not_reached']) if len(cov) > 2 else '?'} "
      f"candidates={len(survivors)} equiv={len(equiv)} unfinished={len(unfinished)}")
