#!/usr/bin/env python3
"""REPORT.json + REPORT.md for box D3-g43 (seat D3-s1)."""
import csv, glob, json, os, shutil
S1 = "/root/audit-r11-D3-s1/dev/audit/rounds/round11/D3/s1"
W = f"{S1}/wave/D3-g43"
REL = "dev/audit/rounds/round11/D3/s1"
RW = f"{REL}/wave/D3-g43"
BASE = "92d38ecb640bd462f2e19c0814d0f0b7df1ee692"
for f in ("gate_wave.sh", "write_results.py", "build_report.py", "runprobes.sh"):
    src = f"/root/{f}"
    if os.path.exists(src):
        shutil.copy(src, f"{W}/{f}")

keys = list(csv.DictReader(open("/root/keys.tsv"), delimiter="\t"))
res = {k["key"]: json.load(open(f"{W}/results/{k['key']}.json")) for k in keys}
gates = {k: json.load(open(f"{W}/gates/{k}.json")) for k in res}
null = json.load(open(f"{W}/gates/null.json"))
u1b = json.load(open(f"{S1}/REPORT-D3-u1b.json"))

gated = [{"key": k, "site": r["site"], "verdict": gates[k]["verdict"], "killed_by": gates[k].get("killed_by", []), "class": r["class"]}
         for k, r in res.items()]
cands = [r for r in res.values() if r["class"] == "candidate"]
eqs = [r for r in res.values() if r["class"] == "equivalent-candidate"]
kills = [r for r in res.values() if r["class"] == "killed"]
tos = [r for r in res.values() if r["class"] == "timeout"]

cov = []
for row in u1b["coverage"]:
    if row["step"] == "D3.M3":
        continue
    row = json.loads(json.dumps(row))
    row["evidence"] = "carried, not re-driven here: " + row["evidence"]
    cov.append(row)
boxes = [f"D3-g{n:02d}" for n in range(1, 48) if n != 43]
cov.append({
    "step": "D3.M3",
    "enumerator": "awk -F'\\t' '$6==\"gate\"' dev/audit/rounds/round11/D3/s1/SURVIVORS.tsv",
    "universe": 742, "examined": len(res),
    "not_reached": [f"assigned to box {b} (its keys.tsv; the full gate of each key is that box's)" for b in boxes] + [f"TIMEOUT: {r['key']}" for r in tos],
    "redispatched": [],
    "evidence": (f"gate_wave.sh run (fullgate.py run --src complete --key <key>, GATE_SCOPE=full GOLDEN_MODE=drift GATE_JOBS=1 ./tests/run.sh) over {RW}/keys.tsv; "
                 f"records {RW}/gates/<key>.json and .log; null control {RW}/gates/null.json; results {RW}/results/<key>.json"),
})

non_findings = []
for r in kills:
    g = r["gate"]
    non_findings.append({"claim": f"{r['key']} ({r['site']}, {r['patch']}) is KILLED by the full gate",
                         "command": f"GATE_SCOPE=full GOLDEN_MODE=drift GATE_JOBS=1 ./tests/run.sh with the one-line mutant, via {REL}/fullgate.py run --src complete --key {r['key']} (box D3-g43, gate_wave.sh)",
                         "value": f"killed_by={g['killed_by']}, gate_rc={g['gate_rc']}, more_fails_than_null={g.get('more_fails_than_null')}, wall={g['wall_s']}s, load1 {g['load1_start']}->{g['load1_end']} (provisional)"})
for r in eqs:
    p = r["probe"]
    non_findings.append({"claim": f"{r['key']} ({r['site']}, {r['patch']}) is an equivalent-candidate: survives the full gate (RED-AS-NULL) and no input tried moves the production value",
                         "command": p["command"],
                         "value": f"baseline_vs_mutant_max_abs_diff={p['mutant_value']} (null 0); scenarios moved={p['metric'].split('= ')[-1]}; inputs tried: {p['inputs_tried']}"})

harn = [f"{REL}/fullgate.py", f"{RW}/probes/_blib.py", f"{RW}/gate_wave.sh", f"{RW}/write_results.py", f"{RW}/runprobes.sh"] + \
       [f"{RW}/probes/probe_{k}.py" for k in res]
