#!/usr/bin/env python3
"""build_report.py: REPORT.json + REPORT.md for wave box D3-g01 (seat D3-s1) from results/<key>.json, gates/,
REPORT-D3-u1b.json (carried rows) and ~/pt/wave_keys.tsv (the 742-key wave list rebuilt from the 47 dispatch refs'
keys.tsv: box, key, site)."""
import json, copy
from pathlib import Path

BASE = "92d38ecb640bd462f2e19c0814d0f0b7df1ee692"
BOX = "D3-g01"
W = Path.home() / "audit-r11-D3-s1/dev/audit/rounds/round11/D3/s1/wave/D3-g01"
S1 = W.parents[1]
REL = "dev/audit/rounds/round11/D3/s1/wave/D3-g01"
keys = [l.split("\t")[0] for l in (W / "keys.tsv").read_text().splitlines()[1:] if l.strip()]
res = {k: json.loads((W / "results" / f"{k}.json").read_text()) for k in keys if (W / "results" / f"{k}.json").exists()}
gates = {k: json.loads((W / "gates" / f"{k}.json").read_text()) for k in keys if (W / "gates" / f"{k}.json").exists()}
null = json.loads((W / "gates" / "null.json").read_text())
wave = [l.split("\t") for l in (Path.home() / "pt/wave_keys.tsv").read_text().splitlines() if l.strip()]
assert len(wave) == 742 and len({w[1] for w in wave}) == 742
assert {w[1] for w in wave if w[0] == BOX} == set(keys)

u1b = json.loads((S1 / "REPORT-D3-u1b.json").read_text())
carried = {r["step"]: r for r in u1b["coverage"]}

gated_ok = [k for k in keys if k in gates and gates[k].get("verdict") in ("KILLED", "SURVIVED", "RED-AS-NULL")]
timeouts = [k for k in keys if k in gates and gates[k].get("verdict") == "TIMEOUT"]
ungated = [k for k in keys if k not in gates]
missing_rec = [k for k in gated_ok if k not in res]

def carry(step):
    r = copy.deepcopy(carried[step])
    r["carried"] = True
    r["evidence"] = f"carried verbatim from dev/audit/rounds/round11/D3/s1/REPORT-D3-u1b.json ({step}): " + r["evidence"]
    return r

m3 = {
    "step": "D3.M3",
    "enumerator": "awk -F'\\t' '$6==\"gate\"' SURVIVORS.tsv",
    "universe": 742,
    "examined": len(gated_ok),
    "not_reached": [f"assigned to box {b}: {k} {site}" for b, k, site in wave if b != BOX]
                   + [f"TIMEOUT on box {BOX}: {k} (past the {gates[k].get('cap_s')} s cap)" for k in timeouts]
                   + [f"not gated on box {BOX}: {k}" for k in ungated],
    "redispatched": carried["D3.M3"]["redispatched"],
    "evidence": (f"box {BOX}: {len(gated_ok)} of its 16 keys gated by `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/"
                 f"fullgate.py run --src complete --key <key>` (GATE_SCOPE=full GOLDEN_MODE=drift GATE_JOBS=1 ./tests/run.sh), "
                 f"records {REL}/gates/<key>.json; null control {REL}/gates/null.json. Earlier boxes' D3.M3 rows: REPORT-D3-top6.json, "
                 "REPORT-D3-rem.json and the slice reports REPORT-D3-u1{a,b,c,d}.json (their 8 overlapping keys are outside this 742). "
                 "The wave list is SURVIVORS.tsv's gate rows; this tree does not carry that file, so the seat rebuilt the 742 keys "
                 "(no duplicate, 16 on this box) from keys.tsv on the 47 refs dispatch/finder-r11-D3-g01..g47."),
}
coverage = [carry("D3.M1"), carry("D3.M2"), m3, carry("D3.M4"), carry("D3.M5")]

def gated_row(k):
    g, r = gates.get(k, {}), res.get(k, {})
    return {"key": k, "site": r.get("site"), "verdict": g.get("verdict"), "killed_by": g.get("killed_by", []),
            "class": r.get("class"), "gate_rc": g.get("gate_rc"), "wall_s": g.get("wall_s"),
            "load1_start": g.get("load1_start"), "load1_end": g.get("load1_end"), "gate_record": f"{REL}/gates/{k}.json"}

