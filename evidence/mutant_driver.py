import subprocess, sys, os
W = sys.argv[1]; wt = W + "/wt"
S = '# -- round-11 ADR-001 (R11-SEAM-kernel-step)'; E = '_fd_spot = _fd_coord()'
block = ["python3", "tools/audit/seat/features_block.py", "--prelude", f'exec(open("{W}/k11pre.py").read())', S, E]
wood = ["python3", "tests/wood_advisor.py"]
P = "custom_components/heatpump_optimizer/"
M = [
 ("M0 none (control)", None, None, None, block),
 ("M0b none (control)", None, None, None, wood),
 ("M1 _in_zone without utc_instant", P+"wood_fuel.py", "return utc_instant(ts).astimezone(local_tz) if", "return ts.astimezone(local_tz) if", wood),
 ("M2 manual_plan coerce back to host zone", P+"manual_plan.py", "return utc_instant(value).replace(tzinfo=None)", "return value.astimezone().replace(tzinfo=None)", block),
 ("M3 null control: D7-s3-04 water check config back to {}", "tests/features.py", "_k11_sensor._gap_probe_terms(\n    {_k11_const.CONF_DHW_ENABLED: True}, [1.0], [1.0], 1.0\n)", "_k11_sensor._gap_probe_terms({}, [1.0], [1.0], 1.0)", block),
 ("M4 gap advisor heat capacity literal 4.186/3600", P+"sensor.py", "volume * band * WATER_SPECIFIC_HEAT * 30.0", "volume * band * (4.186 / 3600.0) * 30.0", block),
 ("M5 gap advisor DHW guard removed", P+"sensor.py", "    if dhw_enabled_from_config(config):\n        terms[\"dhw_extra_kwh\"]", "    if True:\n        terms[\"dhw_extra_kwh\"]", block),
]
env = dict(os.environ, PYTHONPATH="tests/hastub", PYTHONDONTWRITEBYTECODE="1")
for name, f, old, new, cmd in M:
    orig = None
    if f:
        path = os.path.join(wt, f); orig = open(path).read()
        n = orig.count(old)
        if n != 1: print(f"RESULT {name}: PATTERN-COUNT {n}"); continue
        open(path, "w").write(orig.replace(old, new))
    try:
        r = subprocess.run(cmd, cwd=wt, env=env, capture_output=True, text=True, timeout=600)
        out = r.stdout + r.stderr
        fails = [l.strip() for l in out.splitlines() if l.strip().startswith("FAIL")]
        print(f"RESULT {name}: rc={r.returncode} fails={len(fails)}")
        for l in fails: print("   ", l[:300])
    finally:
        if orig is not None: open(path, "w").write(orig)
