#!/usr/bin/env python3
"""Box D3-g33: assemble REPORT.json and REPORT.md for seat D3-s1 (this box only) from results/<key>.json.

Command: python3 dev/audit/rounds/round11/D3/s1/wave/D3-g33/build_report.py
Adapted from box D3-g13's build_report.py (handoff/audit-r11-find-D3-g13) to this box's record shape
(build_records.py writes results/<key>.json from gates/<key>.json and the probe's two RESULT runs).
"""
import json
from pathlib import Path

W = Path(__file__).resolve().parent
S1 = W.parent.parent
BOX = "D3-g33"
REL = f"dev/audit/rounds/round11/D3/s1/wave/{BOX}"
BASE = "92d38ecb640bd462f2e19c0814d0f0b7df1ee692"
rows = [l.split("\t") for l in (W / "keys.tsv").read_text().splitlines()]
ROWS = [dict(zip(rows[0], r)) for r in rows[1:] if r and r[0]]
RES = {r["key"]: json.loads((W / "results" / f"{r['key']}.json").read_text())
       for r in ROWS if (W / "results" / f"{r['key']}.json").exists()}
NULL = json.loads((W / "gates" / "null.json").read_text())
MACHINE_TXT = (W / "MACHINE.txt").read_text().strip()
REFIRE_TXT = (W / "MACHINE-refire.txt").read_text().strip() if (W / "MACHINE-refire.txt").exists() else ""
ART = (W / "gates-artefact" / "NOTE.txt").read_text().strip() if (W / "gates-artefact" / "NOTE.txt").exists() else ""
u1b = json.loads((S1 / "REPORT-D3-u1b.json").read_text())
NOISE = ("thread_factor", "load1", "swapins")


def carried(step):
    r = dict(next(c for c in u1b["coverage"] if c["step"] == step))
    r["carried"] = f"verbatim from REPORT-D3-u1b.json (box D3-u1b); not re-driven on box {BOX}"
    return r


def probe_str(r, arm):
    d = r["probe"][f"all_results_{arm}"]
    return "; ".join(f"{k}={v}" for k, v in d.items() if k not in NOISE)


# ---- D3.M3: the wave list, 742 keys over boxes D3-g01..D3-g47
others, wave_total = [], 0
for f in sorted((W / "wave_boxes").glob("D3-g*.tsv")):
    box = f.stem
    ks = [dict(zip(rows[0], l.split("\t"))) for l in f.read_text().splitlines()[1:] if l.strip()]
    wave_total += len(ks)
    if box == BOX:
        continue
    files = {}
    for k in ks:
        files.setdefault(k["file"].split("/")[-1], []).append(int(k["line"]))
    span = "; ".join(f"{fn} {min(v)}-{max(v)}" for fn, v in sorted(files.items()))
    others.append(f"assigned to box {box}: {len(ks)} keys ({span})")
timeouts = [k for k, r in RES.items() if r["class"] == "timeout"]
missing = [r["key"] for r in ROWS if r["key"] not in RES]
examined = len(RES) - len(timeouts)
not_reached = others + [f"TIMEOUT on box {BOX} (4 h cap): {k} {RES[k]['site']}" for k in timeouts] + \
    [f"not gated on box {BOX} (stopped or skipped): {k}" for k in missing]
m3_prev = next(c for c in u1b["coverage"] if c["step"] == "D3.M3")
m3 = {
    "step": "D3.M3",
    "enumerator": "awk -F'\\t' '$6==\"gate\"' SURVIVORS.tsv",
    "universe": wave_total,
    "examined": examined,
    "not_reached": not_reached,
    "redispatched": m3_prev["redispatched"],
    "evidence": (f"box {BOX} gated {examined} of its {len(ROWS)} keys with `PYTHONPATH=tests/hastub python3 "
                 f"dev/audit/rounds/round11/D3/s1/fullgate.py run --src complete --key <key>` driven by gate_wave.sh run "
                 f"(GATE_SCOPE=full GOLDEN_MODE=drift GATE_JOBS=1, one gate at a time, 4 h cap); records "
                 f"{REL}/gates/<key>.json, per-key analysis {REL}/results/<key>.json; null control "
                 f"{REL}/gates/null.json (gate_rc={NULL.get('gate_rc')}, failed {NULL.get('failed_scripts')}). "
                 f"The wave list is the union of keys.tsv over dispatch/finder-r11-D3-g01..g47 ({REL}/wave_boxes/, "
                 f"{wave_total} keys, as box D3-g13 collected them); earlier boxes' D3.M3 rows (D3-top6, D3-rem) "
                 f"contribute none of these keys (their 8 overlaps were deduped out of the wave). redispatched carried "
                 f"verbatim from REPORT-D3-u1b.json."),
}
coverage = [carried("D3.M1"), carried("D3.M2"), m3, carried("D3.M4"), carried("D3.M5")]

tally, classes = {}, {}
for r in RES.values():
    tally[r["gate"]["verdict"]] = tally.get(r["gate"]["verdict"], 0) + 1
    classes[r["class"]] = classes.get(r["class"], 0) + 1

