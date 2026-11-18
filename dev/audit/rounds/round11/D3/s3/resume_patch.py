#!/usr/bin/env python3
"""Post-crash patch of REPORT.json (seat D3-s3, 2026-11-17 reboot ~17:40Z).
The per-pair pre-screen records (prescreen_local.*, prescreen_cheap.*) lived in
the scratch clone under /private/tmp and were lost to the reboot. This records
that, keeps every finished result whose output file exists, and lists the 38
pool sites as not_reached with the load and CPU-share numbers at 17:50Z.
Command: python3 dev/audit/rounds/round11/D3/s3/resume_patch.py (after
build_report_local.py)."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
LOAD = ("load1 46.2 / load5 153.4 at 17:50Z (9 min after reboot), 8 cores: "
        "CPU share per runnable ~0.17 core; during the run load1 40-226, swap 3.6/4 GB")
r = json.loads((HERE / "REPORT.json").read_text())
pool = [ln.split("#")[0].strip()
        for ln in (HERE / "selection_local.txt").read_text().splitlines()
        if ln.split("#")[0].strip()]
m4 = json.loads((HERE / "m4_answers.json").read_text())
LOST = ("Per-pair verdicts lost: prescreen_local.json/.progress.jsonl and prescreen_cheap.* were in the "
        "scratch clone under /private/tmp, cleared by the machine reboot at ~17:40Z. Attempt 3 (null control "
        "survived every driver, mutants from ~13:59Z) and the cheap-subset screen (from 16:24Z) produced "
        "verdicts that cannot be reported. The only verdict in the progress log, away.py:177 'killed' by "
        "entities.py at 16:58:57Z, fell in the ENOSPC window (~16:57Z) and is suspect, so it is not counted. "
        "examined=0 is the honest count.")
for c in r["coverage"]:
    if c["step"] == "D3.M2":
        c["examined"] = 0
        c["not_reached"] = [f"{s} (pool; {LOAD})" for s in pool] + c["not_reached"]
        c["evidence"] += " RESUME: " + LOST
    if c["step"] in ("D3.M3", "D3.M4"):
        c["enumerator"] = ("python3 dev/audit/rounds/round11/D3/s3/prescreen_table.py --survivors "
                           "(records lost; m4_answers.json names the two survivor candidates recorded before the crash)")
        c["universe"] = len(m4)
        c["examined"] = 0 if c["step"] == "D3.M3" else len(m4)
        c["not_reached"] = list(m4) if c["step"] == "D3.M3" else []
        c["evidence"] += (" RESUME: survivor status of " + ", ".join(m4) + " is unconfirmed (records lost); "
                          "away.py:177's entities.py kill is suspect (ENOSPC window). The M4 answers are kept as provisional.")
r["m4_answers"] = {
    k: dict(v, status=("provisional: pre-screen record lost; kill at 16:58:57Z suspect"
                       if k.startswith("away") else "provisional: pre-screen record lost"))
    for k, v in m4.items()}
r["unfinished"].insert(0, {
    "step": "D3.M2",
    "what": "Re-run the 38-site pool pre-screen (selection_local.txt) on a quiet box. " + LOST +
            " Keep the records inside the worktree, not under /private/tmp."})
r["unfinished"].append({
    "step": "D3.M3/M4",
    "what": "Confirm survival of away.py:177 GUARD_OFF and boost.py:595 CMP_BOUND against the full closure "
            "(features.py, entities.py), then run the quiet-window full gate."})
for f in r["findings"]:
    note = f.get("contention_note", "")
    if "reboot" not in note:
        note += (" Another D3 seat and verifier seats ran on this machine; wall/CPU numbers are provisional. "
                 "Harness outputs predate the 17:40Z reboot and are kept because their files exist.")
    f["contention_note"] = note.strip()
md = ["# D3-s3 REPORT (round 11, box B3, local re-run)", "", f"Findings: {len(r['findings'])}"]
md += [f"- {f['id']} ({f['severity']}): {f['title']}" for f in r["findings"]]
md += ["", "D3-s3-03 is keyed to the 60 main-process repeats. Box B3's total of 113 (60 main + 53 worker "
       "repeats) is a stated difference, not the key.", "", "## Crash", LOST, "", "## Unfinished"]
md += [f"- {u['step']}: {u['what']}" for u in r["unfinished"]]
md += ["", "## Not reached (M2 pool)", f"All 38 pool sites; {LOAD}.", ""] + [f"- {s}" for s in pool]
r["report_md"] = "\n".join(md) + "\n"
(HERE / "REPORT.json").write_text(json.dumps(r, indent=1))
try:
    (HERE / "REPORT.md").write_text(r["report_md"])
except OSError as e:
    print("REPORT.md refused:", e)
print("findings", len(r["findings"]), "unfinished", len(r["unfinished"]))
