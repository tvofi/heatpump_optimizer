#!/usr/bin/env python3
"""REPORT.json and REPORT.md for box D3-g05 (seat D3-s1, round 11), from the wave dir's records."""
import json, re, sys
from pathlib import Path
T = Path.home() / "d3g05-tools"
W = Path.home() / "audit-r11-D3-s1/dev/audit/rounds/round11/D3/s1/wave/D3-g05"
S1 = W.parent.parent
RW = "dev/audit/rounds/round11/D3/s1/wave/D3-g05"
FG = "dev/audit/rounds/round11/D3/s1/fullgate.py"
BASE = "92d38ecb640bd462f2e19c0814d0f0b7df1ee692"
ENUM = "awk -F'\\t' '$6==\"gate\"' SURVIVORS.tsv"
extra_unfinished = json.loads(sys.argv[1]) if len(sys.argv) > 1 else []

keys = [l.split("\t") for l in (W / "keys.tsv").read_text().splitlines()[1:] if l.strip()]
recs = {k[0]: json.loads((W / "results" / f"{k[0]}.json").read_text()) for k in keys if (W / "results" / f"{k[0]}.json").exists()}
null = json.loads((W / "gates/null.json").read_text())
machine = (W / "MACHINE.txt").read_text()
u1b = json.loads((S1 / "REPORT-D3-u1b.json").read_text())

gated = [{"key": k, "site": r["site"], "verdict": r["gate"]["verdict"], "killed_by": r["gate"].get("killed_by") or [],
          "class": r["class"]} for k, r in recs.items()]
timeouts = [k for k, r in recs.items() if r["class"] == "timeout"]
missing = [k[0] for k in keys if k[0] not in recs]
examined = len(recs) - len(timeouts)

others = []
for f in sorted((T / "boxes").glob("g*.tsv")):
    box = "D3-" + f.stem
    if box == "D3-g05":
        continue
    ks = [l.split("\t")[0] for l in f.read_text().splitlines()[1:] if l.strip()]
    others.append(f"assigned to box {box}: {len(ks)} keys ({' '.join(ks)})")
universe = sum(len([l for l in f.read_text().splitlines()[1:] if l.strip()]) for f in (T / "boxes").glob("g*.tsv"))
not_reached = others + [f"TIMEOUT on box D3-g05 (4 h cap): {k} {recs[k]['site']}" for k in timeouts] + \
              [f"not gated on box D3-g05 (run ended): {k}" for k in missing]
m3_prev = next(c for c in u1b["coverage"] if c["step"] == "D3.M3")
m3 = {"step": "D3.M3", "enumerator": ENUM, "universe": universe, "examined": examined, "not_reached": not_reached,
      "redispatched": m3_prev.get("redispatched", []),
      "evidence": ("box D3-g05 wave gate: " + "; ".join(
          f"{r['gate_command']} -> {r['gate']['verdict']} ({RW}/gates/{k}.json)" for k, r in recs.items())
          + f". Null control: PYTHONPATH=tests/hastub python3 {FG} null -> gate_rc {null['gate_rc']}, red {null['failed_scripts']} ({RW}/gates/null.json)."
          + " The wave list is the orchestrator's SURVIVORS.tsv (742 keys, $6 == gate), split over boxes D3-g01..D3-g47 by their dispatch refs' keys.tsv;"
          + " the earlier D3.M3 rows (REPORT-D3-u1b.json 235 of 268, REPORT-D3-top6.json 30 of 35, REPORT-D3-rem.json) stand for their own universes and are carried, not re-counted here.")}
cov = []
for c in u1b["coverage"]:
    if c["step"] == "D3.M3":
        cov.append(m3)
    else:
        cc = dict(c); cc["carried"] = True
        cc["evidence"] = "carried verbatim from REPORT-D3-u1b.json (box D3-u1b), not re-driven on box D3-g05: " + c.get("evidence", "")
        cov.append(cc)

