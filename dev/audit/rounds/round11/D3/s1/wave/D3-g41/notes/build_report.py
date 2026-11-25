#!/usr/bin/env python3
"""REPORT.json / REPORT.md for box D3-g41 (seat D3-s1, round 11) from results/*.json, gates/*.json and notes/."""
import json, sys
from pathlib import Path
S1 = Path(sys.argv[1]); W = S1 / "wave" / "D3-g41"
REL = "dev/audit/rounds/round11/D3/s1/wave/D3-g41"; BASE = "92d38ecb640bd462f2e19c0814d0f0b7df1ee692"
PY = "PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3"
u1b = json.loads((S1 / "REPORT-D3-u1b.json").read_text())
keys = [l.split("\t") for l in (W / "keys.tsv").read_text().splitlines()[1:] if l.strip()]
null = json.loads((W / "gates" / "null.json").read_text())
R = {k[0]: json.loads((W / "results" / f"{k[0]}.json").read_text()) for k in keys if (W / "results" / f"{k[0]}.json").exists()}
G = {k[0]: json.loads((W / "gates" / f"{k[0]}.json").read_text()) for k in keys if (W / "gates" / f"{k[0]}.json").exists()}
machine = "box D3-g41: nproc 4, Intel(R) Xeon(R) Processor @ 2.30GHz, 16 GB, no swap (MACHINE.txt); wall/CPU/load provisional"
cov = []
for row in u1b["coverage"]:
    if row["step"] == "D3.M3":
        timeouts = [k for k, g in G.items() if g.get("verdict") == "TIMEOUT"]
        gated = [k for k, g in G.items() if g.get("verdict") != "TIMEOUT"]
        nr = [f"assigned to box D3-g{n:02d}" for n in range(1, 48) if n != 41]
        nr += [f"TIMEOUT on box D3-g41 (cap 14400 s): {k}" for k in timeouts]
        nr += [f"not yet gated on box D3-g41: {k[0]}" for k in keys if k[0] not in G]
        cov.append({"step": "D3.M3", "enumerator": "awk -F'\\t' '$6==\"gate\"' SURVIVORS.tsv", "universe": 742,
                    "examined": len(gated), "not_reached": nr, "redispatched": row["redispatched"],
                    "evidence": (f"box D3-g41's 15 keys ({REL}/keys.tsv), each `python3 dev/audit/rounds/round11/D3/s1/fullgate.py run --src complete --key <key>` "
                                 f"(GATE_SCOPE=full GOLDEN_MODE=drift GOLDEN_REF={BASE} GATE_JOBS=1 ./tests/run.sh), records {REL}/gates/<key>.json; "
                                 f"null {REL}/gates/null.json (gate_rc {null['gate_rc']}, red {null['failed_scripts']}). "
                                 "The other 727 wave keys are named by box only: SURVIVORS.tsv was not shipped to this box (dispatch tip holds keys.tsv only). "
                                 "Redispatched C-items carried verbatim from REPORT-D3-u1b.json. The earlier boxes' D3.M3 rows (D3-u1a..d full net, D3-top6, D3-rem full gates) stand in their own reports.")})
    else:
        r = dict(row); r["evidence"] = "carried verbatim from REPORT-D3-u1b.json: " + row["evidence"]; cov.append(r)
gated_rows, surv, equiv, nonf, unfinished, leads = [], [], [], [], [], []
for k in keys:
    key = k[0]; r = R.get(key); g = G.get(key, {})
    gated_rows.append({"key": key, "site": f"{k[2]}:{k[3]} {k[8]}", "verdict": g.get("verdict", "NOT-GATED"),
                       "killed_by": g.get("killed_by", []), "class": (r or {}).get("class", "unfinished")})
    if not r:
        unfinished.append({"step": "D3.M3", "what": f"{key} ({k[2]}:{k[3]}): no gate record on this box"}); continue
    if r["class"] == "candidate": surv.append(r)
    elif r["class"] == "equivalent-candidate":
        equiv.append(r)
        nonf.append({"claim": f"equivalent-candidate {key} {r['site']} ({r['patch']}): survives the full gate ({g['verdict']}) and its probe cannot move the number",
                     "command": r["probe"]["command"], "value": f"{r['probe']['metric']}: baseline {r['probe']['baseline_value']}, mutant {r['probe']['mutant_value']}; inputs: {r['probe']['inputs_tried']}"})
    elif r["class"] == "killed":
        nonf.append({"claim": f"killed {key} {r['site']} ({r['patch']}): the full gate fails on it beyond the null; " + r.get("kill_mechanism", ""),
                     "command": r["gate_command"], "value": f"verdict KILLED, killed_by {g['killed_by']}, gate_rc {g['gate_rc']}, wall {g.get('wall_s')} s; " + "; ".join(r.get("failing_check_lines", [])[:2])})
        if r.get("lead"):
            leads.append({"owner_seat": "D3-s1", "file": k[2], "symbol": k[4], "what": r["lead"] + f" (probe {r['probe']['path']}: {r['probe']['metric']} baseline {r['probe']['baseline_value']}, mutant {r['probe']['mutant_value']})"})
    elif r["class"] == "timeout":
        unfinished.append({"step": "D3.M3", "what": f"{key} {r['site']}: TIMEOUT at the 14400 s cap, last script {r.get('last_script')}"})
nonf.insert(0, {"claim": "null control: the unmutated baseline (comment-only marker) under the same full gate on this box",
                "command": "python3 dev/audit/rounds/round11/D3/s1/fullgate.py null",
                "value": f"gate_rc {null['gate_rc']}, red {null['failed_scripts']} (tree/host artefacts, subset of state/gates-prior/null.json), wall {null.get('wall_s')} s, load1 {null.get('load1_start')}->{null.get('load1_end')} (provisional)"})
