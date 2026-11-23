import subprocess, sys, pathlib, os
wt = pathlib.Path(sys.argv[1]); out = pathlib.Path(sys.argv[2])
f = wt / "custom_components/heatpump_optimizer/thermal_model.py"
orig = f.read_text()
M = {
 "M1-slab-series-dropped": ("ua_slab = ua_floor * k_slab / (ua_floor + k_slab)", "ua_slab = ua_floor"),
 "M2-equal-weights": ("        w_sum = w_upper + w_lower\n", "        w_upper = w_lower = 1.0\n        w_sum = w_upper + w_lower\n"),
 "M3-free-heat-dropped": ("free_heat_kw = (w_upper * r + w_lower * (1.0 - r)) * p.internal_gains / w_sum", "free_heat_kw = 0.0"),
 "M4-direct-gate-dropped": ("    elif p.slab_fed_direct:\n        heat_loss_coefficient += lower_heat_loss_coefficient\n", ""),
 "M5-draw-circuits-lower": ("p, None, outdoor_temp, u_upper, ua_rad + ua_floor, u_lower)", "p, None, outdoor_temp, u_upper, ua_rad + ua_floor)"),
 "M6-delivery-lower": ("p, valve_target, outdoor_temp, zone_loss[0], ua_rad + ua_floor, zone_loss[1])", "p, valve_target, outdoor_temp, zone_loss[0], ua_rad + ua_floor)"),
 "M7-batch-lower": ("_valve_flow_set(p, vt, out_i, u_first, ua_rad + ua_floor, u_second)", "_valve_flow_set(p, vt, out_i, u_first, ua_rad + ua_floor)"),
 "M8-fti-two-zone-arm": ("u, u_lower = self._zone_loss(0.0, 0.0) if p.two_zone_enabled else (", "u, u_lower = (self._zone_loss(0.0, 0.0)[0], 0.0) if p.two_zone_enabled else ("),
 "M9-gain-split-swapped": ("(w_upper * r + w_lower * (1.0 - r))", "(w_upper * (1.0 - r) + w_lower * r)"),
 "M10-loss-weights-swapped": ("w_upper * heat_loss_coefficient + w_lower * lower_heat_loss_coefficient) / w_sum", "w_lower * heat_loss_coefficient + w_upper * lower_heat_loss_coefficient) / w_sum"),
 "M11-ua-weights-swapped": ("emitter_ua = (w_upper * ua_rad + w_lower * ua_slab) / w_sum", "emitter_ua = (w_lower * ua_rad + w_upper * ua_slab) / w_sum"),
 "M12-fti-wind": ("self._zone_loss(0.0, 0.0) if p.two_zone_enabled", "self._zone_loss(3.0, 0.0) if p.two_zone_enabled"),
 "M13-inter-zone-c-dropped-upper": ("w_upper = r * (ua_slab + lower_heat_loss_coefficient + c) + (1.0 - r) * c", "w_upper = r * (ua_slab + lower_heat_loss_coefficient) + (1.0 - r) * c"),
 "M14-batch-uses-vt-none": ("_valve_flow_set(p, vt, out_i,", "_valve_flow_set(p, None, out_i,"),
 "M15-fti-direct-into-valved": ("if p.mixing_valve_mode in mixing_valve.THROTTLING_MODES and not p.slab_fed_direct:", "if p.mixing_valve_mode in mixing_valve.THROTTLING_MODES:"),
}
env = dict(os.environ, PYTHONPATH="tests/hastub:tests:custom_components")
try:
    for name, (a, b) in M.items():
        if orig.count(a) != 1:
            print(f"{name}: anchor count {orig.count(a)}, skipped", flush=True)
            continue
        f.write_text(orig.replace(a, b))
        r = subprocess.run([sys.executable, "tools/audit/seat/features_block.py",
                            "# R11-SEAM-two-zone-slab (#3713)", "# R11-VALVE-REFERENCE (carries 0, 1)"],
                           cwd=wt, env=env, capture_output=True, text=True)
        fails = [l.strip()[:140] for l in (r.stdout + r.stderr).splitlines() if "FAIL" in l or "Error" in l]
        print(f"{name}: rc {r.returncode}; " + (" | ".join(fails) if fails else "no FAIL lines"), flush=True)
        (out / f"mut.{name}.txt").write_text(r.stdout + r.stderr)
finally:
    f.write_text(orig)
