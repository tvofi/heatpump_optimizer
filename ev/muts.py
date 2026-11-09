import sys, subprocess, os
T="custom_components/heatpump_optimizer/thermal_model.py"; O="custom_components/heatpump_optimizer/optimizer.py"; B="custom_components/heatpump_optimizer/battery.py"
M=[
("R1 combi_tank_active ignores the option",T,"self.dhw_combi_tank_enabled and self.dhw_enabled","self.dhw_enabled"),
("R2 potable volume dropped",T,"return self.buffer_tank_volume + self.combi_potable_volume_l","return self.buffer_tank_volume"),
("R3 charge-limit min dropped",T,"p.buffer_store_volume, min(p.dhw_max_temp, p.buffer_max_temp),","p.buffer_store_volume, p.dhw_max_temp,"),
("R4 eps cap at 1 dropped",T,"eps = min(1.0, eps) if eps","eps = eps if eps"),
("R5 draw debited at store temp",T,"    draw = draw_nominal_kw * dhw_draw_scale(store.tap_temp_for_store(temp), store.inlet_c)","    draw = draw_nominal_kw * dhw_draw_scale(temp, store.inlet_c)"),
("R6 refused heat not booked",T,"refused, d_temp = (d_temp - cap) * capacity, cap","refused, d_temp = 0.0, cap"),
("R7 injected heat not booked",T,"injected, new_temp = (floor - new_temp) * capacity / max(dt_hours, 1e-6), floor","injected, new_temp = 0.0, floor"),
("R8 exchange rounds 1",O,"_COMBI_EXCHANGE_ROUNDS = 4","_COMBI_EXCHANGE_ROUNDS = 1"),
("R9 battery keeps dhw_tank in combi",B,"if params.dhw_enabled and not store.combi:","if params.dhw_enabled:"),
("R10 exchange skipped",O,"if draw_rates is not None and self.model.params.dhw_store.combi:","if False:"),
("R11 floor ignores ambient",T,"floor = min(store.inlet_c, ambient_temp)","floor = store.inlet_c"),
("R12 tap transform identity in combi",T,"return self.inlet_c + self.effectiveness * (store_c - self.inlet_c)","return store_c"),
("R13 space_flux live off combi",T,"return space_net_kw if self.combi else None","return space_net_kw"),
]
sel=sys.argv[2:] 
for name,f,old,new in M:
    if sel and name.split()[0] not in sel: continue
    src=open(f).read(); n=src.count(old)
    if n!=1: print(f"{name}: SKIP count={n}"); continue
    open(f,"w").write(src.replace(old,new))
    try:
        r=subprocess.run(["timeout","300","python3",sys.argv[1]],capture_output=True,text=True,env=dict(os.environ,PYTHONPATH="tests/hastub:tests:custom_components"))
        fails=[l.strip()[:120] for l in r.stdout.splitlines() if l.startswith("  FAIL") or l.startswith("EXC")]
        print(f"{name}: rc={r.returncode} {'KILLED' if r.returncode else 'SURVIVED'} fails={len(fails)}"); [print("   ",x) for x in fails[:4]]
        sys.stdout.flush()
    finally:
        open(f,"w").write(src)
