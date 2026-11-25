#!/usr/bin/env python3
# Box D3-g40: build REPORT.json and REPORT.md for seat D3-s1 from this wave dir's results/<key>.json, gates/,
# MACHINE.txt and NULL-NOTE.txt, the carried rows of REPORT-D3-u1b.json, and the wave's box assignment
# (boxkeys/<box>.tsv: the keys.tsv of every dispatch/finder-r11-D3-g<NN> ref, read-only).
# Usage (tree root): python3 dev/audit/rounds/round11/D3/s1/wave/D3-g40/build_report.py <boxkeys dir>
import json, sys
from pathlib import Path

W = Path(__file__).resolve().parent
S1 = W.parent.parent
REL = "dev/audit/rounds/round11/D3/s1/wave/D3-g40"
BASE = "92d38ecb640bd462f2e19c0814d0f0b7df1ee692"
BOX = "D3-g40"


def main(boxdir):
    keys = [l.split("\t")[0] for l in (W / "keys.tsv").read_text().splitlines()[1:] if l.strip()]
    recs = {k: json.loads((W / "results" / f"{k}.json").read_text()) for k in keys if (W / "results" / f"{k}.json").exists()}
    null = json.loads((W / "gates" / "null.json").read_text())
    machine = (W / "MACHINE.txt").read_text().strip()
    u1b = json.loads((S1 / "REPORT-D3-u1b.json").read_text())

    # wave universe and box assignment
    assign = {}
    for f in sorted(Path(boxdir).glob("D3-g*.tsv")):
        for l in f.read_text().splitlines()[1:]:
            if l.strip():
                assign[l.split("\t")[0]] = f.stem
    universe = len(assign)
    gated = [k for k in keys if k in recs and recs[k]["class"] != "timeout"]
    timeouts = [k for k in keys if k in recs and recs[k]["class"] == "timeout"]
    ungated = [k for k in keys if k not in recs]
    others = {}
    for k, b in assign.items():
        if b != BOX:
            others.setdefault(b, []).append(k)
    not_reached = [f"assigned to box {b} ({len(v)} keys)" for b, v in sorted(others.items())]
    not_reached += [f"{k}: TIMEOUT on box {BOX} (cap {recs[k]['timeout']['cap_s']} s)" for k in timeouts]
    not_reached += [f"{k}: not gated on box {BOX} (run stopped)" for k in ungated]

    cov = []
    for r in u1b["coverage"]:
        if r["step"] == "D3.M3":
            row = {"step": "D3.M3",
                   "enumerator": "awk -F'\\t' '$6==\"gate\"' SURVIVORS.tsv (the wave list; reproduced here as the union of the 47 dispatch/finder-r11-D3-g<NN> keys.tsv files)",
                   "universe": universe, "examined": len(gated), "not_reached": not_reached,
                   "redispatched": [dict(x, note="carried from REPORT-D3-u1b.json") for x in r.get("redispatched", [])],
                   "evidence": (f"box {BOX}: python3 dev/audit/rounds/round11/D3/s1/fullgate.py run --src complete --key <key> for each of "
                                f"{len(keys)} keys of {REL}/keys.tsv, driven by gate_wave.sh run (GATE_SCOPE=full GOLDEN_MODE=drift "
                                f"GATE_JOBS=1, one gate at a time, cap 14400 s); records {REL}/gates/<key>.json and .log; null control "
                                f"{REL}/gates/null.json (gate_rc {null['gate_rc']}, red only on {', '.join(null['failed_scripts'])}). "
                                f"Gated here: {len(gated)}; universe {universe} = this box's {len(keys)} + {universe - len(keys)} assigned to "
                                f"46 other boxes. Earlier boxes' D3.M3 rows (carried, a different universe: the top six and the "
                                f"remainder): REPORT-D3-top6.json D3.M3 30 of 35, REPORT-D3-rem.json D3.M3 35 of 35; REPORT-D3-u1b.json "
                                f"D3.M3 {r['examined']} of {r['universe']} (fast/full net)."),
                   "carried": False}
            cov.append(row)
        else:
            cov.append(dict(r, carried=True, evidence=f"carried verbatim from REPORT-D3-u1b.json: {r.get('evidence', '')}"))

    gated_rows, survivors, equiv, nonf, unfinished = [], [], [], [], []
    for k in keys:
        r = recs.get(k)
        if r is None:
            unfinished.append({"step": "D3.M3", "what": f"{k} ({assign.get(k)}) not gated on this box"})
            continue
        g = r["gate"]
        gated_rows.append({"key": k, "site": r["site"], "verdict": g.get("verdict"), "killed_by": g.get("killed_by", []),
                           "class": r["class"]})
        if r["class"] == "candidate":
            survivors.append(r)
        elif r["class"] == "equivalent-candidate":
            equiv.append(r)
            p = r["probe"]
            nonf.append({"claim": f"full-gate survivor {k} ({r['site']}, {r['patch']}) is equivalent-candidate: {p['observed']}",
                         "command": p["command"], "value": f"{p['metric']} baseline {p['baseline_value']} mutant {p['mutant_value']} {p['unit']}; gate {g.get('verdict')} gate_rc {g.get('gate_rc')}"})
        elif r["class"] == "killed":
            nonf.append({"claim": f"mutant {k} ({r['site']}, {r['patch']}) is KILLED by the full gate: {', '.join(g.get('killed_by') or [])}"
                                  + (f" -- {r['kill_note']}" if r.get("kill_note") else ""),
                         "command": f"python3 dev/audit/rounds/round11/D3/s1/fullgate.py run --src complete --key {k}",
                         "value": f"gate_rc {g.get('gate_rc')}, killed_by {g.get('killed_by')}, wall {g.get('wall_s')} s (provisional)"})
        elif r["class"] == "timeout":
            unfinished.append({"step": "D3.M3", "what": f"{k} TIMEOUT past {r['timeout']['cap_s']} s; last script {r['timeout']['last_script']}"})

    harn = ["dev/audit/rounds/round11/D3/s1/fullgate.py",
            f"gate_wave.sh (out-of-tree driver on dispatch/finder-r11-{BOX}: null, then run over keys.tsv one gate at a time, cap 14400 s, checkpoint per gate)",
            f"{REL}/build_record.py", f"{REL}/build_report.py", f"{REL}/probes/probe_lib.py", f"{REL}/probes/topk_search.py",
            f"{REL}/probes/metering_search.py"] + [f"{REL}/probes/probe_{k}.py" for k in keys]

    tally = {}
    for row in gated_rows:
        tally[row["verdict"]] = tally.get(row["verdict"], 0) + 1
    kb = {}
    for row in gated_rows:
        for s in row["killed_by"] or []:
            kb[s] = kb.get(s, 0) + 1

    rep = {
        "dimension": "D3", "baseline_sha": BASE, "box": BOX, "report_path": f"{REL}/REPORT.md",
        "exposure": ("Read: the stripped baseline worktree, dev/governance/roles/COMMON.md, dev/governance/dimensions/D3.md, "
                     "dev/audit/README.md, finding.schema.json, bugclasses.json, the D3 s1 slice reports, M4 answer files and "
                     "state/results/complete/<key>.json mutant records for this box's keys, and (read-only) keys.tsv of the 47 "
                     "dispatch/finder-r11-D3-g<NN> refs for the box assignment. Not read: the register, round11/J, any verifier "
                     "report, docs/, GitHub. No gh. Probes import the baseline from `git archive` into temp dirs, never the gate tree. "
                     "$HOME/venv-ci is a symlink this box created to /opt/hpo/venv-ci (the brief's interpreter path)."),
        "coverage": cov, "unfinished": unfinished, "findings": [], "non_findings": nonf, "harnesses": harn, "leads": [],
        "gated": gated_rows, "gate_survivors": survivors, "equivalent_candidates": equiv,
        "null_control": {"record": f"{REL}/gates/null.json", "gate_rc": null["gate_rc"], "failed_scripts": null["failed_scripts"],
                         "fail_lines": null.get("fail_lines"), "wall_s": null.get("wall_s"), "load1_start": null.get("load1_start"),
                         "load1_end": null.get("load1_end"), "provisional": True},
        "machine": machine,
        "driver_notes": (W / "DRIVER-NOTES.txt").read_text().strip() if (W / "DRIVER-NOTES.txt").exists() else "",
    }
    (W / "REPORT.json").write_text(json.dumps(rep, indent=1) + "\n")

    md = [f"# D3-s1 wave box {BOX}: full gate for 15 D3.M3 full-net survivors (round 11)", "",
          f"Baseline `{BASE}`. Seat D3-s1, step D3.M3/D3.M4, box {BOX}. Findings: none numbered here; candidates go under "
          "`gate_survivors` for the orchestrator's consolidation.", "",
          "## Machine and controls", "", "```", machine, "```", "",
          f"Null control: `fullgate.py null` (comment-only marker), gate_rc {null['gate_rc']}, red only on "
          f"{', '.join('`'+s+'`' for s in null['failed_scripts'])} (stripped-tree artefacts: closure shrink pins, one entity check, "
          f"round4/D6 claims.py header drift) -- the profile of D3-rem's accepted null; wall {null.get('wall_s')} s, load1 "
          f"{null.get('load1_start')}..{null.get('load1_end')}. Not re-taken. Wall, CPU and load numbers are provisional "
          "(nproc 4, Intel Xeon @ 2.10GHz); counts are final.", "",
          "Procedure: gate_wave.sh `null` then `run`: for each key, `fullgate.py run --src complete --key <key>` applies the "
          "one-line mutant, commits, runs `GATE_SCOPE=full GOLDEN_MODE=drift GATE_JOBS=1 ./tests/run.sh`, records, resets "
          "to the baseline; one gate at a time, 4 h cap.", "",
          "Driver note: " + ((W / "DRIVER-NOTES.txt").read_text().strip() if (W / "DRIVER-NOTES.txt").exists() else "none")
          + " The interrupted attempt left no record; the key's only gate record is the complete re-run.", "",
          "## Tally", "",
          f"Gated {len(gated_rows)} of {len(keys)}: " + ", ".join(f"{v} {n}" for v, n in sorted(tally.items())) +
          (f"; KILLED by {', '.join(f'`{s}` ({n})' for s, n in kb.items())}" if kb else "") +
          f". TIMEOUT {len(timeouts)}. Candidates {len(survivors)}, equivalent-candidates {len(equiv)}, killed "
          f"{sum(1 for r in gated_rows if r['class']=='killed')}.", "",
          "| key | site | patch | verdict | class | probe metric baseline -> mutant |", "|---|---|---|---|---|---|"]
    for k in keys:
        r = recs.get(k)
        if not r:
            md.append(f"| {k} | | | not gated | | |"); continue
        p = r["probe"]
        md.append(f"| {k} | {r['site']} | `{r['patch']}` | {r['gate'].get('verdict')} | {r['class']} | "
                  f"{p['metric']} {p['baseline_value']} -> {p['mutant_value']} {p['unit']} |")
    md += ["", "## Survivors: step-4 answers", ""]
    for k in keys:
        r = recs.get(k)
        if not r or r["class"] in ("timeout",):
            continue
        p = r["probe"]; sf = r["should_fail"]
        head = f"**{k}** `{r['site']}` `{r['patch']}` ({r['function']}) -- gate {r['gate'].get('verdict')}, class **{r['class']}**."
        body = [head]
        if r["class"] == "killed":
            body.append(f"Killed by {', '.join(r['gate'].get('killed_by') or [])}; failing lines: "
                        + "; ".join(f"`{x}`" for x in r.get("failing_check_lines", [])[:4]) + ".")
            if r.get("kill_note"):
                body.append(r["kill_note"])
        if r["class"] == "candidate":
            f = r["finding"]
            body.append(f"{f['claim']} Severity claimed {f['severity_claimed']}, class_guess {f['class_guess']}.")
        body.append(f"Probe `{p['path']}`: {p['observed']}. Inputs tried: {p['inputs_tried']}.")
        scr = sf["scripts"]
        body.append(f"Should have failed: {', '.join(scr['line_executing_per_carried_m4']) if isinstance(scr['line_executing_per_carried_m4'], list) else scr['line_executing_per_carried_m4']} "
                    f"(the carried M4's line-executing scripts) -- lacking: {sf['assertion_lacking']}.")
        md += [" ".join(body), ""]
    md += ["## Unfinished", ""] + ([f"- {u['what']}" for u in unfinished] or ["- none"]) + [""]
    md += ["## Harnesses", ""] + [f"- `{h}`" for h in harn] + [""]
    (W / "REPORT.md").write_text("\n".join(md))
    print(f"REPORT gated={len(gated_rows)} candidates={len(survivors)} equivalent={len(equiv)} unfinished={len(unfinished)} universe={universe}")


if __name__ == "__main__":
    main(sys.argv[1])
