"""REPORT.json and REPORT.md of wave box D3-g28 (seat D3-s1, round 11), from results/<key>.json, gates/ and the
carried REPORT-D3-u1b.json rows. Usage (from the tree root): python3 <this> <boxkeys-dir>
<boxkeys-dir> holds D3-g01.tsv .. D3-g47.tsv, each the keys.tsv of dispatch/finder-r11-D3-g<NN> (the wave split)."""
import json, sys
from pathlib import Path

ROOT = Path.cwd()
S1 = ROOT / "dev/audit/rounds/round11/D3/s1"
W = S1 / "wave/D3-g28"
REL = "dev/audit/rounds/round11/D3/s1/wave/D3-g28"
BOX = "D3-g28"
BASE = "92d38ecb640bd462f2e19c0814d0f0b7df1ee692"
boxdir = Path(sys.argv[1])

keys = [l.split("\t") for l in (W / "keys.tsv").read_text().splitlines()[1:] if l.strip()]
R = {}
for row in keys:
    p = W / "results" / f"{row[0]}.json"
    if p.exists():
        R[row[0]] = json.loads(p.read_text())
null = json.loads((W / "gates/null.json").read_text())
machine = (W / "MACHINE.txt").read_text().strip()

u1b = json.loads((S1 / "REPORT-D3-u1b.json").read_text())
carried = {}
for c in u1b["coverage"]:
    if c["step"] in ("D3.M1", "D3.M2", "D3.M4", "D3.M5"):
        c = dict(c); c["carried"] = "verbatim from dev/audit/rounds/round11/D3/s1/REPORT-D3-u1b.json (box D3-u1b)"
        carried[c["step"]] = c

# the wave split: every other box's keys, named by box
others, wave_total = [], 0
for f in sorted(boxdir.glob("D3-g*.tsv")):
    b = f.stem
    ks = [l.split("\t")[0] for l in f.read_text().splitlines()[1:] if l.strip()]
    wave_total += len(ks)
    if b != BOX:
        others.append(f"assigned to box {b}: {len(ks)} keys: " + " ".join(ks))
timeouts = [k for k, r in R.items() if r["class"] == "timeout"]
missing = [row[0] for row in keys if row[0] not in R]
examined = len(R) - len(timeouts)
not_reached = others + [f"TIMEOUT on box {BOX} (cap {R[k]['timeout']['cap_s']} s, last script "
                        f"{R[k]['timeout'].get('last_script')}): {k} {R[k]['site']}" for k in timeouts] \
              + [f"not gated on box {BOX} (run ended before it): {k}" for k in missing]
m3 = {
    "step": "D3.M3",
    "enumerator": "awk -F'\\t' '$6==\"gate\"' SURVIVORS.tsv",
    "universe": wave_total,
    "examined": examined,
    "not_reached": not_reached,
    "redispatched": [{"item": "C3", "state": "examined"}, {"item": "C5", "state": "examined"}],
    "evidence": (f"wave list = the 742 u1 full-net survivors left after dedupe (8 already gated by D3-top6/D3-rem under "
                 f"other keys), split over 47 boxes D3-g01..D3-g47 (each dispatch/finder-r11-D3-g<NN>:keys.tsv; "
                 f"{wave_total} keys, all distinct). Box {BOX} gated {examined} of its {len(keys)} keys: per key "
                 f"python3 dev/audit/rounds/round11/D3/s1/fullgate.py run --src complete --key <key> "
                 f"(GATE_SCOPE=full GOLDEN_MODE=drift GOLDEN_REF={BASE} GATE_JOBS=1 ./tests/run.sh), records "
                 f"{REL}/gates/<key>.json, against this box's null {REL}/gates/null.json. C3 (full gate) and C5 carried "
                 f"as examined by boxes D3-top6 and D3-rem (REPORT-D3-rem.json D3.M3 row, 35 of 35).")
}
coverage = [carried["D3.M1"], carried["D3.M2"], m3, carried["D3.M4"], carried["D3.M5"]]

