#!/usr/bin/env python3
"""Build REPORT.json and REPORT.md for wave box D3-g12 from results/<key>.json, gates/ and REPORT-D3-u1b.json.
Run after every key of keys.tsv has a record: python3 build_report.py"""
import json, csv, collections
from pathlib import Path

BOX = "D3-g12"
BASE = "92d38ecb640bd462f2e19c0814d0f0b7df1ee692"
S = Path.home() / "audit-r11-D3-s1/dev/audit/rounds/round11/D3/s1"
W = S / "wave" / BOX
REL = f"dev/audit/rounds/round11/D3/s1/wave/{BOX}"

keys = [r for r in csv.DictReader(open(W / "keys.tsv"), delimiter="\t")]
recs = {r["key"]: json.load(open(W / "results" / f"{r['key']}.json")) for r in keys
        if (W / "results" / f"{r['key']}.json").exists()}
null = json.load(open(W / "gates/null.json"))
u1b = json.load(open(S / "REPORT-D3-u1b.json"))
cov_u1b = {c["step"]: c for c in u1b["coverage"]}

# wave list: every key of the 47 boxes' dispatch keys.tsv (wave_boxes.tsv: box, key, site)
boxes = collections.OrderedDict()
for line in open(W / "wave_boxes.tsv"):
    b, k, site = line.rstrip("\n").split("\t")
    boxes.setdefault(b, []).append(k)
universe = sum(len(v) for v in boxes.values())

gated, survivors, equiv, nonf, unfinished, timeouts = [], [], [], [], [], []
tally = collections.Counter()
killers = collections.Counter()
for r in keys:
    k = r["key"]
    rec = recs.get(k)
    if rec is None:
        unfinished.append({"step": "D3.M3", "what": f"key {k} ({r['file']}:{r['line']}) has no gate record"})
        continue
    g = rec["gate"]
    tally[g["verdict"]] += 1
    for s in g.get("killed_by") or []:
        killers[s] += 1
    gated.append({"key": k, "site": rec["site"], "verdict": g["verdict"],
                  "killed_by": g.get("killed_by") or [], "class": rec["class"]})
    cls = rec["class"]
    if cls == "candidate":
        survivors.append(rec)
    elif cls == "equivalent-candidate":
        equiv.append(rec)
        p = rec["probe"]
        nonf.append({"claim": f"key {k} ({rec['site']}, `{rec['patch']}`): full gate {g['verdict']} (gate_rc {g['gate_rc']}, no script beyond the null), and the probe finds no input that moves the delivered value: equivalent-candidate",
                     "command": f"python3 dev/audit/rounds/round11/D3/s1/fullgate.py run --src complete --key {k}; {p['command']}",
                     "value": f"gate {g['verdict']} failed_scripts={g.get('failed_scripts')} (null: {null['failed_scripts']}); probe {p.get('baseline_value')} vs {p.get('mutant_value')}; inputs tried: {p.get('inputs_tried')}"})
    elif cls == "killed":
        nonf.append({"claim": f"key {k} ({rec['site']}, `{rec['patch']}`): the full gate kills it",
                     "command": f"python3 dev/audit/rounds/round11/D3/s1/fullgate.py run --src complete --key {k}",
                     "value": f"KILLED by {g.get('killed_by')}, gate_rc {g['gate_rc']}"})
    elif cls == "timeout":
        timeouts.append(k)
        unfinished.append({"step": "D3.M3", "what": f"key {k} ({rec['site']}): full gate TIMEOUT past the 4 h cap; last script running: {g.get('last_script', 'see gates/' + k + '.log')}"})

examined = len(gated) - len(timeouts)
not_reached = [f"assigned to box {b}: " + " ".join(v) for b, v in boxes.items() if b != BOX]
not_reached += [f"TIMEOUT on box {BOX}: {k}" for k in timeouts]

def carried(step):
    row = dict(cov_u1b[step])
    row["evidence"] = "carried verbatim from box D3-u1b (dev/audit/rounds/round11/D3/s1/REPORT-D3-u1b.json): " + row["evidence"]
    return row

