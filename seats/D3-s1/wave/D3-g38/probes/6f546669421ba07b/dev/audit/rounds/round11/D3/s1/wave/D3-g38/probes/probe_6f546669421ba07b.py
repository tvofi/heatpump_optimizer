#!/usr/bin/env python3
# Metric: admit (1) or refuse (0) of slab_mode_one_state_identifiability(c_r=1, c_s=1, k_s=1 -> tau_fast 0.5 h, 3 tau 1.5 h, config) per SysIdConfig phase triple; inputs_differing counts triples whose admit differs.
# Command: HPO_PROBE_ROOT=<clean baseline checkout> PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g38/probes/probe_6f546669421ba07b.py
# EXPECTED inputs_differing=2 of 4 (settle 3/step 1/relax 2 and settle 2/step 2/relax 1: shortest phase 1 h refuses in baseline, mutant reads settle_hours and admits); default 1/2/2 and 1/1/1 null
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g38 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB).
# Instrumented symbol: custom_components.heatpump_optimizer.sysid:slab_mode_one_state_identifiability, sysid.py:676 `settle_band = min(config.settle_hours, config.step_hours, config.relax_hours)`
# Perturbation: key 6f546669421ba07b, CLAMP_DROP `min(settle, step, relax)` -> `(config.settle_hours)`, applied in memory (function re-compiled from the baseline source with the
#   one line replaced); the baseline arm is the same source re-compiled unchanged.
# Null control: SysIdConfig() default (settle is the shortest phase) and 1/1/1: same band in both arms
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).resolve().parent))
import _mutlib as L
m = L.module()
base, mut = L.mutant(m, "slab_mode_one_state_identifiability", "    settle_band = min(config.settle_hours, config.step_hours, config.relax_hours)", "    settle_band = (config.settle_hours)")
cases = [("s3_st1_r2", 3.0, 1.0, 2.0), ("s2_st2_r1", 2.0, 2.0, 1.0), ("null_default_1_2_2", 1.0, 2.0, 2.0), ("null_1_1_1", 1.0, 1.0, 1.0)]
diff = 0
for name, s, st, r in cases:
    cfg = m.SysIdConfig(settle_hours=s, step_hours=st, relax_hours=r)
    b, x = int(base(1.0, 1.0, 1.0, cfg)[0]), int(mut(1.0, 1.0, 1.0, cfg)[0])
    diff += b != x
    print(f"RESULT admit[{name}] baseline={b} mutant={x}")
print(f"RESULT inputs_differing={diff} of {len(cases)}")
