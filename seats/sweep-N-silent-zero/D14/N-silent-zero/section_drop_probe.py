"""Probe for the D2 seams of tools/replay/debug_ingest.py (round 11, N-silent-zero sweep).

Drops one top-level bundle section at a time (as a download from an install whose recorder or
debugger was off carries it) and reads the tool's own verdict line. A section whose absence
still ends `smoke_verdict=pass` is an instance (a missing section reads as a clean one); a
section some sibling check fails on is guarded.

Run (repo root): PYTHONPATH=tests/hastub python3 section_drop_probe.py BUNDLE.json [WORKDIR]
Null control: the `none` row (nothing dropped) must pass.
"""
import json
import pathlib
import subprocess
import sys

src = pathlib.Path(sys.argv[1])
work = pathlib.Path(sys.argv[2] if len(sys.argv) > 2 else "/tmp/sz_sections")
work.mkdir(parents=True, exist_ok=True)
doc = json.loads(src.read_text())
root = doc.get("data") if isinstance(doc.get("data"), dict) else doc
blind = 0
for sec in ["none"] + sorted(root):
    d = json.loads(src.read_text())
    r = d.get("data") if isinstance(d.get("data"), dict) else d
    if sec != "none":
        r.pop(sec)
    p = work / f"drop_{sec}.json"
    p.write_text(json.dumps(d))
    out = subprocess.run([sys.executable, "tools/replay/debug_ingest.py", "--bundle", str(p)],
                         capture_output=True, text=True, stdin=subprocess.DEVNULL)
    stages = [l.split()[1] for l in out.stdout.splitlines() if l.startswith("RESULT stages_ok")]
    verdict = "pass" if "smoke_verdict=pass" in out.stdout else ("fail" if out.returncode == 1 else f"crash(rc={out.returncode})")
    if sec != "none" and verdict == "pass":
        blind += 1
    print(f"DROP {sec:14s} verdict={verdict} {' '.join(stages)}", flush=True)
print(f"RESULT sections_dropped_still_pass={blind} unit=count")