survivors = [res[k] for k in keys if res.get(k, {}).get("class") == "candidate"]
equiv = [res[k] for k in keys if res.get(k, {}).get("class") == "equivalent-candidate"]
killed = [res[k] for k in keys if res.get(k, {}).get("class") == "killed"]

non_findings = []
for r in killed:
    non_findings.append({"claim": r["non_finding"], "command": r["gate_command"],
                         "value": f"verdict KILLED, killed_by {r['killed_by']}, gate_rc {r['gate'].get('gate_rc')}"})
for r in equiv:
    p = r["probe"]
    non_findings.append({"claim": r["non_finding"] + f" (inputs tried: {'; '.join(p['inputs_tried'])})",
                         "command": p["command"] + " ; " + r["gate_command"],
                         "value": f"gate RED-AS-NULL; probe {p['metric']}: baseline {p['baseline_value']}, mutant {p['mutant_value']}"})

harnesses = (["dev/audit/rounds/round11/D3/s1/fullgate.py",
              "gate_wave.sh (out-of-tree driver shipped on dispatch/finder-r11-D3-g01: per key in keys.tsv order, one gate at a time, "
              "fullgate.py run --src complete --key <key> under a 14400 s cap, tree reset to the baseline between gates; null via fullgate.py null)",
              f"{REL}/probes/_tools/ (the seat's probe builders, analysis.py, write_result.py, step2.sh)"]
             + [f"{REL}/probes/probe_{k}.py" for k in keys])

unfinished = ([{"step": "D3.M3", "what": f"{k}: TIMEOUT past the {gates[k].get('cap_s')} s cap; last script running per {REL}/gates/{k}.log"} for k in timeouts]
              + [{"step": "D3.M3", "what": f"{k}: not gated"} for k in ungated]
              + [{"step": "D3.M4", "what": f"{k}: gated but no results record"} for k in missing_rec])

exposure = ("Stripped finder worktree of the baseline (prepare_baseline.sh --strip, 1832 files removed) plus the D3-s1 evidence "
            "from e3cb5c019b. Read: COMMON.md, D3.md, dev/audit/README.md, the D3-s1 slice reports and m4 answers, the dispatch refs' "
            "keys.tsv (to rebuild the wave list only). Not read: the register, round11/J/, any verifier report, docs/ or GitHub. "
            "Resumed box: a predecessor container (Intel Xeon @ 2.10GHz) took the null and gates fafb0d2c15e72efb, 0e6080e5385399cb, "
            "021dc21415f3229e, 622996d751dca0c4, 1165914e57f5bd08 and ab918806fc8b4af6 and wrote every probe; this container "
            "(nproc 4, Intel Xeon @ 2.30GHz, 16 GB) restored that checkpoint and ran the other ten gates against the restored null. "
            "The re-gate of 676e8bfb416ff635 on this container reproduced the null's red set and per-script fail counts exactly "
            "(closure.py selftest 2, entities.py 1, harness_headers.py 3), so the null carries across the two containers. "
            "Every probe whose record this container wrote was re-executed here; its numbers are the ones recorded.")

rep = {
    "dimension": "D3", "baseline_sha": BASE, "box": BOX, "seat": "D3-s1",
    "report_path": f"{REL}/REPORT.md", "exposure": exposure, "coverage": coverage, "unfinished": unfinished,
    "findings": [], "non_findings": non_findings, "harnesses": harnesses, "leads": [],
    "gated": [gated_row(k) for k in keys], "gate_survivors": survivors, "equivalent_candidates": equiv,
}

