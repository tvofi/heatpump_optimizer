"""Assemble REPORT.json and REPORT.md for box D3-g09 (seat D3-s1) from results/*.json."""
import json, glob, os, sys
from pathlib import Path
SC = Path(__file__).parent
TR = Path.home() / "audit-r11-D3-s1"
S1 = TR / "dev/audit/rounds/round11/D3/s1"
W = S1 / "wave/D3-g09"
REL = "dev/audit/rounds/round11/D3/s1/wave/D3-g09"
BASE = "92d38ecb640bd462f2e19c0814d0f0b7df1ee692"
keys = [l.split("\t")[0] for l in (W / "keys.tsv").read_text().splitlines()[1:] if l.strip()]
res = {k: json.load(open(W / "results" / f"{k}.json")) for k in keys if (W / "results" / f"{k}.json").exists()}
null = json.load(open(W / "gates/null.json"))
u1b = json.load(open(S1 / "REPORT-D3-u1b.json"))
machine = (W / "MACHINE.txt").read_text()

# other boxes, from their dispatch refs' keys.tsv
others = []
for f in sorted(glob.glob(str(SC / "boxes/D3-g*.tsv"))):
    b = Path(f).stem
    if b == "D3-g09":
        continue
    rows = [l.split("\t") for l in Path(f).read_text().splitlines()[1:] if l.strip()]
    others.append((b, rows))
n_other = sum(len(r) for _, r in others)
not_reached = []
for b, rows in others:
    first, last = rows[0], rows[-1]
    not_reached.append(f"assigned to box {b}: {len(rows)} keys ({os.path.basename(first[2])}:{first[3]} {first[4]} .. "
                       f"{os.path.basename(last[2])}:{last[3]} {last[4]}; keys {' '.join(r[0] for r in rows)})")
timeouts = [k for k, r in res.items() if r["class"] == "timeout"]
for k in timeouts:
    not_reached.append(f"TIMEOUT on box D3-g09 (gate past the {res[k]['gate'].get('cap_s', 14400)} s cap): {k} {res[k]['site']}")
missing = [k for k in keys if k not in res]
for k in missing:
    not_reached.append(f"not gated on box D3-g09 (STOP/SKIP or unfinished): {k}")
examined = len(res) - len(timeouts)

carried = []
for row in u1b["coverage"]:
    if row["step"] in ("D3.M1", "D3.M2", "D3.M4", "D3.M5"):
        r = dict(row)
        r["evidence"] = "carried verbatim from REPORT-D3-u1b.json (not re-driven by box D3-g09): " + str(row["evidence"])
        r["carried"] = True
        carried.append(r)
m3_old = next(r for r in u1b["coverage"] if r["step"] == "D3.M3")
m3 = {
    "step": "D3.M3",
    "enumerator": "awk -F'\\t' '$6==\"gate\"' SURVIVORS.tsv",
    "universe": 742,
    "examined": examined,
    "not_reached": not_reached,
    "redispatched": m3_old.get("redispatched", []),
    "evidence": ("the u1 full-gate wave (owner ruling 2026-11-22: every u1 full-net survivor gets the full gate): 742 keys over "
                 "boxes D3-g01..D3-g47, this box D3-g09 holding 16 (" + REL + "/keys.tsv, identical to the dispatch ref's). "
                 "Per key: gate_wave.sh run -> fullgate.py run --src complete --key <key> (GATE_SCOPE=full GOLDEN_MODE=drift "
                 "GOLDEN_REF=" + BASE + " GATE_JOBS=1 ./tests/run.sh on the committed one-line mutant), records "
                 + REL + "/gates/<key>.json; null control " + REL + "/gates/null.json (gate_rc " + str(null.get("gate_rc")) +
                 ", failed " + json.dumps(null.get("failed_scripts")) + "). Examined = the " + str(examined) +
                 " keys this box gated to a verdict; the earlier boxes' D3.M3 rows (D3-top6, D3-rem) gated the 8 deduplicated "
                 "keys, which sit outside this 742-key universe. The other " + str(n_other) + " keys are named by box from the "
                 "47 dispatch/finder-r11-D3-g<NN> refs' keys.tsv. SURVIVORS.tsv itself is not in this box's tree; the count "
                 "742 is the brief's and the 47 key lists sum to it (742 distinct)."),
}
coverage = carried[:3] + [m3] + carried[3:]
coverage.sort(key=lambda r: int(r["step"].split("M")[1]))

gated = [{"key": k, "site": r["site"], "verdict": r["gate"].get("verdict"), "killed_by": r["gate"].get("killed_by", []),
          "class": r["class"]} for k, r in res.items()]
