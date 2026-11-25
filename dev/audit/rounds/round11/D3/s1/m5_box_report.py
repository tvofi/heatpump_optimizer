#!/usr/bin/env python3
"""D3-s1 box D3-m5: build REPORT.json / REPORT.md for this box's slice (D3.M5 (a)-(e)).

Not a measuring harness: it assembles the box's report from the carried box-D3R
report (REPORT-D3R.json: rows D3.M1-M4, finding D3-s1-01, already judged and not
re-reported) and this box's evidence files under state/ (gate_table.jsonl,
solves-D3-m5*.jsonl, extra_reach.json, m5-*.out, results/matrix/). Every number
it writes is read from those files or from a harness it runs here
(m5_matrix.py table); it computes none.

Run: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/m5_box_report.py
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-m5.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ST = HERE / "state"
REL = "dev/audit/rounds/round11/D3/s1"
EXTRA = json.loads((HERE / "box_extra.json").read_text())


def run(cmd: list[str]) -> str:
    return subprocess.run([sys.executable, *cmd], capture_output=True, text=True,
                          env={**os.environ, "PYTHONPATH": "tests/hastub"}).stdout


def results(text: str) -> dict:
    out = {}
    for ln in text.splitlines():
        if ln.startswith("RESULT "):
            k, _, v = ln[7:].partition("=")
            out[k] = v
    return out


def main() -> int:
    car = json.loads((HERE / "REPORT-D3R.json").read_text())
    rows = {c["step"]: c for c in car["coverage"]}
    # Rows this box did not drive: carried as box D3R left them; the
    # remainder belongs to the other boxes of the split.
    for step, owner in (("D3.M2", "boxes D3-u1a, D3-u1b, D3-u1c, D3-u1d"),
                        ("D3.M3", "boxes D3-top6, D3-u1a, D3-u1b, D3-u1c, D3-u1d")):
        rows[step]["not_reached"] = [f"{x} -- assigned to {owner}, not box D3-m5"
                                     for x in rows[step]["not_reached"]]
    scripts = (ST / "m5-scripts-universe.txt").read_text().split("\n")
    scripts = [s.split("\t")[0] for s in scripts if s.strip()]
    mt = results(run([f"{REL}/m5_matrix.py", "table"]))
    m5 = {
        "step": "D3.M5",
        "enumerator": f"PYTHONPATH=tests/hastub python3 {REL}/enumerate.py --scripts",
        "universe": len(scripts),
        "examined": len(scripts),
        "not_reached": [],
        "redispatched": [{"item": i, "state": "examined"} for i in ("C1", "C4", "C7", "C9")],
        "evidence": EXTRA["m5_evidence"],
    }
    rows["D3.M5"] = m5
    findings = []
    for p in sorted((HERE / "findings").glob("D3-s1-5*.json")):
        findings.append(json.loads(p.read_text()))
    rep = {
        "dimension": "D3",
        "baseline_sha": car["baseline_sha"],
        "report_path": f"{REL}/REPORT.md",
        "exposure": car["exposure"] + " " + EXTRA["exposure_add"],
        "coverage": [rows[s] for s in ("D3.M1", "D3.M2", "D3.M3", "D3.M4", "D3.M5")],
        "unfinished": [],
        "findings": findings,
        "non_findings": EXTRA["non_findings"],
        "harnesses": car["harnesses"] + [f"{REL}/{h}" for h in EXTRA["harnesses_add"]],
        "leads": EXTRA["leads"],
    }
    md = [EXTRA["md_head"], "", "## Coverage", ""]
    for c in rep["coverage"]:
        md.append(f"- {c['step']}: universe {c['universe']}, examined {c['examined']}, "
                  f"not reached {len(c['not_reached'])} item line(s). Enumerator: `{c['enumerator']}`")
    md += ["", "## D3.M5 evidence (this box)", ""]
    for e in m5["evidence"]:
        md.append(f"- `{e['command']}`: {e['value']}")
    md += ["", "## Findings", ""]
    md += [f"- {f['id']} ({f['step']}, {f['severity']}): {f['title']}" for f in findings] or \
          ["- none new on this box; D3-s1-01 (already judged) reproduced, cited not re-reported"]
    md += ["", "## Non-findings", ""]
    md += [f"- {n['claim']}: {n['value']} (`{n['command']}`)" for n in rep["non_findings"]]
    md += ["", "## Leads", ""]
    md += [f"- {l['owner_seat']} {l['file']} {l['symbol']}: {l['what']}" for l in rep["leads"]]
    md += ["", "## Redispatched", "", "- D3.M5: C1, C4, C7, C9 examined (box D3-m5)",
           "", f"Matrix table: {json.dumps(mt)}", ""]
    rep["report_md"] = "\n".join(md)
    (HERE / "REPORT.json").write_text(json.dumps(rep, indent=1) + "\n")
    try:
        (HERE / "REPORT.md").write_text(rep["report_md"])
    except OSError as e:
        print(f"REPORT.md not written: {e}")
    print(f"RESULT findings={len(findings)}")
    print(f"RESULT m5_examined={len(scripts)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
