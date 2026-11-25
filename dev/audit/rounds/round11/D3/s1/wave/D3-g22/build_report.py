#!/usr/bin/env python3
# Box D3-g22: builds REPORT.json and REPORT.md (seat D3-s1, this box only) from gates/*.json, results/*.json,
# MACHINE.txt and REPORT-D3-u1b.json's carried coverage rows. Command, from the tree root:
#   PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g22/build_report.py
import json
from pathlib import Path

W = Path(__file__).resolve().parent
S1 = W.parent.parent
BOX = "D3-g22"
BASE = "92d38ecb640bd462f2e19c0814d0f0b7df1ee692"
WD = "dev/audit/rounds/round11/D3/s1/wave/D3-g22"
FG = "dev/audit/rounds/round11/D3/s1/fullgate.py"
ENUM = "awk -F'\\t' '$6==\"gate\"' SURVIVORS.tsv"

rows = (W / "keys.tsv").read_text().splitlines()
head = rows[0].split("\t")
keys = [dict(zip(head, r.split("\t"))) for r in rows[1:] if r.strip()]
res = {k["key"]: json.loads((W / "results" / f"{k['key']}.json").read_text())
       for k in keys if (W / "results" / f"{k['key']}.json").exists()}
null = json.loads((W / "gates" / "null.json").read_text())
machine = (W / "MACHINE.txt").read_text().strip()

u1b = json.loads((S1 / "REPORT-D3-u1b.json").read_text())
cov = []
for r in u1b["coverage"]:
    if r["step"] == "D3.M3":
        continue
    c = dict(r)
    c["carried"] = True
    c["evidence"] = "carried verbatim from REPORT-D3-u1b.json (box D3-u1b), not re-driven by box D3-g22: " + r["evidence"]
    cov.append(c)
m3_old = next(r for r in u1b["coverage"] if r["step"] == "D3.M3")
timeouts = [k for k, r in res.items() if r["class"] == "timeout"]
done = [k for k, r in res.items() if r["class"] != "timeout"]
missing = [k["key"] for k in keys if k["key"] not in res]
other = [f"assigned to box D3-g{n:02d}" for n in range(1, 48) if n != 22]
m3 = {
    "step": "D3.M3", "enumerator": ENUM, "universe": 742, "examined": len(done),
    "not_reached": other + [f"TIMEOUT on box {BOX} (4 h cap): {k}" for k in timeouts]
                   + [f"not gated on box {BOX} (run ended): {k}" for k in missing],
    "redispatched": m3_old.get("redispatched", []),
    "evidence": (f"the wave list (742 keys after dedupe; 8 already gated by D3-top6/D3-rem under other keys add none "
                 f"here) is the orchestrator's SURVIVORS.tsv, not in this stripped tree; this box's 16 are {WD}/keys.tsv. "
                 f"Each key: PYTHONPATH=tests/hastub python3 {FG} run --src complete --key <key> "
                 f"(GATE_SCOPE=full GOLDEN_MODE=drift GOLDEN_REF={BASE} GATE_JOBS=1 ./tests/run.sh), driven one at a "
                 f"time by gate_wave.sh run; records {WD}/gates/<key>.json and .log; null control {WD}/gates/null.json. "
                 f"examined = {len(done)} gated here + 0 from earlier boxes' D3.M3 rows (none of the 742 was gated "
                 f"before this wave)."),
}
cov.insert(2, m3)

gated, surv, equiv, nonf = [], [], [], []
tally = {}
for k in keys:
    r = res.get(k["key"])
    if not r:
        continue
    v = r["gate"].get("verdict")
    tally[v] = tally.get(v, 0) + 1
    gated.append({"key": r["key"], "site": r["site"], "verdict": v, "killed_by": r["gate"].get("killed_by", []),
                  "class": r["class"]})
    if r["class"] == "candidate":
        surv.append(r)
    elif r["class"] == "equivalent-candidate":
        equiv.append(r)
        nonf.append({"claim": f"{r['key']} {r['site']} ({r['patch']}): full gate {v}; equivalent-candidate: "
                              f"{r['probe']['answer']}",
                     "command": r["probe"]["command"],
                     "value": f"baseline {r['probe']['baseline_value']}; mutant {r['probe']['mutant_value']}; "
                              f"inputs: {'; '.join(r['probe']['inputs_tried'])}"})
    elif r["class"] == "killed":
        nonf.append({"claim": f"{r['key']} {r['site']} ({r['patch']}): the full gate fails on it",
                     "command": r["gate_command"],
                     "value": f"KILLED by {r['gate'].get('killed_by')}, gate_rc {r['gate'].get('gate_rc')}"})

harn = [FG] + sorted(f"{WD}/probes/{p.name}" for p in (W / "probes").glob("*.py")) + [
    f"{WD}/build_results.py", f"{WD}/build_report.py"]
unfinished = [{"step": "D3.M3", "what": f"{k}: gate TIMEOUT at the 4 h cap on box {BOX}; neither killed nor survived"}
              for k in timeouts] + [{"step": "D3.M3", "what": f"{k}: not gated on box {BOX}"} for k in missing]

rep = {
    "dimension": "D3", "baseline_sha": BASE, "box": BOX, "report_path": f"{WD}/REPORT.md",
    "exposure": "", "coverage": cov, "unfinished": unfinished, "findings": [], "non_findings": nonf,
    "harnesses": harn, "leads": [], "gated": gated, "gate_survivors": surv, "equivalent_candidates": equiv,
    "null_control": {k: null.get(k) for k in ("gate_rc", "failed_scripts", "fail_lines", "summary", "wall_s",
                                              "load1_start", "load1_end")},
    "machine": machine,
}

