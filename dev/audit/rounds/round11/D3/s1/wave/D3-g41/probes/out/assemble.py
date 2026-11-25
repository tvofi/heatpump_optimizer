import sys
from pathlib import Path
sp = Path(sys.argv[1]); out = Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
pre = (sp / "pre.py").read_text()
common = (sp / "b" / "_tm_common.txt").read_text()
for f in sorted((sp / "b").glob("*.py")):
    key = f.stem
    lines = f.read_text().splitlines()
    hdr = [l[3:] for l in lines if l.startswith("#H ")]
    body = [l for l in lines if not l.startswith("#H ")]
    body = "\n".join(common if l.strip() == "#INCLUDE _tm_common.txt" else l for l in body)
    p = f"dev/audit/rounds/round11/D3/s1/wave/D3-g41/probes/probe_{key}.py"
    head = ["#!/usr/bin/env python3", f"# Probe for D3.M3 full-gate survivor {key} (box D3-g41, round 11, seat D3-s1)."]
    ix = next(i for i, h in enumerate(hdr) if h.startswith("EXPECTED"))
    head += ["# " + h for h in hdr[:ix]]
    head.append(f"# Command (from the tree root): PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 {p}")
    head += ["# " + h for h in hdr[ix:]]
    head.append("# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g41 (4 vCPU Intel Xeon @ 2.30GHz, 16 GB).")
    head.append("# Each RESULT is computed by calling the production symbol on the stated inputs, both arms in one process.")
    (out / f"probe_{key}.py").write_text("\n".join(head) + "\n" + pre + "\n" + body + "\ntail()\n")
    print(p)
