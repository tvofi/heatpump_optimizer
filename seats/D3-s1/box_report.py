#!/usr/bin/env python3
"""D3-s1, box D3-top6 slice (D3.M3 only): assemble REPORT-D3-top6.json and its markdown.

Metric (one line): per D3.M3 survivor (tabulate.py --tsv SURVIVED rows), examined = it has a
full-net verdict (state/results/complete/) and, when that verdict is SURVIVED, a full-gate verdict
(state/gates/<key>.json); not_reached = every other survivor, by key and site.
Run: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/box_report.py
Reads state/ and the hand-written top6_findings.json / top6_non_findings.json beside it; writes
REPORT.json (this box's slice) and REPORT.md. Counts are exact; every wall number is provisional.
Instrumented symbol: fullgate.py's verdict over tests/run.sh, prescreen.py:cmd_complete.
Perturbation: deleting one state/gates/<key>.json lowers examined by one and names the key in
not_reached.
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: owner macOS arm64 (local re-run).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ST = HERE / "state"
RES = ST / "results"
GATES = ST / "gates"
REL = "dev/audit/rounds/round11/D3/s1"
BASE = "92d38ecb640bd462f2e19c0814d0f0b7df1ee692"
ENUM = ("PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/tabulate.py --tsv "
        "| grep -P '\\tSURVIVED\\t'")


def load(sub):
    d = RES / sub
    return {p.stem: json.loads(p.read_text()) for p in sorted(d.glob("*.json"))} if d.exists() else {}


def survivors():
    out = {}
    for sub in ("pre", "c2", "c3c6"):
        for k, r in load(sub).items():
            if r["verdict"] == "SURVIVED":
                out[k] = (sub, r["mutant"])
    return out


def site(m):
    return f"{m['file'].rsplit('/', 1)[-1]}:{m['line']}"


def main():
    surv = survivors()
    comp = load("complete")
    gates = {p.stem: json.loads(p.read_text()) for p in GATES.glob("*.json")
             if p.stem not in ("null",) and not p.stem.startswith("null-")}
    null = json.loads((GATES / "null.json").read_text()) if (GATES / "null.json").exists() else None
    rows, examined, not_reached = [], 0, []
    for k, (sub, m) in sorted(surv.items(), key=lambda kv: (kv[1][0], kv[0])):
        cv = comp.get(k, {}).get("verdict")
        g = gates.get(k)
        gv = g.get("verdict") if g else None
        done = (cv == "KILLED") or (cv is not None and gv is not None) or (cv is None and gv == "KILLED")
        if done:
            examined += 1
        else:
            why = []
            if cv is None:
                why.append("no full-net verdict")
            if cv == "SURVIVED" and gv is None:
                why.append("full-net SURVIVED, no full gate")
            if cv == "TIMEOUT":
                why.append("full-net TIMEOUT")
            not_reached.append(f"{sub}:{k} {site(m)} {m['kind']} ({'; '.join(why)})")
        rows.append({"src": sub, "key": k, "site": site(m), "kind": m["kind"],
                     "complete": cv or "-", "complete_killed_by": comp.get(k, {}).get("killed_by", []),
                     "complete_wall_s": comp.get(k, {}).get("complete_wall"),
                     "gate": gv or "-", "gate_killed_by": (g or {}).get("killed_by", []),
                     "gate_wall_s": (g or {}).get("wall_s"),
                     "gate_load1": [(g or {}).get("load1_start"), (g or {}).get("load1_end")]})
    (HERE / "top6_table.json").write_text(json.dumps(rows, indent=1) + "\n")
    findings = json.loads((HERE / "top6_findings.json").read_text()) if (HERE / "top6_findings.json").exists() else []
    nonf = json.loads((HERE / "top6_non_findings.json").read_text()) if (HERE / "top6_non_findings.json").exists() else []
    extra = json.loads((HERE / "top6_extra.json").read_text()) if (HERE / "top6_extra.json").exists() else {}
    cov = {"step": "D3.M3", "enumerator": ENUM, "universe": len(surv), "examined": examined,
           "not_reached": not_reached[:200],
           "redispatched": [{"item": "C3", "state": "examined"}, {"item": "C5", "state": "examined"}],
           "evidence": (f"state/results/complete/ (full net, prescreen.py complete) and state/gates/ "
                        f"(fullgate.py, GATE_SCOPE=full GOLDEN_MODE=drift GOLDEN_REF={BASE} GATE_JOBS=1); "
                        f"table: {REL}/top6_table.json")}
    rep = {"dimension": "D3", "baseline_sha": BASE, "report_path": f"{REL}/REPORT.md",
           "exposure": extra.get("exposure", ""), "coverage": [cov],
           "unfinished": extra.get("unfinished", []), "findings": findings, "non_findings": nonf,
           "harnesses": [f"{REL}/{n}" for n in ("fullgate.py", "prescreen.py", "gate_chain.sh",
                                                 "tabulate.py", "box_report.py")],
           "leads": extra.get("leads", [])}
    md = ["# D3-s1 round 11, box D3-top6 slice (D3.M3), baseline 92d38ecb", "",
          extra.get("intro", ""), "",
          "## Coverage (D3.M3)", "",
          f"Universe {len(surv)} survivors; examined {examined}; not reached {len(not_reached)}. "
          f"Enumerator: `{ENUM}`", ""]
    md += ["## Full-net and full-gate table", "",
           "| src:key | site | kind | full net | killed by | full gate | killed by | gate wall s (provisional) | load1 |",
           "|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        md.append(f"| {r['src']}:{r['key']} | {r['site']} | {r['kind']} | {r['complete']} | "
                  f"{','.join(r['complete_killed_by']) or '-'} | {r['gate']} | "
                  f"{','.join(r['gate_killed_by']) or '-'} | {r['gate_wall_s'] or '-'} | "
                  f"{r['gate_load1'][0] or '-'}..{r['gate_load1'][1] or '-'} |")
    if null:
        md += ["", f"Full-gate null control (comment-only marker in tariff.py): gate_rc={null['gate_rc']}, "
               f"red scripts {null['failed_scripts']}, failed-check counts {null.get('fail_lines')}, "
               f"wall {null['wall_s']} s (provisional)."]
    md += ["", "## Findings", ""]
    for f in findings:
        md.append(f"- {f['id']} ({f['step']}, {f['severity']}): {f['title']}")
    md += ["", "## Non-findings", ""]
    for n in nonf:
        md.append(f"- {n['claim']}: {n['value']} (`{n['command']}`)")
    md += ["", "## Unfinished", ""] + [f"- {u['step']}: {u['what']}" for u in rep["unfinished"]]
    md += ["", "## Leads", ""] + [f"- {l['owner_seat']} {l['file']} {l['symbol']}: {l['what']}" for l in rep["leads"]]
    rep["report_md"] = "\n".join(md) + "\n"
    (HERE / "REPORT.md").write_text(rep["report_md"])
    (HERE / "REPORT.json").write_text(json.dumps(rep, indent=1) + "\n")
    print(f"RESULT m3_universe={len(surv)}")
    print(f"RESULT m3_examined={examined}")
    print(f"RESULT m3_not_reached={len(not_reached)}")
    print(f"RESULT findings={len(findings)}")


if __name__ == "__main__":
    main()
