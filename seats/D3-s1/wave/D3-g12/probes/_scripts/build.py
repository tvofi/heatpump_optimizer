import sys, importlib.util
G = sys.argv[1]; OUT = sys.argv[2]
head = open(f"{G}/common_head.py").read(); tail = open(f"{G}/common_tail.py").read()
B = {}
for part in ("bodies1", "bodies2", "bodies3"):
    spec = importlib.util.spec_from_file_location(part, f"{G}/{part}.py"); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); B.update(m.B)
REL = "dev/audit/rounds/round11/D3/s1/wave/D3-g12/probes"
for k, v in B.items():
    hdr = [
        "#!/usr/bin/env python3",
        f"# D3-g12 step-4 probe for full-gate survivor {k} (audit round 11, seat D3-s1).",
        f"# Metric: {v['metric']}",
        f"# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 {REL}/probe_{k}.py",
        f"# Expected: {v['expected']} (exact: counts and values, no tolerance)",
        "# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g12 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB).",
        f"# Instrumented symbol: {v['symbol']}",
        f"# Perturbation: {v['pert']}",
        f"# Null control: {v['null']}",
        "# Count key: the value the production symbol returns or stores (never an input attribute).",
        "# Runs from the repository root, writes nothing; the mutant lives only in memory.",
    ]
    open(f"{OUT}/probe_{k}.py", "w").write("\n".join(hdr) + "\n" + head + v["body"] + tail)
print(len(B), "probes")
