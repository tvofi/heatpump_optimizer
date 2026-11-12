import subprocess, sys, pathlib
O="custom_components/heatpump_optimizer/optimizer.py"; T="custom_components/heatpump_optimizer/thermal_model.py"
M=[("M1",O,"    if short(held) > 0.0:","    if False:"),
   ("M2",O,"lo, hi = (lo, mid) if short(_held_zones(model, state, weather0, mid)) > 0.0 else (mid, hi)","lo, hi = (lo, mid)"),
   ("M3",T,"    return _circuit_draw(circuits, model.params.buffer_max_temp)\n\n\ndef valve_charge_demand","    return float('inf')\n\n\ndef valve_charge_demand"),
   ("M4",O,"    if short(held) > 0.0:","    if True:"),
   ("M5-own-drop-final-assign",O,"        held = _held_zones(model, state, weather0, lo)\n","        pass\n"),
   ("M6-own-need-at-target",O,"zoned(model, h, h.room_temperature, *weather0","zoned(model, h, target, *weather0"),
   ("M7-own-held_need-old",O,"    held_need = need(held)\n","    held_need = need(_held_zones(model, state, weather0, target))\n"),
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
        print(f"RESULT {name}: rc={r.returncode} {last} {fails}")
    finally:
        p.write_text(src)