gated = [{"key": r["key"], "site": RES[r["key"]]["site"] if r["key"] in RES else f"{r['file'].split('/')[-1]}:{r['line']} {r['kind']}",
          "verdict": RES[r["key"]]["gate"]["verdict"] if r["key"] in RES else "NOT-GATED",
          "killed_by": (RES[r["key"]]["gate"].get("killed_by") or []) if r["key"] in RES else [],
          "class": RES[r["key"]]["class"] if r["key"] in RES else "unfinished"} for r in ROWS]
gate_survivors = [RES[k] for k in RES if RES[k]["class"] == "candidate"]
equivalents = [RES[k] for k in RES if RES[k]["class"] == "equivalent-candidate"]

non_findings = [{
    "claim": "null control: the box's full gate on a comment-only marker (fullgate.py null)",
    "command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/fullgate.py null",
    "value": (f"gate_rc={NULL.get('gate_rc')} failed_scripts={NULL.get('failed_scripts')} fail_lines={NULL.get('fail_lines')} "
              f"wall_s={NULL.get('wall_s')} (provisional) load1 {NULL.get('load1_start')}..{NULL.get('load1_end')}")}]
for k, r in RES.items():
    g = r["gate"]
    if r["class"] == "killed":
        non_findings.append({
            "claim": f"{r['site']} ({r['function']}) mutant {k} [{r['patch']}] is pinned by the suite: KILLED by the full gate",
            "command": r["gate_command"],
            "value": (f"killed_by={g.get('killed_by')} gate_rc={g.get('gate_rc')} failed_scripts={g.get('failed_scripts')} "
                      f"wall_s={g.get('wall_s')} (provisional) load1 {g.get('load1_start')}..{g.get('load1_end')}; "
                      f"failing checks: {r.get('fail_lines')}; {r.get('kill_note', '')}")})
    elif r["class"] == "equivalent-candidate":
        non_findings.append({
            "claim": (f"{r['site']} ({r['function']}) mutant {k} [{r['patch']}] full gate {g.get('verdict')}; "
                      f"equivalent-candidate through production: {r['reach']}; {r['should_fail']}"),
            "command": r["probe"]["command"],
            "value": f"baseline: {probe_str(r, 'baseline')} | mutant: {probe_str(r, 'mutant')}"[:1500]})

leads = []
for k, r in RES.items():
    if r["class"] == "killed" and r.get("kill_note"):
        leads.append({"owner": "D3", "file": "custom_components/heatpump_optimizer/sysid.py",
                      "symbol": r["function"],
                      "what": (f"{k} ({r['site']}, {r['patch']}) is KILLED only by the tests/structure.py max_cc ratchet, "
                               f"not by a behavioural check: {r['kill_note']}")})
if ART:
    leads.append({"owner": "orchestrator (gate_wave.sh)", "file": "gate_wave.sh restore",
                  "symbol": "restore",
                  "what": ("a re-fire's `gate_wave.sh restore` copies the checkpointed probes/*.py back into the gated tree, "
                           "where tests/harness_headers.py's inlined-walk check fails on them and fullgate.py reads the next "
                           "gate KILLED; on this box it hit 0b6e291153f1d738 (record set aside under gates-artefact/, key "
                           "re-gated with the probes held outside the tree)")})

unfinished = [{"step": "D3.M3", "what": f"TIMEOUT past the 4 h cap on box {BOX}: {k} {RES[k]['site']}; neither finding nor non-finding"}
              for k in timeouts]
unfinished += [{"step": "D3.M3", "what": f"not gated on box {BOX} (STOP/SKIP): {k}"} for k in missing]
harnesses = ["dev/audit/rounds/round11/D3/s1/fullgate.py", f"{REL}/build_records.py", f"{REL}/build_report.py"] + \
    sorted({r["probe"]["path"] for r in RES.values() if "probe" in r})

rep = {
    "dimension": "D3", "baseline_sha": BASE, "box": BOX,
    "report_path": f"{REL}/REPORT.md",
    "exposure": ("No docs/ or GitHub read. Two seats on this box: the first (stalled) took the null, gated 7 keys and wrote "
                 "the probes and 6 records; the re-fire resumed from its checkpoint and read COMMON.md, D3.md, "
                 "finding.schema.json's location, REPORT-D3-u1b.json's coverage rows, the production lines under test "
                 "(sysid.py, coordinator.py:4045 and :6379), and box D3-g13's returned build_report.py and wave_boxes/ "
                 "key lists (handoff/audit-r11-find-D3-g13; key lists and the report builder only, not its results). "
                 "No register, round11/J/ or verifier report read."),
    "coverage": coverage, "unfinished": unfinished, "findings": [], "non_findings": non_findings,
    "harnesses": harnesses, "leads": leads,
    "gated": gated, "gate_survivors": gate_survivors, "equivalent_candidates": equivalents,
    "tally": {"verdicts": tally, "classes": classes},
    "gate_procedure": ("gate_wave.sh (shipped on dispatch/finder-r11-D3-g33): null once, then for each key of keys.tsv "
                       "in order: reset the tree to the baseline, `timeout -s INT -k 300 14400 python3 "
                       "dev/audit/rounds/round11/D3/s1/fullgate.py run --src complete --key <key>` (apply the one-line "
                       "mutant, commit, take the gate_lock lease, GATE_SCOPE=full GOLDEN_MODE=drift GATE_JOBS=1 "
                       "./tests/run.sh, record, reset), checkpoint after every gate"),
}

