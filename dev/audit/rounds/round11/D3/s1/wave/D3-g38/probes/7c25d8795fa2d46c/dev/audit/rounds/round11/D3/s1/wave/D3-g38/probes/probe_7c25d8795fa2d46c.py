#!/usr/bin/env python3
# Metric: admit (1) or refuse (0) of slab_mode_one_state_identifiability(1e-3, 1e-3, 1e7 -> tau_fast 5e-11 h, config) per shortest-phase length; inputs_differing counts inputs whose admit differs.
# Command: HPO_PROBE_ROOT=<clean baseline checkout> PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g38/probes/probe_7c25d8795fa2d46c.py
# EXPECTED inputs_differing=1 of 3 (all three phases 1e-9 h exactly: baseline refuses 'slab constants not configured', mutant admits since 3 tau_fast 1.5e-10 <= 1e-9)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g38 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB).
# Instrumented symbol: custom_components.heatpump_optimizer.sysid:slab_mode_one_state_identifiability, sysid.py:677
# Perturbation: key 7c25d8795fa2d46c, CMP_BOUND `not settle_band > 1e-9` -> `not settle_band >= 1e-9`, applied in memory (function re-compiled from the baseline source with the
#   one line replaced); the baseline arm is the same source re-compiled unchanged.
# Null control: phases 0.0 h and 1.0 h (same arm in both)
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).resolve().parent))
import _mutlib as L
m = L.module()
base, mut = L.mutant(m, "slab_mode_one_state_identifiability", "    if not (c_r > 1e-9 and c_s > 1e-9 and k_s > 1e-9) or not settle_band > 1e-9:", "    if not (c_r > 1e-9 and c_s > 1e-9 and k_s > 1e-9) or not settle_band >= 1e-9:")
cases = [("band_1e-9_exact", 1e-9), ("null_band_0", 0.0), ("null_band_1h", 1.0)]
diff = 0
for name, h in cases:
    cfg = m.SysIdConfig(settle_hours=h, step_hours=h, relax_hours=h)
    rb, rx = base(1e-3, 1e-3, 1e7, cfg), mut(1e-3, 1e-3, 1e7, cfg)
    diff += rb[0] != rx[0]
    print(f"RESULT admit[{name}] baseline={int(rb[0])} mutant={int(rx[0])} reason_equal={int(rb[1] == rx[1])}")
print(f"RESULT inputs_differing={diff} of {len(cases)}")
