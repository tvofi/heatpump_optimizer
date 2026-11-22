#!/usr/bin/env python3
"""Box D3-g13: assemble REPORT.json and REPORT.md for seat D3-s1 (this box only) from results/<key>.json.

Command: python3 dev/audit/rounds/round11/D3/s1/wave/D3-g13/build_report.py
"""
import json
from pathlib import Path

W = Path(__file__).resolve().parent
S1 = W.parent.parent
REL = "dev/audit/rounds/round11/D3/s1/wave/D3-g13"
BASE = "92d38ecb640bd462f2e19c0814d0f0b7df1ee692"
rows = [l.split("\t") for l in (W / "keys.tsv").read_text().splitlines()]
ROWS = [dict(zip(rows[0], r)) for r in rows[1:] if r and r[0]]
RES = {r["key"]: json.loads((W / "results" / f"{r['key']}.json").read_text())
       for r in ROWS if (W / "results" / f"{r['key']}.json").exists()}
NULL = json.loads((W / "gates" / "null.json").read_text())
MACHINE_TXT = (W / "MACHINE.txt").read_text().strip()
u1b = json.loads((S1 / "REPORT-D3-u1b.json").read_text())
EXTRA = json.loads((W / "report_extra.json").read_text()) if (W / "report_extra.json").exists() else {}


def carried(step):
    r = dict(next(c for c in u1b["coverage"] if c["step"] == step))
    r["carried"] = "verbatim from REPORT-D3-u1b.json (box D3-u1b); not re-driven on box D3-g13"
    return r


# ---- D3.M3: the wave list, 742 keys over boxes D3-g01..D3-g47
others, wave_total = [], 0
for f in sorted((W / "wave_boxes").glob("D3-g*.tsv")):
    box = f.stem
    ks = [dict(zip(rows[0], l.split("\t"))) for l in f.read_text().splitlines()[1:] if l.strip()]
    wave_total += len(ks)
    if box == "D3-g13":
        continue
    files = {}
    for k in ks:
        files.setdefault(k["file"].split("/")[-1], []).append(int(k["line"]))
    span = "; ".join(f"{fn} {min(v)}-{max(v)}" for fn, v in sorted(files.items()))
    others.append(f"assigned to box {box}: {len(ks)} keys ({span})")
timeouts = [k for k, r in RES.items() if r["class"] == "timeout"]
missing = [r["key"] for r in ROWS if r["key"] not in RES]
examined = len(RES) - len(timeouts)
not_reached = others + [f"TIMEOUT on box D3-g13 (4 h cap): {k} {RES[k]['site']}" for k in timeouts] + \
    [f"not gated on box D3-g13 (stopped or skipped): {k}" for k in missing]
m3_prev = next(c for c in u1b["coverage"] if c["step"] == "D3.M3")
m3 = {
    "step": "D3.M3",
    "enumerator": "awk -F'\\t' '$6==\"gate\"' SURVIVORS.tsv",
    "universe": wave_total,
    "examined": examined,
    "not_reached": not_reached,
    "redispatched": m3_prev["redispatched"],
    "evidence": (f"box D3-g13 gated {examined} of its {len(ROWS)} keys with `PYTHONPATH=tests/hastub python3 "
                 f"dev/audit/rounds/round11/D3/s1/fullgate.py run --src complete --key <key>` driven by gate_wave.sh run "
                 f"(GATE_SCOPE=full GOLDEN_MODE=drift GATE_JOBS=1, one gate at a time, 4 h cap); records "
                 f"{REL}/gates/<key>.json, per-key analysis {REL}/results/<key>.json; null control "
                 f"{REL}/gates/null.json (gate_rc={NULL.get('gate_rc')}, failed {NULL.get('failed_scripts')}). "
                 f"The wave list is the union of keys.tsv over dispatch/finder-r11-D3-g01..g47 ({REL}/wave_boxes/, "
                 f"{wave_total} keys); earlier boxes' D3.M3 rows (D3-top6, D3-rem) contribute none of these keys "
                 f"(their 8 overlaps were deduped out of the wave). redispatched carried verbatim from REPORT-D3-u1b.json."),
}
coverage = [carried("D3.M1"), carried("D3.M2"), m3, carried("D3.M4"), carried("D3.M5")]

tally = {}
for r in RES.values():
    tally[r["gate"]["verdict"]] = tally.get(r["gate"]["verdict"], 0) + 1
classes = {}
for r in RES.values():
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
    "value": (f"gate_rc={NULL.get('gate_rc')} failed_scripts={NULL.get('failed_scripts')} summary={NULL.get('summary')} "
              f"wall_s={NULL.get('wall_s')} (provisional) load1 {NULL.get('load1_start')}..{NULL.get('load1_end')}")}]
for k, r in RES.items():
    g = r["gate"]
    if r["class"] == "killed":
        non_findings.append({
            "claim": f"{r['site']} ({r['function']}) mutant {k} [{r['patch']}] is pinned by the suite: KILLED by the full gate",
            "command": r["gate_command"],
            "value": (f"killed_by={g.get('killed_by')} gate_rc={g.get('gate_rc')} failed_scripts={g.get('failed_scripts')} "
                      f"wall_s={g.get('wall_s')} (provisional) load1 {g.get('load1_start')}..{g.get('load1_end')}; "
                      f"failing checks: {' | '.join(r.get('failing_checks', [])[:4])}")})
    elif r["class"] == "equivalent-candidate":
        non_findings.append({
            "claim": (f"{r['site']} ({r['function']}) mutant {k} [{r['patch']}] full gate {g.get('verdict')}; "
                      f"equivalent-candidate: {r['equivalence']}"),
            "command": r["probe"]["command"],
            "value": "; ".join(x[len('RESULT '):] for x in r["probe"]["results"] if "thread_factor" not in x
                               and "swapins" not in x)[:1500]})

