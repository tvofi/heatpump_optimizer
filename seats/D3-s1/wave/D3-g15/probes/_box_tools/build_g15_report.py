"""Box D3-g15's REPORT.json / REPORT.md builder (out of tree; imported by build_g15.py report)."""
import json
from pathlib import Path

import build_g15 as b

WAVEKEYS = b.HOME / "wavekeys"  # each wave box's keys.tsv, read from its dispatch/finder-r11-D3-g<NN> tip


def main():
    keys = b.keys_tsv()
    recs = []
    for r in keys:
        p = b.W / "results" / f"{r['key']}.json"
        if p.exists():
            recs.append(json.loads(p.read_text()))
    done = {x["key"] for x in recs}
    left = [r["key"] for r in keys if r["key"] not in done]
    null = json.loads((b.W / "gates" / "null.json").read_text())
    machine = (b.W / "MACHINE.txt").read_text()
    u1b = json.loads((b.S1 / "REPORT-D3-u1b.json").read_text())

    cov = []
    for row in u1b["coverage"]:
        if row["step"] == "D3.M3":
            continue
        r = dict(row)
        r["evidence"] = "carried verbatim from REPORT-D3-u1b.json (box D3-u1b; not re-driven by box D3-g15): " + row["evidence"]
        cov.append(r)
    m3_old = next(x for x in u1b["coverage"] if x["step"] == "D3.M3")
    timeouts = [x["key"] for x in recs if x["class"] == "timeout"]
    gated_ok = [x["key"] for x in recs if x["class"] != "timeout"]
    not_reached = []
    for f in sorted(WAVEKEYS.glob("D3-g*.tsv")):
        box = f.stem
        if box == "D3-g15":
            continue
        ks = [l.split("\t")[0] for l in f.read_text().splitlines()[1:] if l.strip()]
        not_reached.append(f"assigned to box {box}: {len(ks)} keys ({ks[0]} .. {ks[-1]})")
    for k in timeouts:
        not_reached.append(f"TIMEOUT on box D3-g15 (4 h cap): {k}")
    for k in left:
        not_reached.append(f"not gated by box D3-g15 (run ended before it): {k}")
    other = sum(len([l for l in f.read_text().splitlines()[1:] if l.strip()]) for f in WAVEKEYS.glob("D3-g*.tsv") if f.stem != "D3-g15")
    universe = other + len(keys)
    m3 = dict(step="D3.M3", enumerator="awk -F'\\t' '$6==\"gate\"' SURVIVORS.tsv", universe=universe,
              examined=len(gated_ok), not_reached=not_reached, redispatched=m3_old["redispatched"],
              evidence=("the wave list (742 keys, the owner's 2026-11-22 ruling: every u1 full-net survivor gets the full "
                        "gate) split over boxes D3-g01..D3-g47; this box's 16 keys from its dispatch keys.tsv, the other "
                        "boxes' lists read from their dispatch/finder-r11-D3-g<NN> tips (sum 742). Per key: "
                        "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/fullgate.py run --src complete --key <key> "
                        "(GATE_SCOPE=full GOLDEN_MODE=drift GOLDEN_REF=<baseline> GATE_JOBS=1 ./tests/run.sh), driven one at a time "
                        "by the box's gate_wave.sh run; records " + b.REL_W + "/gates/<key>.json and .log; null control "
                        + b.REL_W + "/gates/null.json. The 8 wave survivors already gated under other keys by boxes D3-top6 "
                        "and D3-rem are those boxes' D3.M3 rows (REPORT-D3-top6.json, REPORT-D3-rem.json), outside this universe. "
                        "Redispatched items carried verbatim from REPORT-D3-u1b.json's D3.M3 row."))
    order = ["D3.M1", "D3.M2", "D3.M3", "D3.M4", "D3.M5"]
    cov.append(m3)
    cov.sort(key=lambda r: order.index(r["step"]))

    tally = {}
    for x in recs:
        tally[x["gate"]["verdict"]] = tally.get(x["gate"]["verdict"], 0) + 1
    killed_by = {}
    for x in recs:
        for s in x["gate"].get("killed_by") or []:
            killed_by[s] = killed_by.get(s, 0) + 1
    cands = [x for x in recs if x["class"] == "candidate"]
    eqs = [x for x in recs if x["class"] == "equivalent-candidate"]
    kills = [x for x in recs if x["class"] == "killed"]

    non_findings = []
    for x in kills:
        g = x["gate"]
        non_findings.append(dict(
            claim=f"full gate {x['key']} {x['site']} ({x['patch']}): KILLED, the suite fails on it",
            command=g["command"],
            value=f"killed_by={','.join(g.get('killed_by') or [])}; gate_rc={g['gate_rc']}; wall {g['wall_s']} s, "
                  f"load1 {g['load1_start']}..{g['load1_end']} (provisional)"))
    for x in eqs:
        g = x["gate"]
        non_findings.append(dict(
            claim=f"full gate {x['key']} {x['site']} ({x['patch']}): {g['verdict']}; equivalent-candidate: {x['probe']['reading']}",
            command=x["probe"]["command"] + " ; " + g["command"],
            value=f"{x['probe']['baseline_value']} | {x['probe']['mutant_value']}; inputs tried: {x['probe']['inputs_tried']}; "
                  f"gate_rc={g['gate_rc']}, wall {g['wall_s']} s (provisional)"))
    harn = [b.FULLGATE, f"{b.REL_W}/probes/_lg_common.py"] + [f"{b.REL_W}/probes/probe_{r['key']}.py" for r in keys]
    unfinished = [dict(step="D3.M3", what=f"TIMEOUT past the 4 h cap on box D3-g15, neither killed nor survived: {k}") for k in timeouts]
    unfinished += [dict(step="D3.M3", what=f"not gated on box D3-g15: {k}") for k in left]
    gated = [dict(key=x["key"], site=x["site"], verdict=x["gate"]["verdict"], killed_by=x["gate"].get("killed_by") or [],
                  **{"class": x["class"]}) for x in recs]
    rep = dict(dimension="D3", baseline_sha=b.BASE, box="D3-g15", report_path=f"{b.REL_W}/REPORT.md", exposure="",
               coverage=cov, unfinished=unfinished, findings=[], non_findings=non_findings, harnesses=harn, leads=[],
               procedure=("gate_wave.sh (shipped on dispatch/finder-r11-D3-g15): null once, then for each key of keys.tsv "
                          "in order, one gate at a time: clean tree at the baseline, fullgate.py run --src complete --key "
                          "<key> under a 4 h cap (SIGINT -> TIMEOUT, never KILLED), record, reset, checkpoint"),
               gated=gated, gate_survivors=cands, equivalent_candidates=eqs,
               null_control=dict(record=f"{b.REL_W}/gates/null.json", gate_rc=null.get("gate_rc"),
                                 failed_scripts=null.get("failed_scripts"), fail_lines=null.get("fail_lines"),
                                 summary=null.get("summary"), wall_s=null.get("wall_s"),
                                 load1=[null.get("load1_start"), null.get("load1_end")], provisional=True))
    (b.W / "REPORT.json").write_text(json.dumps(rep, indent=1) + "\n")

    md = []
    md.append("# D3-s1 wave box D3-g15: full gate for 16 D3.M3 full-net survivors (round 11)\n")
    md.append(f"Baseline `{b.BASE}`. Seat D3-s1, box D3-g15. Keys: `{b.REL_W}/keys.tsv` (all 16 in "
              "`dhw_planner.py`, `DhwPlanner._dhw_legionella_ceilings` lines 740-807 and `DhwPlanner._dhw_legionella_due` "
              "lines 596-659).\n")
    md.append("## Machine and controls\n")
    md.append("```\n" + machine.strip() + "\n```\n")
    md.append(f"Null control (`fullgate.py null`, comment-only marker on tariff.py): gate_rc={null.get('gate_rc')}, "
              f"failed scripts {null.get('failed_scripts')}, fail lines {null.get('fail_lines')}, summary {null.get('summary')}, "
              f"wall {null.get('wall_s')} s, load1 {null.get('load1_start')}..{null.get('load1_end')} (provisional). "
              "A mutant is KILLED only by a script red beyond the null, or failing more checks than in the null. "
              f"Every red check of the null is an environment artefact, no production file involved (`{b.REL_W}/gates/null-note.txt`): "
              "closure.py selftest's two merge-tool pins, entities.py's scoped-gate pin, harness_headers.py's round-4 "
              "D6/claims.py re-run on the finder-wall-stripped tree; the same three scripts box D3-rem's null recorded red.\n")
    md.append("Procedure: `gate_wave.sh run` drove `fullgate.py run --src complete --key <key>` (GATE_SCOPE=full "
              "GOLDEN_MODE=drift GOLDEN_REF=<baseline> GATE_JOBS=1 ./tests/run.sh) one key at a time, alone on the box, 4 h cap. "
              "Every wall, CPU and load number is provisional (nproc 4, Intel Xeon @ 2.10GHz; the judge re-takes it); "
              "counts are final.\n")
    md.append("Probes ran from a separate baseline worktree (never the gate's tree), with the mutant applied in memory "
              "(the method recompiled from its own source with the one line replaced, attached with mock.patch.object). "
              "tests/harness_headers.py rglobs every script under dev/audit/rounds (tracked or not) and requires each inlined "
              "repo_root to equal tools/audit/repo_root.py's; _lg_common.py carries the canonical copy, and inline_scan with "
              "the probes present returns 0 with no depth seams. The probes entered the gate's tree during the null "
              "control (orchestrator NOTE 2, save every probe in the wave dir); every key gate ran with them present.\n")
    md.append("## Tally\n")
    md.append(f"- gated: {len(recs)} of {len(keys)}; " + ", ".join(f"{k} {v}" for k, v in sorted(tally.items())))
    md.append(f"- KILLED by script: {killed_by if killed_by else 'none'}")
    md.append(f"- candidates (full-gate survivors whose probe moves on an in-range input): {len(cands)}")
    md.append(f"- equivalent-candidates: {len(eqs)}")
    md.append(f"- TIMEOUT: {len(timeouts)} {timeouts if timeouts else ''}\n")
    md.append("| key | site | patch | verdict | killed_by | wall s (prov.) | class |")
    md.append("|---|---|---|---|---|---|---|")
    for x in recs:
        g = x["gate"]
        md.append(f"| {x['key']} | {x['site']} | `{x['patch']}` | {g['verdict']} | {','.join(g.get('killed_by') or []) or '-'} "
                  f"| {g.get('wall_s')} | {x['class']} |")
    md.append("")
    md.append("## Survivors: the step-4 answer per key\n")
    for x in recs:
        if x["class"] in ("killed", "timeout"):
            continue
        pr = x["probe"]
        md.append(f"### {x['key']} — {x['site']}, `{x['patch']}` ({x['class']})\n")
        md.append(f"Gate: {x['gate']['verdict']} (gate_rc {x['gate']['gate_rc']}, `{x['gate']['record']}`). "
                  f"Probe `{pr['command']}`: {pr['baseline_value']} | {pr['mutant_value']}. {pr['reading']}. "
                  f"Inputs tried: {pr['inputs_tried']}. Should have failed: {x['should_fail']}.\n")
        if x["class"] == "candidate":
            f = x["finding"]
            md.append(f"Candidate finding (id assigned at consolidation): **{f['title']}**, severity {f['severity']} "
                      f"(claimed), class_guess {f['class_guess']}. Metric: {f['metric_definition']}. Null: {f['null_control']['note']}. "
                      f"Fix scope: {f['proposed_fix_scope']}.\n")
    if kills:
        md.append("## Killed (non-findings)\n")
        for x in kills:
            md.append(f"- {x['key']} {x['site']}: killed_by {x['gate'].get('killed_by')}; `{x['gate']['command']}`; "
                      f"failing lines: {x.get('killed_failing_lines', [])[:4]}")
        md.append("")
    md.append("## Harnesses\n")
    md += [f"- `{h}`" for h in harn]
    md.append("- the box's gate_wave.sh procedure (out of tree, on the dispatch ref), named above\n")
    md.append("## Unfinished\n")
    md += [f"- {u['what']}" for u in unfinished] or ["- none"]
    md.append("")
    md.append("## Coverage\n")
    md.append("D3.M1, D3.M2, D3.M4 and D3.M5 and their redispatched C-items are carried verbatim from REPORT-D3-u1b.json. "
              f"D3.M3 here: universe {universe} (the wave list), examined {len(gated_ok)} (this box's gated keys), "
              f"not_reached by box: {len(not_reached)} rows. Findings: [] — candidates are under gate_survivors for the "
              "orchestrator's consolidation, which assigns ids.\n")
    (b.W / "REPORT.md").write_text("\n".join(md) + "\n")
    print(f"WROTE REPORT.json/REPORT.md: gated {len(recs)}/{len(keys)}, candidates {len(cands)}, equivalent {len(eqs)}, "
          f"killed {len(kills)}, timeout {len(timeouts)}, left {len(left)}")


if __name__ == "__main__":
    main()
