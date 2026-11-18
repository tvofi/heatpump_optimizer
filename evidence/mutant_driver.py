import subprocess, sys, os, json
WT=os.environ.get("WT",os.path.expanduser("~/wt")); env=dict(os.environ, PYTHONPATH="tests/hastub")
A=['python3','tools/audit/seat/features_block.py','--prelude','from datetime import datetime','--prelude','NOW = datetime(2026, 2, 1, 12, 0, tzinfo=UTC)','--prelude','from heatpump_optimizer import const as _r9f41_const','R.section("Non-numeric inputs (v5.3.0)")','R.section("Heat pump operating mode (v5.3.0)")']
P8=['python3','tools/audit/seat/features_block.py','--prelude','from heatpump_optimizer import const as _r9f41_const','R.section("P8 — a price or temperature entity\'s unit is read at the seam (#1513)")','R.section("R8-P8 round 3: mutation survivors on lines this diff\'s files carry")']
E=['python3','tests/entities.py']; OM=['python3','tests/open_meteo.py']; WA=['python3','tests/wood_advisor.py']
CC='custom_components/heatpump_optimizer/'
M=[
("none",None,None,None,[A,P8,OM,WA]),
("M1 parse_bool raw float",CC+"inputs.py","    number = finite_float(token)\n    return None if number is None else number != 0.0","    try:\n        return float(token) != 0.0\n    except (TypeError, ValueError):\n        return None",[A]),
("M2 _begin guard off",CC+"inputs.py","        if not isinstance(entity_id, str):\n            entity_id = None\n","",[A]),
("M3 kept all",CC+"open_meteo.py","kept = [i for i, t in enumerate(times) if t >= floor]","kept = list(range(len(times)))",[OM]),
("M4 repairs empty",CC+"__init__.py","repairs = number_repairs({**entry.data, **entry.options})","repairs = {}",[E]),
("M5 lead not defaulted",CC+"entry_config.py","finite_float, _nonzero_number, _interval_minutes, _lead_minutes,","finite_float, _nonzero_number, _interval_minutes,",[E]),
("M6 wood raw",CC+"wood_fuel.py","lead = EntryConfig.from_mapping(config).wood_lighting_lead_minutes","lead = max(0.0, finite_float(config.get('wood_lighting_lead_minutes'), 60.0))",[WA]),
("M7 interval guard off",CC+"entry_config.py","    if minutes is None or not 0.0 < minutes <= _MAX_PLAN_MINUTES:\n        return default","    if minutes is None:\n        return default",[E]),
("M8 temp_from_c",CC+"inputs.py","    return value_c / factor - offset","    return value_c * factor - offset",[P8]),
("M9 plausible one-sided",CC+"inputs.py","return window is None or window[0] <= value_c <= window[1]","return window is None or window[0] <= value_c",[A]),
("M10 bool branch off",CC+"entry_config.py","(isinstance(value := stored[f.name], bool) or not isinstance(value, (int, float)))","(not isinstance(value := stored[f.name], (int, float)))",[E]),
("M11 None not dropped",CC+"entry_config.py","if key not in repairs or repairs[key] is not None","if True",[E]),
("M12 lt2 to lt1",CC+"open_meteo.py","    if len(kept) < 2:\n        return _EMPTY\n\n    return IrradianceSeries","    if len(kept) < 1:\n        return _EMPTY\n\n    return IrradianceSeries",[OM]),
("M13 lead floor strict",CC+"entry_config.py","not 0.0 <= minutes <= _MAX_PLAN_MINUTES","not 0.0 < minutes <= _MAX_PLAN_MINUTES",[WA]),
("M14 mixing undeclared",CC+"entry_config.py","    mixing_valve_target: float = _key(const.DEFAULT_MIXING_VALVE_TARGET, finite_float)\n","",[E]),
]
sel=sys.argv[1:]
for name,f,old,new,cmds in M:
    if sel and name.split()[0] not in sel: continue
    if not cmds: continue
    if f:
        p=os.path.join(WT,f); src=open(p).read(); assert src.count(old)==1,(name,src.count(old)); open(p,'w').write(src.replace(old,new))
    try:
        for c in cmds:
            r=subprocess.run(c,cwd=WT,env=env,capture_output=True,text=True,timeout=1500)
            out=(r.stdout+r.stderr).strip().splitlines()
            fails=[l for l in out if l.lstrip().startswith(('FAIL','✗')) or 'temperature_from_c inverts' in l or 'plausible window refuses' in l][:3]
            print(f"{name} | {' '.join(c[1:2]) if 'block' not in c[1] else c[2][:30]} | rc={r.returncode} | last={out[-1][:150] if out else ''} | fails={fails}",flush=True)
    finally:
        if f: open(p,'w').write(src)
    st=subprocess.run(['git','status','--porcelain'],cwd=WT,capture_output=True,text=True).stdout.strip()
    print(f"  status-after: '{st}'",flush=True)
