#!/usr/bin/env python3
"""Reviewer's own mutants for PR 3430 at d581d4e0b2e5fab662a2eb70b47b77b82ee5cc6e (builder: the fix reviewer, not the finder).
Each mutant edits one file of a scratch worktree, runs tests/doc_claims.py, records FAIL lines, restores."""
import subprocess, sys, os
from pathlib import Path
W = Path(sys.argv[1])
ENV = dict(os.environ, PYTHONPATH="tests/hastub")
def run():
    r = subprocess.run([sys.executable, "tests/doc_claims.py"], cwd=W, env=ENV, capture_output=True, text=True)
    out = [l.strip()[5:].split("  [")[0][:150] for l in r.stdout.splitlines() if l.strip().startswith("FAIL ")]
    return out or ([f"died rc={r.returncode}: {r.stderr.strip().splitlines()[-1][:140]}"] if r.returncode else [])
T = "tests/doc_claims.py"; D = "dev/README.md"
M = [
 # predicate-side, beyond the fixer's twelve
 ("P1 no-section guard", T, "    if at < 0:\n        return [f\"no {MACHINERY_HEADING!r} section\"]", "    if False:\n        return []"),
 ("P2 no-figure/no-rows guard", T, "    if fig is None or not rows:", "    if False:"),
 ("P3 entry excludes stores", T, 'if nodes[i][1] != "store" and all(b != n for _, _, b in drawn))', 'if all(b != n for _, _, b in drawn))'),
 ("P4 entry must be a seat", T, 'if len(entries) != 1 or kind[entries[0]][0] != "seat":', 'if len(entries) != 1:'),
 ("P5 arrow regex loses dashed", T, r'_M_ARROW = re.compile(r"-{2,}>|-\.+->|={2,}>|---|~~~|--[ox]")', r'_M_ARROW = re.compile(r"-{2,}>")'),
 ("P6 script-only actor-file rule widened off", T, 'if kind.get(a, ("", ""))[0] == "script" and path.rsplit', 'if kind.get(a, ("", ""))[0] == "seat" and path.rsplit'),
 ("P7 due check call dropped", T, "    due = due_marker_findings(rows)\n", "    due = []\n"),
 ("P8 live machinery check dropped", T, "    errs = machinery_edge_findings(text, _read_tracked(tree))\n", "    errs = []\n"),
 ("P9 marker regex matches nothing (relaxed anchors)", T, None, None),
 ("P10 wiring scope test only", T, 'for r in rows if r["due"] and r["scope"] == "wiring"]', 'for r in rows if r["due"]]'),
 ("P11 due test only", T, 'for r in rows if r["due"] and r["scope"] == "wiring"]', 'for r in rows if r["scope"] == "wiring"]'),
 # page-side: the live page under its own check
 ("D1 a quoted citation altered", D, "`tools/audit/seat/tick_loop.sh`: `bash \"$relay\" pass --confirm`", "`tools/audit/seat/tick_loop.sh`: `bash \"$relay\" pass --confirmed`"),
 ("D2 a table row removed", D, "| heartbeat.sh --once | writes | heartbeat ref | `tools/audit/seat/heartbeat.sh`: `\"$c:refs/heads/$REF\"` |\n", ""),
 ("D3 an arrow added with no row", D, '    hb -->|"writes"| hbref\n', '    hb -->|"writes"| hbref\n    watch -->|"writes"| hbref\n'),
 ("D4 a due marker planted on dev/README.md", D, "### The job graph\n", "### The job graph\n\n- the umbrella lands [target: R10-CI-LAYOUT-P2]\n"),
 ("D5 a due marker planted on docs/architecture.md", "docs/architecture.md", "## One owner per concern\n", "## One owner per concern\n\n- one owner [target: R10-PARAMS-OWNER]\n"),
 ("D6 arrow reversed with its row, re-cited to a real line of the other script", D, None, None),
 ("D7 a dashed arrow on the page", D, '    tloop -->|"runs"| relay\n', '    tloop -.->|"runs"| relay\n'),
 ("D8 a second mermaid block in the section with a reversed arrow", D, "Every arrow is one row here, with the line of code or contract that performs\n", "```mermaid\nflowchart TB\n    a[(\"store\")] --> b[\"x.py\"]\n```\n\nEvery arrow is one row here, with the line of code or contract that performs\n"),
 # cited-source side: the closure must carry it
 ("S1 the cited line removed from tick_loop.sh", "tools/audit/seat/tick_loop.sh", 'python3 "$HERE/merge_train.py" sweep', 'python3 "$HERE/merge_train.py"  sweep'),
 ("S2 the cited line removed from beat_jobs.py", "tools/audit/seat/beat_jobs.py", '"tools/audit/seat/roster_queue.py", "run"', '"tools/audit/seat/roster_queue.py",  "run"'),
]
base = run(); print(f"baseline: {len(base)} FAIL line(s) {base}")
surv = 0
for what, f, old, new in M:
    p = W / f; src = p.read_text()
    if what.startswith("P9"):
        import re
        m = re.search(r"^_MARKER = re\.compile\((.*)\)$", src, re.M)
        if not m: print(f"ERROR {what}: no _MARKER line"); continue
        old = m.group(0); new = '_MARKER = re.compile(r"\\[never-a-marker: ([^\\]]+)\\]")'
    if what.startswith("D6"):
        a_old = '    tloop -->|"runs"| relay\n'; a_new = '    relay -->|"runs"| tloop\n'
        r_old = '| tick_loop.sh | runs | cloud_relay.sh pass | `tools/audit/seat/tick_loop.sh`: `bash "$relay" pass --confirm` |'
        r_new = '| cloud_relay.sh pass | runs | tick_loop.sh | `tools/audit/seat/cloud_relay.sh`: `only the orchestrator writes or edits it` |'
        if src.count(a_old) != 1 or src.count(r_old) != 1: print(f"ERROR {what}: anchors {src.count(a_old)} {src.count(r_old)}"); continue
        mut = src.replace(a_old, a_new).replace(r_old, r_new)
    else:
        if src.count(old) != 1: print(f"ERROR {what}: anchor in file {src.count(old)} time(s)"); continue
        mut = src.replace(old, new)
    p.write_text(mut)
    try: got = run()
    finally: p.write_text(src)
    surv += not got
    print(f"{'killed  ' if got else 'SURVIVED'} {what}: {' ;; '.join(got[:3]) or '-'}")
print(f"RESULT rev_mutants={len(M)}"); print(f"RESULT rev_survivors={surv}")
