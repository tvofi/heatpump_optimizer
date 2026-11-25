"""Box D3-g34: assemble REPORT.json / REPORT.md from results/<key>.json, gates/, keys.tsv,
wave_keys_by_box.tsv and REPORT-D3-u1b.json's carried coverage rows. Run from the tree root."""
import json, sys, collections
from pathlib import Path

BOX = "D3-g34"
BASE = "92d38ecb640bd462f2e19c0814d0f0b7df1ee692"
S1 = Path("dev/audit/rounds/round11/D3/s1")
W = S1 / "wave" / BOX
WR = f"dev/audit/rounds/round11/D3/s1/wave/{BOX}"

keys = [l.split("\t") for l in (W / "keys.tsv").read_text().splitlines()[1:] if l.strip()]
recs = {}
for k in keys:
    p = W / "results" / f"{k[0]}.json"
    if p.exists():
        recs[k[0]] = json.loads(p.read_text())
null = json.loads((W / "gates" / "null.json").read_text())
u1b = json.loads((S1 / "REPORT-D3-u1b.json").read_text())

# ---- coverage: M1/M2/M4/M5 carried verbatim from u1b, M3 replaced by this wave's row
cov = []
for row in u1b["coverage"]:
    if row["step"] == "D3.M3":
        m3_redis = row.get("redispatched", [])
        continue
    r = dict(row)
    r["carried"] = "verbatim from dev/audit/rounds/round11/D3/s1/REPORT-D3-u1b.json (box D3-u1b), not re-driven by box D3-g34"
    cov.append(r)

by_box = collections.OrderedDict()
for line in (W / "wave_keys_by_box.tsv").read_text().splitlines():
    if not line.strip():
        continue
    b, k = line.split("\t")[:2]
    by_box.setdefault(b, []).append(k)
universe = sum(len(v) for v in by_box.values())
gated_here = [k for k in recs if recs[k]["gate"]["verdict"] != "TIMEOUT"]
timeouts = [k for k in recs if recs[k]["gate"]["verdict"] == "TIMEOUT"]
missing = [k[0] for k in keys if k[0] not in recs]
not_reached = [f"assigned to box {b} ({len(v)} keys)" for b, v in by_box.items() if b != BOX]
not_reached += [f"{k} (box {BOX}): TIMEOUT past the 4 h cap" for k in timeouts]
not_reached += [f"{k} (box {BOX}): not gated" for k in missing]
m3 = {
    "step": "D3.M3",
    "enumerator": "awk -F'\\t' '$6==\"gate\"' SURVIVORS.tsv (the wave list, 742 keys; this box's copy of the split is "
                  f"{WR}/wave_keys_by_box.tsv, {universe} rows, and its own 16 keys are {WR}/keys.tsv)",
    "universe": universe,
    "examined": len(gated_here),
    "not_reached": not_reached,
    "redispatched": m3_redis,
    "evidence": ("box D3-g34 full gates, one at a time, GATE_JOBS=1, GATE_SCOPE=full GOLDEN_MODE=drift (gate_wave.sh run, out of tree on "
                 "dispatch/finder-r11-D3-g34): PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/fullgate.py run --src complete "
                 "--key <key> for each key of keys.tsv; records " + ", ".join(f"{WR}/gates/{k}.json" for k in recs) +
                 f"; null control {WR}/gates/null.json (fullgate.py null). Earlier D3.M3 full gates (boxes D3-top6, D3-rem: "
                 "REPORT-D3-top6.md, REPORT-D3-rem.md) cover the 8 deduped keys outside this 742-key universe. redispatched carried "
                 "verbatim from REPORT-D3-u1b.json's D3.M3 row."),
}
cov.insert([c["step"] for c in cov].index("D3.M4") if any(c["step"] == "D3.M4" for c in cov) else len(cov), m3)

# ---- per-key rows
def site(r):
    return r["site"]
gated = [{"key": k, "site": f'{r["file"]}:{r["line"]} {r["site"].split()[-1]}', "verdict": r["gate"]["verdict"],
          "killed_by": r["gate"].get("killed_by", []), "class": r["class"]} for k, r in recs.items()]
cands = [r for r in recs.values() if r["class"] == "candidate"]
equivs = [r for r in recs.values() if r["class"] == "equivalent-candidate"]
killed = [r for r in recs.values() if r["class"] == "killed"]