def tally():
    t = {}
    for r in R.values():
        t[r["gate"]["verdict"] if "gate" in r else "TIMEOUT"] = t.get(r["gate"]["verdict"] if "gate" in r else "TIMEOUT", 0) + 1
    return t

gated, survivors, equiv, non_findings, harnesses = [], [], [], [], ["dev/audit/rounds/round11/D3/s1/fullgate.py",
    f"{REL}/probes/_tools/build_result.py", f"{REL}/probes/_tools/build_report.py"]
for row in keys:
    k = row[0]
    if k not in R:
        continue
    r = R[k]; g = r.get("gate", {})
    gated.append({"key": k, "site": r["site"], "verdict": g.get("verdict", "TIMEOUT"),
                  "killed_by": g.get("killed_by") or [], "class": r["class"]})
    if "probe" in r:
        harnesses.append(r["probe"]["path"])
    gcmd = g.get("command", f"python3 dev/audit/rounds/round11/D3/s1/fullgate.py run --src complete --key {k}")
    if r["class"] == "killed":
        non_findings.append({"claim": f"full gate KILLED {k} {r['site']} ({r['patch']})", "command": gcmd,
                             "value": f"killed_by={g.get('killed_by')}; fail_lines={g.get('fail_lines')}; wall {g.get('wall_s')} s (provisional)"})
    elif r["class"] == "equivalent-candidate":
        equiv.append(r)
        pr = r["probe"]["results"]
        non_findings.append({"claim": f"equivalent-candidate {k} {r['site']} ({r['patch']}): full gate {g.get('verdict')}, "
                                      f"probe finds no input that moves the metric. {r.get('equivalence', '')}",
                             "command": r["probe"]["command"],
                             "value": "; ".join(f"{a}={b}" for a, b in pr.items()) + f"; inputs: {r['probe']['inputs_tried']}"})
    elif r["class"] == "candidate":
        survivors.append(r)

unfinished = [{"step": "D3.M3", "what": f"{k}: TIMEOUT past the {R[k]['timeout']['cap_s']} s cap, last script "
               f"{R[k]['timeout'].get('last_script')}"} for k in timeouts] + \
             [{"step": "D3.M3", "what": f"{k}: not gated on this box"} for k in missing]

exposure = (f"Box {BOX} (resumed from the predecessor seat's checkpoint handoff-wip/finder-r11-D3-g28 @ c71606ac: null and "
            "8 gates, results and every probe restored, not redone). Read COMMON.md/D3.md/README.md-derived procedure, "
            "finding.schema.json and check_report.mjs's denominator rules (through a haiku extractor), REPORT-D3-u1b.json "
            "and REPORT-D3-rem.json coverage rows, this box's carried probes and results, and the 47 wave boxes' dispatch "
            "keys.tsv (key lists only). No register, round11/J, verifier report, docs/ or GitHub read. Gate driver: "
            "gate_wave.sh (out of tree, on dispatch/finder-r11-D3-g28): one fullgate.py gate at a time, GATE_JOBS=1, cap "
            "14400 s. Workaround in this box's own tree only: $HOME/venv-ci symlinked to /opt/hpo/venv-ci (the driver's "
            "PATH), and the predecessor's results_loop.sh run from a scratch copy with its build_result.py path pointed "
            "at the in-tree probes/_tools copy; nothing pushed.")

t = tally()
report = {
    "dimension": "D3", "baseline_sha": BASE, "box": BOX, "report_path": f"{REL}/REPORT.md", "exposure": exposure,
    "coverage": coverage, "unfinished": unfinished, "findings": [], "non_findings": non_findings,
    "harnesses": sorted(set(harnesses), key=harnesses.index), "leads": [],
    "gated": gated, "gate_survivors": survivors, "equivalent_candidates": equiv,
}

