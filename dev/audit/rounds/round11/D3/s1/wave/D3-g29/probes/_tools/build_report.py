#!/usr/bin/env python3
"""REPORT.json + REPORT.md for box D3-g29 from results/*.json, gates/*.json, the u1b coverage rows and the wave key list."""
import json, collections
from pathlib import Path
SP = Path(__file__).resolve().parent
H = Path.home()
TR = H / "audit-r11-D3-s1"
S1 = TR / "dev/audit/rounds/round11/D3/s1"
W = S1 / "wave/D3-g29"
REL = "dev/audit/rounds/round11/D3/s1/wave/D3-g29"
BASE = "92d38ecb640bd462f2e19c0814d0f0b7df1ee692"
FG = "dev/audit/rounds/round11/D3/s1/fullgate.py"
keys = [l.split("\t")[0] for l in (W / "keys.tsv").read_text().splitlines()[1:] if l.strip()]
recs = {k: json.loads((W / "results" / f"{k}.json").read_text()) for k in keys if (W / "results" / f"{k}.json").exists()}
null = json.loads((W / "gates/null.json").read_text())
mach = (W / "MACHINE.txt").read_text()
MACH = "box D3-g29: Linux x86_64, nproc 4, Intel Xeon @ 2.10GHz, 16 GB, venv-ci CPython 3.14, alone on its machine"

u1b = json.loads((S1 / "REPORT-D3-u1b.json").read_text())
cov = []
for row in u1b["coverage"]:
    if row["step"] == "D3.M3":
        continue
    r = dict(row)
    r["evidence"] = "carried verbatim from REPORT-D3-u1b.json (not re-driven on box D3-g29): " + row["evidence"]
    cov.append(r)

wave = [l.split("\t") for l in (SP / "wave_keys.tsv").read_text().splitlines() if l.strip()]
by_box = collections.OrderedDict()
for box, key, site in wave:
    by_box.setdefault(box, []).append((key, site))
timeouts = [k for k, r in recs.items() if r["class"] == "timeout"]
ungated = [k for k in keys if k not in recs]
nr = []
for box, items in by_box.items():
    if box == "D3-g29":
        continue
    files = collections.Counter(s.split(":")[0].split("/")[-1] for _, s in items)
    nr.append(f"assigned to box {box}: {len(items)} keys ({', '.join(f'{f} {n}' for f, n in files.items())}; first {items[0][0]}, last {items[-1][0]})")
for k in timeouts:
    nr.append(f"TIMEOUT on box D3-g29 (past the 4 h cap): {k} {recs[k]['site']}")
for k in ungated:
    nr.append(f"not gated on box D3-g29 (STOP/SKIP or unfinished): {k}")
examined = len(keys) - len(timeouts) - len(ungated)
m3 = {"step": "D3.M3", "enumerator": "awk -F'\\t' '$6==\"gate\"' SURVIVORS.tsv",
      "universe": len(wave), "examined": examined, "not_reached": nr, "redispatched": [],
      "evidence": (f"wave list of 742 u1 full-net survivors (the owner's ruling 2026-11-22), reconstructed on this box as the union of the 47 "
                   f"dispatch/finder-r11-D3-gNN keys.tsv files ({len(wave)} keys, 0 duplicates; SURVIVORS.tsv itself is not in the stripped tree). "
                   f"This box full-gated its {len(keys)} keys: PYTHONPATH=tests/hastub python3 {FG} run --src complete --key <key> "
                   f"(GATE_SCOPE=full GOLDEN_MODE=drift GATE_JOBS=1 ./tests/run.sh), records {REL}/gates/<key>.json, null {REL}/gates/null.json. "
                   "The earlier boxes' D3.M3 rows (REPORT-D3-top6.json, REPORT-D3-rem.json: 8 keys gated under other keys) sit outside this 742-key universe.")}
cov.insert(3 if len(cov) >= 3 else len(cov), m3)
cov.sort(key=lambda r: int(r["step"].split(".M")[1]))

