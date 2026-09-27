"""F2.3 mutation runner: one textual edit of a production line in a copy of the
code head, then the R9-F2.3 block (tests/features.py's own block, extracted).
usage: mutate.py <head-tree> <outdir>"""
import os, shutil, subprocess, sys
S = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TM = "custom_components/heatpump_optimizer/thermal_model.py"
OP = "custom_components/heatpump_optimizer/optimizer.py"
MUTANTS = {
    "M0-null": [],
    "M1-ratio-1.5": [(TM, "EULER_MONOTONE_MAX_RATIO: float = 1.0", "EULER_MONOTONE_MAX_RATIO: float = 1.5")],
    "M2-no-ua-rad-row": [(TM, "(u_upper + p.inter_zone_transfer + ua_rad)", "(u_upper + p.inter_zone_transfer)")],
    "M3-no-ua-floor-row": [(TM, "(p.slab_heat_transfer + ua_floor) / p.slab_thermal_mass", "p.slab_heat_transfer / p.slab_thermal_mass")],
    "M4-no-buffer-row": [(TM, "                buf_row,\n", "")],
    "M5-coil-unscaled": [(TM, "            q_coil *= dhw_draw_scale(dhw_temp, inlet)\n", "")],
    "M6-replayed-end": [(OP, "        optimized_end = published_end[0]", "        optimized_end = self._replay_end_state(\n            initial_state, optimal_space, outdoor_temps, wind_speeds,\n            precipitation, solar_radiation, dt,\n            external_heat_kw=h.external_heat_kw,\n            valve_targets=h.valve_targets, humidity=h.humidity,\n        )\n        optimized_end.dhw_temperature = float(dhw_temps[-1])")],
    "M7-reference-no-coil": [(OP, "            if coil_draws is not None:\n                self.model.apply_dhw_coil(", "            if False:\n                self.model.apply_dhw_coil(")],
    "M8-inlet-literal": [(TM, "    dhw_inlet_temp: float = DEFAULT_DHW_INLET_TEMP  # °C", "    dhw_inlet_temp: float = 10.0  # °C")],
    "M9-coil-default-literal": [(TM, "    inlet_temp: float = DEFAULT_DHW_INLET_TEMP,", "    inlet_temp: float = 10.0,")],
    "M10-coil-guard-off": [(OP, "        if not p.dhw_coil_active:\n            coil_draws = None\n", "")],
    "M11-span-unclamped": [(TM, "    span = max(DHW_MIXED_USE_TEMP - inlet_temp, 1e-6)", "    span = DHW_MIXED_USE_TEMP - inlet_temp")],
    "M12-cop-unclamped": [(TM, "                design_power = p.max_electrical_power * max(p.cop_nominal, 1.0)\n                design_dt = max(p.emitter_design_delta_t, 1.0)\n                ua_rad", "                design_power = p.max_electrical_power * p.cop_nominal\n                design_dt = max(p.emitter_design_delta_t, 1.0)\n                ua_rad")],
    "M13-dt-unclamped": [(TM, "                design_dt = max(p.emitter_design_delta_t, 1.0)\n                ua_rad", "                design_dt = p.emitter_design_delta_t\n                ua_rad")],
    "M14-buffer-fallback-off": [(TM, "                if c_buf < 1e-6:\n                    c_buf = 0.04  # the step's own fallback", "                if False:\n                    c_buf = 0.04  # the step's own fallback")],
    "M15-no-wood-guard-off": [(TM, "        wood = state.wood_tank_temperature\n        if wood is None:\n            return draw_kw", "        wood = state.wood_tank_temperature\n        if False:\n            return draw_kw")],
}
head, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
env = dict(os.environ, PYTHONPATH="tests/hastub", OPENBLAS_CORETYPE="Haswell", OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1")
ONLY = sys.argv[3].split(",") if len(sys.argv) > 3 else None
for name, edits in MUTANTS.items():
    if ONLY and name not in ONLY:
        continue
    d = os.path.join(S, "mut", "wt"); shutil.rmtree(d, ignore_errors=True)
    subprocess.run(f"git -C {head} archive HEAD custom_components tests | (mkdir -p {d} && tar -x -C {d})", shell=True, check=True)
    for f, old, new in edits:
        p = os.path.join(d, f); s = open(p).read()
        assert s.count(old) == 1, (name, old); open(p, "w").write(s.replace(old, new))
    r = subprocess.run([os.path.join(S, "vci/bin/python"), os.path.join(S, "f23_run.py")], cwd=d, env=env, capture_output=True, text=True)
    open(os.path.join(out, name + ".txt"), "w").write(r.stdout + r.stderr)
    fails = [l for l in r.stdout.splitlines() if l.startswith("  FAIL")]
    print(f"{name}: rc={r.returncode} fails={len(fails)}")
    for l in fails: print("   ", l[:160])