non_findings, survivors, equiv = [], [], []
for k, r in recs.items():
    if r["class"] == "killed":
        non_findings.append({"claim": f"{r['site']} ({r['patch']}) is pinned by the full gate: KILLED by {', '.join(r['killed_by'])}; gate_rc {r['gate']['gate_rc']}, wall {r['gate']['wall_s']} s (provisional, load1 {r['gate']['load1_start']}..{r['gate']['load1_end']})",
                             "command": r["gate_command"], "value": f"killed=1 count; failing lines: {' | '.join(r['failing_check_lines'][:4])}"})
    elif r["class"] == "equivalent-candidate":
        equiv.append(r)
        non_findings.append({"claim": f"{r['site']} ({r['patch']}) survives the full gate ({r['gate']['verdict']}) but is an equivalent-candidate: {r['m4_answer']}",
                             "command": r["probe"]["command"], "value": f"baseline {r['probe']['baseline_value']}; mutant {r['probe']['mutant_value']}; inputs tried: {'; '.join(r['probe']['inputs_tried'])}"})
    elif r["class"] == "candidate":
        survivors.append(r)
non_findings.append({"claim": f"Box D3-g05 null control (comment-only marker in tariff.py): gate_rc {null['gate_rc']}, red scripts {null['failed_scripts']}, fail counts {null.get('fail_lines')}; a mutant is KILLED only by a script beyond these or more FAIL lines in one",
                     "command": f"PYTHONPATH=tests/hastub python3 {FG} null", "value": f"gate_rc={null['gate_rc']} wall {null['wall_s']} s (provisional)"})

unfinished = [{"step": "D3.M3", "what": f"TIMEOUT past the 4 h cap on box D3-g05: {k} {recs[k]['site']}, last script running {recs[k].get('last_script')}"} for k in timeouts]
unfinished += [{"step": "D3.M3", "what": f"not gated on box D3-g05: {k}"} for k in missing]
unfinished += extra_unfinished
harnesses = [FG] + [f"{RW}/probes/probe_{k}.py" for k, _ in [(x[0], 0) for x in keys]]

rep = {"dimension": "D3", "baseline_sha": BASE, "report_path": f"{RW}/REPORT.md", "box": "D3-g05",
       "exposure": "", "coverage": cov, "unfinished": unfinished, "findings": [], "non_findings": non_findings,
       "harnesses": harnesses, "leads": [], "gated": gated, "gate_survivors": survivors, "equivalent_candidates": equiv,
       "null_control": {k: null.get(k) for k in ("gate_rc", "failed_scripts", "fail_lines", "wall_s", "load1_start", "load1_end")},
       "procedure": "gate_wave.sh (dispatch ref dispatch/finder-r11-D3-g05, out of tree): fullgate.py null once, then fullgate.py run --src complete --key <key> per keys.tsv row, one gate at a time, GATE_SCOPE=full GOLDEN_MODE=drift GATE_JOBS=1, 4 h cap (TIMEOUT), tree reset to the baseline between gates; probes run in a separate baseline worktree, never in the gate tree"}

