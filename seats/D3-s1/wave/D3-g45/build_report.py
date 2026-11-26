#!/usr/bin/env python3
import csv, glob, json, os, collections
S1 = "dev/audit/rounds/round11/D3/s1"
W = f"{S1}/wave/D3-g45"
BASE = "92d38ecb640bd462f2e19c0814d0f0b7df1ee692"
keys = [r for r in csv.DictReader(open("keys.tsv"), delimiter="\t")]
mine = {r["key"] for r in keys}
res = {k: json.load(open(f"results/{k}.json")) for k in (r["key"] for r in keys) if os.path.exists(f"results/{k}.json")}
carried = json.load(open(f"../../REPORT-D3-u1b.json"))
nullg = json.load(open("gates/null.json"))
machine = open("MACHINE.txt").read()
# the other boxes' keys, by box (rebuilt from each box's dispatch ref keys.tsv)
other = {}
for f in sorted(glob.glob(os.path.expanduser("~/boxkeys/g*.tsv"))):
    box = "D3-" + os.path.basename(f)[:-4]
    for r in csv.DictReader(open(f), delimiter="\t"):
        if r["key"] not in mine: other[r["key"]] = box
assert len(other) + len(mine) == 742, (len(other), len(mine))
cov = []
for c in carried["coverage"]:
    c = dict(c)
    if c["step"] == "D3.M3":
        continue
    c["evidence"] = "carried from REPORT-D3-u1b.json unchanged. " + str(c.get("evidence", ""))[:600]
    c["carried"] = True
    cov.append(c)
gate_cmd = "GATE_SCOPE=full GOLDEN_MODE=drift GOLDEN_REF=%s GATE_JOBS=1 ./tests/run.sh via PYTHONPATH=tests/hastub python3 %s/fullgate.py run --src complete --key <key> (driver gate_wave.sh run)" % (BASE, S1)
m3 = {
 "step": "D3.M3",
 "enumerator": "awk -F'\\t' '$6==\"gate\"' SURVIVORS.tsv",
 "universe": 742,
 "examined": len(res),
 "not_reached": [f"{k}: assigned to box {b}" for k, b in sorted(other.items())] + [f"{k}: TIMEOUT (box D3-g45)" for k, r in res.items() if r["class"] == "timeout"],
 "evidence": f"wave list of 742 full-net survivors (keys rebuilt from each box's dispatch-ref keys.tsv; SURVIVORS.tsv itself is not in the box tree); this box gated its 15 keys: {gate_cmd}; records {W}/gates/<key>.json, probes {W}/probes/. The earlier rounds' D3.M3 rows (top6, rem, u1a-d) are carried in their own reports and are not re-counted here.",
}
m3["redispatched"] = next(c for c in carried["coverage"] if c["step"] == "D3.M3")["redispatched"]
m3["examined"] = len([k for k, r in res.items() if r["class"] != "timeout"])
cov.insert(2, m3)
tally = collections.Counter(r["gate"]["verdict"] for r in res.values())
cls = collections.Counter(r["class"] for r in res.values())
cands = [r for r in res.values() if r["class"] == "candidate"]
eqs = [r for r in res.values() if r["class"] == "equivalent-candidate"]
killed = [r for r in res.values() if r["class"] == "killed"]
tmo = [r for r in res.values() if r["class"] == "timeout"]
gated = [{"key": r["key"], "site": r["site"], "verdict": r["gate"]["verdict"], "killed_by": r["gate"].get("killed_by"), "class": r["class"]} for r in res.values()]
nonf = []
for r in killed:
    nonf.append({"claim": f"{r['site']} ({r['function']}): the full gate KILLS the mutant {r['patch']}", "command": f"{r['probe'] and r['probe']['command'] or ''} GATE: fullgate.py run --src complete --key {r['key']}".strip(), "value": f"killed_by={r['gate']['killed_by']}; null red set {nullg['failed_scripts']}; wall {r['gate']['wall_s']} s load1 {r['gate']['load1_start']}..{r['gate']['load1_end']} (provisional)"})
for r in eqs:
    nonf.append({"claim": f"{r['site']} ({r['function']}): equivalent-candidate, {r['patch']}", "command": r["probe"]["command"], "value": f"{r['probe']['mutant']}; inputs tried: {', '.join(r['probe']['inputs_tried'])}"})
