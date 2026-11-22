#!/usr/bin/env python3
# Box D3-g30's REPORT.json / REPORT.md writer, from keys.tsv, gates/*.json, results/*.json, MACHINE.txt and
# REPORT-D3-u1b.json's carried coverage rows. Command (export root): python3 dev/audit/rounds/round11/D3/s1/wave/D3-g30/build_report.py
import json
from pathlib import Path

W = Path(__file__).resolve().parent
S1 = W.parent.parent
REL = "dev/audit/rounds/round11/D3/s1/wave/D3-g30"
BASE = "92d38ecb640bd462f2e19c0814d0f0b7df1ee692"
BOX = "D3-g30"
hdr = (W / "keys.tsv").read_text().splitlines()[0].split("\t")
keys = [dict(zip(hdr, l.split("\t"))) for l in (W / "keys.tsv").read_text().splitlines()[1:] if l.strip()]
res = {k["key"]: json.loads((W / "results" / f"{k['key']}.json").read_text()) for k in keys if (W / "results" / f"{k['key']}.json").exists()}
null = json.loads((W / "gates" / "null.json").read_text())
machine = (W / "MACHINE.txt").read_text().strip()
u1b = json.loads((S1 / "REPORT-D3-u1b.json").read_text())

gated, survivors, equivalents, non_findings, unfinished = [], [], [], [], []
for k in keys:
    r = res.get(k["key"])
    if r is None:
        unfinished.append({"step": "D3.M3", "what": f"key {k['key']} ({k['file']}:{k['line']}) has no record: gate not finished"})
        continue
    g = r["gate"]
    gated.append({"key": r["key"], "site": r["site"], "verdict": g["verdict"], "killed_by": g.get("killed_by") or [], "class": r["class"]})
    if r["class"] == "candidate":
        survivors.append(r)
    elif r["class"] == "equivalent-candidate":
        equivalents.append(r)
        non_findings.append(r["non_finding"] | {"claim": f"{r['key']} {r['site']}: equivalent through production (full gate {g['verdict']}). " + r["non_finding"]["claim"]})
    elif r["class"] == "killed":
        non_findings.append(r["non_finding"])
    elif r["class"] == "timeout":
        unfinished.append({"step": "D3.M3", "what": f"key {r['key']} ({r['site']}) TIMEOUT past the {r['timeout']['cap_s']} s cap; last script line: {r['timeout']['last_script_line']}"})

timeouts = [r["key"] for r in res.values() if r["class"] == "timeout"]
examined = sum(1 for r in res.values() if r["class"] != "timeout")
others = [f"assigned to box D3-g{n:02d}" for n in range(1, 48) if f"D3-g{n:02d}" != BOX]
u1b_m3 = next(c for c in u1b["coverage"] if c["step"] == "D3.M3")
coverage = [dict(c, carried=f"verbatim from dev/audit/rounds/round11/D3/s1/REPORT-D3-u1b.json (box D3-u1b)")
            for c in u1b["coverage"] if c["step"] in ("D3.M1", "D3.M2", "D3.M4", "D3.M5")]
coverage.insert(2, {
    "step": "D3.M3",
    "enumerator": "awk -F'\\t' '$6==\"gate\"' SURVIVORS.tsv",
    "universe": 742,
    "examined": examined,
    "not_reached": others + [f"{k} (TIMEOUT on box {BOX})" for k in timeouts],
    "redispatched": u1b_m3.get("redispatched", []),
    "evidence": (f"Box {BOX} gated its 16 keys of keys.tsv, one at a time, by gate_wave.sh run (the dispatch tool: for each key "
                 "`python3 dev/audit/rounds/round11/D3/s1/fullgate.py run --src complete --key <key>`, i.e. the one-line mutant "
                 f"committed, GATE_SCOPE=full GOLDEN_MODE=drift GOLDEN_REF={BASE} GATE_JOBS=1 ./tests/run.sh, reset), records "
                 f"{REL}/gates/<key>.json and .log; null control {REL}/gates/null.json (gate_rc={null.get('gate_rc')}, "
                 f"failed_scripts={null.get('failed_scripts')}). The other 726 wave keys are assigned to boxes D3-g01..D3-g47 "
                 "(not_reached here by box). The 8 u1 survivors already gated under other keys by D3-top6/D3-rem are outside the "
                 "742. The redispatched items are carried verbatim from REPORT-D3-u1b.json's D3.M3 row."),
})

harnesses = ["dev/audit/rounds/round11/D3/s1/fullgate.py"] + [f"{REL}/probes/probe_{k['key']}.py" for k in keys]
tally = {}
for g in gated:
    tally[g["verdict"]] = tally.get(g["verdict"], 0) + 1
killers = {}
for g in gated:
    for s in g["killed_by"]:
        killers[s] = killers.get(s, 0) + 1

report = {
    "dimension": "D3", "baseline_sha": BASE, "box": BOX, "report_path": f"{REL}/REPORT.md",
    "exposure": ("No docs/ or GitHub read. Read COMMON.md, D3.md, dev/audit/README.md, finding.schema.json, bugclasses.json, the "
                 "slice and box reports under dev/audit/rounds/round11/D3/s1/ the brief names (REPORT-D3-u1{a,b,c,d}, REPORT-u1a, "
                 "REPORT-D3-top6, REPORT-D3-rem), the carried M4 answers for this box's keys, earlier probes as a pattern, "
                 "price_model.py, coordinator.py:4330-4377 and the tests/features.py price-model blocks; and this box's dispatch, "
                 "inbox and wip refs. venv-ci lives at /opt/hpo/venv-ci on this box; $HOME/venv-ci is a box-local symlink to it."),
    "coverage": coverage,
    "unfinished": unfinished,
    "findings": [],
    "non_findings": non_findings,
    "harnesses": harnesses,
    "leads": [],
    "gated": gated,
    "gate_survivors": survivors,
    "equivalent_candidates": equivalents,
    "tally": {"gated": len(gated), "verdicts": tally, "killed_by": killers,
              "candidates": len(survivors), "equivalent_candidates": len(equivalents), "timeouts": len(timeouts)},
    "machine": machine,
    "null_control": {k: null.get(k) for k in ("gate_rc", "failed_scripts", "summary", "wall_s", "load1_start", "load1_end", "command")}
                    | {"record": f"{REL}/gates/null.json"},
}
(W / "REPORT.json").write_text(json.dumps(report, indent=1) + "\n")

