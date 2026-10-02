import shutil, subprocess, sys, re
from pathlib import Path
BASE = Path("trees/r2"); C = "custom_components/heatpump_optimizer/coordinator.py"
anchor_build = '        data["energy_totals_counting_since"] = self._energy_totals_since\n'
anchor_handover = '    handover["plan_stale"] = coord._plan_is_stale()\n'
anchor_meas = '            "measured_power_available": self._measured_power is not None,\n        }\n'
M = {
 "subscript":      (anchor_build, anchor_build + '        data["zz_subscript"] = 1\n'),
 "setdefault":     (anchor_build, anchor_build + '        data.setdefault("zz_setdefault", 1)\n'),
 "ior":            (anchor_build, anchor_build + '        data |= {"zz_ior": 1}\n'),
 "update_kw":      (anchor_build, anchor_build + '        data.update(zz_update_kw=1)\n'),
 "const_key":      (anchor_build, anchor_build + '        data[ZZ_CONST_KEY] = 1\n'),
 "dict_call_ret":  (anchor_meas, anchor_meas.replace('        }\n', '        } if self._measured_power is not None else dict(zz_dict_call=1)\n')),
 "handover_write": (anchor_handover, anchor_handover + '    handover["zz_handover"] = 1\n'),
 "spread_new_src": (anchor_build, anchor_build + '        data.update(self._zz_extra_view())\n'),
}
for name, (a, b) in M.items():
    d = Path(f"trees/egm_{name}"); shutil.rmtree(d, ignore_errors=True); shutil.copytree(BASE, d, symlinks=True)
    p = d / C; s = p.read_text(); assert s.count(a) == 1, (name, s.count(a)); p.write_text(s.replace(a, b))
    if name == "const_key":
        p.write_text(p.read_text().replace("\nclass HeatPumpOptimizerCoordinator(", '\nZZ_CONST_KEY = "zz_const_key"\n\n\nclass HeatPumpOptimizerCoordinator(', 1))
    r = subprocess.run([sys.executable, "../../egb3_check.py"], cwd=d, capture_output=True, text=True)
    res = [l for l in r.stdout.splitlines() if "FAIL" in l or "RESULT" in l]
    caught = any("FAIL" in l for l in res)
    print(f"RESULT mutant={name} caught={caught}"); [print("   ", l[:230]) for l in res]
    shutil.rmtree(d)
