#!/usr/bin/env python3
# Metric: refused (1) or accepted (0) by _slab_refusal(ua, room_cap, gains_kw=0.3, slab_mass) per input; RESULT lines give baseline/mutant per input and the count of inputs whose outcome differs.
# Command: HPO_PROBE_ROOT=<clean baseline checkout> PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g38/probes/probe_d8e588be2e0aba89.py
# EXPECTED inputs_differing=2 of 4 (tau == 0.1 exactly, two ways: baseline accepts, mutant refuses)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g38 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB).
# Instrumented symbol: custom_components.heatpump_optimizer.sysid:_slab_refusal, sysid.py:897 `if not (0.1 <= tau <= 200.0) or not (0.01 <= ua <= 5.0):`
# Perturbation: key d8e588be2e0aba89, CMP_BOUND `0.1 <= tau` -> `0.1 < tau`, applied in memory (function re-compiled from the baseline source with the
#   one line replaced); the baseline arm is the same source re-compiled unchanged.
# Null control: tau=0.2 and tau=0.05 (same arm in both)
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).resolve().parent))
import _mutlib as L
m = L.module()
base, mut = L.mutant(m, "_slab_refusal", "    if not (0.1 <= tau <= 200.0) or not (0.01 <= ua <= 5.0):", "    if not (0.1 < tau <= 200.0) or not (0.01 <= ua <= 5.0):")
def out(f, ua, rc, sm):
    r = f(ua, rc, 0.3, sm)
    return 0 if r is None else 1
cases = [("tau0.1_exact", 1.0, 0.1, 0.0), ("tau0.1_via_slab", 2.0, 0.1, 0.1), ("null_tau0.2", 1.0, 0.2, 0.0), ("null_tau0.05", 1.0, 0.05, 0.0)]
diff = 0
for name, ua, rc, sm in cases:
    b, x = out(base, ua, rc, sm), out(mut, ua, rc, sm)
    diff += b != x
    print(f"RESULT refused[{name}] baseline={b} mutant={x}")
print(f"RESULT inputs_differing={diff} of {len(cases)}")
