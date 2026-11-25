import json, sys
from pathlib import Path
PRE = Path('/root/pgen/prelude.py').read_text()
OUT = Path('/root/d3wave-seat/wave/D3-g04/probes')
BASE = "92d38ecb640bd462f2e19c0814d0f0b7df1ee692"
MACH = "box D3-g04 (4 vCPU Intel Xeon Processor @ 2.10GHz, 16 GB, venv-ci CPython, gate running beside it: load1 ~1)"
def write(key, metric, expected, symbol, perturbation, null, body, extra=""):
    cmd = f"PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g04/probes/probe_{key}.py"
    hdr = ["#!/usr/bin/env python3", f"# Metric: {metric}", f"# Command: {cmd}"]
    hdr += [f"# EXPECTED {e}" for e in expected]
    hdr += [f"# Baseline: {BASE}. Machine: {MACH}.",
            f"# Instrumented symbol: {symbol}",
            f"# Perturbation: {perturbation}",
            f"# Null control: {null}"]
    hdr += [f"# {l}" for l in extra.splitlines() if l.strip()]
    hdr += ["# Run from the repository root; the mutant is applied in memory (the method recompiled from its own",
            "# source with the one line replaced, patched onto the class for the mutant arm only)."]
    (OUT / f"probe_{key}.py").write_text("\n".join(hdr) + "\n" + PRE + "\n" + body.strip() + "\n")
exec(Path(sys.argv[1]).read_text())