gated, survivors, equivs, nonf = [], [], [], []
for k in keys:
    r = recs.get(k)
    if not r:
        continue
    g = r["gate"]
    gated.append({"key": k, "site": r["site"], "verdict": g["verdict"], "killed_by": g.get("killed_by") or [], "class": r["class"]})
    gcmd = g["command"]
    if r["class"] == "killed":
        nonf.append({"claim": f"full gate {k} {r['site']} ({r['patch']}): KILLED, the suite fails on it",
                     "command": gcmd, "value": f"killed_by={','.join(g['killed_by'])}; gate_rc {g['gate_rc']}; wall {g['wall_s']} s, load1 {g['load1_start']}..{g['load1_end']} (provisional)"})
    elif r["class"] == "equivalent-candidate":
        equivs.append(r)
        nonf.append({"claim": f"full gate {k} {r['site']} ({r['patch']}): {g['verdict']}; probe: equivalent-candidate ({r.get('note')}). {r['probe']['reach']}",
                     "command": r["probe"]["command"] + " --reach",
                     "value": f"baseline {r['probe']['baseline_value']}; mutant {r['probe']['mutant_value']}; null_delta={r['probe']['null_delta']}; inputs tried: {'; '.join(r['probe']['inputs_tried'])}"})
    elif r["class"] == "candidate":
        survivors.append(r)

probes = sorted(f"{REL}/probes/{p.name}" for p in (W / "probes").glob("*.py"))
harn = [FG] + probes
tally = collections.Counter(x["verdict"] for x in gated)
cls = collections.Counter(x["class"] for x in gated)
unfinished = []
if timeouts:
    unfinished.append({"step": "D3.M3", "what": "TIMEOUT past the 4 h cap: " + "; ".join(f"{k} {recs[k]['site']} (last script {recs[k].get('last_script')})" for k in timeouts)})
if ungated:
    unfinished.append({"step": "D3.M3", "what": "not gated on this box: " + ", ".join(ungated)})

leads = [{"owner_seat": "unknown", "file": "custom_components/heatpump_optimizer/optimizer.py", "symbol": "stored_heat_survival (line 3184-3186)",
          "what": "The comment 'Capped before exp() so a near-zero demand underflows to 0.0 cleanly rather than raising' describes no reachable behaviour: math.exp of any negative argument underflows to 0.0 without raising (probe_f062e0cc415ee33e: raises 0 in both arms over exponents 720..1e301 and an overflowed one). A docs/comments seat (D5) owns the wording."}]

rep = {"dimension": "D3", "baseline_sha": BASE, "box": "D3-g29", "report_path": f"{REL}/REPORT.md",
       "exposure": "none: no docs/ or GitHub records read; the other 46 boxes' keys.tsv on their dispatch refs were read only to name not_reached by box",
       "coverage": cov, "unfinished": unfinished, "findings": [], "non_findings": nonf, "harnesses": harn, "leads": leads,
       "gated": gated, "gate_survivors": survivors, "equivalent_candidates": equivs,
       "null_control": {"path": f"{REL}/gates/null.json", "gate_rc": null.get("gate_rc"), "failed_scripts": null.get("failed_scripts"),
                        "fail_lines": null.get("fail_lines"), "wall_s": null.get("wall_s"), "load1": [null.get("load1_start"), null.get("load1_end")]},
       "procedure": "gate_wave.sh (shipped on dispatch/finder-r11-D3-g29): null once, then fullgate.py run per key of keys.tsv, one gate at a time, GATE_JOBS=1, 4 h cap, checkpoint after each gate; probes ran from a separate baseline worktree ($HOME/probe-tree) so no probe imported a gate-mutated file",
       "machine": MACH}