m3 = {"step": "D3.M3",
      "enumerator": "awk -F'\\t' '$6==\"gate\"' SURVIVORS.tsv",
      "universe": universe, "examined": examined, "not_reached": not_reached,
      "redispatched": cov_u1b["D3.M3"]["redispatched"],
      "evidence": (f"this box gated {len(gated)} of its 16 keys: python3 dev/audit/rounds/round11/D3/s1/fullgate.py run --src complete --key <key> "
                   f"(GATE_SCOPE=full GOLDEN_MODE=drift GOLDEN_REF={BASE} GATE_JOBS=1 ./tests/run.sh), one gate at a time through {REL}/gate_wave.sh run; "
                   f"records {REL}/gates/<key>.json, null control {REL}/gates/null.json. SURVIVORS.tsv is not in the stripped tree: the 742-key wave list "
                   f"is {REL}/wave_boxes.tsv, read from keys.tsv on the 47 refs dispatch/finder-r11-D3-g01..g47 (742 keys, no duplicate). "
                   "Earlier boxes' D3.M3 rows carried: box D3-top6 gated 30 of 35 and box D3-rem the remaining 5 (REPORT-D3-top6.json, REPORT-D3-rem.json); "
                   "the 8 wave keys already gated there under other keys were deduped out of the 742 before the split. "
                   f"redispatched carried verbatim from REPORT-D3-u1b.json's D3.M3 row.")}

machine = (W / "MACHINE.txt").read_text()
exposure = ("No docs/ or GitHub record read. This seat resumed box D3-g12 from a stalled predecessor's checkpoint (handoff-wip/finder-r11-D3-g12 @ 40ef33e7): "
            "the probes, meta and record builder under probes/_scripts/ and the first six records are the predecessor's, restored by gate_wave.sh restore and kept unchanged. "
            "This seat read the box's own dispatch/inbox/wip refs, keys.tsv on the 47 sibling dispatch refs (key lists only, to name every other key by box), "
            "COMMON.md, D3.md, dev/audit/README.md, finding.schema.json and REPORT-D3-u1b/top6/rem.json (coverage rows) through haiku extractors. "
            "Environment workaround, not pushed: $HOME/venv-ci is a symlink to /opt/hpo/venv-ci, where this container's venv-ci lives.")

def short(rec):
    p = rec["probe"]
    return {"key": rec["key"], "site": rec["site"], "patch": rec["patch"], "function": rec["function"], "cluster": rec["cluster"],
            "gate": {x: rec["gate"].get(x) for x in ("verdict", "killed_by", "gate_rc", "wall_s", "load1_start", "load1_end")},
            "class": rec["class"], "probe": {x: p.get(x) for x in ("path", "command", "baseline_value", "mutant_value", "inputs_tried")},
            "should_fail": rec["should_fail"], **({"finding": rec["finding"]} if "finding" in rec else {})}

harnesses = ["dev/audit/rounds/round11/D3/s1/fullgate.py", f"{REL}/gate_wave.sh"] + \
            sorted(f"{REL}/probes/probe_{r['key']}.py" for r in keys)

report = {
    "dimension": "D3", "baseline_sha": BASE, "box": BOX,
    "report_path": f"{REL}/REPORT.md", "exposure": exposure,
    "coverage": [carried("D3.M1"), carried("D3.M2"), m3, carried("D3.M4"), carried("D3.M5")],
    "unfinished": unfinished, "findings": [], "non_findings": nonf, "harnesses": harnesses, "leads": [],
    "gated": gated,
    "gate_survivors": [short(r) for r in survivors],
    "equivalent_candidates": [short(r) for r in equiv],
}
json.dump(report, open(W / "REPORT.json", "w"), indent=1)