L = [f"# D3-s1 round 11, box {BOX}: the full gate for 16 D3.M3 full-net survivors", "",
     f"Baseline {BASE}. Tree: a `prepare_baseline.sh --strip` worktree plus the D3-s1 evidence from e3cb5c0. "
     "Each gate: `fullgate.py run --src complete --key <key>` (one-line mutant committed, gate_lock lease, "
     f"`GATE_SCOPE=full GOLDEN_MODE=drift GOLDEN_REF={BASE} GATE_JOBS=1 ./tests/run.sh`, reset), driven one at a "
     "time by the dispatch's `gate_wave.sh run` (4 h cap, TIMEOUT never read as KILLED). Probes ran from a "
     "separate clean baseline worktree, never in the gate's tree, each mutant applied in memory.", "",
     "## Machine and controls", "", "```", machine, "```", "",
     f"Null control (`fullgate.py null`, comment-only marker): gate_rc {null.get('gate_rc')}, red scripts "
     f"{null.get('failed_scripts')}, FAIL counts {null.get('fail_lines')}, wall {null.get('wall_s')} s "
     f"(load1 {null.get('load1_start')} -> {null.get('load1_end')}). Walls and loads are provisional.", "",
     "Reach census: `PYTHONPATH=tests/hastub python3 " + WD + "/probes/reach_scan.py` (7 real solves of "
     "features.py's v5.3.0 January scenario: plain, space-blocked, DHW-blocked, 3.6 kW cap, 0.05 kW cap, PV surplus, "
     "forced-off pins) records the shapes each instrumented method receives.", "",
     "## Tally", "",
     f"gated {len(gated)} of {len(keys)}; " + ", ".join(f"{v} {n}" for v, n in sorted(tally.items()))
     + f"; candidates {len(surv)}; equivalent-candidates {len(equiv)}; TIMEOUT {len(timeouts)}.", ""]
kb = {}
for r in res.values():
    if r["class"] == "killed":
        for s in r["gate"].get("killed_by") or []:
            kb[s] = kb.get(s, 0) + 1
if kb:
    L += ["KILLED by: " + ", ".join(f"{s} ({n})" for s, n in sorted(kb.items())), ""]
L += ["| key | site | verdict | gate_rc | wall s | class |", "|---|---|---|---|---|---|"]
for k in keys:
    r = res.get(k["key"])
    if r:
        L.append(f"| {r['key']} | {r['site']} | {r['gate'].get('verdict')} | {r['gate'].get('gate_rc')} | "
                 f"{r['gate'].get('wall_s')} | {r['class']} |")
L += ["", "## Survivors (step-4 answers with probe numbers)", ""]
for k in keys:
    r = res.get(k["key"])
    if not r or r["class"] in ("killed", "timeout"):
        continue
    p = r["probe"]
    L += [f"### {r['key']} — {r['site']} ({r['class']})", "",
          f"Patch `{r['patch']}` in `{r['function']}`. Gate {r['gate'].get('verdict')} (gate_rc {r['gate'].get('gate_rc')}). "
          f"Probe `{p['command']}`: baseline {p['baseline_value']}; mutant {p['mutant_value']}. "
          f"Inputs tried: {'; '.join(p['inputs_tried'])}. Answer: {p['answer']}. "
          f"Check that should have failed: {r['should_fail']}.", ""]
    if r["class"] == "candidate":
        L += [f"Candidate: **{r['title']}** (severity claimed {r['severity_claimed']}, class_guess {r['class_guess']}). "
              f"Metric: {r['metric_definition']}. Null: {r['null_control']['value']}. Id left to consolidation.", ""]
for k in keys:
    r = res.get(k["key"])
    if r and r["class"] == "killed":
        L += [f"- {r['key']} {r['site']}: KILLED by {r['gate'].get('killed_by')} — non-finding; "
              f"`{r['gate_command']}`"]
    if r and r["class"] == "timeout":
        L += [f"- {r['key']} {r['site']}: TIMEOUT (cap {r['timeout']['cap_s']} s, last script "
              f"{r['timeout']['last_script_running']}) — unfinished"]
L += ["", "## Coverage", "",
      f"D3.M3: enumerator `{ENUM}` (742 keys), examined {m3['examined']} here; not reached: the other 46 boxes' keys "
      "(assigned to boxes D3-g01..D3-g47 but this one)"
      + (f" and TIMEOUT {timeouts}" if timeouts else "") + ". D3.M1, D3.M2, D3.M4, D3.M5 carried verbatim from "
      "REPORT-D3-u1b.json.", "",
      "## Harnesses", ""] + [f"- `{h}`" for h in harn] + [
      "- the dispatch's `gate_wave.sh` (out of tree): null, then `run` over keys.tsv, one gate at a time, ckpt after each", "",
      "## Unfinished", ""] + ([f"- {u['what']}" for u in unfinished] or ["- none"]) + [
      "", "## Exposure", "", "none (no docs/, GitHub or register read).", ""]

(W / "REPORT.json").write_text(json.dumps(rep, indent=1) + "\n")
(W / "REPORT.md").write_text("\n".join(L) + "\n")
print(f"RESULT gated={len(gated)} candidates={len(surv)} equivalent={len(equiv)} timeouts={len(timeouts)} "
      f"missing={len(missing)}")
