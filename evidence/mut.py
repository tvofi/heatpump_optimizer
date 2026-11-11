import subprocess, sys, pathlib
root = pathlib.Path(sys.argv[1]); out = pathlib.Path(sys.argv[2])
PA = "custom_components/heatpump_optimizer/pump_arbiter.py"
CO = "custom_components/heatpump_optimizer/const.py"
M = {
 "M1_lows_append_del": (PA, "    lows.append(low)\n", ""),
 "M2_high_dropped": (PA, "rec.cut_hi_c, high]", "rec.cut_hi_c]"),
 "M4_guard_off": (PA, "if low is not None and high is not None and low >= high:", "if False:"),
 "M5_ge_to_gt": (PA, "and low >= high:", "and low > high:"),
 "M6_range_rows_del": (CO, "    CONF_SPACE_SETPOINT_LOW_LIMIT_ENTITY: WATER_RANGE_C,\n    CONF_SPACE_SETPOINT_HIGH_LIMIT_ENTITY: WATER_RANGE_C,\n", ""),
 "M7_ok_guard_del": (PA, "reading.value if reading.ok else None", "reading.value"),
 "M8_limits_none": (PA, "    low, high = _setpoint_limits_c(inp)\n", "    low, high = None, None\n"),
}
sel = sys.argv[3:] or list(M)
for name in sel:
    f, old, new = M[name]; p = root / f; src = p.read_text()
    assert src.count(old) == 1, (name, src.count(old))
    p.write_text(src.replace(old, new, 1))
    try:
        r = subprocess.run([sys.executable, "tests/features.py"], cwd=root, env={"PYTHONPATH": "tests/hastub", "PATH": "/opt/hpo/venv-ci/bin:/usr/bin:/bin", "HOME": "/root"}, capture_output=True, text=True, timeout=1800)
        fails = [l for l in (r.stdout + r.stderr).splitlines() if "FAIL" in l]
        (out / f"mutant_{name}.txt").write_text(f"rc={r.returncode}\n" + "\n".join(fails) + "\n" + (r.stdout + r.stderr)[-1500:])
        print(f"RESULT mutant {name} rc={r.returncode} fails={len(fails)}", flush=True)
        for l in fails[:6]: print("   ", l[:220], flush=True)
    finally:
        p.write_text(src)
