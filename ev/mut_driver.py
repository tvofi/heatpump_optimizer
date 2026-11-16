import subprocess, sys, pathlib, os
ROOT = pathlib.Path("/home/user/wt-head")
TM = "custom_components/heatpump_optimizer/thermal_model.py"
MV = "custom_components/heatpump_optimizer/mixing_valve.py"
LG = "custom_components/heatpump_optimizer/ledger.py"
M = {
 "M1": (TM, "        emitter_ua = emitter_ua * k_slab / (emitter_ua + k_slab)\n", ""),
 "M2": (MV, " - free_heat_kw\n", "\n"),
 "M3": (TM, "        free_heat_kw = p.internal_gains\n", ""),
 "M4": (TM, "    if not p.two_zone_enabled:\n        k_slab", "    if True:\n        k_slab"),
 "M5": (TM, "        if not p.two_zone_enabled and p.mixing_valve_mode in mixing_valve.THROTTLING_MODES:", "        if False:"),
 "M6": (TM, "        if not p.two_zone_enabled and p.mixing_valve_mode in mixing_valve.THROTTLING_MODES:", "        if not p.two_zone_enabled:"),
 "M7": (MV, "    q_hold = max(\n        0.0, heat_loss_coefficient * max(0.0, target_temp - outdoor_temp) - free_heat_kw\n    )", "    q_hold = heat_loss_coefficient * max(0.0, target_temp - outdoor_temp) - free_heat_kw"),
 "R1": (TM, "        free_heat_kw = p.internal_gains\n", "        free_heat_kw = 0.5 * p.internal_gains\n"),
 "R2": (TM, "        k_slab = p.slab_heat_transfer_floored\n", "        k_slab = 2.0 * p.slab_heat_transfer_floored\n"),
 "R3": (TM, "            return _valve_flow_set(p, indoor_target, outdoor_temp, u, _valve_ua(p))", "            return _valve_flow_set(p, indoor_target, outdoor_temp, u, _valve_ua(p)) + 1e-9"),
 "R4": (LG, "REFERENCE_BASIS = 4\n", "REFERENCE_BASIS = 3\n"),
}
names = sys.argv[1:] or list(M)
env = dict(os.environ, PYTHONPATH="tests/hastub:tests:custom_components")
for n in names:
    f, old, new = M[n]
    p = ROOT / f; src = p.read_text()
    assert src.count(old) == 1, (n, src.count(old))
    p.write_text(src.replace(old, new))
    try:
        r = subprocess.run([sys.executable, "tools/audit/seat/features_block.py", "# R11-VALVE-REFERENCE (carry 2)", "# R10-HOTFIX-SAV-ESTIMATE: the settlement books step 0"], cwd=ROOT, env=env, capture_output=True, text=True, timeout=600)
        out = r.stdout + r.stderr
        fails = [l.strip() for l in out.splitlines() if l.strip().startswith("FAIL") or "Error" in l]
        print(f"=== {n} rc={r.returncode} {'KILLED' if r.returncode else 'SURVIVED'}")
        for l in fails[:6]: print("   ", l[:220])
    finally:
        p.write_text(src)
    sys.stdout.flush()