probes = sorted(f"{REL}/probes/{p.name}" for p in (W / "probes").glob("probe_*.py"))
rep = {"dimension": "D3", "baseline_sha": BASE, "box": "D3-g41", "report_path": f"{REL}/REPORT.md",
       "exposure": ("Read: COMMON.md, D3.md, dev/audit/README.md, the u1 slice reports, REPORT-D3-top6/rem, the M4 answer files for this box's keys, "
                    "state/reach.tsv, state/results/complete/<key>.json, production code at the 15 sites and their callers, tests/features.py around the "
                    "batch-parity and cap-twin checks. Not read: the register, round11/J, any verifier report, docs/, GitHub. Probes ran in a separate "
                    "baseline worktree, never in the gate's tree."),
       "coverage": cov, "unfinished": unfinished, "findings": [], "non_findings": nonf,
       "harnesses": ["dev/audit/rounds/round11/D3/s1/fullgate.py"] + probes, "leads": leads,
       "gated": gated_rows, "gate_survivors": surv, "equivalent_candidates": equiv}
(W / "REPORT.json").write_text(json.dumps(rep, indent=1) + "\n")
from collections import Counter
v = Counter(r["verdict"] for r in gated_rows); c = Counter(r["class"] for r in gated_rows)
kb = Counter(s for r in gated_rows for s in r["killed_by"])
md = [f"# D3-s1 box D3-g41 — full gate for 15 D3.M3 full-net survivors (round 11)", "",
      f"Baseline `{BASE}`. Seat D3-s1, dimension D3, step D3.M3 wave (owner ruling 2026-11-22: every u1 full-net survivor gets the full gate).", "",
      "## Machine and controls", "", f"- {machine}.",
      f"- Procedure: gate_wave.sh (dispatch tip, out of tree) runs `fullgate.py run --src complete --key <key>` per key of keys.tsv, one gate at a time, GATE_JOBS=1, cap 14400 s; each gate applies the one-line mutant, commits, takes the gate_lock lease, runs `GATE_SCOPE=full GOLDEN_MODE=drift GOLDEN_REF={BASE} GATE_JOBS=1 ./tests/run.sh`, records, and resets to the baseline.",
      f"- Null control: `fullgate.py null` — gate_rc {null['gate_rc']}, red {', '.join(null['failed_scripts'])}; wall {null.get('wall_s')} s. These are tree/host artefacts (a subset of the earlier boxes' null, which also had optimality.py and stress.py red); harness_headers.py's inlined-walk check also names this box's probes, so the probe files stayed byte-frozen in the gate tree for the whole wave. A key is KILLED only when a script beyond the null is red (or a null script gains FAIL lines).", "",
      "## Tally", "",
      f"- Gated: {sum(1 for r in gated_rows if r['verdict'] not in ('NOT-GATED',))} of 15. Verdicts: " + ", ".join(f"{k} {n}" for k, n in sorted(v.items())) + ".",
      f"- KILLED by: " + (", ".join(f"{s} ({n})" for s, n in kb.items()) or "none") + ".",
      f"- Classes: " + ", ".join(f"{k} {n}" for k, n in sorted(c.items())) + ". Findings: none numbered here (the consolidation step assigns ids); candidates are under `gate_survivors`.", "",
      "| key | site | verdict | killed by | class | probe metric: baseline -> mutant |", "|---|---|---|---|---|---|"]
for row in gated_rows:
    r = R.get(row["key"], {}); p = r.get("probe", {})
    md.append(f"| {row['key']} | {row['site']} | {row['verdict']} | {', '.join(row['killed_by']) or '-'} | {row['class']} | {p.get('metric', '-')}: {p.get('baseline_value', '-')} -> {p.get('mutant_value', '-')} |")
md += ["", "## Survivors: step-4 answers with probe numbers", ""]
for k in keys:
    r = R.get(k[0])
    if not r or r["class"] not in ("candidate", "equivalent-candidate"): continue
    p = r["probe"]
    md.append(f"**{k[0]}** `{r['site']}` (`{r['patch']}`), {r['function']}; gate {r['gate']['verdict']} (gate_rc {r['gate']['gate_rc']}, wall {r['gate']['wall_s']} s). "
              f"Class **{r['class']}**. Probe `{p['path']}`: {p['metric']} baseline {p['baseline_value']}, mutant {p['mutant_value']}. Inputs: {p['inputs_tried']}. "
              f"Should fail: {r['should_fail']}." + (f" Claimed severity {r['severity_claimed']}: {r['claim']}" if r['class'] == 'candidate' else ""))
    md.append("")
md += ["## Non-findings", ""] + [f"- {n['claim']} — `{n['command']}` — {n['value']}" for n in nonf]
md += ["", "## Leads", ""] + ([f"- {l['file']} {l['symbol']}: {l['what']}" for l in leads] or ["- none"])
md += ["", "## Unfinished", ""] + ([f"- {u['what']}" for u in unfinished] or ["- none"])
md += ["", "## Harnesses", "", "- dev/audit/rounds/round11/D3/s1/fullgate.py (gate driver), gate_wave.sh's procedure above (out of tree, dispatch tip)"] + [f"- {p}" for p in probes]
md += ["", "Coverage: D3.M1, D3.M2, D3.M4, D3.M5 rows carried verbatim from REPORT-D3-u1b.json; D3.M3 is this wave's row (universe 742; other boxes named by id because SURVIVORS.tsv was not shipped to this box).", ""]
(W / "REPORT.md").write_text("\n".join(md))
print("REPORT", dict(v), dict(c))
