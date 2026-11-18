import subprocess, sys, os
W="/home/user/wt-mut"; S=os.environ["S"]; P="custom_components/heatpump_optimizer/"
B1=('R.section("Non-numeric inputs (v5.3.0)")','R.section("Heat pump operating mode (v5.3.0)")',S+"/pre1.py")
B2=('R.section("P8 — a price or temperature entity\'s unit is read at the seam (#1513)")','R.section("R8-P8 round 3: mutation survivors on lines this diff\'s files carry")',S+"/pre2.py")
def fb(b): return ["python3","tools/audit/seat/features_block.py","--prelude",f"exec(open('{b[2]}').read())",b[0],b[1]]
ENT=["python3","tests/entities.py"]; OM=["python3","tests/open_meteo.py"]
M=[
 ("M1 parse_bool float revert","inputs.py","    number = finite_float(token)\n    return None if number is None else number != 0.0","    try:\n        return float(token) != 0.0\n    except (TypeError, ValueError):\n        return None",fb(B1)),
 ("M2 _begin str guard deleted","inputs.py","        if not isinstance(entity_id, str):\n            entity_id = None\n","",fb(B1)),
 ("M3 open_meteo kept=all","open_meteo.py","kept = [i for i, t in enumerate(times) if t >= floor]","kept = list(range(len(times)))",OM),
 ("M4 migrate repairs={}","__init__.py","repairs = number_repairs({**entry.data, **entry.options})","repairs = {}",ENT),
 ("M5 number_repairs all None","entry_config.py","        f.name: finite_float(value)\n","        f.name: None\n",ENT),
 ("M6 interval guard off","entry_config.py","if minutes is None or not 0.0 < minutes <= _MAX_INTERVAL_MINUTES:","if minutes is None:",ENT),
 ("M7 mixing_valve_target field removed","entry_config.py","    mixing_valve_target: float = _key(const.DEFAULT_MIXING_VALVE_TARGET, finite_float)\n","",ENT),
 ("M8 bool branch of number_repairs dropped","entry_config.py","and (isinstance(value := stored[f.name], bool) or not isinstance(value, (int, float)))","and (not isinstance(value := stored[f.name], (int, float)))",ENT),
 ("M9 _interval_minutes dropped from _DEFAULTED_NUMBERS","entry_config.py","(finite_float, _nonzero_number, _interval_minutes)","(finite_float, _nonzero_number)",ENT),
 ("M10 D7 pin temperature_from_c multiplies","inputs.py","    return value_c / factor - offset","    return value_c * factor - offset",fb(B2)),
 ("M11 D2 pin minor /100 removed","inputs.py","        return value * per_kwh / 100.0","        return value * per_kwh",fb(B2)),
 ("M12 D1-s2-51 pin plausible_c one-sided","inputs.py","window[0] <= value_c <= window[1]","window[0] <= value_c",fb(B1)),
 ("M13 open_meteo floor off by resolution","open_meteo.py","floor = datetime.min.replace(tzinfo=timezone.utc) + resolution","floor = datetime.min.replace(tzinfo=timezone.utc)",OM),
 ("M14 open_meteo <2 -> <1","open_meteo.py","if len(kept) < 2:","if len(kept) < 1:",OM),
]
sel=sys.argv[1:]
for name,f,old,new,cmd in M:
    if sel and name.split()[0] not in sel: continue
    fp=os.path.join(W,P,f); src=open(fp).read()
    if src.count(old)!=1: print(f"{name}: ANCHOR count={src.count(old)}",flush=True); continue
    open(fp,"w").write(src.replace(old,new))
    try:
        r=subprocess.run(cmd,cwd=W,capture_output=True,text=True,timeout=3000)
        out=r.stdout+r.stderr
        fails=[l.strip() for l in out.splitlines() if "FAIL" in l or "Error" in l][:4]
        print(f"{name}: rc={r.returncode} {'KILLED' if r.returncode else 'SURVIVED'} :: {' | '.join(fails)[:600]}",flush=True)
    finally:
        open(fp,"w").write(src)
st=subprocess.run(["git","status","--porcelain"],cwd=W,capture_output=True,text=True).stdout
print("porcelain:",repr(st))