unfinished = ["none: all 15 keys gated, no TIMEOUT."]
leads = [
 "tools/audit/seat/gate_lock / fullgate.py: a stale zero-byte worktree index.lock (created 13:48Z, 15 min into the gate of a3f2b00cc4aa527e, source unknown: no git process of this seat held it) made fullgate's finally `git reset` fail; gate_wave.sh then recorded keys a3f2b00cc4aa527e, a486806b8f4ff4d7 and 806f3255b74936a9 as TIMEOUT without running them (REFUSE: HEAD is not the baseline). The lock was removed, the three bogus records discarded (kept under $HOME/aborted on the box, not in this report) and the three keys re-gated in full; the reported verdicts are the re-runs.",
]

findings_note = "findings is empty by the wave's rule: the orchestrator assigns ids across boxes; candidates are under gate_survivors."
rep = {
 "dimension": "D3", "baseline_sha": BASE, "box": "D3-g43", "report_path": f"{RW}/REPORT.md",
 "exposure": "No docs/ or GitHub read; no gh. Worked only in the stripped worktree (finder wall) plus scratch copies of the baseline package under $TMPDIR for the probes; the baseline checkout used as the scratch source was never edited.",
 "coverage": cov, "unfinished": unfinished, "findings": [],
 "non_findings": non_findings, "harnesses": harn, "leads": leads,
 "gated": gated, "gate_survivors": cands, "equivalent_candidates": eqs,
}
json.dump(rep, open(f"{W}/REPORT.json", "w"), indent=1)

md = []
md.append("# D3-s1 box D3-g43: full gate for 15 D3.M3 full-net survivors\n")
md.append(f"Baseline {BASE}. Machine: 4 vCPU Intel Xeon @ 2.10GHz, 16 GB, alone on the box; every wall/load number is provisional (see MACHINE.txt).\n")
md.append(f"Null control: `fullgate.py null`, gate_rc={null['gate_rc']}, red on {null['failed_scripts']} only (artefact checks of the stripped tree), wall {null['wall_s']} s, load1 {null['load1_start']}->{null['load1_end']}. Kills are counted beyond it.\n")
tally = {}
for r in res.values(): tally[r["gate"]["verdict"]] = tally.get(r["gate"]["verdict"], 0) + 1
md.append(f"## Tally\n\ngated {len(res)}/15: " + ", ".join(f"{k}={v}" for k, v in sorted(tally.items())) + f"; candidates {len(cands)}, equivalent-candidates {len(eqs)}, timeouts {len(tos)}.\n")
md.append("KILLED by: " + "; ".join(f"{r['key']} -> {','.join(r['gate']['killed_by'])}" for r in kills) + "\n")
md.append("## Per key\n\n| key | site | patch | verdict | class |\n|---|---|---|---|---|")
for r in res.values():
    md.append(f"| {r['key']} | {r['site']} | `{r['patch']}` | {r['gate']['verdict']} {r['gate']['killed_by'] or ''} | {r['class']} |")
md.append("\n## Candidates (gate survivors that change behaviour)\n")
for r in cands:
    md.append(f"### {r['key']} - {r['title']}\n{r['claim']}\n\n- Production line: {r['site']}, `{r['patch']}`\n- Probe: `{r['probe']['command']}`: baseline_vs_mutant max abs diff = {r['probe']['mutant_value']} K, batch-vs-scalar parity mutant {r['probe']['parity_mutant_vs_scalar']} (baseline 0), null control 0.\n- Step 4, the check that should have failed: {r['should_fail']}\n- Severity claimed: {r['severity_claimed']}; class_guess {r['class_guess']}.\n")
md.append("## Equivalent-candidates\n")
for r in eqs:
    md.append(f"- **{r['key']}** ({r['site']}, `{r['patch']}`): {r['probe']['inputs_tried']} (max diff {r['probe']['mutant_value']})")
md.append("\n## Killed (non-findings)\n")
for r in kills:
    md.append(f"- **{r['key']}** ({r['site']}): killed_by {r['gate']['killed_by']}, wall {r['gate']['wall_s']} s")
md.append("\n## Incidents and caveats\n\n- " + leads[0])
md.append("- Probes ran concurrently with gate 1 (`f2ab25c56b407ef9`; load1 peaked about 4.4); its recorded load1 end was 0.95 and its verdict is the same RED-AS-NULL as the null's failing set, but treat its timing as provisional. No probe ran during any other gate.")
md.append("- The batch probes' scenario batteries and every input tried are in `probes/_blib.py` (default_battery, 144 scenarios); simulate_step keys use a 108-scenario step battery (n_sub 1, 2, 7, 25).")
md.append("- " + findings_note)
md.append("\nHarnesses: " + ", ".join(harn))
open(f"{W}/REPORT.md", "w").write("\n".join(md) + "\n")
print("report written", len(cands), "candidates", len(eqs), "eq", len(kills), "killed")
