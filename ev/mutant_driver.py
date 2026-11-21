import subprocess, sys, os, pathlib
WT = pathlib.Path(os.environ["HOME"]) / "rv/wtm"
P = "custom_components/heatpump_optimizer/"
M = {
 "om_keep_all": (P+"open_meteo.py", "kept = [i for i, t in enumerate(times) if t >= floor]", "kept = list(range(len(times)))", "tests/open_meteo.py"),
 "om_lt1": (P+"open_meteo.py", "if len(kept) < 2:", "if len(kept) < 1:", "tests/open_meteo.py"),
 "om_guard_off": (P+"open_meteo.py", "if len(kept) < 2:", "if False:", "tests/open_meteo.py"),
 "lead_field_finite": (P+"entry_config.py", "_key(const.DEFAULT_WOOD_LIGHTING_LEAD_MINUTES, _lead_minutes)", "_key(const.DEFAULT_WOOD_LIGHTING_LEAD_MINUTES, finite_float)", "tests/wood_advisor.py"),
 "lead_floor_excl": (P+"entry_config.py", "not 0.0 <= minutes <= _MAX_PLAN_MINUTES", "not 0.0 < minutes <= _MAX_PLAN_MINUTES", "tests/wood_advisor.py"),
 "lead_ceiling_drop": (P+"entry_config.py", "not 0.0 <= minutes <= _MAX_PLAN_MINUTES", "not 0.0 <= minutes", "tests/wood_advisor.py"),
 "attach_raw": (P+"wood_fuel.py", "lead = EntryConfig.from_mapping(config).wood_lighting_lead_minutes", "lead = max(0.0, finite_float(config.get('wood_lighting_lead_minutes'), 60.0))", "tests/wood_advisor.py"),
 "pb_revert": (P+"inputs.py", "number = finite_float(token)\n    return None if number is None else number != 0.0", "try:\n        return float(token) != 0.0\n    except (TypeError, ValueError):\n        return None", "FEAT_NN"),
 "begin_guard_off": (P+"inputs.py", "if not isinstance(entity_id, str):\n            entity_id = None", "if False:\n            entity_id = None", "FEAT_NN"),
 "plaus_onesided": (P+"inputs.py", "window is None or window[0] <= value_c <= window[1]", "window is None or window[0] <= value_c", "FEAT_NN"),
 "tfc_mult": (P+"inputs.py", "return value_c / factor - offset", "return value_c * factor - offset", "FEAT_P8"),
 "minor_no100": (P+"inputs.py", "return value * per_kwh / 100.0", "return value * per_kwh", "FEAT_P8"),
 "mig_if_off": (P+"__init__.py", "        if repairs:\n", "        if False:\n", "ENT_MIG"),
 "mig_no_repair": (P+"__init__.py", "placed(repaired_numbers(effective, repairs))", "placed(effective)", "ENT_MIG"),
 "nr_drop_interval_lead": (P+"entry_config.py", "finite_float, _nonzero_number, _interval_minutes, _lead_minutes,", "finite_float, _nonzero_number,", "ENT_MIG"),
 "nr_text_dropped": (P+"entry_config.py", "f.name: finite_float(value)\n", "f.name: None\n", "ENT_MIG"),
 "nr_bool_clause": (P+"entry_config.py", "and (isinstance(value := stored[f.name], bool) or not isinstance(value, (int, float)))", "and not isinstance(value := stored[f.name], (int, float))", "ENT_MIG"),
 "rn_keep_none": (P+"entry_config.py", "if key not in repairs or repairs[key] is not None", "if True", "ENT_MIG"),
 "iv_lower_incl": (P+"entry_config.py", "not 0.0 < minutes <= _MAX_PLAN_MINUTES:\n        return default\n    return minutes\n\n\ndef _lead", "not 0.0 <= minutes <= _MAX_PLAN_MINUTES:\n        return default\n    return minutes\n\n\ndef _lead", "ENT_MIG"),
 "iv_ceiling_drop": (P+"entry_config.py", "not 0.0 < minutes <= _MAX_PLAN_MINUTES:", "not 0.0 < minutes:", "ENT_MIG"),
 "iv_field_finite": (P+"entry_config.py", "_key(const.DEFAULT_OPTIMIZATION_INTERVAL, _interval_minutes)", "_key(const.DEFAULT_OPTIMIZATION_INTERVAL, finite_float)", "ENT_MIG"),
}
FEAT_P8_CMD = [sys.executable, "tools/audit/seat/features_block.py", "--prelude", "exec(open('/root/rv/prelude_p8.py').read())", 'R.section("P8 — a price or temperature entity\'s unit is read at the seam (#1513)")', 'R.check(\n    "and an unparseable unit keeps']
env = dict(os.environ, PYTHONPATH="tests/hastub")
for name in sys.argv[1:]:
    path, old, new, test = M[name]
    f = WT / path; src = f.read_text()
    assert src.count(old) == 1, name
    f.write_text(src.replace(old, new))
    try:
        cmd = [sys.executable, test] if test.endswith(".py") else [sys.executable, "tools/audit/seat/features_block.py", "--prelude", "exec(open('/root/rv/prelude_nn.py').read())", 'R.section("Non-numeric inputs (v5.3.0)")'] if test=="FEAT_NN" else [sys.executable, "/root/rv/ent_mig.py"] if test=="ENT_MIG" else FEAT_P8_CMD
        r = subprocess.run(cmd, cwd=WT, env=env, capture_output=True, text=True, timeout=600)
    finally:
        f.write_text(src)
    out = (r.stdout + r.stderr).splitlines()
    fails = [l for l in out if "FAIL" in l][:3]
    print(f"MUTANT {name}: {test} rc={r.returncode} {fails or out[-1:]}")
st = subprocess.run(["git", "status", "--porcelain"], cwd=WT, capture_output=True, text=True).stdout
print("porcelain:", repr(st))
