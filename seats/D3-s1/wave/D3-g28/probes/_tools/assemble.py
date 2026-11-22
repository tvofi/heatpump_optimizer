import sys
sys.path.insert(0, '.')
from headers import H, F
pre = open('prelude.py').read()
out = sys.argv[1]
for k, h in H.items():
    cmd = f"PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g28/probes/probe_{k}.py"
    lines = ["#!/usr/bin/env python3",
             f"# Probe for mutant {k} (box D3-g28, audit round 11, D3.M3/M4 full-gate survivor answer).",
             f"# Metric: {h['metric']}.",
             f"# Command: {cmd}",
             "# Expected (exact; counts and values are deterministic, tolerance 0 unless a float is printed to fewer digits):"]
    lines += [f"#   RESULT {e}" for e in h['expected']]
    lines += ["# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692.",
              "# Machine: cloud box D3-g28, 4 vCPU Intel(R) Xeon(R) Processor @ 2.10GHz, 16 GB; run beside its own full gate",
              "#   (load1 1.0-2.1), so any timing here is provisional; the metrics are counts and values, contention-immune.",
              f"# Instrumented symbol: heatpump_optimizer.optimizer:{h['sym']} ({F}:{h['line']} `{h['old']}`),",
              "#   imported under the package name the suite uses (tests/golden.py puts custom_components on sys.path).",
              f"# Perturbation: `{h['old']}` -> `{h['new']}` (the mutant), applied in memory: the function is re-compiled from its",
              "#   own source with that one line replaced and called directly, or attached with mock.patch.object for the mutant",
              f"#   arm of a caller. Direction: {h['direction']}.",
              f"# Inputs tried: {h['inputs']}.",
              "# Null control: the RESULT null_* lines, an input where the mutated line cannot matter.",
              "# Writes nothing; no Node; no env_drift."]
    body = open(f'bodies/{k}.py').read()
    open(f'{out}/probe_{k}.py', 'w').write("\n".join(lines) + "\n" + pre + "\n\n" + body)
print(len(H))
