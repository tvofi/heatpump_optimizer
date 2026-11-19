#!/usr/bin/env python3
"""D3-s1: run build_report.py, then write REPORT.md and carry its text in REPORT.json's report_md
(run 1's subagent environment refused a .md write). Reads REPORT.json and state/ only."""
import json, subprocess, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
subprocess.run([sys.executable, str(HERE / "build_report.py")], cwd=ROOT, check=True)
r = json.loads((HERE / "REPORT.json").read_text())
tab = subprocess.run([sys.executable, str(HERE / "tabulate.py")], cwd=ROOT, capture_output=True, text=True).stdout
m4 = json.loads((HERE / "m4_answers.json").read_text())
L = ["# D3-s1 round 11 report (baseline 92d38ecb)", "",
     "Seat D3-s1, two runs. Run 1: box B1, local run on the orchestrator machine (macOS arm64), resumed after a reboot at "
     "about 17:40Z; contention load1 30-300 with other seats. Run 2: box D3R (Linux x86_64, nproc 4, Intel Xeon @ 2.10GHz, "
     "alone, load1 0.2-4.2), run inline in the box session: evidence restored (sha256 e2264708...), every driver's traced "
     "baseline re-taken, null and positive controls re-run, C3C6 M22 re-driven, U1 started; halted by orchestrator STOP "
     "(inbox command 1) after 4 U1 mutants.", "",
     "Verdicts and counts are contention-immune; every wall/CPU number is provisional.", "",
     "## Method", "",
     "Universe: tests/mutation_table.py unpinned inventory sites in the 12 cell files (enumerate.py --unpinned). "
     "Pre-screen (prescreen.py): each mutant driven over the fast scripts of its measured closure (recorded < 120 s) plus "
     "tests/env_drift.py --all against HEAD^1 (production byte-identical to the baseline); reach-skip by traced baselines. "
     "Survivors then go to a full-net complete (every closure script, no early stop). Null control LIVES; positive control 2/2 killed.", "",
     "## Coverage", ""]
for c in r["coverage"]:
    L.append(f"- {c['step']}: universe {c['universe']}, examined {c['examined']}, not reached {len(c['not_reached'])} item line(s). Enumerator: `{c['enumerator']}`")
L += ["", "## Findings", ""]
for f in r["findings"]:
    L.append(f"- {f['id']} ({f['step']}, {f['severity']}): {f['title']}")
L += ["", "## Pre-screen tables (tabulate.py)", "", "```", tab.strip(), "```", "",
      "## M4: the verifier's question per survivor", ""]
for k, v in m4.items():
    L.append(f"- `{k}`: {v}")
L += ["", "## Non-findings", ""]
for n in r["non_findings"]:
    L.append(f"- {n['claim']}: {n['value']} (`{n['command']}`)")
L += ["", "## Unfinished", ""]
for u in r["unfinished"]:
    L.append(f"- {u['step']}: {u['what']}")
L += ["", "## Redispatched (C1-C9)", ""]
for c in r["coverage"]:
    L.append(f"- {c['step']}: " + ", ".join(f"{x['item']} {x['state']}" for x in c["redispatched"]))
r["report_md"] = "\n".join(L) + "\n"
(HERE / "REPORT.json").write_text(json.dumps(r, indent=1) + "\n")
(HERE / "REPORT.md").write_text(r["report_md"])
print("RESULT report_md_lines=%d findings=%d" % (len(L), len(r["findings"])))
