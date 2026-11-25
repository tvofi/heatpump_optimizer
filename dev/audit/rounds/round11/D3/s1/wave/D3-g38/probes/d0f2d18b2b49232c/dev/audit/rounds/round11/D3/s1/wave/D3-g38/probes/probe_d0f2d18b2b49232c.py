#!/usr/bin/env python3
# Metric: admit (1) or refuse (0) of slab_mode_one_state_identifiability(c_r, c_s, k_s, SysIdConfig()) per input, with the other two constants at values whose tau_fast settles inside the 1 h shortest phase; inputs_differing counts inputs whose admit differs.
# Command: HPO_PROBE_ROOT=<clean baseline checkout> PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g38/probes/probe_d0f2d18b2b49232c.py
# EXPECTED inputs_differing=1 of 4 (c_s == 1e-9 exactly: baseline refuses 'slab constants not configured', mutant admits)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g38 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB).
# Instrumented symbol: custom_components.heatpump_optimizer.sysid:slab_mode_one_state_identifiability, sysid.py:677 `if not (c_r > 1e-9 and c_s > 1e-9 and k_s > 1e-9) or not settle_band > 1e-9:`
# Perturbation: key d0f2d18b2b49232c, CMP_BOUND, the c_s term `> 1e-9` -> `>= 1e-9`, applied in memory (function re-compiled from the baseline source with the
#   one line replaced); the baseline arm is the same source re-compiled unchanged.
# Null control: c_s = 0.0, 1e-3 and 1.0 (same arm in both)
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).resolve().parent))
import _mutlib as L
m = L.module()
base, mut = L.mutant(m, "slab_mode_one_state_identifiability", "    if not (c_r > 1e-9 and c_s > 1e-9 and k_s > 1e-9) or not settle_band > 1e-9:", "    if not (c_r > 1e-9 and c_s >= 1e-9 and k_s > 1e-9) or not settle_band > 1e-9:")
cfg = m.SysIdConfig()
# other constants: c_r=c_s=0.2 kWh/C, k_s=1 kW/C -> tau_fast 0.1 h, 3*tau 0.3 h <= 1 h (admitted)
P0 = {"c_r": 0.2, "c_s": 0.2, "k_s": 1.0}
if "c_s" == "k_s":
    P0 = {"c_r": 1e-9, "c_s": 1e-9, "k_s": 1.0}  # tau_fast = 5e-10/k_s; with k_s=1e-9 it is 0.5 h (admitted)
cases = [("exact_1e-9", 1e-9), ("null_zero", 0.0), ("null_1e-3", 1e-3), ("null_1.0", 1.0)]
diff = 0
for name, v in cases:
    a = dict(P0, **{"c_s": v})
    if "c_s" == "k_s":
        a = {"c_r": 2e-9, "c_s": 2e-9, "k_s": v}
    b, x = int(base(a["c_r"], a["c_s"], a["k_s"], cfg)[0]), int(mut(a["c_r"], a["c_s"], a["k_s"], cfg)[0])
    diff += b != x
    print(f"RESULT admit[c_s={name}] baseline={b} mutant={x}")
print(f"RESULT inputs_differing={diff} of {len(cases)}")
