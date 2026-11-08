import subprocess, pathlib, sys
R = pathlib.Path("/home/user/rev/custom_components/heatpump_optimizer")
W, C = R/"wood_fuel.py", R/"coordinator.py"
M = [
 ("A coordinator drops partload_at", C, "            partload_at=partload_factor,\n", ""),
 ("B _plan_partload guard always []", W, "    if result is None or partload_at is None:\n        return []", "    if True:\n        return []"),
 ("C _derated drops factor", W, "[c * f for c, f in zip(", "[c for c, f in zip("),
 ("D _derated drops tail", W, " + cops[len(partload):]", ""),
 ("E total drops hot water", W, "finite_float(p, 0.0) + finite_float(h, 0.0)", "finite_float(p, 0.0)"),
 ("F zip not zip_longest", W, "for p, h in zip_longest(", "for p, h in zip("),
 ("F2 fillvalue nan", W, "fillvalue=0.0,", "fillvalue=float('nan'),"),
 ("G nan draw not zeroed", W, "finite_float(p, 0.0) + finite_float(h, 0.0)", "p + finite_float(h, 0.0)"),
 ("H night always flat 3", W, "cops=list(cops) if cops else [3.0] * len(prices)", "cops=[3.0] * len(prices)"),
 ("I night no flat fallback", W, "cops=list(cops) if cops else [3.0] * len(prices)", "cops=list(cops)"),
 ("K dhw schedule ignored", W, 'getattr(result, "dhw_power_schedule", None) or []', "[]"),
 ("M factor const 1", W, "float(partload_at(thermal_params, finite_float(p, 0.0) + finite_float(h, 0.0)))", "1.0"),
 ("N space draw ignored", W, "result.power_schedule or [],", "[],"),
 ("O partload as divisor", W, "[c * f for c, f in zip(", "[c / f for c, f in zip("),
 ("NULL no-op mutant (comment)", W, "def _derated(", "# null\ndef _derated("),
]
for name, f, old, new in M:
    src = f.read_text()
    assert src.count(old) == 1, (name, src.count(old))
    f.write_text(src.replace(old, new))
    try:
        out = subprocess.run(["bash", "/home/user/w/pin.sh"], capture_output=True, text=True, timeout=600).stdout
    finally:
        f.write_text(src)
    killed = "rc=0 features rc=0" not in out
    print(f"{'KILLED ' if killed else 'SURVIVED'} {name}")
    for l in out.splitlines(): print("    " + l)