cands = [r for r in res.values() if r["class"] == "candidate"]
equiv = [r for r in res.values() if r["class"] == "equivalent-candidate"]
killed = [r for r in res.values() if r["class"] == "killed"]
nonf = []
for r in killed:
    nonf.append({"claim": f"{r['site']} ({r['patch']}) is killed by the full gate: {', '.join(r['gate'].get('killed_by') or [])}",
                 "command": r["gate_command"], "value": f"verdict KILLED, gate_rc {r['gate'].get('gate_rc')}, killed_by "
                 + json.dumps(r['gate'].get('killed_by')) + f" beyond this box's null; record {r['gate_record']}"})
for r in equiv:
    nonf.append({"claim": f"{r['site']} ({r['patch']}) survives the full gate ({r['gate'].get('verdict')}) but no reachable input "
                 f"separates it from the baseline: {r['should_fail']}",
                 "command": r["probe"]["command"],
                 "value": f"baseline {r['probe']['baseline_value']}; mutant {r['probe']['mutant_value']}; inputs tried: "
                 + "; ".join(r["probe"]["inputs_tried"])})
harn = [{"path": "dev/audit/rounds/round11/D3/s1/fullgate.py", "what": "the full gate per key and the null (carried, D3-top6's)"},
        {"path": "$HOME/gate_wave.sh (dispatch ref tip, out of tree)", "what": "the wave driver: null once, then fullgate.py run per key of keys.tsv in order, one gate at a time, 4 h cap (TIMEOUT never KILLED), checkpoint after each gate"},
        {"path": REL + "/probes/_probe_lib.py", "what": "shared probe plumbing: thread pin, FakeHass coordinator, in-memory mutant (method recompiled from its source, mock.patch.object)"}]
for k in keys:
    p = W / "probes" / f"probe_{k}.py"
    if p.exists():
        harn.append({"path": f"{REL}/probes/probe_{k}.py", "what": f"step-4 probe for {k}",
                     "command": f"PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 {REL}/probes/probe_{k}.py"})
for h in ("_pred_common.py", "_pv_common.py", "_quiet_common.py", "_sysid_common.py", "_defrost_common.py"):
    harn.append({"path": f"{REL}/probes/{h}", "what": "arms shared by the probes of one function"})

unfinished = [f"TIMEOUT {k} {res[k]['site']}: gate past the cap; last script seen {res[k].get('last_script_seen')}" for k in timeouts]
unfinished += [f"not gated: {k}" for k in missing]
unfinished.append("SURVIVORS.tsv (the D3.M3 enumerator's input) is not in this box's tree; universe 742 is taken from the brief and "
                  "re-derived as the union of the 47 dispatch refs' keys.tsv (742 distinct keys)")
leads = []
if any(r["key"] == "326b26f53972df61" and r["class"] == "candidate" for r in res.values()):
    leads.append({"owner_seat": "unknown", "file": "tests/harness.py", "symbol": "FakeStates.get",
                  "what": "FakeStates.get is a plain dict.get and answers None for entity_id None; Home Assistant's StateMachine.get "
                          "(core.py, 2025.1.0: `self._states_data.get(entity_id) or self._states_data.get(entity_id.lower())`) raises "
                          "AttributeError. Every coordinator read that could pass a falsy id to hass.states.get is untestable on the stub; "
                          "a sweep of `hass.states.get(` call sites whose argument can be None is outside this box's cells"})
if any(r["key"] == "425a9196b86265d0" and r["class"] == "candidate" for r in res.values()):
    leads.append({"owner_seat": "unknown", "file": "custom_components/heatpump_optimizer/coordinator.py",
                  "symbol": "HeatPumpOptimizerCoordinator._run_system_identification",
                  "what": "D9 (CPU on a Pi-class host): the inactive-experiment early return is the only thing keeping an idle sysid off the process worker each cycle; no budget or count pins it (probe_425a9196b86265d0.py: 0 vs 1 off-loop job per idle cycle)"})

report = {
    "dimension": "D3", "baseline_sha": BASE, "box": "D3-g09", "seat": "D3-s1",
    "report_path": REL + "/REPORT.md",
    "exposure": ("No docs/ or GitHub issue/PR text read; no register, J/ or verifier report read. Read from git refs: the 47 "
                 "dispatch/finder-r11-D3-g<NN> tips' keys.tsv (key lists only), to name the other boxes' keys in not_reached. "
                 "Downloaded homeassistant==2025.1.0's wheel to a scratch dir to read StateMachine.get (core.py:2151-2158), "
                 "transcribed in probes/_pv_common.py:HAStates for key 326b26f53972df61."),
    "coverage": coverage, "unfinished": unfinished, "findings": [], "non_findings": nonf, "harnesses": harn, "leads": leads,
    "gated": gated, "gate_survivors": cands, "equivalent_candidates": equiv,
    "machine": machine, "null_control": {"record": REL + "/gates/null.json", "gate_rc": null.get("gate_rc"),
                                          "failed_scripts": null.get("failed_scripts"), "summary": null.get("summary"),
                                          "wall_s": null.get("wall_s"), "load1_start": null.get("load1_start"),
                                          "load1_end": null.get("load1_end"), "provisional": True},
}