md = [f"# D3-s1 wave box {BOX}: full gate for 16 u1 full-net survivors (round 11)", "",
      f"Baseline `{BASE}`. Seat D3-s1, box {BOX}; keys: `{REL}/keys.tsv`.", "",
      "## Machine and controls", "", "```", machine, "```", "",
      f"Null control `python3 dev/audit/rounds/round11/D3/s1/fullgate.py null` (comment-only marker): gate_rc "
      f"{null['gate_rc']}, red scripts {null['failed_scripts']} with fail lines {null['fail_lines']}, summary "
      f"`{null['summary'][0]}`, wall {null['wall_s']} s, load1 {null['load1_start']} -> {null['load1_end']} (provisional). "
      "Every red script is an artefact of the detached, stripped worktree (merge-bot selftest and closure re-derive "
      "reading git state; harness_headers naming this box's untracked probes and the stripped round4 claims); no "
      "machine-caused red. Assessment: `NULL-ASSESSMENT.md`. Counts are final; wall, CPU and load1 are provisional "
      "(nproc 4, Intel Xeon @ 2.10GHz).", "",
      "Procedure: `gate_wave.sh run` drove `fullgate.py run --src complete --key <key>` "
      "(GATE_SCOPE=full GOLDEN_MODE=drift GATE_JOBS=1 ./tests/run.sh) down keys.tsv one gate at a time, cap 14400 s; "
      "each result built by `probes/_tools/build_result.py` from the gate record and the key's probe.", "",
      "## Tally", "",
      f"- gated: {len(gated)} of {len(keys)}",
      "- " + ", ".join(f"{v}: {n}" for v, n in sorted(t.items())),
      f"- KILLED by script: " + (", ".join(f"{x['key']} by {x['killed_by']}" for x in gated if x['verdict'] == 'KILLED') or "none"),
      f"- candidates (gate_survivors): {len(survivors)}",
      f"- equivalent-candidates: {len(equiv)}",
      f"- TIMEOUT: {len(timeouts)}" + (f" ({', '.join(timeouts)})" if timeouts else ""), "",
      "| key | site | verdict | class |", "|---|---|---|---|"]
md += [f"| {x['key']} | {x['site']} | {x['verdict']} | {x['class']} |" for x in gated]
md += ["", "## Survivors: step-4 answers and probe numbers", ""]
for r in survivors + equiv:
    pr = r["probe"]
    md.append(f"### {r['key']} — {r['site']} ({r['function']}), {r['class']}")
    md.append("")
    md.append(f"Patch: `{r['patch']}`. Gate: {r['gate']['verdict']} (gate_rc {r['gate']['gate_rc']}, killed_by "
              f"{r['gate']['killed_by'] or 'none'}, wall {r['gate']['wall_s']} s provisional), record `{r['gate']['record']}`. "
              f"Carried M4 answer: `{r['m4_source']}`. Probe `{pr['path']}` (`{pr['command']}`), metric: {pr['metric']}. "
              f"Inputs tried: {pr['inputs_tried']}. Numbers: " + "; ".join(f"{a}={b}" for a, b in pr["results"].items()) +
              f". Direction: {pr['direction']}.")
    if r["class"] == "candidate":
        sf = r["should_fail"]; f = r["finding"]
        md.append("")
        md.append(f"Candidate: {f['claim']} Should have failed: `{sf['script']}` — {sf['assertion']}. "
                  f"Severity claimed {f['severity_claimed']}, class_guess {f['class_guess']}.")
    else:
        md.append("")
        md.append(f"Equivalent-candidate: {r.get('equivalence', '')}")
    md.append("")
md += ["## Unfinished", ""] + ([f"- {u['what']}" for u in unfinished] or ["- none"]) + [""]
md += ["Findings: none numbered here; every candidate is under `gate_survivors` for the orchestrator's id "
       "consolidation (FINDING IDS rule).", ""]

(W / "REPORT.json").write_text(json.dumps(report, indent=1) + "\n")
(W / "REPORT.md").write_text("\n".join(md))
print(f"REPORT gated={len(gated)} survivors={len(survivors)} equiv={len(equiv)} timeouts={len(timeouts)} "
      f"missing={len(missing)} universe={wave_total} examined={examined} not_reached={len(not_reached)}")