harn = [f"{S1}/fullgate.py", f"gate_wave.sh run/null/ckpt (out-of-tree driver: applies each one-line mutant, GATE_SCOPE=full GOLDEN_MODE=drift GATE_JOBS=1 ./tests/run.sh, 4 h cap, resets the tree)", f"{W}/probes/mutmod.py", f"{W}/probes/valvecommon.py"] + sorted({r["probe"]["path"] for r in res.values() if r["probe"]})
unfinished = [f"{r['key']}: TIMEOUT at the 4 h cap" for r in tmo]
leads = ["box_comms.sh left its mkdir lock stale three times (after the container restart at 22:18 and at a gate-start heartbeat 23:11); `comms: lock stuck`, cleared by rmdir of the lock dir. Instrument fault, not pushed.", "Probes read a pristine git-archive export of the baseline (~/probe-tree), never the gate's tree, because the tree carries a committed mutant while a gate runs."]
exposure = ("Box D3-g45, 4 vCPU Xeon @ 2.10GHz, alone on its machine; null control taken on this box (gate_rc=%s, red %s: stripped-tree artefact checks, no machine-caused red); every wall/CPU/load number is provisional. "
            "Gates of 14 of the keys ran before and 1 after a container restart that left the driver running. No gh, no register, no round-11/J, no verifier report read." % (nullg["gate_rc"], nullg["failed_scripts"]))
rep = {"dimension": "D3", "baseline_sha": BASE, "box": "D3-g45", "report_path": f"{W}/REPORT.md", "exposure": exposure, "coverage": cov,
       "unfinished": unfinished, "findings": [], "non_findings": nonf, "harnesses": harn, "leads": leads,
       "gated": gated, "gate_survivors": cands, "equivalent_candidates": eqs}
md = [f"# D3-s1 box D3-g45: full gate of 15 D3.M3 full-net survivors", "", "## Machine and controls", "```", machine.strip(), "```",
      f"Null control (fullgate.py null): gate_rc={nullg['gate_rc']}, red scripts {nullg['failed_scripts']} with fail lines {nullg['fail_lines']}, wall {nullg['wall_s']} s, load1 {nullg['load1_start']}..{nullg['load1_end']} (provisional). The mutants' red sets are compared against it.", "",
      "## Tally", f"gated {len(res)}/15; verdicts {dict(tally)}; candidates {len(cands)}; equivalent-candidates {len(eqs)}; KILLED {len(killed)} (by " + ", ".join(sorted({s for r in killed for s in r['gate']['killed_by']})) + f"); TIMEOUT {len(tmo)}.", "",
      "## Gated keys", "| key | site | verdict | killed_by | class |", "|---|---|---|---|---|"] + [f"| {g['key']} | {g['site']} | {g['verdict']} | {g['killed_by']} | {g['class']} |" for g in gated]
md += ["", "## Survivors that change behaviour (gate_survivors)", ""]
for r in cands:
    f = r["finding"]; p = r["probe"]
    md += [f"### {r['key']}: {f['title']}", f"{f['claim']}", f"Mechanism: {f['mechanism']}", f"Step 4: should fail: {r['should_fail']}.", f"Probe `{p['command']}`: baseline {p['baseline']}; mutant {p['mutant']}; inputs {', '.join(p['inputs_tried'])}.", f"Gate: {r['gate']['verdict']}, gate_rc {r['gate']['gate_rc']}, red set identical to the null, wall {r['gate']['wall_s']} s (provisional).", ""]
md += ["## Equivalent-candidates", ""]
for r in eqs:
    p = r["probe"]; md += [f"- {r['key']} {r['site']} `{r['patch']}`: {p['mutant']}; probe `{p['command']}`; inputs {', '.join(p['inputs_tried'])}."]
md += ["", "## KILLED (non-findings)", ""] + [f"- {r['key']} {r['site']} ({r['function']}): killed_by {r['gate']['killed_by']}; fail lines {r['gate'].get('failed_scripts')}." for r in killed]
md += ["", "## Unfinished", ""] + (unfinished or ["none"]) + ["", "## Leads / instrument notes", ""] + [f"- {x}" for x in leads]
open("REPORT.md", "w").write("\n".join(md) + "\n")
json.dump(rep, open("REPORT.json", "w"), indent=1)
print("wrote REPORT", len(res), dict(cls))