nf = [{"claim": "null control: fullgate.py null on box D3-g34 (comment-only marker) is red only on tree-state artefact checks",
       "command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/fullgate.py null",
       "value": f"gate_rc={null.get('gate_rc')} failed_scripts={null.get('failed_scripts')} wall_s={null.get('wall_s')} "
                f"load1 {null.get('load1_start')}..{null.get('load1_end')} (provisional; nproc 4, Intel Xeon @ 2.10GHz)"}]
for r in killed:
    nf.append({"claim": f"{r['key']} {r['file']}:{r['line']} ({r['patch']}) is KILLED by the full gate",
               "command": r["gate_command"],
               "value": f"verdict=KILLED killed_by={r['gate']['killed_by']} gate_rc={r['gate']['gate_rc']} wall_s={r['gate']['wall_s']} "
                        f"(provisional). {r.get('kill_note', '')}"})
for r in equivs:
    p = r["probe"]
    nf.append({"claim": f"{r['key']} {r['file']}:{r['line']} ({r['patch']}) survives the full gate as RED-AS-NULL and is an "
                        "equivalent-candidate: no input found that separates it",
               "command": p["command"],
               "value": f"cases_differing={p.get('cases_differing')} null_differing={p.get('null_differing')} baseline={p.get('baseline_value')} "
                        f"mutant={p.get('mutant_value')}; inputs tried: {'; '.join(p.get('inputs_tried', []))}; gate {r['gate']['verdict']} "
                        f"gate_rc={r['gate']['gate_rc']}"})

harn = ["dev/audit/rounds/round11/D3/s1/fullgate.py", f"{WR}/build_results.py", f"{WR}/probes/_sysid_lib.py"]
harn += sorted({r["probe"]["path"] for r in recs.values() if r.get("probe") and r["probe"].get("path")})

leads = []
for r in killed:
    if "structure.py" in " ".join(r["gate"].get("killed_by", [])):
        leads.append({"owner_seat": "D3-s1", "file": r["file"], "symbol": r["function"],
                      "what": (f"{r['key']} ({r['file']}:{r['line']}, {r['patch']}) is KILLED only by tests/structure.py's max_cc ratchet "
                               "reading the tree as IMPROVED (44 -> 43), not by a behavioural assertion; its probe separates 1 of 1 input "
                               "(the refusal reason changes, the outcome stays a refusal). Any GUARD_OFF on identify() that lowers max_cc is "
                               "killed this way regardless of behaviour.")})

unfinished = [{"step": "D3.M3", "what": f"{k}: TIMEOUT past the 4 h cap; last script in {WR}/gates/{k}.log"} for k in timeouts]
unfinished += [{"step": "D3.M3", "what": f"{k}: not gated on this box"} for k in missing]

exposure = ("Box D3-g34 read COMMON.md, D3.md, dev/audit/README.md and finding.schema.json (through haiku extractors and the predecessor "
            "seat), the slice reports and M4 answers its keys came from, REPORT-D3-top6.md / REPORT-D3-rem.md as the pattern, its own "
            "keys' production lines in sysid.py, and its gate logs. No docs/, register, round11/J/, verifier report or GitHub record "
            "read beyond the box's own dispatch, inbox and wip refs. Resumed from a predecessor seat's checkpoint "
            "(handoff-wip/finder-r11-D3-g34 @ d552338441): its seven gate records, probes and results were kept, not redone; the "
            "a9bc37e9 gate it had running was lost with its container and re-run here; a container restart on this fire killed "
            "the a9bc37e9 gate once more at 01:14Z and it was re-run from the start.")

rep = {
    "dimension": "D3", "baseline_sha": BASE, "box": BOX, "report_path": f"{WR}/REPORT.md", "exposure": exposure,
    "coverage": cov, "unfinished": unfinished, "findings": [], "non_findings": nf, "harnesses": harn, "leads": leads,
    "gated": gated, "gate_survivors": cands, "equivalent_candidates": equivs,
    "procedure": ("gate_wave.sh (out of tree, dispatch/finder-r11-D3-g34): null once, then each key of keys.tsv in order, one gate at a "
                  "time, GATE_JOBS=1, 4 h cap, checkpoint after each; per key build_results.py writes results/<key>.json and runs the "
                  "key's probe in $HOME/probe-tree, a clean detached worktree of the baseline it checks before every run."),
}
(W / "REPORT.json").write_text(json.dumps(rep, indent=1) + "\n")