md = [f"# D3-s1 round 11, box D3-g29: full gate of 16 u1 full-net survivors (D3.M3) and their D3.M4 answers", "",
      f"Baseline {BASE}. {MACH}. Every wall and load1 is provisional; counts and probe values are exact.", "",
      "## Machine and controls", "", "```", mach.strip(), "```", "",
      f"Null control (`python3 {FG} null`, a comment-only marker): gate_rc={null.get('gate_rc')}, red scripts {null.get('failed_scripts')}, "
      f"FAIL counts {null.get('fail_lines')}, wall {null.get('wall_s')} s, load1 {null.get('load1_start')}..{null.get('load1_end')}. "
      "A mutant is KILLED only by a script red beyond the null or failing more checks than in it; red on the null's scripts alone reads RED-AS-NULL (survived).", "",
      "Procedure: gate_wave.sh's null then run (one gate at a time, GATE_JOBS=1, 4 h cap, a checkpoint after each). Probes were executed in a separate baseline worktree so none imported a gate-mutated file; each applies its mutant in memory. The reach sweep (`probes/reach_sweep.py`, output `probes/reach_sweep.out`) solves the 50 tests/golden.py scenarios with recording spies on the five mutated symbols.", "",
      "## Tally", "",
      f"Gated {len(gated)} of {len(keys)}: " + ", ".join(f"{v} {n}" for v, n in sorted(tally.items())) + ".",
      "Killed by script: " + (", ".join(f"{x['key']} by {','.join(x['killed_by'])}" for x in gated if x["verdict"] == "KILLED") or "none") + ".",
      f"Classes: " + ", ".join(f"{c} {n}" for c, n in sorted(cls.items())) + ".", "",
      "| key | site | patch | verdict | killed_by | wall s | load1 | class |", "|---|---|---|---|---|---|---|---|"]
for x in gated:
    r = recs[x["key"]]; g = r["gate"]
    md.append(f"| {x['key']} | {r['site']} | `{r['patch']}` | {g['verdict']} | {','.join(g.get('killed_by') or []) or '-'} | {g.get('wall_s')} | {g.get('load1_start')}..{g.get('load1_end')} | {r['class']} |")
md += ["", "## Gate survivors with a moving probe (finding candidates, ids left to consolidation)", ""]
for r in survivors:
    md += [f"### {r['key']} {r['site']}: {r['title']}", "",
           f"{r['claim']} Probe `{r['evidence_command']}`: baseline {r['probe']['baseline_value']}, mutant {r['probe']['mutant_value']}; null_delta={r['probe']['null_delta']}. "
           f"Inputs tried: {'; '.join(r['probe']['inputs_tried'])}. Reach: {r['probe']['reach']}. "
           f"Step 4: the production line is {r['site']} (`{r['patch']}`); the check that should have failed is {r['should_fail']['script']}: {r['should_fail']['assertion']}. "
           f"Severity claimed {r['severity_claimed']}, class_guess {r['class_guess']}.", ""]
md += ["## Equivalent-candidates (non-findings unless a later seat finds the input)", ""]
for r in equivs:
    md += [f"- {r['key']} {r['site']} (`{r['patch']}`), gate {r['gate']['verdict']}: {r['note']}. Baseline {r['probe']['baseline_value']}; mutant {r['probe']['mutant_value']}; null_delta={r['probe']['null_delta']}. "
           f"Inputs tried: {'; '.join(r['probe']['inputs_tried'])}. Reach: {r['probe']['reach']}. Step 4: {r['should_fail']['script']}: {r['should_fail']['assertion']}. Command `{r['probe']['command']} --reach`."]
md += ["", "## Killed (non-findings)", ""]
for x in gated:
    if x["class"] == "killed":
        r = recs[x["key"]]
        md.append(f"- {x['key']} {r['site']}: KILLED by {', '.join(x['killed_by'])} (`{r['gate']['command']}`); failing lines in {REL}/results/{x['key']}.json")
if not any(x["class"] == "killed" for x in gated):
    md.append("- none")
md += ["", "## Unfinished", ""] + ([f"- {u['what']}" for u in unfinished] or ["- none"])
md += ["", "## Coverage", ""] + [f"- {c['step']}: universe {c['universe']}, examined {c['examined']}, not reached {len(c['not_reached'])} line(s). Enumerator `{c['enumerator']}`." for c in cov]
md += ["", "## Leads", ""] + [f"- {l['owner_seat']} {l['file']} {l['symbol']}: {l['what']}" for l in leads]
md += ["", "## Harnesses", ""] + [f"- {h}" for h in harn]
md += ["", "## Exposure", "", rep["exposure"], ""]
(W / "REPORT.json").write_text(json.dumps(rep, indent=1) + "\n")
(W / "REPORT.md").write_text("\n".join(md))
print("REPORT written:", len(gated), "gated", dict(cls))
