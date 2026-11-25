#!/usr/bin/env python3
# Metric: admit (1) or refuse (0) of slab_mode_one_state_identifiability(2, 2, 1 -> tau_fast 1.0 h, 3 tau 3.0 h, config) per shortest phase; inputs_differing counts inputs whose admit differs.
# Command: HPO_PROBE_ROOT=<clean baseline checkout> PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g38/probes/probe_4467ecd198f47483.py
# EXPECTED inputs_differing=1 of 3 (shortest phase 3.0 h == 3 tau_fast exactly: baseline admits, mutant refuses 'slab mode too slow')
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g38 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB).
# Instrumented symbol: custom_components.heatpump_optimizer.sysid:slab_mode_one_state_identifiability, sysid.py:683 `if FAST_MODE_SETTLE_TAUS * tau_fast <= settle_band:`
# Perturbation: key 4467ecd198f47483, CMP_BOUND `<= settle_band` -> `< settle_band`, applied in memory (function re-compiled from the baseline source with the
#   one line replaced); the baseline arm is the same source re-compiled unchanged.
# Null control: shortest phase 4.0 h and 2.0 h (same arm in both)
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).resolve().parent))
import _mutlib as L
m = L.module()
base, mut = L.mutant(m, "slab_mode_one_state_identifiability", "    if FAST_MODE_SETTLE_TAUS * tau_fast <= settle_band:", "    if FAST_MODE_SETTLE_TAUS * tau_fast < settle_band:")
assert m.FAST_MODE_SETTLE_TAUS * m.slab_mode_tau_fast(2.0, 2.0, 1.0) == 3.0
cases = [("band_3h_tie", 3.0), ("null_band_4h", 4.0), ("null_band_2h", 2.0)]
diff = 0
for name, h in cases:
    cfg = m.SysIdConfig(settle_hours=h, step_hours=h + 1.0, relax_hours=h + 1.0)
    b, x = int(base(2.0, 2.0, 1.0, cfg)[0]), int(mut(2.0, 2.0, 1.0, cfg)[0])
    diff += b != x
    print(f"RESULT admit[{name}] baseline={b} mutant={x}")
print(f"RESULT inputs_differing={diff} of {len(cases)}")
