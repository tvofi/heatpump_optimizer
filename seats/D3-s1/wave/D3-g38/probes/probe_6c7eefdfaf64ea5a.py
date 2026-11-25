#!/usr/bin/env python3
# Metric: admit (1) or refuse (0) of adoption_decision(SysIdResult(completed, ua_profile_halfwidth=0.01, heat_loss 0.5), ThermalParameters(base UA), SysIdConfig()) per configured base UA; inputs_differing counts inputs whose admit differs.
# Command: HPO_PROBE_ROOT=<clean baseline checkout> PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g38/probes/probe_6c7eefdfaf64ea5a.py
# EXPECTED inputs_differing=2 of 5 (base UA exactly 1e-6, one zone and two zones 5e-7+5e-7: baseline refuses 'no configured heat-loss coefficient to scale', mutant admits with scale 5e5)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g38 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB).
# Instrumented symbol: custom_components.heatpump_optimizer.sysid:adoption_decision, sysid.py:1279 `if not base_u > 1e-6:`
# Perturbation: key 6c7eefdfaf64ea5a, CMP_BOUND `> 1e-6` -> `>= 1e-6`, applied in memory (function re-compiled from the baseline source with the
#   one line replaced); the baseline arm is the same source re-compiled unchanged.
# Null control: base UA 0.0, 2e-6 and 0.2 kW/K (same arm in both)
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).resolve().parent))
import _mutlib as L
import dataclasses
m = L.module(); tm = L.module("thermal_model")
base, mut = L.mutant(m, "adoption_decision", "    if not base_u > 1e-6:", "    if not base_u >= 1e-6:")
res = m.SysIdResult(completed=True, ua_profile_halfwidth=0.01, heat_loss_kw_per_c=0.5, reason="ok")
cfg = m.SysIdConfig()
P0 = tm.ThermalParameters()
cases = [("one_zone_1e-6", dict(heat_loss_coefficient=1e-6)),
         ("two_zone_5e-7+5e-7", dict(two_zone_enabled=True, upper_floor_heat_loss=5e-7, lower_floor_heat_loss=5e-7)),
         ("null_0", dict(heat_loss_coefficient=0.0)), ("null_2e-6", dict(heat_loss_coefficient=2e-6)),
         ("null_0.2", dict(heat_loss_coefficient=0.2))]
diff = 0
for name, kw in cases:
    p = dataclasses.replace(P0, **kw)
    db, dx = base(res, p, cfg), mut(res, p, cfg)
    diff += db.admit != dx.admit
    print(f"RESULT admit[{name}] baseline={int(db.admit)} mutant={int(dx.admit)} reasons={db.reason!r}|{dx.reason!r}")
print(f"RESULT inputs_differing={diff} of {len(cases)}")
