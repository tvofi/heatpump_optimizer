import subprocess, sys, pathlib
R = pathlib.Path("/home/user/rv"); C = "custom_components/heatpump_optimizer/"
M = [
 ("A can_duty_cycle on_off early return deleted", C+"thermal_model.py", "        if self.on_off:\n            return False\n", ""),
 ("B probe on_off never set", C+"thermal_model.py", "on_off=declared_modulation(cfg) is False,", "on_off=False,"),
 ("C cap ignores DHW", C+"thermal_model.py", "float(p_min) - other, float(p_max) - other", "float(p_min) - other, float(p_max) - 0 * other"),
 ("D raise ignores DHW", C+"thermal_model.py", "float(p_min) - other, float(p_max) - other", "float(p_min), float(p_max) - other"),
 ("E joint returns per-channel space", C+"optimizer.py", "return project_space_against(space, tank, p_min, p_max), tank", "return project_planned_levels(space, p_min, p_max), tank"),
 ("F space against raw (unprojected) DHW", C+"optimizer.py", "return project_space_against(space, tank, p_min, p_max), tank", "return project_space_against(space, dhw, p_min, p_max), tank"),
 ("G DHW shipped unprojected", C+"optimizer.py", "return project_space_against(space, tank, p_min, p_max), tank", "return project_space_against(space, tank, p_min, p_max), dhw"),
 ("H legacy true ignored", C+"thermal_model.py", "        else False if legacy is True\n", ""),
 ("I modulating select ignored", C+"thermal_model.py", "        else True if mode == const.COMPRESSOR_MODULATION_MODULATING\n", ""),
 ("J duty_cycle_realizable opt-out on any declaration", C+"thermal_model.py", "        if declared_modulation(cfg) is True\n        else True if cap.fully_metered()", "        if declared_modulation(cfg) is not None\n        else True if cap.fully_metered()"),
 ("K publish reverted to space-only projection, DHW raw", C+"optimizer.py", "        optimal_space, optimal_dhw = _realize_joint(\n            self.config.clamp_planned_levels, optimal_space, optimal_dhw,\n            p_min, p_max,\n        )", "        optimal_space = _published_levels(self.config.clamp_planned_levels, optimal_space, p_min, p_max)"),
 ("L _realize_joint ignores clamp", C+"optimizer.py", "    if not clamp:\n        return space, dhw\n    tank", "    tank"),
]
cmd = sys.argv[1]
for name, f, old, new in M:
    p = R/f; src = p.read_text(); assert src.count(old) == 1, name
    p.write_text(src.replace(old, new, 1))
    try:
        r = subprocess.run(cmd, shell=True, cwd=R, capture_output=True, text=True, timeout=1800)
        fails = [l for l in r.stdout.splitlines() if l.lstrip().startswith("FAIL")]
        print(f"{name}: rc={r.returncode} fails={len(fails)}" + ("".join("\n    "+l.strip()[:150] for l in fails[:6])), flush=True)
    finally:
        p.write_text(src)
st = subprocess.run("git status --porcelain", shell=True, cwd=R, capture_output=True, text=True).stdout
print("git status clean:", st.strip() == "")
