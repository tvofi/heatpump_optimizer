#!/usr/bin/env python3
# Box D3-g39: REPORT.json and REPORT.md for seat D3-s1 (this box only), from results/<key>.json,
# gates/null.json, MACHINE.txt and REPORT-D3-u1b.json's carried coverage rows.
# Command: python3 dev/audit/rounds/round11/D3/s1/wave/D3-g39/build_report.py
import json
from pathlib import Path
W = Path(__file__).resolve().parent
S1 = W.parents[1]
R = "dev/audit/rounds/round11/D3/s1/wave/D3-g39"
BOX = "D3-g39"
keys = [l.split("\t") for l in (W / "keys.tsv").read_text().splitlines()[1:] if l.strip()]
recs = {k[0]: json.loads((W / "results" / f"{k[0]}.json").read_text()) for k in keys if (W / "results" / f"{k[0]}.json").exists()}
null = json.loads((W / "gates" / "null.json").read_text())
machine = (W / "MACHINE.txt").read_text()
u1b = json.loads((S1 / "REPORT-D3-u1b.json").read_text())
cov = []
for row in u1b["coverage"]:
    if row["step"] in ("D3.M1", "D3.M2", "D3.M4", "D3.M5"):
        r = dict(row); r["carried"] = True
        r["evidence"] = "carried verbatim from dev/audit/rounds/round11/D3/s1/REPORT-D3-u1b.json; " + row.get("evidence", "")
        cov.append(r)
m3_u1b = next(r for r in u1b["coverage"] if r["step"] == "D3.M3")
gated = [k for k, r in recs.items() if r["class"] != "timeout"]
timeouts = [k for k, r in recs.items() if r["class"] == "timeout"]
unrec = [k[0] for k in keys if k[0] not in recs]
others = [f"assigned to box D3-g{n:02d}" for n in range(1, 48) if f"D3-g{n:02d}" != BOX]
cov.append({
    "step": "D3.M3",
    "enumerator": "awk -F'\\t' '$6==\"gate\"' SURVIVORS.tsv",
    "universe": 742,
    "examined": len(gated),
    "not_reached": others + [f"{k} (TIMEOUT on box {BOX}, past the 4 h cap)" for k in timeouts] + [f"{k} (not gated on box {BOX})" for k in unrec],
    "redispatched": [dict(x, carried=True) for x in m3_u1b.get("redispatched", [])],
    "evidence": f"box {BOX}: GATE_SCOPE=full GOLDEN_MODE=drift GATE_JOBS=1 ./tests/run.sh via `python3 dev/audit/rounds/round11/D3/s1/fullgate.py run --src complete --key <key>` "
                f"(driver gate_wave.sh run) for each of the {len(keys)} keys of {R}/keys.tsv; records {R}/gates/<key>.json and {R}/results/<key>.json; null {R}/gates/null.json. "
                "The earlier boxes' D3.M3 rows (REPORT-D3-top6.json, REPORT-D3-rem.json, REPORT-D3-u1a..d.json) stand on their own universes and are not re-counted here.",
})
tally = {}
for r in recs.values():
    tally[r["gate"]["verdict"]] = tally.get(r["gate"]["verdict"], 0) + 1
cands = [r for r in recs.values() if r["class"] == "candidate"]
equiv = [r for r in recs.values() if r["class"] == "equivalent-candidate"]
killed = [r for r in recs.values() if r["class"] == "killed"]
nonf = [r["non_finding"] for r in killed + equiv]
harn = [{"path": "dev/audit/rounds/round11/D3/s1/fullgate.py", "what": "the full gate per key (apply mutant, GATE_SCOPE=full GOLDEN_MODE=drift GATE_JOBS=1 ./tests/run.sh, verdict against the box null)"},
        {"path": f"{R}/gate_wave.sh (procedure; out-of-tree driver shipped on dispatch/finder-r11-D3-g39)", "what": "null once, then every key of keys.tsv one gate at a time, 4 h cap, checkpoint after each"},
        {"path": f"{R}/probes/_mutload.py", "what": "loads a sibling copy of the production module with the mutant's one line replaced, in memory"},
        {"path": f"{R}/build_results.py", "what": "per-key record from gate record, probe output and traced reach"}]
for k in keys:
    harn.append({"path": f"{R}/probes/probe_{k[0]}.py", "what": f"step-4 probe for {k[0]} ({Path(k[2]).name}:{k[3]})"})
unfinished = [{"step": "D3.M3", "what": f"{k}: gate TIMEOUT past the 4 h cap; last script in log {recs[k]['timeout']['last_script_in_log']}"} for k in timeouts]
unfinished += [{"step": "D3.M3", "what": f"{k}: not gated on this box"} for k in unrec]
rows = [{"key": k[0], "site": recs[k[0]]["site"] if k[0] in recs else f"{Path(k[2]).name}:{k[3]} {k[8]}",
         "verdict": recs.get(k[0], {}).get("gate", {}).get("verdict", "NOT-GATED"),
         "killed_by": recs.get(k[0], {}).get("gate", {}).get("killed_by"),
         "class": recs.get(k[0], {}).get("class", "unfinished")} for k in keys]
