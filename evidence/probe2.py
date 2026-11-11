import subprocess,sys,os
os.chdir(sys.argv[1]); f="tests/block_duty.py"; src=open(f).read()
anchor='    check(\n        "a disinfection temperature above the entity\'s range stays bounded'
assert src.count(anchor)==1
st='{"min": 30, "max": 65, "step": 5}'
probe=(f'    print("RESULT probe held cycle, everyday 57 > disinfection 50, step 5: write", written(_dhw_snap(disinfecting=True, configured=57.0, disinfection=50.0, attrs={st}), "dhw"))\n'
       f'    print("RESULT probe booked cycle, same install: write", written(_dhw_snap(action={{"dhw_reason": "legionella"}}, configured=57.0, disinfection=50.0, attrs={st}), "dhw"))\n'
       f'    print("RESULT probe null, no cycle, same install: write", written(_dhw_snap(configured=57.0, disinfection=50.0, attrs={st}), "dhw"))\n')
open(f,"w").write(src.replace(anchor,probe+anchor))
try:
    p=subprocess.run([sys.executable,f],capture_output=True,text=True,env=dict(os.environ,PYTHONPATH="tests/hastub:custom_components:tests"))
    print("\n".join(l for l in (p.stdout+p.stderr).splitlines() if "RESULT probe" in l or "Error" in l))
finally: open(f,"w").write(src)
