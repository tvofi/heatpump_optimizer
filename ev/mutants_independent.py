import sys, subprocess, shutil, os, re
W, S = sys.argv[1], sys.argv[2]
HC="custom_components/heatpump_optimizer/heat_curve.py"
OR="custom_components/heatpump_optimizer/off_restore.py"
CF="custom_components/heatpump_optimizer/config_flow.py"
M = [
 ("R01 reserve +2 -> +1", HC, "writes_today(state, now) + 2 > budget", "writes_today(state, now) + 1 > budget"),
 ("R02 edit: no async_rebaseline", HC, "        await off_restore.async_rebaseline(hass, entry, CONSUMER, entity_id, baseline)\n", ""),
 ("R03 classify never missed", HC, 'return "missed" if previous is not None', 'return "missed" if False'),
 ("R04 _persistent_restored no-op", HC, '    if state.get("entity_id") != entity_id:\n        return\n    _record_write', '    return\n    _record_write'),
 ("R05 False write counts as sent", OR, "sent = await write(hass, entity_id, value) is not False", "sent = (await write(hass, entity_id, value)) or True"),
 ("R06 arm ignores entity change", OR, 'elif restorer.neutral is None and current["entity_id"] == restorer.entity_id:', 'elif restorer.neutral is None:'),
 ("R07 state never saved", OR, "    if held.consumers:  #", "    if False:  #"),
 ("R08 no state reset on entity change", HC, 'if state.get("entity_id") != entity_id:  # another', 'if False:  # another'),
 ("R09 dwell ignored", HC, 'if _age_s(state, now) < 60.0 * float', 'if False and _age_s(state, now) < 60.0 * float'),
 ("R10 forget warns nothing", OR, "        if isinstance(current, dict):\n            _LOGGER.warning(\"Removed", "        if False:\n            _LOGGER.warning(\"Removed"),
 ("R11 _entry_of drops mappings", OR, "    if isinstance(raw, Mapping):\n        entity_id, value", "    if False:\n        entity_id, value"),
 ("R12 edit baseline = reading", HC, 'baseline = reading.value - (state["written"] - baseline)', 'baseline = reading.value'),
 ("R13 persistent restorer as offset", HC, "    if config.heat_curve_target_kind == HEAT_CURVE_KIND_PERSISTENT:\n        return off_restore.Restorer(entity_id, write_setpoint, baseline_of", "    if False:\n        return off_restore.Restorer(entity_id, write_setpoint, baseline_of"),
 ("R14 flow: out-of-range accepted", CF, "        if heat_curve.outside_own_range(reading):\n            return {CONF_HEAT_CURVE_DISPLACE_ENTITY: \"heat_curve_out_of_range\"}", "        if False:\n            return {CONF_HEAT_CURVE_DISPLACE_ENTITY: \"heat_curve_out_of_range\"}"),
 ("R15 W3 latch off", HC, 'retry and bool(state.get("misses"))', 'False'),
 ("R16 misses never set", HC, 'state["misses"] = int(retry)', 'state["misses"] = 0'),
 ("R17 floor -> ceil (leaves band)", HC, "math.floor(abs(delta) / step + 1e-9)", "math.ceil(abs(delta) / step - 1e-9)"),
 ("R18 diagnostics persistent branch off", HC, "    if config.heat_curve_target_kind == HEAT_CURVE_KIND_PERSISTENT:\n        held_record", "    if False:\n        held_record"),
 ("R19 write_persistent keeps foreign armed", HC, "        armed = None  # the arm restores", "        pass  # the arm restores"),
 ("R20 W1 tolerance zero", HC, "    if abs(reading - target) <= half_step:\n        state[\"misses\"] = 0", "    if abs(reading - target) <= 0:\n        state[\"misses\"] = 0"),
 ("R21 send before record (no write-ahead)", HC, "    _record_write(state, target, now, reading)\n    state[\"misses\"] = int(retry)\n    await off_restore.async_save_state(hass, entry)\n    return await _send(hass, entry, entity_id, target)", "    ok = await _send(hass, entry, entity_id, target)\n    _record_write(state, target, now, reading)\n    state[\"misses\"] = int(retry)\n    await off_restore.async_save_state(hass, entry)\n    return ok"),
 ("R22 save_state never called", HC, "    await off_restore.async_save_state(hass, entry)\n    return await _send", "    return await _send"),
 ("R23 registered writer ignored", OR, "write = restorer.write if restorer is not None else _WRITERS.get(key)", "write = restorer.write if restorer is not None else None"),
 ("R24 restore baseline: no pop", OR, "        restorer.restored(entry, entity_id, value)\n    held.armed.pop(key)\n", "        restorer.restored(entry, entity_id, value)\n"),
]
sel = sys.argv[3:] 
for name, path, old, new in M:
    if sel and name.split()[0] not in sel: continue
    d = os.path.join(S, "mt"); shutil.rmtree(d, ignore_errors=True)
    shutil.copytree(W, d, ignore=shutil.ignore_patterns(".git"))
    p = os.path.join(d, path); src = open(p).read()
    n = src.count(old)
    if n != 1: print(f"{name}: APPLY-FAIL count={n}", flush=True); continue
    open(p, "w").write(src.replace(old, new))
    cmds = [["bash", os.path.join(S,"mcmd.sh"), d]]
    if path == CF: cmds.append(["bash","-c",f"cd {d} && env PYTHONPATH=tests/hastub python3 tests/config_flow_steps.py"])
    res=[]
    for c in cmds:
        r = subprocess.run(c, capture_output=True, text=True, timeout=900)
        out = r.stdout + r.stderr
        fails = [l for l in out.splitlines() if l.startswith("FAIL") or "FAILED" in l]
        res.append(f"rc={r.returncode} " + (fails[0][:150] if fails else out.strip().splitlines()[-1][:150] if out.strip() else ""))
    print(f"{name}: " + " || ".join(res), flush=True)