L = [f"# D3-s1, box {BOX}: full gate for 16 D3.M3 full-net survivors (price_model.py)", "",
     f"Baseline {BASE}. Seat D3-s1, round 11, wave box {BOX}. Walls, CPU and load are provisional; counts and probe values are final.", "",
     "## Machine and controls", "", "```", machine, "```", "",
     f"Null control (`python3 dev/audit/rounds/round11/D3/s1/fullgate.py null`, comment-only marker): gate_rc={null.get('gate_rc')}, "
     f"failed_scripts={null.get('failed_scripts')}, summary={null.get('summary')}, wall {null.get('wall_s')} s, "
     f"load1 {null.get('load1_start')}..{null.get('load1_end')}. Record `{REL}/gates/null.json`.", "",
     "Procedure: gate_wave.sh (dispatch tool) ran `fullgate.py run --src complete --key <key>` for each key of keys.tsv in order, one "
     "gate at a time (GATE_SCOPE=full GOLDEN_MODE=drift GATE_JOBS=1 ./tests/run.sh with the one-line mutant committed, 4 h cap). "
     "Each survivor's step-4 answer was executed by a probe that re-executes price_model.py from its own source with the one line "
     "replaced, in memory, run from a separate clean baseline worktree (never the gate's tree), driving the production caller "
     "PriceShapeLearner.fold / from_dict / summary / predict / expected_daily_min where one exists.", "",
     "## Tally", "",
     f"- gated: {len(gated)} of 16",
     f"- verdicts: {', '.join(f'{k} {v}' for k, v in sorted(tally.items())) or 'none'}",
     f"- KILLED by: {', '.join(f'{k} ({v})' for k, v in sorted(killers.items())) or 'none'}",
     f"- TIMEOUT: {', '.join(timeouts) or 'none'}",
     f"- candidates (full-gate survivors whose probe moves): {len(survivors)}",
     f"- equivalent-candidates: {len(equivalents)}", "",
     "## Gated", "", "| key | site | patch | verdict | killed_by | wall s | load1 | class |", "|---|---|---|---|---|---|---|---|"]
for k in keys:
    r = res.get(k["key"])
    if not r:
        L.append(f"| {k['key']} | {k['file'].split('/')[-1]}:{k['line']} | | not gated | | | | unfinished |")
        continue
    g = r["gate"]
    L.append(f"| {r['key']} | {r['site'].split('/')[-1]} | `{r['patch']}` | {g['verdict']} | {', '.join(g.get('killed_by') or []) or '-'} | "
             f"{g.get('wall_s')} | {g.get('load1_start')}..{g.get('load1_end')} | {r['class']} |")
L += ["", "## Survivors: step-4 answers and probe numbers", ""]
for r in survivors + equivalents:
    p = r["probe"]
    nums = "; ".join(f"{m}: baseline {p['baseline'][m]} -> mutant {p['mutant'][m]}" for m in p["baseline"])
    L += [f"### {r['key']} {r['site'].split('/')[-1]} ({r['class']}, gate {r['gate']['verdict']})", "",
          f"Patch `{r['patch']}`. {r['step4_answer']}", "",
          f"Probe `{p['command']}`: {nums}; null_delta {p['null_delta']}; inputs tried: {p['inputs_tried']}.", "",
          f"Should have failed: {r['should_fail']}", ""]
    if r["class"] == "candidate":
        f = r["finding"]
        L += [f"Finding fields: title \"{f['title']}\"; class_guess {f['class_guess']}; severity_claimed {f['severity_claimed']}; "
              f"perturbation {f['perturbation']}.", ""]
if any(r["class"] == "killed" for r in res.values()):
    L += ["## Killed (non-findings)", ""]
    for r in res.values():
        if r["class"] == "killed":
            L += [f"- {r['key']} {r['site'].split('/')[-1]} `{r['patch']}`: killed by {', '.join(r['gate']['killed_by'])}; "
                  f"gate_rc {r['gate']['gate_rc']}; `{r['gate']['command']}`; first fail lines: "
                  + " / ".join(x.strip() for x in r.get('killed_fail_lines', [])[:3])]
    L.append("")
L += ["## Unfinished", ""] + ([f"- {u['step']}: {u['what']}" for u in unfinished] or ["- none"]) + [""]
L += ["## Harnesses", ""] + [f"- `{h}`" for h in harnesses] + ["- gate_wave.sh (the dispatch's out-of-tree driver; procedure above)", ""]
L += ["## Findings", "", "None numbered here: every candidate is under `gate_survivors` in REPORT.json for the orchestrator's "
      "consolidation to assign ids across the wave.", ""]
(W / "REPORT.md").write_text("\n".join(L) + "\n")
print(f"REPORT gated={len(gated)} candidates={len(survivors)} equivalent={len(equivalents)} unfinished={len(unfinished)}")
