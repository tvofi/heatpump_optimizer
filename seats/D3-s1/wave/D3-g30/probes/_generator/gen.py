import json, sys, csv
from pathlib import Path
sys.path.insert(0, ".")
from bodies import K
S1 = Path.home() / "audit-r11-D3-s1/dev/audit/rounds/round11/D3/s1"
OUT = S1 / "wave/D3-g30/probes"
common = Path("common.py").read_text()
expected = json.loads(Path("expected.json").read_text()) if Path("expected.json").exists() else {}
for key, k in K.items():
    mut = json.loads((S1 / f"state/results/complete/{key}.json").read_text())["mutant"]
    assert mut["line"] == k["line"], key
    rel = f"dev/audit/rounds/round11/D3/s1/wave/D3-g30/probes/probe_{key}.py"
    exp = expected.get(key, ["(filled after the first run)"])
    hdr = [
        "#!/usr/bin/env python3",
        f"# Metric: {k['metric']}; printed per input for the baseline and the mutant arm.",
        f"# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 {rel}",
        *[f"# EXPECTED {e}" for e in exp],
        "# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g30 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB, CPython 3.14 venv-ci).",
        f"# Instrumented symbol: {k['sym']}, price_model.py line {k['line']}.",
        f"# Perturbation: key {key} ({mut['kind']}), line {k['line']} `{mut['old'].strip()}` -> `{mut['new'].strip()}`, applied in memory: the",
        "#   module is re-executed from its own source with that one line replaced (never on disk); the mutant arm uses that copy.",
        "#   Direction: see the EXPECTED lines (baseline value -> mutant value); `<metric>_inputs_moved` counts inputs that separate the arms.",
        "# Null control: the null_* inputs, where the mutated line is inert or takes the same branch, must give null_delta=0.",
        "# Count key: the value the production symbol returns or stores (never an input attribute).",
    ]
    consts = f"OLD = {mut['old']!r}\nNEW = {mut['new']!r}\nLINE = {mut['line']}\n"
    body = common.replace("\nROOT = repo_root(__file__)", "\n" + consts + "\nROOT = repo_root(__file__)", 1)
    (OUT / f"probe_{key}.py").write_text("\n".join(hdr) + "\n" + body + "\n# ---- the measurement ----" + k["body"] + "\nfooter()\n")
print("written", len(K))
