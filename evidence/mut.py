import subprocess, sys, pathlib
W = pathlib.Path(sys.argv[1])
OPT = W/"custom_components/heatpump_optimizer/optimizer.py"
TM = W/"custom_components/heatpump_optimizer/thermal_model.py"
M = [
 ("drop-valve-top-call", OPT, "held = _held_at_valve_top(model, held, need(held), weather0, humidity) or _held_bisected(", "held = None or _held_bisected("),
 ("ignore-pump-bound", OPT, "return None if _pump_unreachable(model, top, made, outdoor, humidity) else top", "return top"),
 ("drop-need-gt-topdraw", OPT, "            and need_kw > valve_top_draw(model, held, outdoor, wind, rain)):", "            ):"),
 ("drop-throttling", OPT, "if not (p.two_zone_enabled and mixing_valve.is_throttling(p.mixing_valve_mode)", "if not (p.two_zone_enabled"),
 ("drop-two-zone", OPT, "if not (p.two_zone_enabled and mixing_valve.is_throttling", "if not (True and mixing_valve.is_throttling"),
 ("guard-off-eq", TM, "    if upper >= t_rad or slab >= t_floor:\n        return None", "    if False:\n        return None"),
 ("guard-upper-only", TM, "    if upper >= t_rad or slab >= t_floor:", "    if upper >= t_rad:"),
 ("guard-slab-only", TM, "    if upper >= t_rad or slab >= t_floor:", "    if slab >= t_floor:"),
 ("clamp-drop-rad", TM, "t_rad, t_floor = min(top_rad, p.buffer_max_temp), min(top_floor, p.buffer_max_temp)", "t_rad, t_floor = top_rad, min(top_floor, p.buffer_max_temp)"),
 ("clamp-drop-floor", TM, "t_rad, t_floor = min(top_rad, p.buffer_max_temp), min(top_floor, p.buffer_max_temp)", "t_rad, t_floor = min(top_rad, p.buffer_max_temp), top_floor"),
 ("room-mean-upper-only", TM, "room_temperature=float(upper * p.upper_floor_area_ratio\n                               + lower * (1.0 - p.upper_floor_area_ratio)),", "room_temperature=float(upper),"),
 ("made-dt-zero", OPT, "outdoor, wind, rain, math.inf)", "outdoor, wind, rain, 0.25)"),
 ("top-none-guard-off", OPT, "    if top is None:\n        return None\n    # A steady", "    # A steady"),
 ("x0-origin-zero", TM, "x0 = np.array([state.upper_floor_temperature, state.lower_floor_temperature, state.slab_temperature])", "x0 = np.zeros(3)"),
]
CMD = ["python3","tools/audit/seat/features_block.py","# --- R10-SAV-VALUATION-RESIDUE: stored heat bought back","# --- R10-WATER-SETPOINT-FEEDBACK (outside report #3380"]
env = {**__import__("os").environ, "PYTHONPATH":"tests/hastub:tests:custom_components"}
def run():
    r = subprocess.run(CMD, cwd=W, env=env, capture_output=True, text=True, timeout=200)
    out = r.stdout + r.stderr
    last = [l for l in out.splitlines() if "FEATURES BLOCK" in l or "Error" in l][-1:] 
    fails = [l.strip()[:110] for l in out.splitlines() if l.strip().startswith("FAIL")]
    return r.returncode, (last[0] if last else out[-200:]), fails
rc, last, _ = run(); print(f"RESULT NULL rc={rc} {last}")
for name, f, old, new in M:
    src = f.read_text()
    if src.count(old) != 1: print(f"RESULT {name} NOT-APPLIED count={src.count(old)}"); continue
    f.write_text(src.replace(old, new))
    try:
        rc, last, fails = run()
    finally:
        f.write_text(src)
    print(f"RESULT {name} {'KILLED' if rc else 'SURVIVED'} rc={rc} {last}")
    for x in fails: print("    ", x)
rc, last, _ = run(); print(f"RESULT NULL-after rc={rc} {last}")