# ---- REPORT.md
L = [f"# D3-s1 wave box {BOX}: full gate of 16 D3.M3 full-net survivors (round 11)", "",
     f"Baseline `{BASE}`. Findings: none numbered here (ids are assigned at consolidation); candidates are under `gate_survivors`.", "",
     "## Method", "",
     "Each key's one-line mutant was applied, committed and run through the full gate "
     f"(`GATE_SCOPE=full GOLDEN_MODE=drift GOLDEN_REF={BASE} GATE_JOBS=1 ./tests/run.sh`) by "
     "`dev/audit/rounds/round11/D3/s1/fullgate.py run --src complete --key <key>`, one gate at a time, driven down keys.tsv by "
     f"`{REL}/gate_wave.sh run` (4 h cap, resumable, tree reset to the baseline after each gate). "
     "Verdicts: KILLED (a script red beyond this box's null), SURVIVED (gate_rc 0), RED-AS-NULL (red only on the null's scripts: read as survived), TIMEOUT. "
     "Every survivor got the D3.md step-4 answer as an executed probe (`probes/probe_<key>.py`, baseline vs the mutant applied in memory). "
     "The box was resumed mid-run from a stalled predecessor's checkpoint; gates 1-6 and the null are the predecessor's, gates 7-16 this seat's, on the same machine class.", "",
     "## Machine and controls", "", "```", machine.strip(), "```", "",
     f"Null control (`fullgate.py null`, comment-only marker): gate_rc {null['gate_rc']}, failed scripts {null['failed_scripts']} "
     f"(fail lines {null.get('fail_lines')}), wall {null['wall_s']} s (provisional), load1 {null['load1_start']}..{null['load1_end']}. "
     "All three are artefact checks of the stripped tree and the in-tree wave dir (see NULL-NOTES.md); no card.mjs heap or stress/budget failure. Read as usable.", "",
     "Every wall/CPU/load number is provisional (provisional: true; nproc 4, Intel Xeon @ 2.10GHz); counts and verdicts are final.", "",
     "## Tally", "",
     f"- gated: {len(gated)} of 16",
     f"- KILLED: {tally['KILLED']}" + (f" ({dict(killers)})" if killers else ""),
     f"- SURVIVED: {tally['SURVIVED']}", f"- RED-AS-NULL: {tally['RED-AS-NULL']}", f"- TIMEOUT: {tally['TIMEOUT']}",
     f"- candidates (probe moves the value): {len(survivors)}", f"- equivalent-candidates: {len(equiv)}", "",
     "| key | site | verdict | gate_rc | wall_s | class |", "|---|---|---|---|---|---|"]
for g in gated:
    rec = recs[g["key"]]
    L.append(f"| {g['key']} | {g['site']} | {g['verdict']} | {rec['gate']['gate_rc']} | {rec['gate']['wall_s']} | {g['class']} |")
L += ["", "## Survivors: step-4 answers with probe numbers", ""]
for rec in survivors + equiv:
    p = rec["probe"]; f = rec.get("finding", {})
    L += [f"### {rec['key']}: {rec['site']} ({rec['function']}), {rec['class']}", "",
          f"Patch: `{rec['patch']}`. Gate: {rec['gate']['verdict']}, gate_rc {rec['gate']['gate_rc']}, failed scripts {rec['gate'].get('failed_scripts')} (= the null's).",
          "",
          (f"{f.get('claim', '')} " if f else "") +
          f"Probe `{p['command']}`: baseline {p.get('baseline_value')}, mutant {p.get('mutant_value')}; inputs tried: {p.get('inputs_tried')}. "
          f"Should have failed: {rec['should_fail']}." +
          (f" Severity claimed {f.get('severity_claimed')}, class_guess {f.get('class_guess')}." if f else ""), ""]
L += ["## Non-findings", ""] + [f"- {n['claim']}: `{n['command']}` -> {n['value']}" for n in nonf] + ["",
      "## Unfinished", ""] + ([f"- {u['step']}: {u['what']}" for u in unfinished] or ["- none"]) + ["",
      "## Harnesses", ""] + [f"- `{h}`" for h in harnesses] + ["",
      "## Coverage", "", f"D3.M3 (this wave): universe {universe}, examined {examined} here; every other key named by its box in REPORT.json. "
      "D3.M1, D3.M2, D3.M4, D3.M5 and their redispatched C-items are carried verbatim from REPORT-D3-u1b.json.", "",
      "## Exposure", "", exposure, ""]
(W / "REPORT.md").write_text("\n".join(L))
print(f"REPORT gated={len(gated)} candidates={len(survivors)} equivalent={len(equiv)} unfinished={len(unfinished)} tally={dict(tally)}")
