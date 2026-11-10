import json,subprocess,sys,os
D="custom_components/heatpump_optimizer/"
M=[
("M2 tank_levels combi branch off","coordinator.py","    if combi:\n        level = combi_tank_seed","    if False:\n        level = combi_tank_seed","F"),
("M3 seed skips dhw probe","coordinator.py",'else _seed_store(dhw, result, "buffer_temp_trajectory", now)','else _seed_store(buffer, result, "buffer_temp_trajectory", now)',"F"),
("M4 learner gate dropped","coordinator.py","tank is not None and not combi and (frozen","tank is not None and (frozen","F"),
("M5 > to >=","thermal_model.py","> const.COMBI_LEGIONELLA_POTABLE_LIMIT_L",">= const.COMBI_LEGIONELLA_POTABLE_LIMIT_L","F"),
("M6 force term dropped","thermal_model.py","\n            or self.dhw_combi_legionella_force\n","\n","F"),
("M7r (reviewer's) not combi_tank_active disjunct dropped","thermal_model.py","not self.dhw_combi_tank_enabled or not self.combi_tank_active","not self.dhw_combi_tank_enabled","F"),
("M8 rating reads raw flag","thermal_model.py","        if self.legionella_cycle_active:\n            top = max(top, self.dhw_legionella_temp)","        if self.dhw_legionella_enabled:\n            top = max(top, self.dhw_legionella_temp)","F"),
("M10 combi edge from pump","topology.py",'("buffer_tank" if combi else "heat_pump", "dhw_tank")','("heat_pump", "dhw_tank")',"F"),
("M11 dhw_source always tank","topology.py",'"dhw_source": "combi" if p.combi_tank_active else "tank"','"dhw_source": "tank"',"F"),
("M12 advisor combi zero dropped","topology.py","if config.get(CONF_DHW_TEMP_ENTITY) or _combi_store_probed(config)","if config.get(CONF_DHW_TEMP_ENTITY)","F"),
("M13 prefill on kept type","config_flow.py","if preset is not None and kind != stored.get(CONF_DHW_COMBI_TANK_TYPE, DEFAULT_DHW_COMBI_TANK_TYPE):","if preset is not None:","F"),
("M15 combi_needs_store refusal off","config_flow.py","if merged.get(CONF_DHW_COMBI_TANK_ENABLED) and not params.combi_tank_active:","if False:","C"),
]
only=sys.argv[1:]
for name,f,old,new,kind in M:
    if only and name.split()[0] not in only: continue
    p=D+f; s=open(p,encoding="utf-8").read(); n=s.count(old)
    if n!=1: print(f"RESULT {name}: SKIP old occurs {n}x",flush=True); continue
    open(p,"w",encoding="utf-8").write(s.replace(old,new))
    try:
        if kind=="F":
            cmd=["timeout","1800","python3","tools/audit/seat/features_block.py","--through","# --- R10-HOTFIX-LEARNER-INPUTS"]; env=dict(os.environ)
        else:
            cmd=["timeout","900","python3","tests/config_flow_steps.py"]; env=dict(os.environ,PYTHONPATH="tests/hastub")
        r=subprocess.run(cmd,capture_output=True,text=True,env=env)
        out=r.stdout+r.stderr
        fails=[l.strip() for l in out.splitlines() if l.strip().startswith("FAIL")]
        tail=[l for l in out.splitlines() if l.strip()][-1:]
        print(f"RESULT {name}: rc={r.returncode} fails={len(fails)} last={tail}",flush=True)
        for l in fails[:4]: print("   ",l[:240],flush=True)
    finally:
        subprocess.run(["git","checkout","--",p])
print("DONE",subprocess.run(["git","status","--short","custom_components"],capture_output=True,text=True).stdout or "clean",flush=True)
