import subprocess, sys, pathlib
W=sys.argv[1]; root=pathlib.Path(W)/"wt"
CO="custom_components/heatpump_optimizer/coordinator.py"; EC="custom_components/heatpump_optimizer/early_cutoff.py"
M=[(CO,"return supply_hold.FREEZE_HELD","pass","learners not frozen on a held interval"),
   (EC,"return tank_reason(inp)","return None","early cut-off ignores tank exemption"),
   (EC,"if run is None or run < MIN_ON:","if run is not None and run < MIN_ON:","early cut-off cuts a run of unknown age")]
for f,a,b,why in M:
    p=root/f; s=p.read_text(); n=s.count(a)
    if n!=1: print("NOMATCH",n,a); continue
    p.write_text(s.replace(a,b,1))
    try:
        r=subprocess.run(["bash",f"{W}/mutant_cmd.sh"],capture_output=True,text=True,timeout=200)
        print(("KILLED  " if r.returncode else "SURVIVED"), f.split('/')[-1], repr(a), "->", repr(b), "|", why, "|", r.stdout.strip().splitlines()[-1][:150])
    finally: p.write_text(s)
