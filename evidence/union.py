import json,subprocess,sys
KEYS={"name","space_setpoint_unit","pv_production_entity","away_dhw_min_temperature","dhw_free_disinfection_enabled","vvc_pump_entity","main_fuse_amperes","open_window_relax_enabled"}
P="custom_components/heatpump_optimizer/"
mb=sys.argv[1]
def L(rev,f):
    try: d=json.loads(subprocess.check_output(["git","show",f"{rev}:{P}{f}"],stderr=subprocess.DEVNULL))
    except subprocess.CalledProcessError: return {}
    out={}
    def w(x,p):
        if isinstance(x,dict):
            for k,v in x.items(): w(v,p+(k,))
        else: out[p]=x
    w(d,()); return out
tot=0
for f in ["strings.json","translations/en.json","translations/de.json","translations/sv.json"]:
    H,T,B,M=L("a0784de9",f),L("a117bad4^2",f),L("d6a7b00b",f),L(mb,f)
    bad=[];both=[];eight=0
    for p in set(H)|set(T)|set(B):
        h,t,b,m=H.get(p),T.get(p),B.get(p),M.get(p)
        if "data_description" in p and p[-1] in KEYS and t!=b:
            eight+=1; continue
        if t!=m and b!=m and t!=b: both.append(p)
        # expected: if only branch changed -> b; else t
        exp = b if (t==m) else t
        if h!=exp: bad.append((p,h,t,b))
    print(f"RESULT {f}: leaves={len(H)} eight-conflict-leaves={eight} other both-changed={len(both)} mismatches={len(bad)}")
    for x in bad[:5]: print("  ",x)
    for x in both: print("  BOTH",x)
