import sys, json, subprocess
from pathlib import Path
root=Path(sys.argv[1]).resolve(); tdir=Path(sys.argv[2]); out=Path(sys.argv[3])
sys.path.insert(0,str(root/"tools/ci")); import selftest_scope as s
steps=s.workflow_steps(root)
measured,broken=s.fold(tdir,steps,root)
json.dump(measured,open(out,"w"),indent=1,sort_keys=True)
print("measured",len(measured),"broken",len(broken)); [print(" ",b) for b in broken]
for name,rev in (("MAIN 2b4515dc","2b4515dc52821ad721225090d329c224dbddafae"),("HEAD f5a2c9cb","f5a2c9cba6b6bab1242e381bed5b2960043eb45f")):
    t=json.loads(subprocess.check_output(["git","-C",str(root),"show",rev+":tools/ci/selftest_closures.json"]))
    ref,notes=s.drift(t,measured,steps)
    ref=[r for r in ref if not r.startswith("UNMEASURED")]
    print(f"== {name}: {len(ref)} refusal(s) over {len(measured)} measured step(s)")
    for r in ref: print("  ",r)