# ---- REPORT.md
tally = collections.Counter(r["gate"]["verdict"] for r in recs.values())
kb = collections.Counter(s for r in killed for s in r["gate"]["killed_by"])
md = [f"# D3-s1 box {BOX}: full gates for 16 u1 full-net survivors (round 11)", "",
      f"Baseline `{BASE}`. All 16 keys mutate `SystemIdentification.identify` in `custom_components/heatpump_optimizer/sysid.py`.", "",
      "## Machine and controls", "",
      "nproc 4, Intel(R) Xeon(R) Processor @ 2.10GHz, 16 GB, no swap; load1 0.4-1.0 throughout (wall, CPU and load are provisional: true; the judge re-takes them). "
      "One gate at a time, GATE_JOBS=1, GATE_SCOPE=full GOLDEN_MODE=drift.", "",
      f"Null control (`fullgate.py null`, {WR}/gates/null.json): gate_rc={null.get('gate_rc')}, red on {null.get('failed_scripts')} only. "
      "All three are tree-state artefacts of the stripped detached worktree (closure.py selftest's skip-not-under-scoped pins, "
      "entities.py's scoped-path record, harness_headers.py's round-4 header the finder-wall strip removes). No machine red, "
      "so the null was usable as taken. Every key's gate was red on exactly these three, plus structure.py for the one KILLED key.", "",
      "Probes run in `$HOME/probe-tree`, a clean baseline worktree, never in the gate's tree. The predecessor's first five records were rebuilt there "
      "after a contamination (see NOTES.md; the superseded records are kept in results-superseded/).", "",
      "## Tally", "",
      f"- gated: {len(gated_here)} of {len(keys)}; TIMEOUT: {len(timeouts)}; not gated: {len(missing)}",
      f"- KILLED: {tally.get('KILLED', 0)} ({', '.join(f'{s}: {n}' for s, n in kb.items()) or 'none'})",
      f"- SURVIVED: {tally.get('SURVIVED', 0)}; RED-AS-NULL: {tally.get('RED-AS-NULL', 0)}",
      f"- candidates (probe moves): {len(cands)}; equivalent-candidates: {len(equivs)}", "",
      "findings: [] — candidates go under `gate_survivors` for the orchestrator's consolidation to number.", "",
      "| key | site | patch | verdict | class | probe differing |", "|---|---|---|---|---|---|"]
for r in recs.values():
    p = r.get("probe") or {}
    md.append(f"| {r['key']} | sysid.py:{r['line']} {r['site'].split()[-1]} | `{r['patch']}` | {r['gate']['verdict']} | {r['class']} | {p.get('cases_differing', '')} |")
md += ["", "## KILLED", ""]
for r in killed:
    md.append(f"**{r['key']}** sysid.py:{r['line']} `{r['patch']}`: {r.get('kill_note', '')}")
md += ["", "## Survivors: step-4 answers", ""]
for r in cands + equivs:
    p = r["probe"]; f = r.get("finding") or {}
    md.append(f"### {r['key']} — sysid.py:{r['line']} {r['site'].split()[-1]} ({r['class']})")
    md.append("")
    md.append(f"Patch `{r['patch']}`. Gate {r['gate']['verdict']} (gate_rc {r['gate']['gate_rc']}, wall {r['gate']['wall_s']} s, load1 "
              f"{r['gate']['load1_start']}..{r['gate']['load1_end']}, provisional).")
    md.append(f"Probe `{p['command']}`: baseline `{p.get('baseline_value')}`, mutant `{p.get('mutant_value')}`; cases differing "
              f"{p.get('cases_differing')}, null differing {p.get('null_differing')}. Inputs tried: {'; '.join(p.get('inputs_tried', []))}.")
    if f:
        md.append(f"Candidate: {f.get('title')}. {f.get('claim', '')}")
    md.append(f"Should have failed: {r.get('should_fail')}")
    md.append("")
md += ["## Leads", ""] + [f"- {l['what']}" for l in leads] + ["", "## Unfinished", ""]
md += [f"- {u['what']}" for u in unfinished] or ["- none"]
md += ["", "## Coverage", "",
       f"D3.M3: universe {universe} (the wave list), examined {len(gated_here)} on this box; the rest are assigned to boxes D3-g01..D3-g47 "
       "(not_reached in REPORT.json). D3.M1, D3.M2, D3.M4 and D3.M5 rows and their redispatched C-items are carried verbatim from REPORT-D3-u1b.json."]
(W / "REPORT.md").write_text("\n".join(md) + "\n")
print(f"REPORT gated={len(gated_here)} candidates={len(cands)} equivalent={len(equivs)} killed={len(killed)} timeouts={len(timeouts)} missing={len(missing)}")
