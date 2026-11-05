import sys, shutil, pathlib
W = pathlib.Path("/tmp/tmp.7evDx9Kuim")
OPT = "custom_components/heatpump_optimizer/optimizer.py"
LED = "custom_components/heatpump_optimizer/ledger.py"
DEM = "required_thermal = max(0.0, _thermostat_demand("
M = {
 "null": [(OPT, "    p = model.params\n    if not p.two_tank_modelled", "    p = model.params  # null\n    if not p.two_tank_modelled")],
 "wood0": [(OPT, "    return min(1.0, usable_kwh_th / p.cop_nominal_floored / reference_kwh)", "    return 0.0")],
 "wood1": [(OPT, "    return min(1.0, usable_kwh_th / p.cop_nominal_floored / reference_kwh)", "    return 1.0")],
 "floordel": [(OPT, DEM, "required_thermal = (_thermostat_demand(")],
 "floorlate": [(OPT, DEM, "required_thermal = (_thermostat_demand("),
               (OPT, "            baseline_power = self._apportion_by_steady_demand(baseline_power, weather, targets)\n        return baseline_power, state",
                     "            baseline_power = self._apportion_by_steady_demand(baseline_power, weather, targets)\n        return np.maximum(baseline_power, 0.0), state")],
 "floorpower": [(OPT, DEM, "required_thermal = (_thermostat_demand("),
                (OPT, "            baseline_power[i] = power\n", "            baseline_power[i] = max(0.0, power)\n")],
 "migguard": [(LED, 'if isinstance(meta, dict) and isinstance(lines, dict) and "savings_baseline" in lines:', "if isinstance(meta, dict):")],
}
name = sys.argv[1]
dst = W / "mut" / name
if dst.exists(): shutil.rmtree(dst)
shutil.copytree(W / "wt", dst, ignore=shutil.ignore_patterns(".git"))
for f, old, new in M[name]:
    p = dst / f; s = p.read_text(); assert s.count(old) == 1, (name, old); p.write_text(s.replace(old, new))
print("made", name)
