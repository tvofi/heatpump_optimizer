#!/usr/bin/env python3
# Box D3-g14 (round 11, D3-s1): assembles REPORT.json and REPORT.md for this box from
# keys.tsv, gates/<key>.json, gates/null.json, results/<key>.json, MACHINE.txt and the
# carried coverage rows of REPORT-D3-u1b.json.
# Command: python3 dev/audit/rounds/round11/D3/s1/wave/D3-g14/build_report.py [--out DIR]
import json, sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent


def _repo(p):
    for c in (p, *p.parents):
        if (c / "custom_components/heatpump_optimizer/manifest.json").is_file():
            return c
    raise RuntimeError("no repository root")


BOX = "D3-g14"
BASE = "92d38ecb640bd462f2e19c0814d0f0b7df1ee692"
S1R = "dev/audit/rounds/round11/D3/s1"
WR = f"{S1R}/wave/{BOX}"
ROOT = _repo(HERE)
S1 = ROOT / S1R
W = ROOT / WR
FG_CMD = "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/fullgate.py"
PROCEDURE = ("gate_wave.sh (the dispatch ref's driver, run out of tree): `gate_wave.sh null` = fullgate.py null once; "
             "`gate_wave.sh run` = fullgate.py run --src <src> --key <key> for each keys.tsv row in order, one gate at a time, "
             "GATE_JOBS=1, capped at 4 h (TIMEOUT), the record copied to gates/<key>.json(.log) and checkpointed")


