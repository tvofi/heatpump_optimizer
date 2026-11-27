import subprocess, sys, pathlib, os
P = "custom_components/heatpump_optimizer/"
DH = ("    setpoint = float(candidate.get(CONF_DHW_SETPOINT, current.get(CONF_DHW_SETPOINT, DEFAULT_DHW_SETPOINT)))\n"
      "    minimum = float(candidate.get(CONF_DHW_MIN_TEMP, current.get(CONF_DHW_MIN_TEMP, DEFAULT_DHW_MIN_TEMP)))\n"
      "    return minimum, setpoint, setpoint - DHW_MIN_TEMP_SETPOINT_MARGIN")
MUTS = [
 ("M01", "comfort_band.py", "    return finite_float(candidate.get(key, current.get(key, default)), float(default))", "    return float(candidate.get(key, current.get(key, default)))", "tests/config_flow_steps.py"),
 ("M09", "thermal_model.py", "values[\"buffer_max_temp\"] = finite_float(\n            config.get(const.CONF_BUFFER_MAX_TEMP), const.DEFAULT_BUFFER_MAX_TEMP\n        )", "values[\"buffer_max_temp\"] = float(\n            config.get(const.CONF_BUFFER_MAX_TEMP, const.DEFAULT_BUFFER_MAX_TEMP)\n        )", "tests/config_flow_steps.py"),
 ("M13", "modbus_prefill.py", "cop = finite_float(current.get(CONF_HEAT_PUMP_COP_NOMINAL)) or DEFAULT_HEAT_PUMP_COP_NOMINAL", "cop = float(current.get(CONF_HEAT_PUMP_COP_NOMINAL) or DEFAULT_HEAT_PUMP_COP_NOMINAL)", "tests/config_flow_steps.py"),
 ("M14", "quick_setup.py", "heated_area = finite_float(answers.get(CONF_HEATED_AREA), DEFAULT_HEATED_AREA)", "heated_area = float(answers.get(CONF_HEATED_AREA, DEFAULT_HEATED_AREA))", "tests/config_flow_steps.py"),
 ("M17", "comfort_band.py", "    return minimum, setpoint, setpoint - DHW_MIN_TEMP_SETPOINT_MARGIN", DH, "tests/config_flow_steps.py"),
 ("M18", "comfort_band.py", "    return minimum, setpoint, setpoint - DHW_MIN_TEMP_SETPOINT_MARGIN", DH, "tests/entities.py"),
]
only = sys.argv[1:]
for mid, f, new, old, script in MUTS:
    if only and mid not in only:
        continue
    p = pathlib.Path(P + f)
    src = p.read_text()
    assert src.count(new) == 1, (mid, src.count(new))
    p.write_text(src.replace(new, old))
    try:
        r = subprocess.run([sys.executable, script], capture_output=True, text=True,
                           env={**os.environ, "PYTHONPATH": "tests/hastub"})
        out = r.stdout + r.stderr
        fails = [l for l in out.splitlines() if "FAIL" in l and ("R11-LATE" in l or "migrated module" in l)]
        tail = [l for l in out.splitlines() if "checks" in l and ("PASSED" in l or "FAILED" in l or "failed" in l)][-1:]
        print(mid, script, "rc", r.returncode, tail, "named-fails", len(fails), flush=True)
        for l in fails[:10]:
            print("   ", l[:220], flush=True)
    finally:
        p.write_text(src)
