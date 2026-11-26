#!/usr/bin/env python3
# D3 wave judge instrument, round 11. Run from the repository root of a checkout of the baseline
# 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 with dev/audit/rounds/round11/D3/ copied over it (git fetch the handoff ref first):
#   PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/wave-judge/harness/render.py
# Order: build_master, rerun, gatecmp, cross, analyse, dedup, compose, render. Writes only under $JUDGE_DIR and $TMPDIR.
"""Render JUDGE.md, the class sweep and the issue drafts (ISSUES.json) from JUDGE.json.
One class (I1) carries every survivor; the drafts are cut by owning production file, the seam a tests-only fix
lands in, each naming the existing class issue (#3755) so the filer appends rather than opens a second [R11-I1]."""
import os, json, sys, pathlib, collections
WORK = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".")
J = json.load(open(WORK / "JUDGE.json"))
extra = json.load(open(WORK / "md_extra.json")) if (WORK / "md_extra.json").exists() else {}
V = J["verdicts"]
SUR = [v for v in V if v["verdict"] in ("verified", "weakened")]
SEVR = ["nit", "low", "medium", "high", "critical"]
cnt = collections.Counter(v["verdict"] for v in V)
sev = collections.Counter(v["severity"] for v in SUR)
byfile = collections.defaultdict(list)
for v in SUR:
    byfile[v["site"].split(":")[0]].append(v)
L = []
L.append("# Audit round 11, D3 u1 full-gate wave: judge record")
L.append("")
L.append(extra.get("intro", ""))
L.append("")
L.append(f"Findings judged: {len(V)}. Verdicts: " + ", ".join(f"{k} {cnt[k]}" for k in ("verified", "weakened", "refuted", "unreproduced", "merged") if cnt[k]) + ".")
L.append(f"Canonical after dedup: {len(V) - cnt['merged']}. Survivor severities: " + ", ".join(f"{s} {sev[s]}" for s in reversed(SEVR) if sev[s]) + ".")
L.append("")
for sec in extra.get("sections", []):
    L.append(f"## {sec['title']}")
    L.append("")
    L += sec["lines"]
    L.append("")
L.append("## Class sweep")
L.append("")
L.append(f"Every survivor is class I1 ({V[0]['class_mechanism'] if V else ''}): {len(SUR)} judged instances this round in this unit. "
         "The enumerator is the wave itself, so no seam lies beyond a finding (beyond_finding 0); RCA: owed (N >= 3, defect-root-cause.md), "
         "already owed under the class's open issue #3755.")
L.append("")
L.append("| file | survivors | boundary | guard | clamp | constant | high | medium | low | nit |")
L.append("|---|---|---|---|---|---|---|---|---|---|")
for fn in sorted(byfile, key=lambda f: -len(byfile[f])):
    vs = byfile[fn]; gk = collections.Counter(v["gap_kind"] for v in vs); sv = collections.Counter(v["severity"] for v in vs)
    L.append(f"| {fn} | {len(vs)} | {gk['boundary']} | {gk['guard']} | {gk['clamp']} | {gk['constant']} | {sv['high']} | {sv['medium']} | {sv['low']} | {sv['nit']} |")
L.append("")
L.append("## Verdicts")
L.append("")
L.append("| id | site | verdict | severity | stop | class | value |")
L.append("|---|---|---|---|---|---|---|")
for v in V:
    if v["verdict"] == "merged":
        L.append(f"| {v['id']} | {v['site']} | merged | | | | {v['note'][:260]} |")
    else:
        L.append(f"| {v['id']} | {v['site']} | {v['verdict']} | {v['severity']} | {v['stop_rule_class']} | {v['class']} | {str(v['value'])[:260].replace('|', '/')} |")
(WORK / "JUDGE.md").write_text("\n".join(L) + "\n")

issues = []
for fn in sorted(byfile, key=lambda f: -len(byfile[f])):
    vs = sorted(byfile[fn], key=lambda v: (-SEVR.index(v["severity"]), v["site"]))
    top = vs[0]["severity"]
    gk = collections.Counter(v["gap_kind"] for v in vs)
    b = [f"## Class I1, unit D3 u1 full-gate wave: `custom_components/heatpump_optimizer/{fn}`", "",
         f"Mechanism: {vs[0]['class_mechanism']}.", "",
         f"Class issue: #3755 (open). {len(vs)} production mutants in this file survive the full gate (GATE_SCOPE=full GOLDEN_MODE=drift, "
         "red only on the box null's own three scripts, with no failing-check line beyond the null), and each one's probe moves under the one-line mutant. "
         f"Gap kinds: " + ", ".join(f"{k} {n}" for k, n in gk.most_common()) + ".", "",
         "Fix scope: tests only. A check per row, at the probe's distinguishing input, that pins the baseline value; "
         "mutation proof: the row's mutant must turn the new check red. Probes: `dev/audit/rounds/round11/D3/s1/wave/<box>/probes/probe_<key>.py`.", "",
         "| id | site | mutant | severity | verdict | judge number |", "|---|---|---|---|---|---|"]
    mg = collections.defaultdict(list)
    for x in V:
        if x["verdict"] in ("merged",):
            mg[x["into"]].append(x["id"])
    for v in vs:
        tail = f"; merged here: {', '.join(mg[v['id']])}" if mg.get(v["id"]) else ""
        b.append(f"| {v['id']} | {v['site']} | `{v['patch'][:90].replace('|', '/')}` | {v['severity']} | {v['verdict']} | {str(v['value'])[:180].replace('|', '/')}{tail} |")
    b += ["", "Enumerator: `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/fullgate.py run --src complete --key <key>` per key (the wave), "
          "probe re-run `dev/audit/rounds/round11/D3/wave-judge/harness/rerun.py`.",
          f"RCA: owed (N={len(SUR)} in this unit; class I1, defect-root-cause.md)."]
    issues.append({"class": "I1", "file": f"custom_components/heatpump_optimizer/{fn}", "existing_class_issue": 3755,
                   "title": f"[R11-I1] D3 wave: {len(vs)} mutant{'s' if len(vs) > 1 else ''} in {fn} survive{'' if len(vs) > 1 else 's'} the full gate",
                   "labels": ["audit", "round-11", "class:I1", f"sev:{top}"], "findings": [v["id"] for v in vs], "body": "\n".join(b) + "\n"})
json.dump(issues, open(WORK / "ISSUES.json", "w"), indent=1)
print(len(issues), "drafts;", dict(cnt), dict(sev))