unfinished = [{"step": "D3.M3", "what": f"TIMEOUT past the 4 h cap on box D3-g13: {k} {RES[k]['site']}, last script "
               f"running {RES[k]['timeout']['last_script_running']}; neither finding nor non-finding"} for k in timeouts]
unfinished += [{"step": "D3.M3", "what": f"not gated on box D3-g13 (STOP/SKIP): {k}"} for k in missing]
unfinished += EXTRA.get("unfinished", [])
harnesses = ["dev/audit/rounds/round11/D3/s1/fullgate.py",
             f"{REL}/build_records.py", f"{REL}/build_report.py"] + \
    sorted({r["probe"]["path"] for r in RES.values() if "probe" in r})

rep = {
    "dimension": "D3", "baseline_sha": BASE, "box": "D3-g13",
    "report_path": f"{REL}/REPORT.md",
    "exposure": ("No docs/ or GitHub read. Read COMMON.md, D3.md, dev/audit/README.md, finding.schema.json, "
                 "bugclasses.json ids, the carried slice reports (REPORT-D3-u1{a,b,c,d}, REPORT-u1a, REPORT-D3-top6, "
                 "REPORT-D3-rem) and their M4 answers for this box's keys, the production lines under test, and the "
                 "keys.tsv of the sibling dispatch refs dispatch/finder-r11-D3-g01..g47 (key lists only, for the "
                 "not_reached rows). No register, round11/J/ or verifier report read."),
    "coverage": coverage, "unfinished": unfinished, "findings": [], "non_findings": non_findings,
    "harnesses": harnesses, "leads": EXTRA.get("leads", []),
    "gated": gated, "gate_survivors": gate_survivors, "equivalent_candidates": equivalents,
    "tally": {"verdicts": tally, "classes": classes},
    "gate_procedure": ("gate_wave.sh (shipped on dispatch/finder-r11-D3-g13): null once, then for each key of keys.tsv "
                       "in order: reset the tree to the baseline, `timeout -s INT -k 300 14400 python3 "
                       "dev/audit/rounds/round11/D3/s1/fullgate.py run --src complete --key <key>` (apply the one-line "
                       "mutant, commit, take the gate_lock lease, GATE_SCOPE=full GOLDEN_MODE=drift GATE_JOBS=1 "
                       "./tests/run.sh, record, reset), checkpoint after every gate"),
}

# ---- REPORT.md
L = [f"# D3-s1 round 11, box D3-g13: full gate for 16 D3.M3 full-net survivors (wave), baseline {BASE[:8]}", "",
     "## Machine and controls", "", "```", MACHINE_TXT, "```", "",
     f"Null control (`fullgate.py null`, comment-only marker): gate_rc={NULL.get('gate_rc')}, failed scripts "
     f"{NULL.get('failed_scripts')}, fail lines {NULL.get('fail_lines')}, summary {NULL.get('summary')}, wall "
     f"{NULL.get('wall_s')} s, load1 {NULL.get('load1_start')}..{NULL.get('load1_end')} (provisional). A mutant counts "
     "KILLED only when a script fails beyond this null; red with no script beyond it is RED-AS-NULL (read as survived).",
     "", "Every wall, CPU and load figure is provisional (nproc 4, Intel Xeon @ 2.30GHz; the judge re-takes it); "
     "counts are final. Probes ran from a separate clean baseline worktree, never from the gate's tree.", "",
     "## Tally", "",
     f"Gated {len(RES) - len(timeouts)} of {len(ROWS)} keys; verdicts {tally}; classes {classes}.", "",
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
    res = "; ".join(x[len("RESULT "):] for x in r["probe"]["results"] if "swapins" not in x)
    L.append(f"### {k} {r['site']} ({r['function']}): {r['gate']['verdict']}, {r['class']}")
    L.append("")
    L.append(f"Patch `{r['patch']}`. Probe `{r['probe']['command']}`: {res}.")
    L.append("")
    L.append(f"Inputs tried: {'; '.join(r['probe']['inputs_tried'])}.")
    L.append("")
    L.append(f"Should have failed (D3.M4): {r['should_fail']}" + (f" {r['reach_note']}" if r.get("reach_note") else ""))
    L.append("")
    if r["class"] == "candidate":
        f = r["finding"]
        L.append(f"Candidate: **{f['title']}** ({f['severity_claimed']}, class_guess {f['class_guess']}). {f['claim']} "
                 f"Perturbation direction: {f['perturbation']['expected_direction']}. Null: {f['null_control']['note']}.")
    else:
        L.append(f"Equivalent-candidate: {r['equivalence']}.")
    L.append("")
L += ["## Killed (non-findings)", ""]
for k, r in RES.items():
    if r["class"] == "killed":
        L.append(f"- {k} {r['site']}: KILLED by {r['gate'].get('killed_by')} (`{r['gate_command']}`); "
                 f"{' | '.join(r.get('failing_checks', [])[:3])}")
L += ["", "## Unfinished", ""] + ([f"- {u['what']}" for u in unfinished] or ["- none"])
L += ["", "## Harnesses", ""] + [f"- `{h}`" for h in harnesses]
L += ["", "## Exposure", "", rep["exposure"], ""]
md = "\n".join(L) + "\n"
(W / "REPORT.md").write_text(md)
rep["report_md"] = md
(W / "REPORT.json").write_text(json.dumps(rep, indent=1) + "\n")
print(f"RESULT gated={len(RES)} examined={examined} timeouts={len(timeouts)} missing={len(missing)} "
      f"candidates={len(gate_survivors)} equivalents={len(equivalents)}")