# ---- markdown
def tally():
    from collections import Counter
    v = Counter(r["gate"].get("verdict") for r in res.values())
    kb = Counter(s for r in killed for s in (r["gate"].get("killed_by") or []))
    return v, kb
v, kb = tally()
md = [f"# D3-s1, box D3-g09 -- full gate for 16 u1 full-net survivors (round 11)", "",
      f"Baseline `{BASE}`. Report path `{REL}/REPORT.md`. Seat D3-s1, step D3.M3 (+ D3.M4 answers by probe).", "",
      "## Machine and controls", "", "```", machine.strip(), "```", "",
      f"Null control (`fullgate.py null`, a comment-only marker): gate_rc {null.get('gate_rc')}, failed scripts "
      f"{null.get('failed_scripts')}, summary {null.get('summary')}, wall {null.get('wall_s')} s, load1 "
      f"{null.get('load1_start')} -> {null.get('load1_end')} (provisional). Record `{REL}/gates/null.json`.", "",
      "Procedure: `gate_wave.sh run` (dispatch ref) applies each key's one-line mutant with `fullgate.py run --src complete "
      "--key <key>`: commit, gate_lock lease, `GATE_SCOPE=full GOLDEN_MODE=drift GOLDEN_REF=<baseline> GATE_JOBS=1 ./tests/run.sh`, "
      "record, reset; one gate at a time, 4 h cap. Wall, CPU and load numbers are provisional; verdicts and probe values are counts.", "",
      "## Tally", "",
      f"- gated: {len(res)} of {len(keys)}",
      f"- KILLED: {v.get('KILLED', 0)}" + (f" (by script: {dict(kb)})" if kb else ""),
      f"- SURVIVED: {v.get('SURVIVED', 0)}", f"- RED-AS-NULL: {v.get('RED-AS-NULL', 0)}", f"- TIMEOUT: {v.get('TIMEOUT', 0)}",
      f"- candidates: {len(cands)}", f"- equivalent-candidates: {len(equiv)}", "",
      "| key | site | patch | verdict | killed_by | gate wall s | class |", "|---|---|---|---|---|---|---|"]
for k in keys:
    if k in res:
        r = res[k]
        md.append(f"| {k} | {r['site']} | `{r['patch']}` | {r['gate'].get('verdict')} | {', '.join(r['gate'].get('killed_by') or []) or '-'} | {r['gate'].get('wall_s', '-')} | {r['class']} |")
    else:
        md.append(f"| {k} | - | - | not gated | - | - | unfinished |")
md += ["", "## Survivors: step-4 answers with probe numbers", ""]
for k in keys:
    r = res.get(k)
    if not r or r["class"] in ("killed", "timeout"):
        continue
    p = r["probe"]
    head = f"### {k} -- {r['site']} ({r['class']}" + (f", severity claimed {r['severity_claimed']}, class guess {r['class_guess']}" if r["class"] == "candidate" else "") + ")"
    md += [head, "",
           f"`{r['patch']}` in `{r['function']}`; gate {r['gate'].get('verdict')} (gate_rc {r['gate'].get('gate_rc')}).",
           (f"**{r['title']}.** {r['claim']}" if r["class"] == "candidate" else ""),
           f"Probe `{p['path']}`: {p['metric']}. Baseline **{p['baseline_value']}**; mutant **{p['mutant_value']}**. "
           f"Null: {p['null_control']}. Inputs tried: {'; '.join(p['inputs_tried'])}. load1 {p['load1']}, thread_factor {p['thread_factor']}.",
           f"Should have failed: {r['should_fail']}.", ""]
if killed:
    md += ["## Non-findings: KILLED by the full gate", ""]
    for r in killed:
        md.append(f"- {r['key']} {r['site']}: killed by {', '.join(r['gate'].get('killed_by') or [])} (gate_rc {r['gate'].get('gate_rc')}); `{r['gate_record']}`")
    md.append("")
md += ["## Leads", ""] + [f"- {l['file']} `{l['symbol']}`: {l['what']}" for l in leads] + ["",
       "## Unfinished", ""] + [f"- {u}" for u in unfinished] + ["", "## Exposure", "", report["exposure"], ""]
(W / "REPORT.json").write_text(json.dumps(report, indent=1, ensure_ascii=False) + "\n")
(W / "REPORT.md").write_text("\n".join(md))
print(f"REPORT written: gated {len(res)} candidates {len(cands)} equivalent {len(equiv)} killed {len(killed)} timeouts {len(timeouts)}")
