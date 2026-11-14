import json,subprocess,sys
KEYS=["name","space_setpoint_unit","pv_production_entity","away_dhw_min_temperature","dhw_free_disinfection_enabled","vvc_pump_entity","main_fuse_amperes","open_window_relax_enabled"]
P="custom_components/heatpump_optimizer/"
FILES={"strings":P+"strings.json","en":P+"translations/en.json","de":P+"translations/de.json","sv":P+"translations/sv.json"}
def load(rev,f): return json.loads(subprocess.check_output(["git","show",f"{rev}:{f}"]))
def leaves(d,p=()):
    if isinstance(d,dict):
        for k,v in d.items(): yield from leaves(v,p+(k,))
    else: yield p,d
revs={"head":"a0784de9","t3561":"a117bad4^2","b3564":"d6a7b00b","base":sys.argv[1] if len(sys.argv)>1 else None}
for fn,f in FILES.items():
    H=dict(leaves(load("a0784de9",f)));T=dict(leaves(load("a117bad4^2",f)));B=dict(leaves(load("d6a7b00b",f)))
    for p,v in H.items():
        if "data_description" in p and p[-1] in KEYS:
            print(f"== {fn} {'.'.join(p)}")
            print("  HEAD :",v)
            print("  3561 :",T.get(p) if T.get(p)!=v else "(=head)")
            print("  3564 :",B.get(p) if B.get(p)!=v else "(=head)")
