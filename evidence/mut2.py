import subprocess, sys, pathlib
O="custom_components/heatpump_optimizer/optimizer.py"
M=[("P1-pump-bound-off",O,"    return bool(power_for_heat_per_cop_kw(p, made / cop) > p.max_electrical_power)","    return False"),
   ("P2-valve-bound-off",O,"    if mixing_valve.is_throttling(p.mixing_valve_mode) and need_kw > valve_top_draw(","    if False and need_kw > valve_top_draw("),
   ("P3-entry-off",O,"    if unreachable(held):\n","    if False:\n"),
   ("P4-bisect-step",O,"lo, hi = (lo, mid) if unreachable(held_at(mid)) else (mid, hi)","lo, hi = (lo, mid)"),
   ("P5-final-assign-drop",O,"        held = held_at(lo)\n","        pass\n"),
   ("P6-cop-nominal",O,"    cop = _reference_cop(model, held, outdoor, humidity)\n","    cop = p.cop_nominal_floored\n"),
   ("P7-humidity-none",O,"    humidity = None if weather.humidity is None else float(weather.humidity[0])\n","    humidity = None\n"),
   ("P8-made-is-need",O,"    return bool(power_for_heat_per_cop_kw(p, made / cop) > p.max_electrical_power)","    return bool(power_for_heat_per_cop_kw(p, need_kw / cop) > p.max_electrical_power)"),
   ("P9-lo-outdoor",O,"        lo, hi = min(outdoor, target), target\n","        lo, hi = outdoor, target\n"),
   ("NULL",O,"        # Zones level at their own temperature: no pull-back, the steady need.","        # edited comment"),
]
cmd='PYTHONPATH=tests/hastub python3 tools/audit/seat/features_block.py "# --- R10-SAV-VALUATION-RESIDUE: stored heat" "# --- R10-WATER-SETPOINT-FEEDBACK"'
for name,f,old,new in M:
    p=pathlib.Path(f); src=p.read_text(); assert src.count(old)==1,(name,src.count(old))
    p.write_text(src.replace(old,new))
    try:
        r=subprocess.run(cmd,shell=True,capture_output=True,text=True)
        out=r.stdout+r.stderr
        fails=[l.strip()[:110] for l in out.splitlines() if l.strip().startswith("FAIL")]
        last=[l for l in out.splitlines() if "BLOCK" in l or "Error" in l][-1:]
        print(f"RESULT {name}: rc={r.returncode} {last} {fails}", flush=True)
    finally:
        p.write_text(src)
