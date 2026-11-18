import subprocess, sys, os, pathlib
H="54b8b9d469c448d54d5d8e204e651c908682e511"
R="/home/user/heatpump_optimizer"
CF="custom_components/heatpump_optimizer/config_flow.py"
EC="custom_components/heatpump_optimizer/entry_config.py"
IN="custom_components/heatpump_optimizer/__init__.py"
M={
 "M1_placed_all_to_data":(EC,"if k in DATA_ONLY},","},","config_flow_steps"),
 "M2_migrate_minor":(IN," or minor < CONFIG_ENTRY_MINOR_VERSION","","entities"),
 "M3_computed_current":(CF,"computed = row.default.of(saving, hass)","computed = row.default.of(current, hass)","config_flow_steps"),
 "M4_window_placeholders":(CF,"**_WINDOW_PLACEHOLDERS, **device_prefill.disclaimer(), **notes,","**device_prefill.disclaimer(), **notes,","config_flow_steps"),
 "M5_uncapped_gt":(CF,"if float(fraction) >= 1.0:","if float(fraction) > 1.0:","config_flow_steps"),
 "M6_setup_entry_unplaced":(CF,"            data=data,\n            options=options,\n        )\n\n    async def async_step_quick_setup","            data=self._data,\n        )\n\n    async def async_step_quick_setup","config_flow_steps"),
 "M7_undone_unplaced":(EC,"    return placed({**data_side, **options_side})\n\n\ndef factory_settings","    return data_side, options_side\n\n\ndef factory_settings","features"),
 "M8_factory_unplaced":(EC,"    data_side, options_side = with_settings((data, {**options, **pinned}), ({}, {}))\n    return placed({**data_side, **options_side})","    return with_settings((data, {**options, **pinned}), ({}, {}))","features"),
 "M9_paired_empty":(CF,"_PREFILL_PAIRED: Final = {CONF_SILENT_MODE_WINDOWS: CONF_SILENT_MODE_FRACTION}","_PREFILL_PAIRED: Final = {}","config_flow_steps"),
 "M10_reconf_no_options":(CF,"            data=data,\n            options=options,\n            unique_id=self.unique_id,","            data=data,\n            unique_id=self.unique_id,","config_flow_steps"),
 "M11_migrate_no_place":(IN,"            data=data,\n            options=options,\n            version=CONFIG_ENTRY_VERSION,","            version=CONFIG_ENTRY_VERSION,","entities"),
 "M12_uncapped_guard_off":(CF,"    if CONF_SILENT_MODE_WINDOWS not in errors:\n        errors.update(","    if False:\n        errors.update(","config_flow_steps"),
}
name=sys.argv[1]; f,old,new,suite=M[name]
wt=f"/root/mut/wt_{name}"
subprocess.run(["git","-C",R,"worktree","add","-q","--detach",wt,H],check=True)
p=pathlib.Path(wt,f); s=p.read_text(); n=s.count(old)
if n!=1: print(f"{name}: APPLY-FAIL count={n}"); sys.exit(9)
p.write_text(s.replace(old,new))
r=subprocess.run(["python3",f"tests/{suite}.py"],cwd=wt,env={**os.environ,"PYTHONPATH":"tests/hastub"},capture_output=True,text=True)
out=r.stdout+r.stderr
pathlib.Path(f"/root/mut/{name}.log").write_text(out)
fails=[l for l in out.splitlines() if "FAIL" in l][:12]
print(f"{name}: suite={suite} rc={r.returncode} last={out.strip().splitlines()[-1] if out.strip() else ''}")
for l in fails: print("   ",l[:220])
subprocess.run(["git","-C",R,"worktree","remove","--force",wt])