# ---- markdown
from collections import Counter
vc = Counter(g["verdict"] for g in gated)
kb = Counter(s for g in gated if g["verdict"] == "KILLED" for s in g["killed_by"])
md = [f"# D3-s1 round 11, box D3-g05: full gate for 16 D3.M3 full-net survivors (D3 u1 wave)", "",
      f"Baseline {BASE}. Keys: {RW}/keys.tsv (the box's 16 of the wave's 742; every other key belongs to boxes D3-g01..D3-g47).", "",
      "## Machine and controls", "", "```", machine.strip(), "```", "",
      f"Null control (`PYTHONPATH=tests/hastub python3 {FG} null`, comment-only marker in tariff.py): gate_rc {null['gate_rc']}, red scripts {null['failed_scripts']}, fail counts {null.get('fail_lines')}, wall {null['wall_s']} s, load1 {null['load1_start']}..{null['load1_end']} (provisional). "
      "A mutant is KILLED only when run.sh is red and a script beyond the null fails, or a null-red script prints more FAILs; red with nothing beyond the null is RED-AS-NULL, read as survived.", "",
      "Procedure: gate_wave.sh (out of tree, on the dispatch ref) drives fullgate.py once per key, one gate at a time, GATE_SCOPE=full GOLDEN_MODE=drift GATE_JOBS=1, 4 h cap. Probes ran in a second detached worktree of the baseline (never the gate tree); each recompiles the mutated coordinator method from its own source with the one line replaced and calls it beside the baseline method on the same inputs. Walls and load are provisional; counts and probe values are exact.", "",
      "## Tally", "",
      f"- gated: {len(gated)} of {len(keys)}; " + ", ".join(f"{k} {n}" for k, n in sorted(vc.items())),
      f"- KILLED by script: " + (", ".join(f"{k} {n}" for k, n in kb.most_common()) or "none"),
      f"- candidates (gate survivors whose probe moves): {len(survivors)}",
      f"- equivalent-candidates: {len(equiv)}", f"- TIMEOUT: {len(timeouts)}", "",
      "## Gate table", "", "| key | site | patch | verdict | killed_by | class | wall s (prov.) | load1 |", "|---|---|---|---|---|---|---|---|"]
for k, r in recs.items():
    g = r["gate"]
    md.append(f"| {k} | {r['site']} | `{r['patch']}` | {g['verdict']} | {', '.join(g.get('killed_by') or []) or '-'} | {r['class']} | {g.get('wall_s')} | {g.get('load1_start')}..{g.get('load1_end')} |")
md += ["", "## Survivors: the step-4 answer per key", ""]
for k, r in recs.items():
    if r["class"] in ("candidate", "equivalent-candidate"):
        md.append(f"**{k}** {r['site']} `{r['patch']}` ({r['gate']['verdict']}, {r['class']}). {r['m4_answer']} "
                  f"Probe: `{r['probe']['command']}`: baseline {r['probe']['baseline_value']}; mutant {r['probe']['mutant_value']}. "
                  f"Inputs tried: {'; '.join(r['probe']['inputs_tried'])}. Should have failed: {r['should_fail']}.")
        if r["class"] == "candidate":
            f = r["finding"]
            md.append(f"Candidate (id assigned at consolidation): *{f['title']}*; severity {f['severity_claimed']}; class_guess {f['class_guess']}; metric: {f['metric_definition']}; perturbation direction {f['perturbation']['expected_direction']}, observed {f['perturbation']['observed_value']}; null: {f['null_control']['note']}.")
        md.append("")
killed = [r for r in recs.values() if r["class"] == "killed"]
if killed:
    md += ["## KILLED (non-findings)", ""]
    for r in killed:
        md.append(f"- {r['key']} {r['site']}: killed by {', '.join(r['killed_by'])} (`{r['gate_command']}`); " + "; ".join(r["failing_check_lines"][:3]))
    md.append("")
md += ["## Coverage", "", f"D3.M3 (this box): enumerator `{ENUM}`, universe {universe}, examined {examined}, not reached {len(not_reached)} groups (every other key, by box; TIMEOUTs by name). D3.M1, D3.M2, D3.M4, D3.M5 and their redispatched C-items are carried verbatim from REPORT-D3-u1b.json.", "",
       "## Findings", "", "None numbered here: findings: []. The candidates above are returned under `gate_survivors` for the orchestrator's consolidation to number.", "",
       "## Unfinished", ""] + ([f"- {u['step']}: {u['what']}" for u in unfinished] or ["- none"]) + ["",
       "## Exposure", "", "None (no docs/ or GitHub records read). Other boxes' dispatch refs were read for their keys.tsv only, to name not_reached by box.", ""]
(W / "REPORT.json").write_text(json.dumps(rep, indent=1) + "\n")
(W / "REPORT.md").write_text("\n".join(md) + "\n")
print(f"REPORT gated={len(gated)} candidates={len(survivors)} equivalent={len(equiv)} timeouts={len(timeouts)} missing={len(missing)} universe={universe} examined={examined}")
