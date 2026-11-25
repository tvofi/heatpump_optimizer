#!/usr/bin/env python3
# Metric: admit (1) or refuse (0) of slab_mode_identifiability(ThermalParameters with one slab constant set, SysIdConfig()) per input, the constant set through the constructor (ThermalParameters.clamp() floors room/slab thermal mass at 0.1) and, as a reachability control, written after construction; inputs_differing_via_constructor counts constructor inputs whose admit differs.
# Command: HPO_PROBE_ROOT=<clean baseline checkout> PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g38/probes/probe_b0d27be4975eb62b.py
# EXPECTED inputs_differing_via_constructor=0 of 4 (clamp floors c_s at 0.1, so 1e-9 never reaches the guard); setattr_bypass differs at c_s == 1e-9 only (c_s == 1e-9 exactly: baseline refuses 'slab constants not configured', mutant admits)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g38 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB).
# Instrumented symbol: custom_components.heatpump_optimizer.sysid:slab_mode_identifiability, sysid.py:643 `if not (c_r > 1e-9 and c_s > 1e-9 and k_s > 1e-9):`
# Perturbation: key b0d27be4975eb62b, CMP_BOUND, the c_s term `> 1e-9` -> `>= 1e-9`, applied in memory (function re-compiled from the baseline source with the
#   one line replaced); the baseline arm is the same source re-compiled unchanged.
# Null control: c_s = 0.0, 1e-3 and the default (same arm in both)
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).resolve().parent))
import _mutlib as L
import dataclasses
m = L.module(); tm = L.module("thermal_model")
base, mut = L.mutant(m, "slab_mode_identifiability", "    if not (c_r > 1e-9 and c_s > 1e-9 and k_s > 1e-9):", "    if not (c_r > 1e-9 and c_s >= 1e-9 and k_s > 1e-9):")
cfg = m.SysIdConfig()
fields = {"c_r": "room_thermal_mass", "c_s": "slab_thermal_mass", "k_s": "slab_heat_transfer"}
P0 = dataclasses.replace(tm.ThermalParameters(), room_thermal_mass=10.0, slab_thermal_mass=20.0, slab_heat_transfer=2.0)
cases = [("exact_1e-9", 1e-9), ("null_zero", 0.0), ("null_1e-3", 1e-3), ("null_default", getattr(P0, fields["c_s"]))]
diff = 0
for name, v in cases:
  for route in ("constructor", "setattr_bypass"):
    if route == "constructor":
        p = dataclasses.replace(P0, **{fields["c_s"]: v})
    else:  # the attribute written after construction, past ThermalParameters.clamp()'s 0.1 floor
        p = dataclasses.replace(P0); setattr(p, fields["c_s"], v)
    b, x = int(base(p, cfg)[0]), int(mut(p, cfg)[0])
    if route == "constructor":
        diff += b != x
    print(f"RESULT admit[c_s={name},{route}] baseline={b} mutant={x} (attribute read {getattr(p, fields['c_s'])!r})")
print(f"RESULT inputs_differing_via_constructor={diff} of {len(cases)}")