# ---- REPORT.md
L = [f"# D3-s1 round 11, box {BOX}: full gate for {len(ROWS)} D3.M3 full-net survivors (wave), baseline {BASE[:8]}", "",
     "## Machine and controls", "", "First container (null and gates 1-7):", "", "```", MACHINE_TXT, "```", ""]
if REFIRE_TXT:
    L += ["Re-fired container (gates 8-16 and the 0b6e291153f1d738 re-gate; the null reused from the checkpoint):", "",
          "```", REFIRE_TXT, "```", ""]
L += [f"Null control (`fullgate.py null`, comment-only marker): gate_rc={NULL.get('gate_rc')}, failed scripts "
      f"{NULL.get('failed_scripts')}, fail lines {NULL.get('fail_lines')}, summary {NULL.get('summary')}, wall "
      f"{NULL.get('wall_s')} s, load1 {NULL.get('load1_start')}..{NULL.get('load1_end')} (provisional). The three red scripts "
      "are artefact checks of the stripped tree. A mutant counts KILLED only when a script fails beyond this null; red with "
      "no script beyond it is RED-AS-NULL (read as survived).", "",
      "Every wall, CPU and load figure is provisional (nproc 4; Intel Xeon @ 2.10GHz first container, @ 2.30GHz re-fire; "
      "the judge re-takes it); counts are final. Probes apply the mutant in memory to `git show <baseline>:sysid.py`, never "
      "to the gate's tree.", ""]
if ART:
    L += ["### Box artefact, set aside", "", ART, ""]
L += ["## Tally", "",
      f"Gated {examined} of {len(ROWS)} keys; verdicts {tally}; classes {classes}.", "",
      "| key | site | function | full gate | killed by | wall s | load1 | class |", "|---|---|---|---|---|---|---|---|"]
for g in gated:
    r = RES.get(g["key"], {})
    gg = r.get("gate", {})
    L.append(f"| {g['key']} | {g['site']} | {r.get('function', '')} | {g['verdict']} | {', '.join(g['killed_by']) or '-'} "
             f"| {gg.get('wall_s', '-')} | {gg.get('load1_start', '-')}..{gg.get('load1_end', '-')} | {g['class']} |")
L += ["", "## Survivors: the step-4 answer and the probe numbers", ""]
for k, r in RES.items():
    if r["class"] not in ("candidate", "equivalent-candidate"):
        continue
    p = r["probe"]
    L += [f"### {k} {r['site']} ({r['function']}): {r['gate']['verdict']}, {r['class']}", "",
          f"Patch `{r['patch']}`. Probe `{p['command']}`: metric {p['metric']} {p['baseline_value']} -> {p['mutant_value']}, "
          f"null {p['null_metric']} {p['null_baseline']} -> {p['null_mutant']}. Baseline: {probe_str(r, 'baseline')}. "
          f"Mutant: {probe_str(r, 'mutant')}.", "",
          f"Inputs tried: {p['inputs_tried']}.", "",
          f"Reach: {r['reach']}.", "",
          f"Should have failed (D3.M4): {r['should_fail']}", ""]
    if r["class"] == "candidate":
        L += [f"Candidate: **{r['title']}** ({r['severity_claimed']}, class_guess {r['class_guess']}). "
              f"Perturbation direction {r['perturbation']['expected_direction']}. Null: {r['null_control']['probe_arm']}.", ""]
L += ["## Killed (non-findings)", ""]
for k, r in RES.items():
    if r["class"] == "killed":
        L.append(f"- {k} {r['site']} `{r['patch']}`: KILLED by {r['gate'].get('killed_by')} (`{r['gate_command']}`); "
                 f"{r.get('fail_lines')}. {r.get('kill_note', '')}")
L += ["", "## Leads", ""] + ([f"- {x['owner']}, {x['file']} {x['symbol']}: {x['what']}" for x in leads] or ["- none"])
L += ["", "## Unfinished", ""] + ([f"- {u['what']}" for u in unfinished] or ["- none"])
L += ["", "## Harnesses", ""] + [f"- `{h}`" for h in harnesses]
L += ["", "Procedure: " + rep["gate_procedure"], "", "## Exposure", "", rep["exposure"], ""]
md = "\n".join(L) + "\n"
(W / "REPORT.md").write_text(md)
rep["report_md"] = md
(W / "REPORT.json").write_text(json.dumps(rep, indent=1) + "\n")
print(f"RESULT gated={len(RES)} examined={examined} timeouts={len(timeouts)} missing={len(missing)} "
      f"candidates={len(gate_survivors)} equivalents={len(equivalents)}")