nproc = next(l for l in machine.splitlines() if l.startswith("nproc"))
cpu = next(l for l in machine.splitlines() if "model name" in l).split(":", 1)[1].strip()
rep = {
    "dimension": "D3", "baseline_sha": "92d38ecb640bd462f2e19c0814d0f0b7df1ee692", "box": BOX,
    "report_path": f"{R}/REPORT.md",
    "exposure": "Read the slice and earlier-box reports the brief names (REPORT-D3-u1a..d, REPORT-u1a, REPORT-D3-top6, REPORT-D3-rem) and the M4 answer files for this box's keys; no register, J/ or verifier report.",
    "coverage": cov, "unfinished": unfinished, "findings": [], "non_findings": nonf, "harnesses": harn,
    "leads": [],
    "gated": rows,
    "gate_survivors": cands,
    "equivalent_candidates": equiv,
    "null_control": {"record": f"{R}/gates/null.json", "gate_rc": null["gate_rc"], "failed_scripts": null["failed_scripts"],
                      "fail_lines": null["fail_lines"], "wall_s": null["wall_s"], "load1_start": null["load1_start"], "load1_end": null["load1_end"],
                      "note": (W / "NULL-NOTE.txt").read_text().strip(), "provisional": True},
    "machine": {"nproc": int(nproc.split()[1]), "cpu": cpu, "provisional": True, "record": f"{R}/MACHINE.txt"},
}
(W / "REPORT.json").write_text(json.dumps(rep, indent=1) + "\n")
L = [f"# D3-s1 box {BOX}: full gate for {len(keys)} D3.M3 full-net survivors", "",
     "Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Dimension D3, step D3.M3 (full gate) with each survivor's D3.M4 answer executed by a probe.", "",
     "## Machine and controls", "", f"{nproc}, {cpu}; MACHINE.txt in this directory. Every wall, CPU and load number is provisional (the judge re-takes it).", "",
     f"Null control (`fullgate.py null`, comment-only marker): gate_rc {null['gate_rc']}, red scripts {', '.join(null['failed_scripts'])} "
     f"(fail lines {null['fail_lines']}), wall {null['wall_s']} s, load1 {null['load1_start']} -> {null['load1_end']}. "
     "All three are in the earlier boxes' null and are artefact checks of the stripped tree; none is machine-caused, so it was not re-taken. "
     "A key red on exactly these scripts with no more fail lines reads RED-AS-NULL (survived).", "",
     "Procedure: gate_wave.sh run (out-of-tree driver) ran `fullgate.py run --src complete --key <key>` per key, one gate at a time, GATE_JOBS=1, 4 h cap. "
     "Probes ran from a second baseline worktree (never the gate's tree), loading the mutated module in memory via probes/_mutload.py.", "",
     "## Tally", "",
     f"- gated: {len(gated)} of {len(keys)}; verdicts: " + ", ".join(f"{v} {n}" for v, n in sorted(tally.items())),
     f"- KILLED: {len(killed)}" + ("".join(f"\n  - {r['key']} by {', '.join(r['gate']['killed_by'] or [])}" for r in killed)),
     f"- TIMEOUT: {len(timeouts)}" + (f" ({', '.join(timeouts)})" if timeouts else ""),
     f"- candidates (survived, probe moves): {len(cands)}",
     f"- equivalent-candidates (survived, no input found that moves the probe): {len(equiv)}", "",
     "Findings are returned as `findings: []`; candidates sit under `gate_survivors` for the orchestrator's id assignment.", "",
     "## Per key", ""]
for k in keys:
    r = recs.get(k[0])
    if not r:
        L += [f"### {k[0]} — not gated", ""]; continue
    g = r["gate"]
    head = f"### {r['key']} — {r['site']} — {g['verdict']} — {r['class']}"
    L += [head, "", f"`{r['patch']}` in `{r['function']}`. Gate: gate_rc {g['gate_rc']}, killed_by {g['killed_by']}, wall {g['wall_s']} s, load1 {g['load1_start']} -> {g['load1_end']}.", ""]
    if r["class"] == "killed":
        L += [f"Non-finding: the suite fails on it. {r['non_finding']['value']}.", ""]
    elif r["class"] == "timeout":
        L += [f"TIMEOUT at the {r['timeout']['cap_s']} s cap; last script in the log {r['timeout']['last_script_in_log']}. Unfinished.", ""]
    else:
        p = r["probe"]
        tried = "; ".join(f"{c}: {v['baseline']} / {v['mutant']}" for c, v in p["inputs_tried"].items())
        L += [f"Step 4: should have failed {', '.join(r['should_fail']['scripts'])} (their traced baseline executes the line): {r['should_fail']['assertion']}.", "",
              f"Probe `{p['command']}`: cases moved {p['cases_moved']}, null cases moved {p['null_cases_moved']}. Inputs (baseline / mutant): {tried}.", ""]
        if r["class"] == "candidate":
            f = r["finding"]
            L += [f"Candidate ({f['severity_claimed']}, class_guess {f['class_guess']}): {f['title']}. {f['value']}.", ""]
        else:
            L += ["Equivalent-candidate: no input tried moves the number; a non-finding unless a later seat finds one.", ""]
(W / "REPORT.md").write_text("\n".join(L) + "\n")
print("REPORT", len(recs), "records", tally, "candidates", len(cands), "equivalent", len(equiv))