def main():
    out = W
    if "--out" in sys.argv:
        out = Path(sys.argv[sys.argv.index("--out") + 1])
    keys = [l.split("\t") for l in (W / "keys.tsv").read_text().splitlines()[1:] if l.strip()]
    null = json.loads((W / "gates/null.json").read_text())
    u1b = json.loads((S1 / "REPORT-D3-u1b.json").read_text())
    recs, missing = {}, []
    for row in keys:
        k = row[0]
        p = W / "results" / f"{k}.json"
        if p.is_file():
            recs[k] = json.loads(p.read_text())
        else:
            missing.append(k)

    gated = []
    for row in keys:
        k = row[0]
        r = recs.get(k)
        if not r:
            continue
        g = r["gate"]
        gated.append(dict(key=k, site=r["site"], verdict=g["verdict"], killed_by=g.get("killed_by") or [],
                          cls=r["class"], gate_rc=g.get("gate_rc"), wall_s=g.get("wall_s"),
                          load1=f"{g.get('load1_start')}..{g.get('load1_end')}", record=f"{WR}/gates/{k}.json"))
    for x in gated:
        x["class"] = x.pop("cls")
    timeouts = [x for x in gated if x["verdict"] == "TIMEOUT"]
    examined = len(gated) - len(timeouts)
    cand = [recs[x["key"]] for x in gated if x["class"] == "candidate"]
    equiv = [recs[x["key"]] for x in gated if x["class"] == "equivalent-candidate"]
    killed = [recs[x["key"]] for x in gated if x["class"] == "killed"]

    rows = {c["step"]: c for c in u1b["coverage"]}
    cov = []
    for step in ("D3.M1", "D3.M2", "D3.M3", "D3.M4", "D3.M5"):
        if step != "D3.M3":
            c = dict(rows[step])
            c["carried"] = "verbatim from dev/audit/rounds/round11/D3/s1/REPORT-D3-u1b.json (slice box D3-u1b)"
            cov.append(c)
            continue
        nr = [f"assigned to box D3-g{n:02d}: its keys of the wave list (SURVIVORS.tsv rows with box D3-g{n:02d})"
              for n in range(1, 48) if n != 14]
        nr += [f"TIMEOUT on box {BOX}: {x['key']} {x['site']} (past the 4 h cap; unfinished)" for x in timeouts]
        nr += [f"not gated on box {BOX}: {k} (no gate record; unfinished)" for k in missing]
        cov.append(dict(
            step="D3.M3",
            enumerator="awk -F'\\t' '$6==\"gate\"' SURVIVORS.tsv",
            universe=742,
            examined=examined,
            not_reached=nr,
            redispatched=rows["D3.M3"]["redispatched"],
            redispatched_carried="verbatim from REPORT-D3-u1b.json's D3.M3 row",
            evidence=(f"box {BOX} gated {len(gated)} of its 16 keys (keys.tsv), {examined} with a verdict: "
                      + "; ".join(f"{FG_CMD} run --src complete --key {x['key']} -> {x['verdict']} ({x['record']})" for x in gated)
                      + f". Null control: {FG_CMD} null -> {WR}/gates/null.json (gate_rc {null.get('gate_rc')}, failed {null.get('failed_scripts')}). "
                      "The earlier boxes' D3.M3 rows (D3-top6, D3-rem: the 8 deduped keys gated under other keys; slice boxes D3-u1a..d: the fast and full nets) stand in their own reports; "
                      "every other wave key is another box's (D3-g01..D3-g47), named above by box."),
        ))

    nf = []
    for r in killed:
        g = r["gate"]
        nf.append(dict(claim=f"full gate {r['key']} {r['site']} ({r['patch']}): pinned by the suite (KILLED)",
                       command=g.get("command") or f"{FG_CMD} run --src complete --key {r['key']}",
                       value=f"killed_by={', '.join(g.get('killed_by') or [])}; gate_rc {g.get('gate_rc')}; wall {g.get('wall_s')} s, load1 {g.get('load1_start')}..{g.get('load1_end')} (provisional)"))
    for r in equiv:
        g, p = r["gate"], r["probe"]
        nf.append(dict(claim=f"full gate {r['key']} {r['site']} ({r['patch']}): {g['verdict']} and equivalent-candidate: no input tried separates the arms ({p.get('production_reach')})",
                       command=p["command"],
                       value=f"baseline {p['baseline_value']}; mutant {p['mutant_value']}; inputs tried: {'; '.join(p.get('inputs_tried') or [])}; gate {g['verdict']} gate_rc {g.get('gate_rc')}"))

    probes = sorted({h for r in recs.values() for h in ([r["probe"]["path"]] if r.get("probe") else [])})
    harnesses = [f"{S1R}/fullgate.py", f"{WR}/build_records.py", f"{WR}/build_report.py", f"{WR}/probes/_g14lib.py", f"{WR}/probes/_mk.py"] + probes

    unfinished = [dict(step="D3.M3", what=f"TIMEOUT: {x['key']} {x['site']} passed the 4 h cap (gates/{x['key']}.json); neither finding nor non-finding") for x in timeouts]
    unfinished += [dict(step="D3.M3", what=f"not gated: {k} has no gate record on box {BOX}") for k in missing]

    machine = (W / "MACHINE.txt").read_text()
    rep = dict(
        dimension="D3", baseline_sha=BASE, box=BOX, report_path=f"{WR}/REPORT.md",
        exposure=u1b.get("exposure"),
        coverage=cov, unfinished=unfinished, findings=[], non_findings=nf, harnesses=harnesses, leads=[],
        procedure=PROCEDURE,
        gated=gated, gate_survivors=cand, equivalent_candidates=equiv,
    )

    vc = Counter(x["verdict"] for x in gated)
    kb = Counter(s for x in gated for s in x["killed_by"])
    md = [f"# Round 11 D3-s1 box {BOX}: full gate for 16 D3.M3 full-net survivors", "",
          f"Baseline `{BASE}`. Seat D3-s1, box {BOX}. Findings: none numbered here; candidates go under `gate_survivors` for the orchestrator's consolidation.", "",
          "## Machine and controls", "",
          "Every wall, CPU and load number is provisional (the judge re-takes it).", "", "```", machine.strip(), "```", "",
          f"Null control: `{FG_CMD} null` -> `{WR}/gates/null.json`: gate_rc {null.get('gate_rc')}, failed scripts {null.get('failed_scripts')}, "
          f"fail lines {null.get('fail_lines')}, wall {null.get('wall_s')} s (provisional). Take 1 (`gates/null-take1.json`) was re-taken once; see NULL-NOTE.md. "
          "A mutant is KILLED only by a script not red in the null, or by more FAIL lines in one than the null shows.", "",
          f"Procedure: {PROCEDURE}.", "",
          "Resume: gates 1-8 and every probe were run by the box's first seat (another container; MACHINE.txt's first block). "
          "This seat restored that checkpoint and gated keys 9-16 on the machine of MACHINE.txt's re-fire block, against the same null.", "",
          "## Tally", "",
          f"- gated: {len(gated)} of 16" + (f" (not gated: {', '.join(missing)})" if missing else ""),
          f"- KILLED: {vc.get('KILLED', 0)}" + (f" (by {dict(kb)})" if kb else ""),
          f"- SURVIVED: {vc.get('SURVIVED', 0)}",
          f"- RED-AS-NULL: {vc.get('RED-AS-NULL', 0)} (red only on the null's artefact checks: read as survived)",
          f"- TIMEOUT: {vc.get('TIMEOUT', 0)}",
          f"- candidates: {len(cand)}", f"- equivalent-candidates: {len(equiv)}", "",
          "| key | site | patch | verdict | gate_rc | wall s | load1 | class |", "|---|---|---|---|---|---|---|---|"]
    for x in gated:
        md.append(f"| {x['key']} | {x['site']} | `{recs[x['key']]['patch']}` | {x['verdict']} | {x['gate_rc']} | {x['wall_s']} | {x['load1']} | {x['class']} |")
    md += ["", "## Survivors: the step-4 answer per key", ""]
    for x in gated:
        r = recs[x["key"]]
        if r["class"] in ("killed", "timeout"):
            continue
        p, s = r["probe"], r.get("should_fail") or {}
        para = (f"**{r['key']}** `{r['site']}` in `{r['function']}`, `{r['patch']}`: gate {r['gate']['verdict']} (gate_rc {r['gate'].get('gate_rc')}). "
                f"Probe `{p['command']}`: baseline {p['baseline_value']}; mutant {p['mutant_value']}. Inputs tried: {'; '.join(p.get('inputs_tried') or [])}. "
                f"Reach: {p.get('production_reach')}. Class: {r['class']}.")
        if r["class"] == "candidate":
            f = r["finding"]
            para += (f" Should have failed: {s.get('script')}; missing assertion: {s.get('assertion')}. "
                     f"Candidate: \"{f['title']}\" (severity claimed {f['severity_claimed']}, direction {f['perturbation']['direction']}).")
        md += [para, ""]
    if killed:
        md += ["## Killed", ""]
        for r in killed:
            md += [f"- {r['key']} `{r['site']}`: killed_by {', '.join(r['gate'].get('killed_by') or [])}", ""]
    if unfinished:
        md += ["## Unfinished", ""] + [f"- {u['what']}" for u in unfinished] + [""]
    out.mkdir(parents=True, exist_ok=True)
    (out / "REPORT.json").write_text(json.dumps(rep, indent=1) + "\n")
    (out / "REPORT.md").write_text("\n".join(md) + "\n")
    print(f"RESULT gated={len(gated)} examined={examined} candidates={len(cand)} equivalent={len(equiv)} killed={len(killed)} timeout={len(timeouts)} missing={len(missing)}")


if __name__ == "__main__":
    main()
