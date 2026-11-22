"""REPORT.json / REPORT.md for box D3-g32 (imported by build.py --report; no measurement of its own)."""
import json
from collections import Counter, defaultdict

REL = "dev/audit/rounds/round11/D3/s1/wave/D3-g32"
BASE = "92d38ecb640bd462f2e19c0814d0f0b7df1ee692"
FG = "dev/audit/rounds/round11/D3/s1/fullgate.py"
ENUM = "awk -F'\\t' '$6==\"gate\"' SURVIVORS.tsv"


def main(W, A, keys, gate, record):
    S1 = W.parent.parent
    rows = keys()
    recs = [r for r in (record(row) for row in rows) if r is not None]
    null = json.loads((W / "gates" / "null.json").read_text())
    u1b = json.loads((S1 / "REPORT-D3-u1b.json").read_text())
    machine = (W / "MACHINE.txt").read_text()

    # --- coverage: M1, M2, M4, M5 carried verbatim from REPORT-D3-u1b.json; M3 is this wave's row
    cov = []
    for c in u1b["coverage"]:
        if c["step"] == "D3.M3":
            continue
        c = dict(c)
        c["evidence"] = "CARRIED verbatim from REPORT-D3-u1b.json (not re-driven by box D3-g32). " + c.get("evidence", "")
        cov.append(c)
    wave = [l.split("\t") for l in (W / "WAVE-KEYS.tsv").read_text().splitlines() if l.strip()]
    mine = {r[0] for r in rows}
    timeouts = [r["key"] for r in recs if r["class"] == "timeout"]
    ungated = [r[0] for r in rows if gate(r[0]) is None]
    examined = len(recs) - len(timeouts)
    by_box = defaultdict(list)
    for b, k, *rest in wave:
        if b != "D3-g32":
            by_box[b].append(k)
    nr = [f"assigned to box {b}: {len(ks)} keys ({', '.join(ks)})" for b, ks in sorted(by_box.items())]
    nr += [f"box D3-g32 TIMEOUT past the 4 h cap: {k}" for k in timeouts]
    nr += [f"box D3-g32 not gated (run ended before it): {k}" for k in ungated]
    cov.append({
        "step": "D3.M3", "enumerator": ENUM, "universe": len(wave), "examined": examined,
        "not_reached": nr, "redispatched": [],
        "evidence": (f"Box D3-g32 ran the full gate (GATE_SCOPE=full GOLDEN_MODE=drift GOLDEN_REF={BASE} GATE_JOBS=1 ./tests/run.sh, "
                     f"one gate at a time, via gate_wave.sh run -> `{FG} run --src complete --key <key>`) on its {len(rows)} keys "
                     f"({REL}/keys.tsv); records {REL}/gates/<key>.json, null control {REL}/gates/null.json. SURVIVORS.tsv is not in "
                     f"this box's tree; the 742-key wave list was re-assembled from the 47 dispatch refs' keys.tsv into {REL}/WAVE-KEYS.tsv "
                     f"(742 keys, 0 duplicates). The 8 deduped keys gated earlier under other keys are box D3-top6's and D3-rem's "
                     f"D3.M3 rows (REPORT-D3-top6.json, REPORT-D3-rem.json), outside this universe. Examined {examined} = this box's "
                     f"gated keys less TIMEOUTs.")})

    v = Counter(r["gate"]["verdict"] for r in recs)
    kb = Counter(s for r in recs if r["gate"]["verdict"] == "KILLED" for s in r["gate"]["killed_by"])
    cands = [r for r in recs if r["class"] == "candidate"]
    eqs = [r for r in recs if r["class"] == "equivalent-candidate"]
    non = []
    for r in recs:
        g = r["gate"]
        if g["verdict"] == "KILLED":
            non.append({"claim": f"full gate KILLED {r['key']} {r['site']} ({r['patch']}) by {', '.join(g['killed_by'])}",
                        "command": g["command"],
                        "value": f"gate_rc={g['gate_rc']} killed_by={g['killed_by']} wall {g['wall_s']} s, load1 {g['load1_start']}..{g['load1_end']} (provisional)"})
    for r in eqs:
        g = r["gate"]
        non.append({"claim": f"equivalent-candidate {r['key']} {r['site']} ({r['patch']}): full gate {g['verdict']}, and no reachable input moves the probe's number; {r['should_fail']}",
                    "command": r["probe"]["command"],
                    "value": f"baseline {r['probe']['baseline_value']} / mutant {r['probe']['mutant_value']}; inputs tried: {r['probe']['inputs_tried']}"})
    unfinished = [{"step": "D3.M3", "what": f"TIMEOUT (past the 4 h cap) {k}: re-gate on a quieter box"} for k in timeouts]
    unfinished += [{"step": "D3.M3", "what": f"not gated: {k}"} for k in ungated]
    harn = [FG, f"{REL}/build.py", f"{REL}/report.py"] + [r["probe"]["path"] for r in recs]
    gated = [{"key": r["key"], "site": r["site"], "verdict": r["gate"]["verdict"], "killed_by": r["gate"]["killed_by"],
              "class": r["class"]} for r in recs]
    rep = {
        "dimension": "D3", "baseline_sha": BASE, "box": "D3-g32", "report_path": f"{REL}/REPORT.md",
        "exposure": ("Read the slice boxes' carried reports and step-4 answers (REPORT-D3-u1a..d, REPORT-u1a, m4_*), "
                     "REPORT-D3-top6.md and REPORT-D3-rem.md, as the brief requires; the other 46 wave boxes' keys.tsv "
                     "from their dispatch refs (key lists only) for the D3.M3 denominator; no GitHub reads."),
        "coverage": cov, "unfinished": unfinished, "findings": [], "non_findings": non, "harnesses": harn, "leads": [],
        "gated": gated, "gate_survivors": cands, "equivalent_candidates": eqs,
        "procedure": ("gate_wave.sh (dispatch ref tool, out of tree): null control once (`fullgate.py null`, comment-only "
                      "marker on tariff.py), then per key of keys.tsv in order `fullgate.py run --src complete --key <key>` "
                      "under a 4 h cap, one gate at a time, tree reset to the baseline between gates; the verdict is "
                      "fullgate.py's (KILLED = red and a failing script beyond the null)."),
        "null_control": {"gate_rc": null.get("gate_rc"), "failed_scripts": null.get("failed_scripts"),
                         "summary": null.get("summary"), "wall_s": null.get("wall_s"),
                         "record": f"{REL}/gates/null.json"},
    }
    (W / "REPORT.json").write_text(json.dumps(rep, indent=1) + "\n")

    md = [f"# D3-s1 wave box D3-g32 — full gate for 16 D3.M3 full-net survivors (round 11)", "",
          f"Baseline `{BASE}`. Seat D3-s1, dimension D3, step D3.M3/M4. Findings are returned as `gate_survivors` "
          "(ids are assigned at consolidation).", "",
          "## Machine and controls", "", "```", machine.strip(), "```", "",
          f"Null control (`{FG} null`): gate_rc={null.get('gate_rc')}, failed scripts {null.get('failed_scripts')}, "
          f"summary {null.get('summary')}, wall {null.get('wall_s')} s (provisional), load1 "
          f"{null.get('load1_start')}..{null.get('load1_end')}.", "",
          "Procedure: " + rep["procedure"], "",
          "## Tally", "",
          f"- gated: {len(recs)} of {len(rows)}",
          f"- KILLED: {v.get('KILLED', 0)}" + (f" (by script: {dict(kb)})" if kb else ""),
          f"- SURVIVED: {v.get('SURVIVED', 0)}", f"- RED-AS-NULL: {v.get('RED-AS-NULL', 0)}",
          f"- TIMEOUT: {v.get('TIMEOUT', 0)}",
          f"- candidates (probe moves): {len(cands)}", f"- equivalent-candidates: {len(eqs)}", "",
          "| key | site | patch | verdict | killed_by | wall s | class |", "|---|---|---|---|---|---|---|"]
    for r in recs:
        g = r["gate"]
        md.append(f"| {r['key']} | {r['site']} | `{r['patch']}` | {g['verdict']} | {', '.join(g['killed_by']) or '-'} | {g['wall_s']} | {r['class']} |")
    md += ["", "## Survivors: the step-4 answers", ""]
    for r in recs:
        if r["class"] in ("killed", "timeout"):
            continue
        md += [f"### {r['key']} — {r['site']} ({r['class']})", "",
               f"Patch `{r['patch']}` in `{r['function']}`. Full gate: {r['gate']['verdict']} (gate_rc {r['gate']['gate_rc']}). "
               f"Probe `{r['probe']['command']}`: baseline {r['probe']['baseline_value']}; mutant {r['probe']['mutant_value']}. "
               f"Inputs tried: {r['probe']['inputs_tried']}.", "",
               f"Check that should have failed: {r['should_fail']}.", ""]
        if r["class"] == "candidate":
            f = r["finding"]
            md += [f"Candidate: **{f['title']}** — severity claimed {f['severity_claimed']}. {f['claim']}", ""]
    if any(r["class"] == "killed" for r in recs):
        md += ["## KILLED (non-findings)", ""]
        for r in recs:
            if r["class"] == "killed":
                md.append(f"- {r['key']} {r['site']}: killed by {', '.join(r['gate']['killed_by'])}; {r['gate']['command']}")
        md.append("")
    md += ["## Unfinished", ""] + ([f"- {u['what']}" for u in unfinished] or ["- none"]) + ["",
           "## Harnesses", ""] + [f"- `{h}`" for h in harn] + [""]
    (W / "REPORT.md").write_text("\n".join(md))
    print(f"REPORT gated={len(recs)} candidates={len(cands)} equivalent={len(eqs)} killed={v.get('KILLED', 0)} timeout={len(timeouts)}")