# ---- markdown
from collections import Counter
vc = Counter(gates[k].get("verdict") for k in gates)
cc = Counter(res[k].get("class") for k in res)
mach = (W / "MACHINE.txt").read_text()
md = [f"# D3-s1 wave box {BOX}: full gate for 16 D3.M3 full-net survivors (round 11)", "",
      f"Baseline `{BASE}`. Seat D3-s1. Report path `{REL}/REPORT.md`; machine-readable twin `REPORT.json`.", "",
      "## Machine and controls", "",
      "Counts are final; every wall, CPU and load number is provisional (the judge re-takes it).", "",
      "```", mach.strip(), "```", "",
      f"Null control: `fullgate.py null` (comment-only marker), gate_rc {null.get('gate_rc')}, red "
      f"{null.get('failed_scripts')} with fail lines {null.get('fail_lines')}, wall {null.get('wall_s')} s. "
      "All three are artefacts of the stripped finder tree / branch environment (see gates/null-note.txt); no production-facing "
      "check is red, card.mjs did not OOM. fullgate.py counts KILLED only on a script beyond the null or more FAIL lines in one.", "",
      exposure, "",
      "## Tally", "",
      f"- gated: {len(gated_ok)} of 16 ({', '.join(f'{v}={n}' for v, n in sorted(vc.items()))})",
      f"- KILLED: {vc.get('KILLED', 0)}; SURVIVED: {vc.get('SURVIVED', 0)}; RED-AS-NULL: {vc.get('RED-AS-NULL', 0)} "
      f"(every one with exactly the null's red set and fail counts); TIMEOUT: {vc.get('TIMEOUT', 0)}",
      f"- candidates (probe moves): {cc.get('candidate', 0)}; equivalent-candidates: {cc.get('equivalent-candidate', 0)}; killed: {cc.get('killed', 0)}",
      "- findings: [] by the brief (ids are assigned at consolidation); candidates are under `gate_survivors`.", "",
      "| key | site | patch | verdict | wall s | class | probe baseline -> mutant |", "|---|---|---|---|---|---|---|"]
for k in keys:
    r, g = res.get(k, {}), gates.get(k, {})
    p = r.get("probe", {})
    md.append(f"| {k} | {r.get('site','')} | `{r.get('patch','')}` | {g.get('verdict','not gated')} | {g.get('wall_s','')} | "
              f"{r.get('class','')} | {p.get('baseline_value','')} -> {p.get('mutant_value','')} |")
md += ["", "## Survivors: the step-4 answer per key", ""]
for k in keys:
    r = res.get(k)
    if not r or r.get("class") == "killed":
        continue
    p = r["probe"]
    md += [f"### {k} — {r['site']} ({r['class']})", "",
           f"Patch `{r['patch']}` in `{r['function']}`. Gate: {r['gate']['verdict']}, gate_rc {r['gate']['gate_rc']}, "
           f"wall {r['gate']['wall_s']} s, load1 {r['gate']['load1_start']}..{r['gate']['load1_end']} (`{r['gate_command']}`).", "",
           f"Probe `{p['path']}` (`{p['command']}`), metric: {p['metric']}. Baseline **{p['baseline_value']}**, mutant "
           f"**{p['mutant_value']}**. Inputs tried: {'; '.join(p['inputs_tried'])}.", ""]
    if r["class"] == "candidate":
        f = r["finding"]
        md += [f"Candidate: {f['title']}. Should have failed: {r['should_fail']}. Class guess {f['class_guess']}, "
               f"severity claimed {f['severity_claimed']}; perturbation direction {f['perturbation']['expected_direction']} "
               f"({f['perturbation']['unit']}).", ""]
    else:
        md += [f"Equivalent-candidate (non-finding unless a later seat finds the input): {r['should_fail']}.", ""]
md += ["## Coverage", ""]
for c in coverage:
    md.append(f"- {c['step']}{' (carried from REPORT-D3-u1b.json)' if c.get('carried') else ''}: universe {c['universe']}, "
              f"examined {c['examined']}, not reached {len(c['not_reached'])}; enumerator `{c['enumerator']}`; redispatched {c['redispatched']}")
md += ["", f"D3.M3 not_reached: every other wave key by its box (D3-g02..D3-g47, {len([w for w in wave if w[0] != BOX])} keys), "
       "listed in REPORT.json.", "", "## Unfinished", ""]
md += [f"- {u['step']}: {u['what']}" for u in unfinished] or ["- none: all 16 keys gated and recorded; no TIMEOUT, STOP or SKIP."]
md += ["", "## Harnesses", ""] + [f"- {h}" for h in harnesses] + [""]
(W / "REPORT.md").write_text("\n".join(md))
rep["report_md"] = "\n".join(md)
(W / "REPORT.json").write_text(json.dumps(rep, indent=1) + "\n")
print(f"REPORT gated={len(gated_ok)} timeouts={len(timeouts)} ungated={len(ungated)} candidates={len(survivors)} "
      f"equiv={len(equiv)} killed={len(killed)} m3_not_reached={len(m3['not_reached'])} unfinished={len(unfinished)}")
